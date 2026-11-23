"""A ``cd`` before the word (spec gate-f56-f60, story 9).

Gap 1: after ``cd ~/.claude`` (a literal target the gate resolves) a relative operand got an ask
where the literal path is refused. Each row is measured on ``c9304bc``.
"""

from __future__ import annotations

import json
import time

import pytest


def decide(rules, command, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, None, cwd)[0].decision


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A HOME with the config dir, its sealed folders, a project with its own ``.claude`` and a
    cache folder; the working directory is a plain folder outside it."""
    home = tmp_path / "home"
    for folder in (".claude/cobot", ".claude/shell-snapshots", "proj/.claude", ".cache"):
        (home / folder).mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("CDPATH", raising=False)
    (tmp_path / "work").mkdir()
    monkeypatch.chdir(tmp_path / "work")
    return home


# ---------------------------------------------------------------- gap 1: a literal cd target

LITERAL_PAIRS = [
    # c9304bc: ask, through the cd; deny, written out
    ("cd ~/.claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd ~/.claude && cat cobot/x", "cat ~/.claude/cobot/x"),
    ("cd ~/.claude/cobot && rm x", "rm ~/.claude/cobot/x"),
    ("cd ~/.claude/cobot && cat x", "cat ~/.claude/cobot/x"),
    ("cd ~/.claude/shell-snapshots && rm s.sh", "rm ~/.claude/shell-snapshots/s.sh"),
    ("cd ~/.claude/cobot && ls", "ls ~/.claude/cobot"),
    ("pushd ~/.claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd ~ && cd .claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd ~/.claude; rm -r cobot", "rm -r ~/.claude/cobot"),
    # extractions and downloads into the working directory: as their folder option does
    ("cd ~/.claude && tar -xf e.tar", "tar -C ~/.claude -xf e.tar"),
    ("cd ~/.claude && unzip e.zip", "unzip -d ~/.claude e.zip"),
    ("cd ~/.claude && curl -OJ https://h/x", "curl --output-dir ~/.claude -OJ https://h/x"),
    ("cd ~/.claude && jar xf e.jar", "jar xf e.jar -C ~/.claude"),
    ("cd ~/.claude && ar x e.a", "ar --output ~/.claude x e.a"),
    ("cd ~/.claude && unar e.rar", "unar -o ~/.claude e.rar"),
    ("cd ~/.claude && bsdunzip e.zip", "bsdunzip -d ~/.claude e.zip"),
    ("cd ~/.claude && ar -v -x a.a", "ar --output ~/.claude -v -x a.a"),
    ("cd ~/.claude && ar --plugin p x a.a", "ar --output ~/.claude --plugin p x a.a"),
    ("cd ~/.claude && jar -xf e.jar", "jar -xf e.jar -C ~/.claude"),
    # T12 review: other spellings of a literal cd
    ("cd -P ~/.claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd -- ~/.claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd && cd .claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd ~/proj && cd ../.claude && rm -r cobot", "rm -r ~/.claude/cobot"),
    ("cd ~/.claude && cd .. && rm -r .claude/cobot", "rm -r ~/.claude/cobot"),
    ("cd ~ && cd .claude && cd cobot && rm x", "rm ~/.claude/cobot/x"),
]


@pytest.mark.parametrize(("through_cd", "written_out"), LITERAL_PAIRS)
def test_gap1_literalCd_getsTheLiteralPathsDecision(rules, home, through_cd, written_out):
    assert decide(rules, written_out) == "deny"
    assert decide(rules, through_cd) == "deny"


def test_gap1_literalCd_keepsTheLiteralPathsAsk(rules, home):
    """Q3: a lock asks, written out or through the cd."""
    assert decide(rules, "chmod -R 700 ~/.claude") == "ask"
    assert decide(rules, "cd ~/.claude && chmod -R 700 .") == "ask"


@pytest.mark.parametrize("command", ["cd ~ && tar -xf e.tar", "cd ~ && unzip x.zip"])
def test_gap1_extractionInHome_stillAsks(rules, home, command):
    """Q1 (owner): a working directory that only holds the config dir asks, where ``tar -C ~``
    is refused; the cd being followed now does not change that."""
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "cd ~/.claude && cd /tmp && rm -r cobot",  # a later known cd leaves the folder
        # T12 review: the owner pass follows the latest cd, it does not collect them all
        "cd ~ && cd proj && rm -r .claude",
        "cd ~/.claude && cd sub && rm -r cobot",
        "cd ~/.claude; cd ~/proj; rm -r cobot",
        "cd ~/.claude; cd -; rm -r cobot",
        "pushd ~/.claude; popd; rm -r cobot",
        'cd ~/.claude && cd "$X" && rm -r cobot',
        "cd ~/.cache && tar -xf e.tar",  # the walk keeps a ``~`` cd unknown, as on c9304bc
        "cd ~ && make",  # runners stay opaque after it
    ],
)
def test_gap1_literalCd_staysAnAskWhereTheFolderIsLeftOrUnknown(rules, home, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "cd ~/.claude && ls",
        "cd ~/.claude && touch x",
        "cd ~ && ls",
        "cd ~/proj && rm -r build",
        "cd ~/missing && rm x",
        'cd ~; cd "$X"; cd .claude; rm -r cobot',  # T12 review: as on c9304bc
    ],
)
def test_gap1_literalCdElsewhere_staysSilent(rules, home, command):
    assert decide(rules, command) is None


def test_gap1_longChainOfCds_isJudgedWithinTheHookTimeout(rules, home):
    """A first build rebuilt the reached folders per segment and joined every relative cd: 200
    cds took 44 s. One pass following the latest cd, and HOME_TARGETS_MAX, keep it under the
    hook's 10 s (about 2x the c9304bc time)."""
    command = "cd ~ && " + " && ".join(["cd a"] * 200) + " && rm x"
    started = time.monotonic()
    decide(rules, command)
    assert time.monotonic() - started < 8


# ---------------------------------------------------------------- both runtimes


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("cd ~/.claude && rm -r cobot", "deny"),
        ("cd ~/.claude && tar -xf e.tar", "deny"),
        ("cd ~/.gemini/config && tar -xf e.tar", "force_ask"),
        ("cd ~/proj && rm -r build", "allow"),
    ],
)
def test_gaps_agy_sameJudgement(rules, home, tmp_path, monkeypatch, command, expected):
    """ADR-0007: under agy, run_command reaches the same judgement; ``allow`` there is no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    (home / ".gemini" / "config").mkdir(parents=True)
    workspace = tmp_path / "ws"
    (workspace / ".agent").mkdir(parents=True)
    (workspace / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(workspace)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected
