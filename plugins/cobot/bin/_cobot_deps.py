"""Dependency currency (decision 21): how far a repository's dependencies are behind, cached.

Each ecosystem is detected by its lockfile and asked through its own tool, with a hardened
environment: ``cargo update --dry-run --verbose`` (stock cargo, no external subcommand so no
``.cargo/config.toml`` alias can redirect it), ``cargo-deny`` or ``cargo-audit`` called as binaries,
``go list -m -u`` under ``GOTOOLCHAIN=local``, ``npm``/``pnpm`` with scripts off, ``uv tree
--outdated``, ``poetry show --outdated``, and the Terraform registry over HTTPS because no
read-only CLI exists for it. A missing tool is reported, never installed. Output is scrubbed with
the secret pattern before it is cached.

The cache lives under the data directory, keyed by the origin remote (``host/owner/repo``), else
the root commit, else a hash of the path; it is fresh for seven days while the lockfiles' hashes
hold. ``brief`` reads it and never runs a tool: the SessionStart hook has thirty seconds and no
network promise. ``check`` runs the tools at onboard, before a PR and on demand.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from _cobot_common import SECRET_RE, data_dir, host_owner_repo, remotes, root_commits

CACHE_DAYS = 7
ITEM_CAP = 20
TOOL_TIMEOUT = 180
HTTP_TIMEOUT = 10
REGISTRY = "https://registry.terraform.io/v1/providers/{ns}/{name}"
CHECKPOINT = "https://checkpoint-api.hashicorp.com/v1/check/terraform"


@dataclass
class Result:
    ecosystem: str
    lockfile: str
    total: int = 0
    behind: int = 0
    advisories: int | None = None  # None = no advisory tool ran
    tool: str = ""
    advisory_tool: str = ""
    notes: list[str] = field(default_factory=list)
    items: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        self.notes = list(dict.fromkeys(self.notes))
        return {
            "ecosystem": self.ecosystem,
            "lockfile": self.lockfile,
            "total": self.total,
            "behind": self.behind,
            "advisories": self.advisories,
            "tool": self.tool,
            "advisory_tool": self.advisory_tool,
            "notes": self.notes,
            "items": self.items[:ITEM_CAP],
        }


Run = Callable[[list[str], Path, dict[str, str] | None], tuple[int | None, str, str]]


def run(argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int | None, str, str]:
    """Run a tool; ``(None, "", reason)`` when it is missing or times out."""
    binary = shutil.which(argv[0])
    if binary is None:
        return None, "", f"{argv[0]} not installed"
    full_env = {**os.environ, **(env or {})}
    try:
        out = subprocess.run(  # noqa: S603 - fixed argv per adapter, no shell
            [binary, *argv[1:]],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TOOL_TIMEOUT,
            env=full_env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "", f"{argv[0]} timed out after {TOOL_TIMEOUT}s"
    except OSError as error:
        return None, "", f"{argv[0]} failed to start: {error}"
    return out.returncode, out.stdout, out.stderr


def scrub(text: str) -> str:
    return SECRET_RE.sub("[redacted]", text)


def json_objects(text: str) -> list:
    """Every JSON value in a stream of concatenated or line-separated JSON."""
    decoder = json.JSONDecoder()
    found, index = [], 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        try:
            value, end = decoder.raw_decode(text, index)
        except ValueError:
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline + 1
            continue
        found.append(value)
        index = end
    return found


def first_json(text: str):
    objects = json_objects(text)
    return objects[0] if objects else None


# ---------------------------------------------------------------- adapters


DENY_SCOPE_NOTE = "cargo-deny checks only the deny.toml [graph] targets; cargo-audit reads all of Cargo.lock"
DENY_CONFIGS = ("deny.toml", ".deny.toml", ".cargo/deny.toml")  # where cargo-deny looks, in order


def deny_targets(root: Path) -> bool:
    """Whether cargo-deny's config limits the graph to listed targets, so an advisory on a crate
    built only for another target (wasm32, say) is not counted."""
    for name in DENY_CONFIGS:
        path = root / name
        if not path.is_file():
            continue
        try:
            config = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
        except tomllib.TOMLDecodeError:
            return False
        return bool((config.get("graph") or {}).get("targets"))
    return False


def rust(root: Path, runner: Run) -> Result:
    result = Result("rust", "Cargo.lock", tool="cargo update --dry-run --verbose")
    result.total = sum(
        1
        for line in (root / "Cargo.lock").read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() == "[[package]]"
    )
    # the whole graph: `--workspace` would update only the members and report every
    # compatible dependency update as "Unchanged … (available: …)"
    code, out, err = runner(
        ["cargo", "update", "--dry-run", "--verbose"], root, {"CARGO_NET_OFFLINE": "false"}
    )
    if code is None:
        result.notes.append(err)
    elif code != 0:
        result.notes.append(
            f"cargo update failed: {err.strip().splitlines()[-1][:120] if err.strip() else code}"
        )
    else:
        for line in err.splitlines():
            updating = re.match(r"\s*Updating (\S+) (v\S+) -> (v\S+)", line)
            behind = re.match(r"\s*Unchanged (\S+) (v\S+) \(available: (v[^,)\s]+)", line)
            match = updating or behind
            if match:
                result.behind += 1
                result.items.append(
                    f"{match.group(1)} {match.group(2)} -> {match.group(3)}"
                    + ("" if updating else " (outside the requirement)")
                )
    if shutil.which("cargo-deny"):
        result.advisory_tool = "cargo-deny check advisories"
        if deny_targets(root):
            result.notes.append(DENY_SCOPE_NOTE)
        code, out, err = runner(["cargo-deny", "--format", "json", "check", "advisories"], root, None)
        diagnostics = [
            o for o in json_objects(out + "\n" + err) if isinstance(o, dict) and o.get("type") == "diagnostic"
        ]
        summary = next(
            (o for o in json_objects(out + "\n" + err) if isinstance(o, dict) and o.get("type") == "summary"),
            {},
        )
        counts = (summary.get("fields") or {}).get("advisories") or {}
        result.advisories = (
            len(diagnostics) if diagnostics else int(counts.get("errors", 0)) + int(counts.get("warnings", 0))
        )
        if code is None:
            result.notes.append(err)
            result.advisories = None
    elif shutil.which("cargo-audit"):
        result.advisory_tool = "cargo-audit"
        code, out, err = runner(["cargo-audit", "audit", "--json"], root, None)
        data = first_json(out) or {}
        result.advisories = (
            int(((data.get("vulnerabilities") or {}).get("count")) or 0) if code is not None else None
        )
        if code is None:
            result.notes.append(err)
    else:
        result.notes.append("no advisory tool (cargo-deny or cargo-audit)")
    return result


def go(root: Path, runner: Run) -> Result:
    result = Result("go", "go.mod", tool="go list -m -u (GOTOOLCHAIN=local)")
    code, out, err = runner(
        ["go", "list", "-m", "-u", "-json", "all"], root, {"GOTOOLCHAIN": "local", "GOFLAGS": "-mod=mod"}
    )
    if code is None:
        result.notes.append(err)
    elif code != 0:
        result.notes.append(f"go list failed: {err.strip().splitlines()[-1][:140] if err.strip() else code}")
    else:
        for module in json_objects(out):
            if not isinstance(module, dict) or module.get("Main") or module.get("Indirect"):
                continue
            result.total += 1
            update = module.get("Update")
            if update:
                result.behind += 1
                result.items.append(
                    f"{module.get('Path')} {module.get('Version')} -> {update.get('Version')}"
                )
    if shutil.which("govulncheck"):
        result.advisory_tool = "govulncheck ./..."
        code, out, err = runner(["govulncheck", "./..."], root, {"GOTOOLCHAIN": "local"})
        if code is None:
            result.notes.append(err)
        else:
            result.advisories = len(re.findall(r"^Vulnerability #\d+", out, re.M))
    else:
        result.notes.append("govulncheck not installed")
    return result


def node(root: Path, runner: Run, manager: str, lockfile: str) -> Result:
    result = Result(manager, lockfile, tool=f"{manager} outdated --json")
    env = {"npm_config_ignore_scripts": "true", "CI": "1"}
    argv = [manager, "outdated", "--json"] if manager == "npm" else [manager, "outdated", "--format", "json"]
    code, out, err = runner(argv, root, env)
    if code is None:
        result.notes.append(err)
    else:
        data = first_json(out)
        if not isinstance(data, dict):
            result.notes.append(f"{manager} outdated gave no JSON (exit {code})")
            data = {}
        rows = {name: row for name, row in data.items() if isinstance(row, dict)}
        missing = [name for name, row in rows.items() if not row.get("current")]
        if rows and len(missing) == len(rows):
            result.notes.append(f"no installed tree: run `{manager} install` first")
        for name, row in rows.items():
            if row.get("current") and row.get("latest") and row["current"] != row["latest"]:
                result.behind += 1
                result.items.append(f"{name} {row['current']} -> {row['latest']}")
        result.total = declared_node_total(root) or len(rows)
    result.advisory_tool = f"{manager} audit --json"
    code, out, err = runner([manager, "audit", "--json"], root, env)
    data = first_json(out) if code is not None else None
    if isinstance(data, dict):
        counts = (data.get("metadata") or {}).get("vulnerabilities") or {}
        result.advisories = (
            sum(int(v) for k, v in counts.items() if k != "total" and isinstance(v, int))
            if "total" not in counts
            else int(counts["total"])
        )
    else:
        result.notes.append(err if code is None else f"{manager} audit gave no JSON (exit {code})")
    return result


def declared_node_total(root: Path) -> int:
    try:
        data = json.loads((root / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    return sum(len(data.get(key) or {}) for key in ("dependencies", "devDependencies"))


def uv_tree(root: Path, runner: Run) -> Result:
    result = Result("python", "uv.lock", tool="uv tree --depth 1 --outdated")
    code, out, err = runner(
        ["uv", "tree", "--depth", "1", "--outdated", "--no-dev"], root, {"UV_NO_SYNC": "1"}
    )
    if code is None:
        result.notes.append(err)
    elif code != 0:
        result.notes.append(f"uv tree failed: {err.strip().splitlines()[-1][:140] if err.strip() else code}")
    else:
        for line in out.splitlines()[1:]:
            match = re.match(r"^[│├└─\s]*(\S+) v(\S+)(?: \(latest: v(\S+)\))?", line)
            if match:
                result.total += 1
                if match.group(3):
                    result.behind += 1
                    result.items.append(f"{match.group(1)} {match.group(2)} -> {match.group(3)}")
    python_advisories(root, runner, result, ["uv", "export", "--no-hashes", "--no-emit-project", "--quiet"])
    return result


def poetry(root: Path, runner: Run) -> Result:
    result = Result("python", "poetry.lock", tool="poetry show --outdated --top-level")
    code, out, err = runner(["poetry", "show", "--top-level", "--no-ansi"], root, None)
    if code is None:
        result.notes.append(err)
        return result
    result.total = sum(1 for line in out.splitlines() if line.strip() and not line.startswith(" "))
    code, out, err = runner(["poetry", "show", "--outdated", "--top-level", "--no-ansi"], root, None)
    if code == 0:
        for line in out.splitlines():
            parts = [part for part in line.split() if part != "(!)"]
            if len(parts) >= 3 and not line.startswith(" "):
                result.behind += 1
                result.items.append(f"{parts[0]} {parts[1]} -> {parts[2]}")
    python_advisories(
        root, runner, result, ["poetry", "export", "--without-hashes", "-f", "requirements.txt"]
    )
    return result


def python_advisories(root: Path, runner: Run, result: Result, export: list[str]) -> None:
    if not shutil.which("pip-audit"):
        result.notes.append("pip-audit not installed")
        return
    result.advisory_tool = "pip-audit"
    code, out, err = runner(export, root, None)
    if code != 0:
        result.notes.append(f"{export[0]} export failed; pip-audit skipped")
        return
    requirements = root / ".agent" / ".deps-requirements.txt"
    try:
        requirements.parent.mkdir(parents=True, exist_ok=True)
        requirements.write_text(out, encoding="utf-8")
        code, out, err = runner(
            ["pip-audit", "-r", str(requirements), "--format", "json", "--progress-spinner", "off"],
            root,
            None,
        )
    finally:
        requirements.unlink(missing_ok=True)
    data = first_json(out) if code is not None else None
    deps = data.get("dependencies") if isinstance(data, dict) else data
    if isinstance(deps, list):
        result.advisories = sum(len(d.get("vulns") or []) for d in deps if isinstance(d, dict))
    else:
        result.notes.append(err if code is None else f"pip-audit gave no JSON (exit {code})")


def fetch_json(url: str) -> dict | None:
    request = urllib.request.Request(url, headers={"User-Agent": "cobot-deps"})  # noqa: S310 - https only  # noqa: E501
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, OSError):
        return None


def terraform(root: Path, runner: Run, fetch: Callable[[str], dict | None] = fetch_json) -> Result:
    result = Result("terraform", ".terraform.lock.hcl", tool="registry.terraform.io + checkpoint")
    text = (root / ".terraform.lock.hcl").read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(
        r'provider "registry\.terraform\.io/([\w-]+)/([\w-]+)"\s*\{\s*version\s*=\s*"([^"]+)"', text
    ):
        namespace, name, version = match.groups()
        result.total += 1
        data = fetch(REGISTRY.format(ns=namespace, name=name))
        latest = (data or {}).get("version")
        if latest is None:
            result.notes.append(f"registry unreachable for {namespace}/{name}")
        elif latest != version:
            result.behind += 1
            result.items.append(f"{namespace}/{name} {version} -> {latest}")
    code, out, _err = runner(["terraform", "version", "-json"], root, {"CHECKPOINT_DISABLE": "1"})
    installed = (first_json(out) or {}).get("terraform_version") if code == 0 else None
    if installed:
        result.total += 1
        current = (fetch(CHECKPOINT) or {}).get("current_version")
        if current is None:
            result.notes.append("checkpoint unreachable for terraform core")
        elif current != installed:
            result.behind += 1
            result.items.append(f"terraform {installed} -> {current}")
    result.notes.append("no advisory feed; provider changelogs are the source")
    return result


ADAPTERS: list[tuple[str, Callable[[Path, Run], Result]]] = [
    ("Cargo.lock", rust),
    ("go.mod", go),
    ("package-lock.json", lambda root, runner: node(root, runner, "npm", "package-lock.json")),
    ("pnpm-lock.yaml", lambda root, runner: node(root, runner, "pnpm", "pnpm-lock.yaml")),
    ("uv.lock", uv_tree),
    ("poetry.lock", poetry),
    (".terraform.lock.hcl", terraform),
]
UNSUPPORTED = {"yarn.lock": "yarn", "bun.lock": "bun", "bun.lockb": "bun", "requirements.txt": "pip"}


# ---------------------------------------------------------------- cache and check


def lockfiles(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for name in [*(n for n, _ in ADAPTERS), *UNSUPPORTED]:
        path = root / name
        if path.is_file():
            found[name] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return found


def cache_key(root: Path) -> str:
    origin = remotes(root).get("origin")
    parsed = host_owner_repo(origin) if origin else None
    if parsed:
        return "/".join(parsed)
    roots = root_commits(root)
    if roots:
        return f"local/{roots[0][:12]}"
    return f"path/{hashlib.sha256(str(root).encode()).hexdigest()[:12]}"


def cache_path(root: Path) -> Path:
    return data_dir().parent / "deps" / f"{cache_key(root).replace('/', '__')}.json"


def read_cache(root: Path) -> dict | None:
    try:
        return json.loads(cache_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def cache_state(root: Path, cached: dict | None, today: date) -> str:
    """``fresh``, ``none``, ``old`` (over CACHE_DAYS) or ``changed`` (a lockfile differs)."""
    if not cached:
        return "none"
    try:
        age = (today - date.fromisoformat(cached.get("checked", ""))).days
    except ValueError:
        return "none"
    if age > CACHE_DAYS:
        return "old"
    if cached.get("lockfiles") != lockfiles(root):
        return "changed"
    return "fresh"


# ---------------------------------------------------------------- toolchains (spec memory-and-ship, story 7)

FLOATING_WORDS = frozenset({"stable", "beta", "nightly", "latest", "lts", "node", "current"})
MISE_FILES = ("mise.toml", ".mise.toml", ".config/mise.toml", "mise/config.toml")
GO_NOTE = "go.mod: no toolchain line (note: go is a minimum; setup-go and GOTOOLCHAIN=auto may take newer)"


def floats(value: str) -> bool:
    """A channel naming no exact release: a moving word, ``lts/<codename>``, or a major alone."""
    word = value.strip().strip("\"'").lower()
    return bool(word) and (
        word in FLOATING_WORDS or word.startswith("lts/") or bool(re.fullmatch(r"v?\d+", word))
    )


def first_line(path: Path) -> str:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return lines[0] if lines and not lines[0].startswith("#") else ""


def mise_versions(path: Path) -> list[tuple[str, str]]:
    """``(tool, version)`` from a mise file's ``[tools]``: a string, a list, or ``{ version = … }``."""
    tools = tomllib.loads(path.read_text(encoding="utf-8")).get("tools") or {}
    pairs = []
    for tool, spec in tools.items():
        values = spec if isinstance(spec, list) else [spec]
        for value in values:
            version = value.get("version") if isinstance(value, dict) else value
            if isinstance(version, str):
                pairs.append((str(tool), version))
    return pairs


