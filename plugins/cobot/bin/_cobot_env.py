"""The machine's development environment by presence, and the owner's answers per host (decision 29).

Detection reads files and environment variables only. It never runs a program, so nothing a
repository chooses runs: not a binary on a PATH entry it controls, not a mise or asdf shim, not a
direnv hook. A hit on a PATH entry under the repository root or a relative entry is not trusted;
a hit in a shims folder is reported as a shim (a tool the owner installed, at the version the
repository pins). Neither is followed: no link resolved, no file read. Nothing detected is
stored; the profile holds only what the owner answered.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import socket
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

ENGINES = ("docker", "podman")
MANAGERS = {"mise": ("mise",), "asdf": ("asdf",)}
ISOLATION = {
    "distrobox": ("distrobox", "distrobox-enter"),
    "toolbox": ("toolbox",),
    "nix": ("nix",),
    "devcontainer": ("devcontainer",),
}
PACKAGE_MANAGERS = {
    "apt": ("apt-get", "apt"),
    "dnf": ("dnf",),
    "pacman": ("pacman",),
    "zypper": ("zypper",),
    "apk": ("apk",),
    "brew": ("brew",),
}
# the curated helpers cobot benefits from (skills/onboard/references/workstation.md), by command
HELPERS = {"rtk": ("rtk",), "ripgrep": ("rg",), "fd": ("fd", "fdfind"), "jq": ("jq",), "gh": ("gh",)}
REPOSITORY_FILES = (
    "Containerfile",
    "Dockerfile",
    "compose.yaml",
    "compose.yml",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".mise.toml",
    "mise.toml",
    ".tool-versions",
    "distrobox.ini",
    ".devcontainer",
)
ROUTES = ("mise", "brew", "apt", "dnf", "pacman", "zypper", "apk", "nix", "distrobox")
OTHER_ENGINES = ("podman", "colima", "orbstack")  # what a docker socket or context may name
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
PROGRAM_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}")
KEY_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,252}(/[A-Za-z0-9][A-Za-z0-9._-]{0,63})?")
SCRIPT_HEAD = 1024  # bytes of a trusted docker wrapper read to see whether it execs podman
BRIEF_CAP = 160
VIA_REPOSITORY = "repository"
NOT_RECORDED = "answer not recorded:"
PROFILE_HEAD = (
    "# cobot machine profile\n\n"
    "The owner's answers per host or host/container, written by `cobot-env prefer` and\n"
    "`cobot-env decline`. Lines you add are kept. Nothing detected is stored here.\n"
)


class NotRecorded(Exception):
    """The profile could not be written (Claude Code's sandbox keeps the config directory read-only
    to Bash); the message names the command for the owner's own terminal."""


@dataclass(frozen=True)
class Hit:
    name: str
    path: str
    via: str  # "" on a trusted entry, else where the entry came from


def described(hit: Hit) -> str:
    return f"{hit.name} via {hit.via}" if hit.via else hit.name


def shown(hit: Hit | None) -> str | None:
    """A lookup's value in the report: the path, ``via <where> (<path>)`` when untrusted, None."""
    if hit is None:
        return None
    return f"via {hit.via} ({hit.path})" if hit.via else hit.path


# ---------------------------------------------------------------- PATH, by presence


def find_root(cwd: Path) -> Path:
    """The nearest folder holding ``.git`` (a folder or a worktree's file); cwd when none. No git
    call: git itself could be a program the repository chooses."""
    for folder in (cwd, *cwd.parents):
        if (folder / ".git").exists():
            return folder
    return cwd


def shim_folders(env: Mapping[str, str]) -> dict[Path, str]:
    home = Path(env.get("HOME") or Path.home())
    data = Path(env.get("XDG_DATA_HOME") or home / ".local" / "share")
    mise = Path(env["MISE_DATA_DIR"]) if env.get("MISE_DATA_DIR") else data / "mise"
    asdf = Path(env["ASDF_DATA_DIR"]) if env.get("ASDF_DATA_DIR") else home / ".asdf"
    return {mise / "shims": "mise shim", asdf / "shims": "asdf shim"}


def classify(entry: str, cwd: Path, root: Path, shims: dict[Path, str]) -> tuple[Path, str]:
    """A PATH entry as the folder the shell would search and why it is not trusted ("" if it is)."""
    if not entry or not os.path.isabs(entry):
        return cwd / entry, VIA_REPOSITORY
    folder = Path(entry)
    real = Path(os.path.realpath(folder))
    if real == root or root in real.parents or folder == root or root in folder.parents:
        return folder, VIA_REPOSITORY
    for shim, label in shims.items():
        if folder == shim or real == Path(os.path.realpath(shim)) or folder.parts[-2:] == shim.parts[-2:]:
            return folder, label
    return folder, ""


