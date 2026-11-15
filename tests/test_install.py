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


TOOLS = ("sh", "sed", "grep", "readlink", "basename", "dirname", "pwd", "true", "mv", "rm", "ln")


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


# ---------------------------------------------------------------- migration from agentic-partner (ADR-0004)

FAKE_CLAUDE_OLD_REMAINS = FAKE_CLAUDE.replace(
    '"plugin marketplace list") echo "Configured marketplaces:"; echo "  cobot" ;;',
    '"plugin marketplace list") echo "Configured marketplaces:"; echo "  cobot"; echo "  agentic-partner" ;;',
).replace(
    '"plugin list ") echo "Installed plugins:"; echo "  cobot@cobot"; echo "    Scope: project" ;;',
    '"plugin list ") echo "Installed plugins:"; echo "  partner@agentic-partner"; echo "    Scope: local" ;;',
)
FAKE_CLAUDE_OLD_GONE = FAKE_CLAUDE_OLD_REMAINS.replace(
    'echo "  partner@agentic-partner"; echo "    Scope: local"',
    'echo "  cobot@cobot"; echo "    Scope: project"',
).replace('"plugin install "*)', '"plugin marketplace remove") echo "removed $4" ;;\n  "plugin install "*)')


@pytest.fixture
def old_state(home):
    data = home / "share" / "agentic-partner" / "repos" / "github.com" / "o" / "r"
    data.mkdir(parents=True)
    (data / "CONTEXT.md").write_text("# r\n")
    conf = home / ".claude" / "partner"
    conf.mkdir()
    (conf / "identities").write_text("github.com/o\n")
    repo = home / "work" / "r"
    repo.mkdir(parents=True)
    (repo / ".agent").symlink_to(data, target_is_directory=True)
    return {"data": data, "conf": conf, "repo": repo}


def run_migrating(args, home, fake=None):
    exe = hermetic_bin(home, fake_claude=fake is None) / "claude"
    if fake is not None:
        exe.write_text(fake)
        exe.chmod(0o755)
    env = {
        "PATH": str(home / "bin"),
        "HOME": str(home),
        "XDG_DATA_HOME": str(home / "share"),
        "CLAUDE_CONFIG_DIR": str(home / ".claude"),
    }
    return subprocess.run(
        ["/bin/sh", str(INSTALL), *args], capture_output=True, text=True, env=env, check=False
    )


def test_install_refresh_movesStateAndRelinksForeignAgent(home, old_state):
    result = run_migrating(["--refresh", str(old_state["repo"])], home)
    assert result.returncode == 0, result.stderr
    new_data = home / "share" / "cobot" / "repos" / "github.com" / "o" / "r"
    assert (new_data / "CONTEXT.md").is_file() and not old_state["data"].exists()
    assert (home / ".claude" / "cobot" / "identities").is_file() and not old_state["conf"].exists()
    assert os.readlink(old_state["repo"] / ".agent") == str(new_data)
    assert "moved" in result.stdout and "re-pointed" in result.stdout


def test_install_check_reportsMigrationWithoutMoving(home, old_state):
    result = run_migrating(["--check"], home)
    assert "would move" in result.stdout
    assert old_state["data"].exists() and old_state["conf"].exists()


def test_install_dev_doesNotMigrate(home, old_state):
    result = run_migrating(["--dev"], home)
    assert result.returncode == 0
    assert old_state["data"].exists() and "moved" not in result.stdout


def test_install_refresh_bothDirsPresent_movesNothing(home, old_state):
    (home / "share" / "cobot").mkdir()
    result = run_migrating(["--refresh", str(old_state["repo"])], home)
    assert "both exist; nothing moved" in result.stdout
    assert old_state["data"].exists()


def test_install_refresh_reportsOwnerRulesFile(home, old_state):
    (home / ".claude" / "partner.rules").write_text("ask Bash(x*)\n")
    result = run_migrating(["--refresh", str(old_state["repo"])], home)
    assert "partner.rules is yours" in result.stdout
    assert (home / ".claude" / "partner.rules").is_file()


def test_install_project_cobotFolderNamedAgenticPartner_removesNothing(home, tmp_path):
    # the real list prints the folder on the line under the name; the checkout is still
    # ~/workspace/agentic-partner, which must not read as the old marketplace
    fake = FAKE_CLAUDE.replace(
        'echo "  cobot" ;;',
        'echo "  \u276f cobot"; echo "    Source: Folder (/home/u/workspace/agentic-partner)" ;;',
    )
    target = tmp_path / "proj"
    target.mkdir()
    result = run_migrating(["--project", str(target)], home, fake=fake)
    assert result.returncode == 0
    assert "marketplace remove" not in result.stdout
    assert "removed marketplace" not in result.stdout


def test_install_refresh_keepsOldMarketplaceWhileInstallsRemain(home, old_state):
    result = run_migrating(["--refresh", str(old_state["repo"])], home, fake=FAKE_CLAUDE_OLD_REMAINS)
    assert "marketplace agentic-partner kept: 1 install(s)" in result.stdout
    assert "removed" not in result.stdout


