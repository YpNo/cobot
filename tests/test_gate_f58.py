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


# ---------------------------------------------------------------- story 8: both runtimes

AGY_ROWS = [
    ("claude plugin disable cobot", "deny"),
    ("claude plugin update x", "force_ask"),
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