class Scanner:
    """Looks names up along PATH as the shell would, remembering every untrusted hit."""

    def __init__(self, cwd: Path, env: Mapping[str, str]) -> None:
        root = Path(os.path.realpath(find_root(cwd)))
        shims = shim_folders(env)
        self.entries = [classify(e, cwd, root, shims) for e in env.get("PATH", "").split(os.pathsep)]
        self.untrusted: list[Hit] = []  # repository and relative entries: never run
        self.shims: list[Hit] = []  # shims folders: never followed by detection, runnable

    def find(self, name: str) -> Hit | None:
        for folder, via in self.entries:
            candidate = folder / name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                hit = Hit(name, str(candidate), via)
                seen = self.untrusted if via == VIA_REPOSITORY else self.shims
                if via and hit not in seen:
                    seen.append(hit)
                return hit
        return None

    def first(self, names: tuple[str, ...]) -> Hit | None:
        for name in names:
            hit = self.find(name)
            if hit:
                return hit
        return None


# ---------------------------------------------------------------- engines


def docker_is_podman(path: str) -> bool:
    """A trusted ``docker`` that is podman: a link to it, or podman-docker's wrapper script."""
    if Path(os.path.realpath(path)).name.startswith("podman"):
        return True
    try:
        with open(path, "rb") as handle:
            head = handle.read(SCRIPT_HEAD)
    except OSError:
        return False
    return head.startswith(b"#!") and b"podman" in head


def named_engine(text: str) -> str:
    lowered = text.lower()
    return next((name for name in OTHER_ENGINES if name in lowered), "")


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def context_endpoint(env: Mapping[str, str]) -> str:
    """The engine the current docker context names, by its name or its endpoint host."""
    home = Path(env.get("HOME") or Path.home())
    config = Path(env["DOCKER_CONFIG"]) if env.get("DOCKER_CONFIG") else home / ".docker"
    context = env.get("DOCKER_CONTEXT") or read_json(config / "config.json").get("currentContext")
    if not isinstance(context, str) or not context or context == "default":
        return ""
    if named_engine(context):
        return named_engine(context)
    digest = hashlib.sha256(context.encode()).hexdigest()
    meta = read_json(config / "contexts" / "meta" / digest / "meta.json")
    host = ((meta.get("Endpoints") or {}).get("docker") or {}).get("Host")
    return named_engine(host) if isinstance(host, str) else ""


def docker_endpoint(env: Mapping[str, str]) -> str:
    return named_engine(env.get("DOCKER_HOST", "")) or context_endpoint(env)


def engines(docker: Hit | None, podman: Hit | None, endpoint: str) -> list[str]:
    """One entry per engine: docker that is podman, or talks to a podman socket, counts once."""
    found: list[str] = []
    if docker is not None:
        if docker.via:
            found.append(described(docker))
        elif docker_is_podman(docker.path):
            found.append("podman (docker is podman)")
        elif endpoint == "podman":
            found.append("podman (docker talks to podman)")
        else:
            found.append(f"docker ({endpoint})" if endpoint else "docker")
    if podman is not None and not any(entry.startswith("podman") for entry in found):
        found.append(described(podman))
    return found


# ---------------------------------------------------------------- the machine


def hostname() -> str:
    name = socket.gethostname().split(".")[0]
    return "".join(c for c in name if c.isalnum() or c in "-_") or "host"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def containerenv_name(fs_root: Path) -> str:
    match = re.search(r'(?m)^name="([^"]*)"', read_text(fs_root / "run" / ".containerenv"))
    return match.group(1) if match and NAME_RE.fullmatch(match.group(1)) else ""


def inside(env: Mapping[str, str], fs_root: Path) -> str:
    """Which container the session runs in (``distrobox dev``, ``toolbox tb``, ``docker``), or ""."""
    if "CONTAINER_ID" in env:
        name = env["CONTAINER_ID"]
        return f"distrobox {name}" if NAME_RE.fullmatch(name) else "distrobox"
    if (fs_root / "run" / ".containerenv").exists():
        kind = "toolbox" if (fs_root / "run" / ".toolboxenv").exists() else "podman"
        return f"{kind} {containerenv_name(fs_root)}".strip()
    return "docker" if (fs_root / ".dockerenv").exists() else ""