def test_install_refresh_sharedFolder_removesOldMarketplaceBeforeTheNew(home, old_state):
    fake = FAKE_CLAUDE_OLD_REMAINS.replace(
        'echo "  agentic-partner" ;;',
        f'echo "  agentic-partner"; echo "    Source: Folder ({INSTALL.parent})" ;;',
    ).replace(
        '"plugin install "*)', '"plugin marketplace remove") echo "removed $4" ;;\n  "plugin install "*)'
    )
    result = run_migrating(["--refresh", str(old_state["repo"])], home, fake=fake)
    out = result.stdout
    assert "share this folder with cobot; refresh them next" in out
    assert out.index("removed marketplace agentic-partner") < out.index("installing cobot@cobot")


def test_install_refresh_removesOldMarketplaceWhenNoneRemain(home, old_state):
    (home / ".claude" / "settings.json").write_text('{"extraKnownMarketplaces": {"agentic-partner": {}}}')
    result = run_migrating(["--refresh", str(old_state["repo"])], home, fake=FAKE_CLAUDE_OLD_GONE)
    assert "removed marketplace agentic-partner" in result.stdout
    # the real CLI clears the record itself; the fake leaves the file, so the report shows
    assert "settings.json still has extraKnownMarketplaces.agentic-partner" in result.stdout


# ---------------------------------------------------------------- --agy (spec antigravity, story 6)

FAKE_AGY = """#!/bin/sh
echo "$*" >> "$HOME/agy-argv"
case "$1 $2" in
  "--version ") echo "1.5.9" ;;
  "plugin validate")
    [ -e "$HOME/agy-fail-validate" ] && { echo "invalid manifest" >&2; exit 1; }
    echo "ok" ;;
  "plugin install") [ -e "$HOME/agy-fail-install" ] && { echo "boom" >&2; exit 4; }; echo "Installed cobot" ;;
  "plugin list")
    if [ -e "$HOME/agy-installed" ]; then echo "cobot 0.3.0 enabled"; else echo "No plugins installed."; fi ;;
  *) echo "fake agy: $*" ;;
esac
"""


def with_agy(home_dir, fake_claude=True):
    exe = hermetic_bin(home_dir, fake_claude) / "agy"
    exe.write_text(FAKE_AGY)
    exe.chmod(0o755)
    return home_dir


def agy_calls(home_dir):
    argv = home_dir / "agy-argv"
    return argv.read_text().splitlines() if argv.exists() else []


def test_install_agy_validatesThenInstallsTheCheckout(home):
    result = run_install(["--agy"], with_agy(home, fake_claude=False))
    assert result.returncode == 0, result.stderr
    assert agy_calls(home) == [f"plugin validate {PLUGIN}", f"plugin install {PLUGIN}"]
    assert "no agy session open" in result.stdout


@pytest.mark.parametrize("args", [["--agy", "--project", "{t}"], ["--project", "{t}", "--agy"]])
def test_install_agy_isAModifier_bothOrdersRunBoth(home, tmp_path, args):
    target = tmp_path / "repo"
    target.mkdir()
    result = run_install([a.replace("{t}", str(target)) for a in args], with_agy(home))
    assert result.returncode == 0, result.stderr
    assert "installed cobot@cobot --scope project" in result.stdout
    assert agy_calls(home) == [f"plugin validate {PLUGIN}", f"plugin install {PLUGIN}"]


def test_install_agy_failedValidate_installsNothingAndFailsLoudly(home):
    with_agy(home)
    (home / "agy-fail-validate").write_text("")
    result = run_install(["--agy"], home)
    assert result.returncode == 1
    assert agy_calls(home) == [f"plugin validate {PLUGIN}"]
    assert "agy plugin validate failed" in result.stderr


def test_install_agy_failedInstall_failsLoudly(home):
    with_agy(home)
    (home / "agy-fail-install").write_text("")
    result = run_install(["--agy"], home)
    assert result.returncode == 1
    assert "agy plugin install failed (exit 4)" in result.stderr
    assert "previous copy" in result.stderr


def test_install_agy_withoutAgy_exitsOne(home):
    result = run_install(["--agy"], home)
    assert result.returncode == 1
    assert "agy not found" in result.stderr


@pytest.mark.parametrize(
    "args", [["--agy", "--uninstall"], ["--uninstall", "user", "--agy"], ["--dev", "--agy"]]
)
def test_install_agy_neverUninstallsAndRefusesTheOtherActions(home, args):
    result = run_install(args, with_agy(home))
    assert result.returncode == 2
    assert not any("uninstall" in call for call in agy_calls(home))


def test_install_agy_refreshNeverUninstallsFromAgy(home, tmp_path):
    result = run_install(["--refresh", str(tmp_path), "--agy"], with_agy(home))
    assert result.returncode == 0, result.stderr
    assert agy_calls(home) == [f"plugin validate {PLUGIN}", f"plugin install {PLUGIN}"]


def test_install_check_reportsAgyState(home):
    with_agy(home)
    result = run_install(["--check"], home)
    assert "== Antigravity" in result.stdout and "1.5.9" in result.stdout
    assert "cobot: not installed" in result.stdout
    (home / "agy-installed").write_text("")
    result = run_install(["--check", "--agy"], home)
    assert result.returncode == 0
    assert "cobot 0.3.0 enabled" in result.stdout
    assert "plugin install" not in "\n".join(agy_calls(home))


def test_install_check_withoutAgy_saysNotFound(home):
    result = run_install(["--check"], home)
    assert "agy: not found" in result.stdout
