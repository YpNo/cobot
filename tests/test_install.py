"""install.sh: argument handling and --check against a fake home and a fake claude."""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest
from conftest import INSTALL, PLUGIN

FAKE_CLAUDE = """#!/bin/sh
case "$1 $2 $3" in
  "--version  ") echo "9.9.9 (Claude Code)" ;;
  "plugin marketplace list") echo "Configured marketplaces:"; echo "  cobot" ;;
  "plugin list ") echo "Installed plugins:"; echo "  cobot@cobot"; echo "    Scope: project" ;;
  "plugin install "*) echo "installed $3 $4 $5"; pwd ;;
  "plugin uninstall "*)
    case "$5" in local) echo "not installed at local scope" >&2; exit 1 ;; esac
    echo "uninstalled $3 $4 $5" ;;
  *) echo "fake claude: $*" ;;
esac
"""


@pytest.fixture
def home(tmp_path):
    (tmp_path / ".agents" / "agents").mkdir(parents=True)
    claude_dir = tmp_path / ".claude"
    (claude_dir / "agents").mkdir(parents=True)
    (claude_dir / "skills").mkdir()
    (claude_dir / "agents" / "challenger.md").symlink_to(tmp_path / ".agents" / "agents" / "challenger.md")
    (claude_dir / "agents" / "other.md").write_text("not a link")
    (claude_dir / "CLAUDE.md").symlink_to(tmp_path / ".agents" / "AGENTS.md")
    return tmp_path


TOOLS = ("sh", "sed", "grep", "readlink", "basename", "dirname", "pwd", "true")


def hermetic_bin(home_dir, fake_claude):
    """A PATH with only the tools install.sh needs, so the real claude can never leak in."""
    bin_dir = home_dir / "bin"
    if not bin_dir.exists():
        bin_dir.mkdir()
        for tool in TOOLS:
            (bin_dir / tool).symlink_to(shutil.which(tool))
    exe = bin_dir / "claude"
    if fake_claude and not exe.exists():
        exe.write_text(FAKE_CLAUDE)
        exe.chmod(0o755)
    return bin_dir


def run_install(args, home_dir, fake_claude=True, cwd=None):
    bin_dir = hermetic_bin(home_dir, fake_claude)
    env = {"PATH": str(bin_dir), "HOME": str(home_dir)}
    return subprocess.run(
        ["/bin/sh", str(INSTALL), *args], capture_output=True, text=True, env=env, cwd=cwd, check=False
    )


def test_install_noArgs_printsUsageExitsTwo(home):
    result = run_install([], home)
    assert result.returncode == 2
    assert "--dev" in result.stdout


def test_install_unknownOption_exitsTwo(home):
    result = run_install(["--bogus"], home)
    assert result.returncode == 2
    assert "unknown option" in result.stderr


def test_install_badSource_exitsTwo(home):
    assert run_install(["--dev", "--source", "ftp"], home).returncode == 2


def test_install_dev_printsAliasWritesNothing(home):
    hermetic_bin(home, fake_claude=True)
    before = sorted(p.relative_to(home) for p in home.rglob("*"))
    result = run_install(["--dev"], home)
    assert result.returncode == 0
    assert f"alias claude-cobot='claude --plugin-dir \"{PLUGIN}\"'" in result.stdout
    assert sorted(p.relative_to(home) for p in home.rglob("*")) == before


def test_install_check_reportsLegacyAndOverlaps(home):
    result = run_install(["--check"], home)
    assert result.returncode == 0
    assert "9.9.9 (Claude Code)" in result.stdout
    assert "registered" in result.stdout
    assert "Scope: project" in result.stdout
    assert ".agents: present" in result.stdout
    assert "agents: 1" in result.stdout
    assert "skills: 0" in result.stdout
    assert "CLAUDE.md ->" in result.stdout
    assert "agent 'challenger': also present" in result.stdout


def test_install_check_withoutClaude_stillReports(home):
    result = run_install(["--check"], home, fake_claude=False)
    assert result.returncode == 0
    assert "claude: not found" in result.stdout
    assert "not registered" in result.stdout


def test_install_project_installsInDir(home, tmp_path):
    target = tmp_path / "repo"
    target.mkdir()
    result = run_install(["--project", str(target)], home)
    assert result.returncode == 0
    assert "already registered" in result.stdout
    assert "installed cobot@cobot --scope project" in result.stdout
    assert str(target) in result.stdout


def test_install_local_defaultsToCwd(home, tmp_path):
    result = run_install(["--local"], home, cwd=tmp_path)
    assert "--scope local" in result.stdout


def test_install_user_usesRepoDir(home):
    assert "--scope user" in run_install(["--user"], home).stdout


def test_install_uninstall_defaultScopeProject(home):
    assert "uninstalled cobot@cobot --scope project" in run_install(["--uninstall"], home).stdout
    assert "--scope user" in run_install(["--uninstall", "user"], home).stdout


def test_install_withoutClaude_installFails(home):
    result = run_install(["--project"], home, fake_claude=False)
    assert result.returncode == 1
    assert "claude not found" in result.stderr


def test_install_sourceGithub_registersFromGithub(home, tmp_path):
    exe = hermetic_bin(home, fake_claude=False) / "claude"
    exe.write_text(FAKE_CLAUDE.replace('echo "  cobot"', "true"))
    exe.chmod(0o755)
    result = run_install(["--project", str(tmp_path), "--source", "github"], home, fake_claude=False)
    assert "registering marketplace from YpNo/cobot" in result.stdout
    assert os.path.isdir(tmp_path)


def test_install_refresh_uninstallsThenInstallsAtTheInstalledScope(home, tmp_path):
    target = tmp_path / "repo"
    target.mkdir()
    result = run_install(["--refresh", str(target)], home)
    assert result.returncode == 0
    assert "uninstalled cobot@cobot --scope project" in result.stdout
    assert "installing cobot@cobot at scope project" in result.stdout
    assert "at scope local" not in result.stdout and "nothing to uninstall" not in result.stdout
    assert str(target) in result.stdout


def test_install_usage_listsRefresh(home):
    result = run_install(["--help"], home)
    assert "--refresh [DIR]" in result.stdout and "--uninstall [SCOPE]" in result.stdout