def os_name(fs_root: Path) -> str:
    fields = dict(re.findall(r'(?m)^([A-Z_]+)="?([^"\n]*)"?$', read_text(fs_root / "etc" / "os-release")))
    words = [fields.get("ID", ""), fields.get("VERSION_ID", "")]
    name = " ".join(w for w in words if NAME_RE.fullmatch(w))
    if name:
        return name
    return "macos" if sys.platform == "darwin" else sys.platform


def present(scanner: Scanner, table: dict[str, tuple[str, ...]]) -> list[str]:
    return [
        described(Hit(key, hit.path, hit.via))
        for key, names in table.items()
        if (hit := scanner.first(names))
    ]


def isolation(scanner: Scanner, fs_root: Path) -> list[str]:
    """Isolation tools on PATH; nix also by its store, which a nix install always has."""
    found = []
    for key, names in ISOLATION.items():
        hit = scanner.first(names)
        if hit:
            found.append(described(Hit(key, hit.path, hit.via)))
        elif key == "nix" and (fs_root / "nix" / "store").is_dir():
            found.append(key)
    return found


def repository_files(root: Path) -> list[str]:
    return [name for name in REPOSITORY_FILES if (root / name).exists()]


def detect(
    cwd: Path, env: Mapping[str, str], fs_root: Path = Path("/"), programs: tuple[str, ...] = ()
) -> dict:
    """Everything detection knows, from files and environment variables; runs nothing."""
    bad = [name for name in programs if not PROGRAM_RE.fullmatch(name)]
    if bad:
        raise ValueError(f"not a program name: {', '.join(bad)}")
    scanner = Scanner(cwd, env)
    where = inside(env, fs_root)
    pms = [key for key, names in PACKAGE_MANAGERS.items() if (hit := scanner.first(names)) and not hit.via]
    found = {
        "key": hostname() + (f"/{where.split()[-1]}" if where else ""),
        "os": os_name(fs_root),
        "package_managers": pms,
        "inside": where,
        "engines": engines(scanner.find("docker"), scanner.find("podman"), docker_endpoint(env)),
        "managers": present(scanner, MANAGERS),
        "isolation": isolation(scanner, fs_root),
        "helpers": {key: shown(scanner.first(names)) for key, names in HELPERS.items()},
        "programs": {name: shown(scanner.find(name)) for name in programs},
        "repository": repository_files(find_root(cwd)),
    }
    found["untrusted"] = [f"{described(hit)} ({hit.path})" for hit in scanner.untrusted]
    found["shims"] = [f"{described(hit)} ({hit.path})" for hit in scanner.shims]
    return found


# ---------------------------------------------------------------- choices for the per-repo question


def ordered(options: list[str], recommended: str) -> list[str]:
    return [recommended, *(o for o in options if o != recommended)]


def engine_choice(found: dict) -> tuple[str, list[str], str] | None:
    names = list(dict.fromkeys(e.split()[0] for e in found["engines"] if " via " not in e))
    if len(names) < 2:
        return None
    files = found["repository"]
    preferred = "podman" if "Containerfile" in files else "docker" if "Dockerfile" in files else names[0]
    return "engine", ordered(names, preferred), preferred


def builds_choice(found: dict) -> tuple[str, list[str], str] | None:
    boxes = [b for b in ("distrobox", "toolbox", "devcontainer") if b in found["isolation"]]
    if found["inside"] or not boxes:
        return None
    files = found["repository"]
    preferred = "distrobox" if "distrobox.ini" in files and "distrobox" in boxes else "host"
    if ".devcontainer" in files and "devcontainer" in boxes and preferred == "host":
        preferred = "devcontainer"
    return "builds", ordered([*boxes, "host"], preferred), preferred


def manager_choice(found: dict) -> tuple[str, list[str], str] | None:
    names = [m for m in found["managers"] if " via " not in m]
    if len(names) < 2:
        return None
    files = found["repository"]
    preferred = "asdf" if ".tool-versions" in files else "mise"
    return "runtime manager", ordered(names, preferred), preferred


def choices(found: dict) -> list[tuple[str, list[str], str]]:
    """The topics of onboarding's one combined question: only where the machine offers more than
    one way, each with its options (the recommendation first, from the repository's files)."""
    picks = (engine_choice(found), builds_choice(found), manager_choice(found))
    return [pick for pick in picks if pick]


# ---------------------------------------------------------------- the owner's answers


def valid_route(route: str) -> bool:
    if route.startswith("distrobox:"):
        return bool(NAME_RE.fullmatch(route.removeprefix("distrobox:")))
    return route in ROUTES