def toolchain_versions(root: Path) -> list[tuple[str, str]]:
    """``(label, channel)`` for every toolchain pin file present, read from the file alone."""
    found: list[tuple[str, str]] = []
    toml = root / "rust-toolchain.toml"
    if toml.is_file():
        channel = (tomllib.loads(toml.read_text(encoding="utf-8")).get("toolchain") or {}).get("channel")
        found += [("rust-toolchain.toml", channel)] if isinstance(channel, str) else []
    for name in ("rust-toolchain", ".nvmrc", ".node-version"):
        if (root / name).is_file():
            found.append((name, first_line(root / name)))
    if (root / ".python-version").is_file():
        lines = (root / ".python-version").read_text(encoding="utf-8").split()
        found += [(".python-version", line) for line in lines]
    if (root / ".tool-versions").is_file():
        for line in (root / ".tool-versions").read_text(encoding="utf-8").splitlines():
            words = line.split("#", 1)[0].split()
            found += [(f".tool-versions: {words[0]}", words[1])] if len(words) > 1 else []
    for name in MISE_FILES:
        if (root / name).is_file():
            found += [(f"{name}: {tool}", version) for tool, version in mise_versions(root / name)]
    return found


def toolchain_rows(root: Path) -> list[str]:
    """Floating channels (CI and the local proof may take different releases, F-37), and the note
    that go.mod's lines are minimums when it names no toolchain. Never runs a tool."""
    rows = []
    try:
        for label, channel in toolchain_versions(root):
            if floats(channel):
                named = f"{label} {channel}" if ": " in label else f"{label}: {channel}"
                rows.append(f"{named} floats; pin a release")
        gomod = root / "go.mod"
        if gomod.is_file():
            text = gomod.read_text(encoding="utf-8")
            if re.search(r"(?m)^go \S+", text) and not re.search(r"(?m)^toolchain \S+", text):
                rows.append(GO_NOTE)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        rows.append(f"toolchain files unreadable: {type(error).__name__}")
    return rows


def has_workflows(root: Path) -> bool:
    folder = root / ".github" / "workflows"
    return folder.is_dir() and (any(folder.glob("*.yml")) or any(folder.glob("*.yaml")))


def file_facts(root: Path) -> dict:
    """What the report reads from files alone: fresh on every call, a cached result too."""
    return {"workflows": has_workflows(root), "toolchains": toolchain_rows(root)}


def check(root: Path, today: date, force: bool = False, runner: Run = run) -> dict:
    cached = read_cache(root)
    state = cache_state(root, cached, today)
    if state == "fresh" and not force:
        return {**cached, **file_facts(root), "cached": True}
    found = lockfiles(root)
    results = []
    for name, adapter in ADAPTERS:
        if name in found:
            try:
                results.append(adapter(root, runner).as_dict())
            except Exception as error:  # noqa: BLE001 - one broken adapter must not hide the others
                results.append(
                    Result(name, name, notes=[f"adapter failed: {type(error).__name__}: {error}"]).as_dict()
                )
    skipped = sorted({UNSUPPORTED[name] for name in found if name in UNSUPPORTED})
    data = {
        "checked": today.isoformat(),
        "root": str(root),
        "lockfiles": found,
        "ecosystems": json.loads(scrub(json.dumps(results))),
        "unsupported": skipped,
        **file_facts(root),
        "cached": False,
    }
    path = cache_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({k: v for k, v in data.items() if k != "cached"}, indent=1) + "\n", encoding="utf-8"
    )
    return data


