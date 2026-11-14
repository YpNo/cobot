"""Shared helpers for the cobot scripts: paths, git, remotes. Standard library only."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

REMOTE_RE = re.compile(r"^(?:[\w.-]+@)?([\w.-]+):(?!//)([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")
SECRET_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|(?i:password|passwd|secret|token)\s*[:=]\s*\S{6,})"
)
URL_RE = re.compile(r"^[a-z+]+://(?:[\w.-]+@)?([\w.-]+)(?::\d+)?/([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")
HELP_ARGS = ("-h", "--help")
# git reads repository config: an index refresh would run the repository's core.fsmonitor program
NO_FSMONITOR = ["-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false"]


class HelpRequested(Exception):
    """``-h`` or ``--help`` anywhere: print the usage, run nothing."""


class UsageError(Exception):
    """An option the command does not take, or one missing its value."""


def find_command(argv: list[str], values: dict[str, set[str]]) -> str:
    """The first positional, skipping the value of any option that takes one; after ``--``, the next."""
    takes_value = set().union(*values.values()) if values else set()
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--":
            return argv[i + 1] if i + 1 < len(argv) else ""
        if not arg.startswith("-"):
            return arg
        i += 2 if arg[2:] in takes_value else 1
    return ""


def parse_cli(
    argv: list[str], values: dict[str, set[str]], switches: dict[str, set[str]]
) -> tuple[list[str], dict[str, str], set[str]]:
    """Split argv into positionals, ``--name value`` options and ``--name`` switches, per command.

    Raises HelpRequested for ``-h``/``--help`` and UsageError for an option the command's tables
    do not name: a typo or ``--help`` must never fall through to the command (``init --help`` once
    wrote the memory files). An option's value is data, and ``--`` ends the options, so a payload
    may start with dashes.
    """
    command = find_command(argv, values)
    takes_value, takes_switch = values.get(command, set()), switches.get(command, set())
    positional: list[str] = []
    options: dict[str, str] = {}
    flags: set[str] = set()
    i, ended = 0, False
    while i < len(argv):
        arg, name = argv[i], argv[i][2:]
        if ended or not (arg.startswith("--") or arg in HELP_ARGS):
            positional.append(arg)
        elif arg == "--":
            ended = True
        elif arg in HELP_ARGS:
            raise HelpRequested
        elif name in takes_value:
            if i + 1 >= len(argv):
                raise UsageError(f"{arg} needs a value")
            options[name] = argv[i + 1]
            i += 1
        elif name in takes_switch:
            flags.add(name)
        else:
            raise UsageError(f"unknown option {arg} for '{command or '(no command)'}'")
        i += 1
    return positional, options, flags


def plugin_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[1]


def config_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def cobot_config_dir() -> Path:
    return config_dir() / "cobot"


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "cobot" / "repos"


def git(args: list[str], cwd: Path) -> str | None:
    """Run git and return stdout, or None when git is missing or the call fails. Every call turns
    the repository's fsmonitor program and untracked cache off."""
    try:
        out = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [shutil.which("git") or "git", *NO_FSMONITOR, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def repo_root(cwd: str | os.PathLike | None) -> Path:
    """The main checkout that holds .agent/, shared by its worktrees; cwd when not a repo."""
    override = os.environ.get("COBOT_RULES_PROJECT_DIR")
    if override:
        return Path(override)
    base = Path(cwd or os.getcwd())
    common = git(["rev-parse", "--git-common-dir"], base)
    if common is None:
        return base
    path = Path(common)
    if not path.is_absolute():
        path = base / path
    return path.resolve().parent


def checkout_root(cwd: str | os.PathLike | None) -> Path:
    """The checkout cwd is in: a worktree's own top level, whose HEAD is the branch being worked
    on; repo_root when overridden or outside a repository."""
    if not os.environ.get("COBOT_RULES_PROJECT_DIR"):
        top = git(["rev-parse", "--show-toplevel"], Path(cwd or os.getcwd()))
        if top:
            return Path(top)
    return repo_root(cwd)


def memory_dir(cwd: str | os.PathLike | None) -> Path:
    """The worktree's own .agent/ when it is a real directory there (a tracked .agent/ is checked
    out per branch, so its journal belongs to that branch); else the main checkout's, which
    foreign mode keeps as one symlink shared by every worktree."""
    own = checkout_root(cwd) / ".agent"
    if own.is_dir() and not own.is_symlink():
        return own
    return repo_root(cwd) / ".agent"


def remotes(root: Path) -> dict[str, str]:
    """Configured remotes as name -> url."""
    out = git(["remote", "-v"], root) or ""
    found: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            found.setdefault(parts[0], parts[1])
    return found


def host_owner_repo(url: str) -> tuple[str, str, str] | None:
    """``git@github.com:YpNo/x.git`` and ``https://github.com/YpNo/x`` -> (github.com, YpNo, x)."""
    for pattern in (URL_RE, REMOTE_RE):
        match = pattern.match(url.strip())
        if match:
            host, owner, repo = match.groups()
            return host.lower(), owner.lower(), repo
    return None


def root_commits(root: Path) -> list[str]:
    out = git(["rev-list", "--max-parents=0", "HEAD"], root) or ""
    return out.split()


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def external_memory(root: Path) -> Path | None:
    """Where foreign mode keeps the memory of the repository whose origin is at ``root``."""
    origin = remotes(root).get("origin")
    parts = host_owner_repo(origin) if origin else None
    return data_dir() / parts[0] / parts[1] / parts[2] if parts else None


def remote_owners(root: Path) -> tuple[dict[str, str], set[str]]:
    """Each remote's ``host/owner`` and the owner's identities (``~/.claude/cobot/identities``)."""
    owners = {name: f"{p[0]}/{p[1]}" for name, url in remotes(root).items() if (p := host_owner_repo(url))}
    return owners, {line.lower() for line in read_lines(cobot_config_dir() / "identities")}


def trusted_roots() -> set[str]:
    return {line.split()[0] for line in read_lines(cobot_config_dir() / "trusted") if line.split()}


def repo_trust(root: Path, agent_dir: Path) -> tuple[bool, str]:
    """Whether the memory at ``agent_dir`` may be read as the owner's: foreign mode resolving to the
    external memory, every remote owner an identity, or a root commit listed in
    ``~/.claude/cobot/trusted``. Reads remotes, root commits and two config files; scans no tree."""
    if agent_dir.is_symlink():
        expected = external_memory(root)
        if expected and agent_dir.resolve() == expected.resolve():
            return True, "foreign mode, memory outside the tree"
        return (
            False,
            f".agent is a symlink that does not resolve to the external memory for origin ({expected})",
        )
    remote_map = remotes(root)
    owners, identities = remote_owners(root)
    strangers: list[str] = []
    if remote_map:
        if owners and set(owners.values()) <= identities:
            return True, f"every remote owner is an identity ({', '.join(sorted(set(owners.values())))})"
        strangers = [
            f"{name} -> {owner}" for name, owner in sorted(owners.items()) if owner not in identities
        ]
    roots = set(root_commits(root))
    if roots and roots & trusted_roots():
        return True, "root commit listed in ~/.claude/cobot/trusted"
    if not remote_map and not roots:
        return False, "no remote and no commit: /cobot:onboard starts it"
    detail = f" ({', '.join(strangers)})" if strangers else ""
    return False, f"no identity matches every remote{detail} and the root commit is not trusted"