def helper_id(name: str) -> str:
    for key, names in HELPERS.items():
        if name == key or name in names:
            return key
    raise ValueError(f"{name} is not a curated helper ({', '.join(HELPERS)})")


def section(lines: list[str], key: str) -> tuple[int, int] | None:
    """The heading index of ``## key`` and the index where its section ends."""
    try:
        start = lines.index(f"## {key}")
    except ValueError:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def field(lines: list[str], key: str, name: str) -> str:
    bounds = section(lines, key)
    if bounds is None:
        return ""
    prefix = f"{name}:"
    return next(
        (line[len(prefix) :].strip() for line in lines[bounds[0] : bounds[1]] if line.startswith(prefix)), ""
    )


def set_field(lines: list[str], key: str, name: str, value: str) -> list[str]:
    """Replace the field's line in the key's section, or add it under the heading; nothing else moves."""
    bounds = section(lines, key)
    if bounds is None:
        return [*lines, "", f"## {key}", f"{name}: {value}"]
    start, end = bounds
    for i in range(start + 1, end):
        if lines[i].startswith(f"{name}:"):
            return [*lines[:i], f"{name}: {value}", *lines[i + 1 :]]
    return [*lines[: start + 1], f"{name}: {value}", *lines[start + 1 :]]


def profile_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else PROFILE_HEAD.splitlines()


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=".machine.", delete=False
    ) as out:
        out.write(text)
    try:
        os.replace(out.name, path)
    except OSError:
        os.unlink(out.name)
        raise


def update(path: Path, key: str, name: str, value: str, command: str) -> None:
    """Re-read the profile, replace one field and write it back atomically."""
    if not KEY_RE.fullmatch(key):
        raise ValueError(f"not a host key: {key}")
    try:
        lines = set_field(profile_lines(path), key, name, value)
        write_atomic(path, "\n".join(lines) + "\n")
    except OSError as error:
        script = shlex.quote(str(Path(__file__).resolve().parent / "cobot-env"))
        raise NotRecorded(
            f"{NOT_RECORDED} cannot write {path} ({error.strerror}); Claude Code's sandbox keeps the"
            f" config directory read-only to Bash. The owner runs, in their own terminal: {script} {command}"
        ) from error


def prefer(route: str, key: str, path: Path) -> str:
    if not valid_route(route):
        raise ValueError(f"unknown install route {route!r} ({', '.join(ROUTES)}, distrobox:<box>)")
    update(path, key, "route", route, f"prefer {shlex.quote(route)}")
    return f"route for {key}: {route} ({path})"


def decline(helper: str, key: str, path: Path) -> str:
    name = helper_id(helper)
    declined = answers(key, path)["declined"]
    if name not in declined:
        update(path, key, "declined", ", ".join([*declined, name]), f"decline {name}")
    return f"declined for {key}: {name} ({path})"


def answers(key: str, path: Path) -> dict:
    """The owner's route and declined helpers for ``key``; anything not a known value is dropped,
    so nothing the file holds besides those reaches a prompt."""
    try:
        lines = profile_lines(path)
    except OSError:
        lines = []
    route = field(lines, key, "route")
    declined = [w.strip() for w in field(lines, key, "declined").split(",")]
    return {
        "route": route if valid_route(route) else "",
        "declined": list(dict.fromkeys(w for w in declined if w in HELPERS)),
    }


# ---------------------------------------------------------------- the brief line


def advised(found: dict, declined: list[str]) -> list[str]:
    return [key for key, value in found["helpers"].items() if value is None and key not in declined]


def brief(found: dict, path: Path) -> str:
    """One line of at most BRIEF_CAP characters for the session brief."""
    given = answers(found["key"], path)
    platform = ", ".join(
        [found["os"], *(["/".join(found["package_managers"])] if found["package_managers"] else [])]
    )
    parts = [f"machine: {found['key']} ({platform})"]
    if found["untrusted"]:
        parts.append("not trusted: " + ", ".join(u.split(" (", 1)[0] for u in found["untrusted"]))
    if found["inside"]:
        parts.append(f"inside: {found['inside']}")
    parts.append("engines: " + (", ".join(found["engines"]) or "none"))
    for label in ("managers", "isolation"):
        if found[label]:
            parts.append(f"{label}: " + ", ".join(found[label]))
    if given["route"]:
        parts.append(f"route: {given['route']}")
    helpers = advised(found, given["declined"])
    if helpers:
        parts.append("advise: " + ", ".join(helpers))
    line = " · ".join(parts)
    return line if len(line) <= BRIEF_CAP else line[: BRIEF_CAP - 1] + "…"