def totals(data: dict) -> tuple[int, int, int | None]:
    ecosystems = data.get("ecosystems") or []
    behind = sum(int(e.get("behind") or 0) for e in ecosystems)
    total = sum(int(e.get("total") or 0) for e in ecosystems)
    counted = [e["advisories"] for e in ecosystems if e.get("advisories") is not None]
    return behind, total, (sum(counted) if counted else None)


def headline(data: dict, today: date) -> str:
    behind, total, advisories = totals(data)
    age = (today - date.fromisoformat(data["checked"])).days
    when = "today" if age == 0 else f"{age} day(s) ago"
    advisory = (
        f"{advisories} advisor{'y' if advisories == 1 else 'ies'}"
        if advisories is not None
        else "advisories not checked"
    )
    if not data.get("ecosystems"):
        return f"deps: no supported lockfile (checked {when})"
    return f"deps: {behind} of {total} behind, {advisory} (checked {when})"


def report(data: dict, today: date) -> str:
    lines = [headline(data, today) + (" [cached]" if data.get("cached") else "")]
    for eco in data.get("ecosystems") or []:
        advisory = (
            f"{eco['advisories']} advisories ({eco['advisory_tool']})"
            if eco.get("advisories") is not None
            else "advisories: not checked"
        )
        lines.append(
            f"  {eco['ecosystem']} ({eco['lockfile']}): {eco['behind']} of {eco['total']} behind · {eco['tool']} · {advisory}"  # noqa: E501
        )
        lines.extend(f"    {item}" for item in eco.get("items") or [])
        lines.extend(f"    note: {note}" for note in eco.get("notes") or [])
    if data.get("unsupported"):
        lines.append(f"  unsupported here, check by hand: {', '.join(data['unsupported'])}")
    lines.extend(f"  toolchain: {row}" for row in data.get("toolchains") or [])
    if data.get("workflows"):
        lines.append("  GitHub Actions pins: /cobot:consult gha")
    return "\n".join(lines)


def brief(root: Path, today: date) -> str:
    """One line from the cache; never runs a tool."""
    cached = read_cache(root)
    state = cache_state(root, cached, today)
    if state == "none":
        return "deps: not checked; run cobot-deps check" if lockfiles(root) else "deps: no lockfile"
    line = headline(cached, today)
    if state == "old":
        return line + "; stale, run cobot-deps check"
    if state == "changed":
        return line + "; a lockfile changed since, run cobot-deps check"
    return line
