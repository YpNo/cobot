#!/usr/bin/env python3
"""Build a pure host-specific plugin bundle from plugins/cobot (Option C).

Usage:
  python3 scripts/package-plugin.py --host agy|claude --out <dir> [options]

Options:
  --host agy|claude   Target host runtime (required).
  --out <dir>         Destination plugin folder (required; created cleanly).
  --zip <file>        Also write a .zip archive with entries under cobot/.
  --plugin <dir>      Source plugin root (default: plugins/cobot).
  --models <file>     JSON file of per-agent model overrides ({"agy": {...}, "claude": {...}}).
  --no-user-models    Ignore the owner's models.json override file.
  --fixed-group       Keep hook group name "cobot" instead of randomizing (agy only).
  -h, --help          Show this help and exit 0 (writes nothing). Unknown options exit 2.
"""

from __future__ import annotations

import json
import re
import secrets
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "cobot" / "bin"))

import _cobot_common as common  # noqa: E402
from _cobot_agy import AGENT_TIERS  # noqa: E402

HOSTS = frozenset({"agy", "claude"})
CLAUDE_MODELS = frozenset({"opus", "sonnet", "haiku", "inherit"})
VALUE_OPTIONS = {"": {"host", "out", "zip", "plugin", "models"}}
SWITCHES = {"": {"no-user-models", "fixed-group"}}
MODEL_LINE = re.compile(r"^model:\s*\S+\s*$", re.M)
IGNORED_GLOBS = ("__pycache__", "*.pyc", ".pytest_cache", ".DS_Store")

STRIPPED_PATHS: dict[str, tuple[str, ...]] = {
    "agy": (
        ".claude-plugin",
        "claude-agents",
        "agent-defs",
        "hooks/hooks.json",
        "hooks/gate.sh",
        "hooks/report.sh",
        "hooks/session.sh",
        "evals",
        "evals-blocked",
        "rules",
    ),
    "claude": (
        ".antigravity-plugin",
        "agents",
        "agent-defs",
        "hooks.json",
        "hooks/gate-agy.sh",
        "hooks/session-agy.sh",
        "evals",
        "evals-blocked",
        "rules",
    ),
}


def remove_path(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)


def load_overrides(host: str, explicit: str | None, skip_user: bool) -> dict[str, str]:
    """Validated agent -> model overrides for ``host``; invalid entries raise ValueError."""
    if explicit:
        path = Path(explicit)
    elif skip_user:
        return {}
    else:
        path = common.cobot_config_dir() / "models.json"
        if not path.is_file():
            return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    mapping = raw.get(host, {}) if isinstance(raw, dict) else {}
    if not isinstance(mapping, dict):
        raise ValueError(f"{path}: '{host}' must map agent names to model names")
    allowed = AGENT_TIERS if host == "agy" else CLAUDE_MODELS
    for agent, model in mapping.items():
        if not isinstance(agent, str) or model not in allowed:
            raise ValueError(f"{path}: invalid model {model!r} for {agent!r} (allowed: {sorted(allowed)})")
    return dict(mapping)


def apply_model_overrides(dest: Path, host: str, overrides: dict[str, str]) -> None:
    folder = dest / ("agents" if host == "agy" else "claude-agents")
    for agent, model in overrides.items():
        agent_file = folder / f"{agent}.md"
        if agent_file.is_file():
            updated = MODEL_LINE.sub(f"model: {model}", agent_file.read_text(encoding="utf-8"), count=1)
            agent_file.write_text(updated, encoding="utf-8")


def randomize_agy_hook_group(dest: Path) -> None:
    """Rename the root hooks.json group to an unguessable per-install name (smoke h2)."""
    hooks_path = dest / "hooks.json"
    hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
    if "cobot" not in hooks:
        raise ValueError(f"{hooks_path}: missing 'cobot' hook group")
    group_name = f"cobot-{secrets.token_hex(8)}"
    renamed = {group_name: hooks["cobot"], **{k: v for k, v in hooks.items() if k != "cobot"}}
    hooks_path.write_text(json.dumps(renamed, indent=2) + "\n", encoding="utf-8")


def write_zip(source: Path, archive: Path, prefix: str = "cobot") -> None:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(p for p in source.rglob("*") if p.is_file()):
            zf.write(file, f"{prefix}/{file.relative_to(source).as_posix()}")


def package_bundle(source: Path, dest: Path, host: str, overrides: dict[str, str], fixed_group: bool) -> None:
    if dest.exists():
        remove_path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*IGNORED_GLOBS))
    for rel in STRIPPED_PATHS[host]:
        remove_path(dest / rel)
    if overrides:
        apply_model_overrides(dest, host, overrides)
    if host == "agy" and not fixed_group:
        randomize_agy_hook_group(dest)


def main(argv: list[str]) -> int:
    try:
        positional, options, flags = common.parse_cli(argv, VALUE_OPTIONS, SWITCHES)
        if positional:
            raise common.UsageError(f"unexpected argument {positional[0]!r}")
        host, out = options.get("host", ""), options.get("out", "")
        if host not in HOSTS or not out:
            raise common.UsageError("--host agy|claude and --out <dir> are required")
    except common.HelpRequested:
        print((__doc__ or "").strip())
        return 0
    except common.UsageError as error:
        print(f"package-plugin: {error}\n\n{(__doc__ or '').strip()}", file=sys.stderr)
        return 2

    source = Path(options["plugin"]) if "plugin" in options else REPO_ROOT / "plugins" / "cobot"
    dest = Path(out)
    try:
        overrides = load_overrides(host, options.get("models"), "no-user-models" in flags)
        package_bundle(source, dest, host, overrides, "fixed-group" in flags)
        if "zip" in options:
            write_zip(dest, Path(options["zip"]))
    except (OSError, ValueError) as error:
        print(f"package-plugin: {error}", file=sys.stderr)
        return 1

    if host == "agy" and "fixed-group" not in flags:
        print("agy: hook group renamed to a random name for this install")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
