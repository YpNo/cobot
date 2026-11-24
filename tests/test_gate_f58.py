"""Nested Claude Code, plugin removal, launchers and copies (spec gate-f58, F-58).

Each Goal row is measured on ``de4a125`` with the owner and project layers empty; the friction
rows stay silent. Fixtures hold no secret-shaped literal: ``x`` stands for any value.
"""

from __future__ import annotations

import json

import pytest


def verdict(rules, command, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, None, cwd)[0]


def decide(rules, command, cwd=None):
    return verdict(rules, command, cwd).decision


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project folder as the working directory, with a HOME outside it and no owner layer."""
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    work = tmp_path / "proj"
    work.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("CDPATH", raising=False)
    monkeypatch.chdir(work)
    return work


# ---------------------------------------------------------------- story 1: cobot's plugin

PLUGIN_DENY = [
    "claude plugin disable cobot",
    "claude plugins disable cobot@cobot",
    "claude plugin disable -s user cobot",
    "claude plugin disable --all",
    "claude plugin disable -a",
    "claude plugin uninstall cobot",
    "claude plugin remove cobot@cobot",
    "claude plugin marketplace remove cobot",
    "claude plugin marketplace rm cobot",
    # T01 review: the name in any case
    "claude plugin uninstall COBOT",
    "claude plugins remove Cobot@cobot",
]
PLUGIN_ASK = [
    "claude plugin i x",
    "claude plugin update x",
    "claude plugin init x",
    "claude plugin new x",
    "claude plugin eval --trust-plugin x",
    "claude plugin prune",
    "claude plugin autoremove",
    "claude plugin configure x --values-stdin",
    "claude plugin disable x",
    "claude plugin marketplace remove x",
    "claude plugin marketplace update",
    # T01 review
    "claude plugin tag plugins/cobot --push -f",
    "claude plugin uninstall x --prune -y",
]
PLUGIN_FRICTION = [
    "claude plugin list",
    "claude plugin details x",
    "claude plugin validate plugins/cobot --strict",
    "claude plugin eval . --runs 1 --no-publish",
    "claude plugin marketplace list",
    "claude plugin configure x",
    # T01 review: a prompt's words or --plugin-dir's value are not the plugin verb
    "claude plugin eval plugins/cobot --filter update-check",
    "claude plugin details cobot",
    "claude plugin tag plugins/cobot",
]


def test_story1_promptWords_neverDeny(rules, project):
    """A prompt naming the verbs asks at most (through --plugin-dir), never a refusal."""
    assert decide(rules, 'claude -p "summarize the plugin changes, removed nothing from cobot"') is None
    assert decide(rules, 'claude --plugin-dir plugins/cobot -p "explain how disable works in cobot"') == "ask"


@pytest.mark.parametrize("command", PLUGIN_DENY)
def test_story1_disablingOrRemovingCobot_isRefused(rules, project, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", PLUGIN_ASK)
def test_story1_changingPlugins_asks(rules, project, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", PLUGIN_FRICTION)
def test_story1_readingPlugins_staysSilent(rules, project, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 2: a nested session's options

NESTED_ASK = [
    # the gate's hooks do not load
    "claude -p x --bare",
    "claude --bare -p x",
    "claude -r --bare",
    "claude -p x --safe-mode",
    "claude -p x --setting-sources project",
    "claude -p x --setting-sources=user",
    "claude --restricted -p x",
    # settings, a permission answerer, a transport or plugin code from outside
    "claude -p x --managed-settings {}",
    "claude -p x --permission-prompt-tool x",
    "claude -p x --sdk-url wss://h",
    "claude -p x --dangerously-load-development-channels server:x",
    "claude -p x --plugin-url https://h/p.zip",
    # Q2: widening
    "claude -p x --dangerously-skip-permissions",
    "claude -p x --allow-dangerously-skip-permissions",
    "claude -p x --permission-mode bypassPermissions",
    "claude -p x --permission-mode=auto",
    "claude -p x --permission-mode dontAsk",
    "claude -p x --add-dir ~/.claude",
    "claude -p x --add-dir src ~/.claude/projects",
    "claude -p x --add-dir ~",
    # Q3: elsewhere
    "claude --cloud x",
    "claude --cloud",
    "claude --remote-control",
    "claude --environment e",
    "claude --teleport",
    "claude --desktop",
    "claude ultrareview",
    # a subcommand's own options
    "claude agents --dangerously-skip-permissions",
    "claude agents --permission-mode bypassPermissions",
    "claude agents --setting-sources project",
    # Q1: an option the table lacks
    "claude -p x --flag-not-in-the-binary",
    "claude -pZ x",
    # every unwrapped form
    'bash -c "claude --bare"',
    "env claude --bare",
    "claude-code --bare",
    "/usr/bin/claude --bare -p x",
    "mise exec -- claude --bare",
    "npm exec -- claude --bare",
    # T02 review: Claude Code finds these in the raw argv, so a value slot does not hide them
    "claude --model --bare -p x",
    "claude --append-system-prompt --safe-mode -p x",
    "claude -n --bare",
    "claude attach abc --bare",
    "claude respawn abc --bare",
    "claude logs abc --restricted",
    "claude --project-config-root /tmp/empty -p x",
    "claude --add-dir ${HOME}",
    "claude --add-dir /",
    "claude --add-dir .claude",
    'claude --agents \'{"x":{"permissionMode":"bypassPermissions"}}\' -p x',
]
NESTED_FRICTION = [
    "claude",
    "claude -p x",
    "claude -c",
    "claude --resume",
    "claude -r abc",
    "claude --version",
    "claude -v",
    "claude -p x -- --bare",
    'claude -p "explain --bare in the docs"',
    "claude -p x --model sonnet --output-format json",
    "claude -p x --max-turns 3",
    "claude -p x --max-budget-usd 1",
    "claude -p x --permission-mode plan",
    "claude -p x --permission-mode acceptEdits",
    'claude -p x --allowedTools "Bash(git push:*)"',
    "claude -p x --allowedTools Read Grep",
    "claude -p x --add-dir ../other",
    "claude --bg x",
    "claude -w x",
    "claude mcp list",
    "claude doctor",
    "claude agents",
    "claude agents --json",
    "claude mcp get x",
    "claude auth status",
    # T02 review
    "claude -- --bare",
    "claude --setting-sources user,project,local -p x",
    "claude --add-dir .claude/worktrees/x/docs",
    'claude --agents \'{"x":{"prompt":"y"}}\' -p x',
]


def test_story2_addDir_resolvesFromTheSegmentsFolder(rules, project):
    """A relative ``--add-dir`` is read from the folder the walk gives (T02 review: ``../..``)."""
    (project / "a" / "b").mkdir(parents=True)
    (project / ".claude").mkdir()
    assert decide(rules, "cd a/b && claude --add-dir ../../.claude -p x") == "ask"
    assert decide(rules, "cd a/b && claude --add-dir .. -p x") is None
    assert decide(rules, f"claude --add-dir {project.parent} -p x") == "ask"  # HOME's parent


@pytest.mark.parametrize("command", NESTED_ASK)
def test_story2_nestedSessionOption_asks(rules, project, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", NESTED_FRICTION)
def test_story2_nestedFriction_staysSilent(rules, project, command):
    assert decide(rules, command) is None


def test_story2_reason_namesTheOption(rules, project):
    assert "--bare" in verdict(rules, "claude -p x --bare").note


# ---------------------------------------------------------------- story 3: the start variables

VARIABLE_ASK = [
    "CLAUDE_CODE_SIMPLE=1 claude -p x",
    "CLAUDE_CODE_SAFE_MODE=1 claude",
    "CLAUDE_CODE_RESTRICTED=1 claude",
    "export CLAUDE_CODE_SIMPLE=1; claude -p x",
    "env CLAUDE_CODE_SIMPLE=1 claude",
    "CLAUDE_CONFIG_DIR=/tmp/c claude -p x",
    "CLAUDE_CODE_PLUGIN_DIRS=/tmp/p claude -p x",
    "CLAUDE_CODE_MANAGED_SETTINGS_PATH=/tmp/s.json claude -p x",
    "CLAUDE_CODE_SHELL_PREFIX=/tmp/w claude",
    "CLAUDE_ENV_FILE=/tmp/e claude",
    "declare -x CLAUDE_CODE_PLUGIN_CACHE_DIR=/tmp/c",
    "export CLAUDE_{CODE_SIMPLE,X}=1; claude",
    # T03 review: a quoted separator, an arithmetic assignment
    "export X='a;b' CLAUDE_CODE_SIMPLE; claude",
    "export X=';' CLAUDE_CODE_SIMPLE; claude -p x",
    "export X='a|b' BASH_ENV",
    "((a=1,CLAUDE_CODE_SIMPLE=1)); claude -p x",
    "let a,CLAUDE_CODE_SHELL_PREFIX=1",
    "let x=CLAUDE_CODE_SIMPLE=1",
    "a[CLAUDE_CODE_SIMPLE=1]=x",
    "((a=1,BASH_ENV=1))",
]
VARIABLE_FRICTION = [
    "echo $CLAUDE_CODE_SIMPLE",
    "printenv CLAUDE_CONFIG_DIR",
    "CLAUDE_MODEL=x ls",  # make would ask anyway: it is opaque
]


@pytest.mark.parametrize("command", VARIABLE_ASK)
def test_story3_claudeStartVariable_asks(rules, project, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", VARIABLE_FRICTION)
def test_story3_readingTheVariables_staysSilent(rules, project, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- stories 4 and 5: launchers, cli.js

LAUNCHER_ASK = [
    "volta run claude mcp add x",
    "volta run --node 22 claude --bare",
    "volta run --env A=1 claude -- --bare",
    "asdf exec claude mcp add x",
    "fnm exec --using=22 claude --bare",
    "fnm exec -- claude --bare",
    "nvm exec 22 claude --bare",
    "nvm exec --lts claude --bare",
    "npm explore x -- claude --bare",
    "pnpx @anthropic-ai/claude-code mcp add x",
    "dx npm:@anthropic-ai/claude-code -p x",
    "uv tool run x",
    "volta run --unknown claude",
    "/x/node_modules/@anthropic-ai/claude-code/cli.js mcp add x",
    "/x/node_modules/@anthropic-ai/claude-code/cli.js --bare",
    # T04 review
    "nvm exec 22 -- claude --bare",
    "nvm exec 22 -- claude mcp add x",
    "nvm run 22 /x/node_modules/@anthropic-ai/claude-code/cli.js --bare",
    "nvm run --silent 22 /x/node_modules/@anthropic-ai/claude-code/cli.js mcp add x",
    "fnm --log-level quiet exec claude --bare",
    "fnm --arch x64 exec claude mcp add x",
    "nodenv exec claude --bare",
    "n exec 22 claude --bare",
    "n run 22 /x/node_modules/@anthropic-ai/claude-code/cli.js --bare",
]
LAUNCHER_DENY = [
    "nvm exec default -- claude plugin disable cobot",
    "volta run claude plugin uninstall cobot",
]


@pytest.mark.parametrize("command", LAUNCHER_DENY)
def test_story4_launcher_keepsTheDeny(rules, project, command):
    assert decide(rules, command) == "deny"


LAUNCHER_FRICTION = [
    "volta run node --version",
    "volta run --node 22 node s.js",
    "asdf exec node s.js",
    "fnm exec --using=22 node s.js",
    "nvm exec 22 node s.js",
    "volta install node",
    "asdf install",
    "uv tool list",
    "nvm run 22 s.js",
    "nvm exec --lts node -v",
    "fnm exec --using=.nvmrc node -v",
    "volta run --bundled-npm npm ci",
    "n 22",
    "nodenv exec node s.js",
]


@pytest.mark.parametrize("command", LAUNCHER_ASK)
def test_story4_launcherOrEntry_isReadAsClaude(rules, project, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", LAUNCHER_FRICTION)
def test_story4_launcherFriction_staysSilent(rules, project, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- story 6: globs on protected files


@pytest.fixture
def state_files(project):
    home = project.parent / "home"
    (home / ".claude.json").write_text("{}")
    (home / ".claude.json.backup1").write_text("{}")
    (project / ".mcp.json").write_text("{}")
    return home


GLOB_ASK = [
    "tee ~/.claude.js?n",
    "cp x ~/.claude.j*",
    "rm ~/.claude.j*",
    "tee .mc?.json",
    "tee ~/.claude.json.b*",
    "cat ~/.cl*.json",
    "ls ~/.c*",
    # T05 review: a .. after a hole, $PWD with a glob
    "cat ~/.cl*/../.claude.json",
    "tee ~/.c*/../.claude.json",
    "tee $PWD/.mc?.json",
    'tee "$PWD"/.mc?.json',
    "cp x ${PWD}/.mc*",
    "cat $HOME/.claude.j*",
]


@pytest.mark.parametrize("command", GLOB_ASK)
def test_story6_globMatchingAProtectedFile_asks(rules, state_files, command):
    assert decide(rules, command) == "ask"


def test_story6_globMatchingNothingProtected_staysSilent(rules, project):
    """No ``.mcp.json`` here and no ``~/.claude.json``: the same globs name nothing protected."""
    for command in ("tee .mc?.json", "cat ~/.cl*.json", "ls ~/.c*", "cat *.json", "ls src/*"):
        assert decide(rules, command) is None, command


def test_story6_otherGlobs_staySilent(rules, state_files):
    """Without dotglob a glob reaches a dotfile only through a leading dot (T05 review: ``ls *`` in
    a repository with a ``.mcp.json``)."""
    (state_files / ".bashrc.d").mkdir()
    for command in (
        "cat *.py",
        "ls ~/.bashrc.d/*",
        "cat ~/.config/*.toml",
        "ls *",
        "cat *.json",
        "ls ~/?claude.json",
    ):
        assert decide(rules, command) is None, command


# ---------------------------------------------------------------- story 8: both runtimes

AGY_ROWS = [
    ("claude plugin disable cobot", "deny"),
    ("claude plugin update x", "force_ask"),
    ("claude -p x --bare", "force_ask"),
    ("claude plugin list", "allow"),
]


@pytest.mark.parametrize(("command", "expected"), AGY_ROWS)
def test_story8_agy_sameJudgement(rules, project, monkeypatch, command, expected):
    """ADR-0007: under agy, run_command reaches the same judgement; ``allow`` there is no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    (project / ".agent").mkdir()
    (project / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(project)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected
