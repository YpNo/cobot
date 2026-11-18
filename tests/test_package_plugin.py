"""scripts/package-plugin.py: pure host-specific plugin bundles (Option C)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from conftest import PLUGIN, REPO

SCRIPT = REPO / "scripts" / "package-plugin.py"


def run_package(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_packagePlugin_agy_producesPureBundleWithRandomHookGroup(tmp_path: Path) -> None:
    out = tmp_path / "cobot"
    result = run_package("--host", "agy", "--out", str(out), "--no-user-models")
    assert result.returncode == 0, result.stderr
    assert (out / ".antigravity-plugin" / "plugin.json").is_file()
    assert (out / "policy" / "default.rules").is_file()
    assert (out / "bin" / "cobot-rules").is_file()
    assert (out / "hooks" / "gate-agy.sh").is_file()
    assert (out / "hooks" / "session-agy.sh").is_file()
    assert list((out / "agents").glob("*.md"))
    assert list((out / "skills").glob("*/SKILL.md"))
    for stripped in (
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
    ):
        assert not (out / stripped).exists(), stripped
    assert not list(out.rglob("__pycache__"))

    hooks = json.loads((out / "hooks.json").read_text(encoding="utf-8"))
    (group_name,) = hooks.keys()
    assert re.fullmatch(r"cobot-[0-9a-f]{16}", group_name), group_name
    assert group_name not in result.stdout + result.stderr


def test_packagePlugin_claude_producesPureClaudeBundle(tmp_path: Path) -> None:
    out = tmp_path / "cobot"
    result = run_package("--host", "claude", "--out", str(out), "--no-user-models")
    assert result.returncode == 0, result.stderr
    assert (out / ".claude-plugin" / "plugin.json").is_file()
    assert (out / "policy" / "default.rules").is_file()
    assert (out / "hooks" / "hooks.json").is_file()
    assert (out / "hooks" / "gate.sh").is_file()
    assert list((out / "claude-agents").glob("*.md"))
    for stripped in (
        ".antigravity-plugin",
        "agents",
        "agent-defs",
        "hooks.json",
        "hooks/gate-agy.sh",
        "hooks/session-agy.sh",
        "evals",
        "evals-blocked",
        "rules",
    ):
        assert not (out / stripped).exists(), stripped


def test_packagePlugin_zip_writesArchiveWithCobotPrefix(tmp_path: Path) -> None:
    out = tmp_path / "cobot"
    archive = tmp_path / "cobot-agy.zip"
    result = run_package("--host", "agy", "--out", str(out), "--zip", str(archive), "--no-user-models")
    assert result.returncode == 0, result.stderr
    assert archive.is_file()
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "cobot/.antigravity-plugin/plugin.json" in names
    assert "cobot/policy/default.rules" in names
    assert "cobot/hooks/hooks.json" not in names


@pytest.mark.parametrize(
    "args",
    [
        ["--host", "cursor", "--out", "out"],
        ["--host", "agy"],
        ["--bogus"],
    ],
)
def test_packagePlugin_invalidArgs_exitTwo(tmp_path: Path, args: list[str]) -> None:
    resolved = [str(tmp_path / a) if a == "out" else a for a in args]
    assert run_package(*resolved).returncode == 2


def test_packagePlugin_help_exitsZeroAndWritesNothing(tmp_path: Path) -> None:
    out = tmp_path / "cobot"
    result = run_package("--host", "agy", "--out", str(out), "--help")
    assert result.returncode == 0
    assert "--host" in result.stdout
    assert not out.exists()
    assert PLUGIN.is_dir()
