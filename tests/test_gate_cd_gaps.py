"""A ``cd`` before the word (spec gate-f56-f60, story 9).

Gap 1: after ``cd ~/.claude`` (a literal target the gate resolves) a relative operand got an ask
where the literal path is refused. Gap 2: after a ``cd`` the gate cannot follow,
``ln -sfn /tmp/o .claude`` reached no decision. Each row is measured on ``c9304bc``.
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


def test_gap1_extractionAfterLeavingTheConfigDir_asksNamingNoLeftFolder(rules, home):
    """Wrap code review: after ``cd ~/.claude && cd ~/proj`` the reason named ``~/.claude``."""
    loaded, _, _ = rules.load_rules(None)
    verdict = rules.judge_bash("cd ~/.claude && cd ~/proj && tar -xf e.tar", loaded, None, None)[0]
    assert verdict.decision == "ask"
    assert "'~/.claude'" not in verdict.note


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
        "cd ~/.claude && pushd +1 && rm -r cobot",  # wrap code review: the stack, not a folder
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
    ],
)
def test_gap1_literalCdElsewhere_staysSilent(rules, home, command):
    assert decide(rules, command) is None


# ---------------------------------------------------------------- gap 2: a cd the gate cannot follow

UNKNOWN_CD_ASKED = [
    'cd "$X" && ln -sfn /tmp/o .claude',  # c9304bc: none
    'cd "$X" && ln -s /tmp/o .claude',
    'cd "$X" && rm -r .claude',
    'cd "$X" && rm -r ./.claude/',
    'cd "$X" && rm -r .Claude',
    'cd "$X" && mv .claude /tmp/y',
    'cd "$X" && rm -r .claude/cobot',
    'cd "$X" && cp e x/.claude/cobot/y',
    'cd "$(pwd)/x" && ln -sfn /tmp/o .claude',
    "cd - && ln -sfn /tmp/o .claude",
    "popd && ln -sfn /tmp/o .claude",
    'cd ~/.claude && cd "$X" && ln -sfn /tmp/o .claude',
    # T13 review: option values, and a cd into the name
    'cd "$X" && mv --target-directory=.claude /tmp/o',
    'cd "$X" && cp --target-directory=.claude/cobot /tmp/o',
    'cd "$X" && cp -t.claude/cobot /tmp/o',
    'cd "$X" && tar -xf a.tar -C .claude',
    'cd "$X" && tar -xf a.tar --directory=.claude',
    'cd "$X" && unzip a.zip -d .claude',
    'cd "$X" && cd .claude && ln -sfn /tmp/o cobot',
    'cd "$X"/.claude && ln -sfn /tmp/o cobot',
    'cd "$X" && pushd .claude && ln -sfn /tmp/o cobot',
    'cd ~; cd "$X"; cd .claude; rm -r cobot',  # none on c9304bc and after T12
    # wrap code review: a short option cluster with the value joined
    'cd "$X" && cp -vt.claude/cobot evil',
    'cd "$X" && ln -sfnt.claude /tmp/o',
    # wrap bypass review: a guess kept through a cd that may lead back
    'cd "$X"/.claude && (cd ~) && rm -r cobot',
    'cd "$X"/.claude && cd /tmp && cd - && rm -r cobot',
    'cd "$X"/.claude && pushd /tmp && popd && rm -r cobot',
    'cd "$X"/.claude && cd ~/nonexist; rm -r cobot',
]


@pytest.mark.parametrize("command", UNKNOWN_CD_ASKED)
def test_gap2_unknownCdThenTheConfigDirsName_asks(rules, home, command):
    """An ask, not a deny: the unknown folder may be a project with its own ``.claude``."""
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        'cd "$X" && ls .claude',
        'cd "$X" && cat .claude/notes.md',
        'cd "$X" && rm -r build',
        'cd "$X" && ln -s a b',
        'cd "$X" && rm -r .claude-old',
        "ln -sfn /tmp/o .claude",  # the working directory is known, and not HOME
        "cd ~/proj && ln -sfn /tmp/o .claude",  # the owner pass knows the folder (story 9)
        "cd ~/proj && rm -r .claude",
        'cd "$X" && cd .claude && ls',
        'cd "$X" && cd .claude && mkdir -p agents',
        'cd "$X" && ls -la .claude',
        'cd "$X" && cp -vt.cache x',
    ],
)
def test_gap2_unknownCdElsewhere_staysSilent(rules, home, command):
    assert decide(rules, command) is None


def test_gap2_movedConfigDir_isReadByItsOwnName(rules, home, tmp_path, monkeypatch):
    (tmp_path / "cc" / "cobot").mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "cc"))
    assert decide(rules, 'cd "$X" && ln -sfn /tmp/o cc') == "ask"
    assert decide(rules, 'cd "$X" && rm -r cc/cobot') == "ask"


def test_gap2_paddedName_isJudgedInTimeAndALaterDenyStands(rules, home):
    """T13 review: a word of 1000 ``.claude`` parts took 37 s (a check per part), so the hook
    timed out before the literal deny after it; one check per word now."""
    padded = ".claude/" * 1000 + "z"
    started = time.monotonic()
    verdict = decide(rules, f'cd "$X" && ls {padded}; rm -f ~/.claude/cobot.rules')
    assert time.monotonic() - started < 5
    assert verdict == "deny"


def test_gaps_relativeCdsBeforeALiteralDeny_judgedWithinTheHookTimeout(rules, home):
    """Wrap bypass review: folders a relative cd reached were read for every segment, so a 3 KB
    command took 13.3 s and the hook's timeout let the ``rm`` run (c9304bc: 4.8 s). Measured
    against the same command without the ``~`` cd, so the bound holds under coverage's load:
    the global set cost about 3x per segment."""
    body = " ".join(f"cd a && cd b && cd c && cd d && cd .. && x q{i};" for i in range(30))
    started = time.monotonic()
    assert decide(rules, f"cd /tmp && {body} rm -r ~/.claude/cobot") == "deny"
    baseline = time.monotonic() - started
    started = time.monotonic()
    assert decide(rules, f"cd ~ && {body} rm -r ~/.claude/cobot") == "deny"
    assert time.monotonic() - started < 2 * baseline + 1


def test_gap1_longChainOfCds_isJudgedWithinTheHookTimeout(rules, home):
    """A first build rebuilt the reached folders per segment and joined every relative cd: 200
    cds took 44 s. One pass following the latest cd keeps it under the hook's 10 s (about 2x the
    c9304bc time)."""
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
        ('cd "$X" && ln -sfn /tmp/o .claude', "force_ask"),
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
