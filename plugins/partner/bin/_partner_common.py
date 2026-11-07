"""Shared helpers for the partner scripts: paths, git, remotes. Standard library only."""

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


def plugin_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[1]


def config_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def partner_config_dir() -> Path:
    return config_dir() / "partner"


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "agentic-partner" / "repos"


def git(args: list[str], cwd: Path) -> str | None:
    """Run git and return stdout, or None when git is missing or the call fails."""
    try:
        out = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [shutil.which("git") or "git", *args],
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
    override = os.environ.get("PARTNER_RULES_PROJECT_DIR")
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


def memory_dir(cwd: str | os.PathLike | None) -> Path:
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
