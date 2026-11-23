"""A shell variable is a hole, not text (spec gate-f55, story 1, F-55).

The scanner emits a ``variable`` hole for ``$NAME``, ``${NAME}``, the positional parameters,
``$_``, ``${!…}`` and subscripts. The gate reads each one by its class in the whole command:
a value the command spells out is put in, a value it computes is a full hole (never spared,
pathlike), and an inherited name or run-time data is spared as a whole word, as ``$(…)`` is.
"""

from __future__ import annotations

import json
import time

import pytest

# argv-level rows the differential test runs under bash too: the stubs' HOME is fake, so the
# protected-file rows above are unit rows only (tests/test_gate_differential.py, its docstring)
VARIABLES_JUDGED = [
    "X=publish; cargo $X",
    "export X=publish; cargo $X",
    "cargo ${X:-publish}",
    "for v in publish; do cargo $v; done",
    "set -- publish; cargo $1",
    "X=delete; gh repo $X o/r",
    "X='push --force'; git $X",
    "f(){ cargo $V; }; V=publish; f",
]


def decide(rules, command, agent=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent)[0].decision


@pytest.mark.parametrize(
    "command",
    [
        "X=cobot.rules; cp x ~/.claude/$X",
        "D=~/.claude/cobot.rules; cp x $D",
        "export D=cobot.rules; cp x ~/.claude/$D",
        "cp x ${X:+~/.claude/cobot.rules}",
        "cp x ${X:-~/.claude/cobot.rul}es",
        "for D in ~/.claude/cobot.rules; do cp x $D; done",
        "HOME=~/.claude; cp x ~/cobot.rules",
        "X=delete; gh repo $X o/r",
        # wrap reviews: nothing falls below the text reading, a literal hit wins, words split
        "cat ${!N}; cp x ~/.claude/cobot.rules",
        'f() { cp x "$1"; }; f ~/.claude/cobot.rules',
        "cp x ~/.claude/cobot/$D",
        "cp x ~/.claude/$D ~/.claude/cobot.rules",
        "D=1; cd ~; cp x D=$D/../.claude/cobot.rules",
        "cp /tmp/a ${D:-/tmp ~/.claude/cobot.rules}",
        "HOME=~/.claude; cp x ~/cobot.rules ${A:-a} ${A:-b} ${A:-c} ${A:-d} ${A:-e} ${A:-f}",
        "F=--force; git push $F origin ${A:-a} ${A:-b} ${A:-c} ${A:-d} ${A:-e} ${A:-f}",
    ],
)
def test_story1_valueInTheCommand_isPutInAndRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cp x ~/.claude/$X",
        "cp x ~/.claude/${X}",
        'cp x "$HOME/.claude/${X}"',
        "tee ~/$X",
        "gh repo $V o/r",
        "set -- ~/.claude/cobot.rul; cp x ${1}es",
        "ls ~/.claude/cobot.rul; cp x ${_}es",
        'A=(~/.claude/cobot.rules); cp x "${A[0]}"',
        "R=D; D=~/.claude/cobot.rules; cp x ${!R}",
        "declare -n N=D; cp x $N",
        "f(){ cp x $D; }; D=~/.claude/cobot.rules; f",
        "read D; cp x ~/.claude/$D",
        "D='e/a ~/.claude.json'; tee $D",
        "D=e/a; D=~/.claude/cobot.rules; cp x $D",
        "true && D=~/.claude/cobot.rules; cp x $D",
        "D=~/.claude/cobot.rules bash -c 'cp x $D'",
        "env D=~/.claude/cobot.rules sh -c 'cp x \"$D\"'",
        "bash -c 'cp x \"$1\"' _ ~/.claude/cobot.rules",
        "sh -c 'cp x $0' ~/.claude/cobot.rules",
        "IFS=/; D='a ~/.claude/cobot.rules'; cp x $D",
        "printf -v D %s ~/.claude/cobot.rules; cp x $D",
        "cp x ${D%.bak}",
        # T01 bypass review: an assigned PWD, a run-time HOME, indirect assigners
        'PWD=~/.claude; cp x "$PWD/cobot.rules"',
        "export PWD=~/.claude; cp x ${PWD}/cobot.rules",
        "read -r HOME <<< ~/.claude; cp x ~/cobot.rules",
        'read -r HOME <<< ~/.claude; cp x "$HOME/cobot.rules"',
        'N=X; printf -v "$N" %s%s ~/.claude /cobot.rules; cp x "$X"',
        'N=HOME; printf -v "$N" %s ~/.claude; cp x ~/cobot.rules',
        "if true; then D=~/.claude/cobot.rules; fi; cp x $D",
    ],
)
def test_story1_hiddenValue_isNeverSilent(rules, command):
    assert decide(rules, command) in ("ask", "deny")


@pytest.mark.parametrize(
    "command",
    [
        "cp x $DEST",
        'cat "$f"',
        "D=out; cp a $D",
        'for f in *.md; do wc -l "$f"; done',
        "echo $HOME",
        'echo "$X"',
        '[ -n "$X" ] && echo ok',
        "echo ${#X}",
        "export PATH=$PATH:x",
        "git log $REV",
        'while read f; do wc -l "$f"; done < list.txt',
        "cat $HOME/notes.md",
        "echo $? $$ $#",
        "cd $PWD && ls",
        'NAME=foo; if [ -d x ]; then echo "$NAME"; fi',
        'NAME=foo; mkdir -p "build/$NAME"',
        'x=$(git rev-parse HEAD); git show "$x"',
        'for f in *.py; do ruff check "$f"; done',
    ],
)
def test_story1_frictionRows_staySilent(rules, command):
    assert decide(rules, command) is None


@pytest.mark.parametrize("command", VARIABLES_JUDGED)
def test_story1_variableDecidesWhatRuns_isJudged(rules, command):
    assert decide(rules, command) in ("ask", "deny")


def test_story1_runTimeDataAsWholeWord_isTheAcceptedResidual(rules):
    """F-59, owner 2026-11-23 ("Spare, then build"): spared like ``cp x $(cat e/p)``."""
    assert decide(rules, "read D < e/p; cp x $D") is None
    assert decide(rules, "cp x $(cat e/p)") is None


def test_story1_runnerBodyVariable_isAFullHole(rules, tmp_path):
    """A package.json script is classed by text the gate did not read here: a full hole."""
    script = "E=$HOME/.claude; G=/cobot.rules; F=$E$G; cp x $F"
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {"g": script}}))
    loaded, _, _ = rules.load_rules(None)
    assert rules.judge_bash("npm run g", loaded, None, str(tmp_path))[0].decision in ("ask", "deny")


@pytest.mark.parametrize("piece", ["((a ", "export a b c ", "read x x x ", "a=$b; "])
def test_story1_longHostileCommand_staysBoundedAndNeverSilentOnSetters(rules, piece):
    """The gate reads every Bash call: a 5 000-character command must not stall it (wrap code
    review: ``((a `` repeated ran past two minutes before the patterns were bounded)."""
    started = time.monotonic()
    verdict = decide(rules, piece * (5000 // len(piece)))
    assert time.monotonic() - started < 30
    assert verdict == "ask" or piece == "a=$b; "


def test_story1_sessionGrant_neverCoversTheNewVerdicts(rules):
    loaded, _, _ = rules.load_rules(None)
    verdict = rules.judge_bash("cp x ~/.claude/$X", loaded, None)[0]
    assert verdict.decision == "ask" and verdict.rule is None


def test_story1_scanner_emitsVariableHoles(rules):
    shell = rules.shell
    scanned = shell.scan('cp "$A" ${B} $1 $_ ${!C} ${D[0]} $? ${#E}')
    kinds = [hole.kind for hole in scanned.holes.values()]
    assert kinds.count("variable") == 6
    assert "$?" in scanned.outer and "${#E}" in scanned.outer


# ---------------------------------------------------------------- story 2: files sourced between calls

# Claude Code sources ~/.claude/shell-snapshots/snapshot-bash-*.sh into every Bash call (read at
# build, 2026-11-23: a script that unaliases, exports and defines functions); session-env/ holds
# the env files SessionStart hooks write (empty on this machine). A planted line there sets an
# "inherited" variable or runs code ungated in a later call.
SOURCED_REFUSED = [
    "cp e/s.sh ~/.claude/shell-snapshots/snapshot-bash-1.sh",
    "tee -a ~/.claude/shell-snapshots/snapshot-bash-1.sh",
    "cp e/s.sh ~/.claude/session-env/abc/hook-1.sh",
    "echo 'export D=x' >> ~/.claude/session-env/abc/hook-1.sh",
]
SOURCED_ASKED = [
    "tee -a ~/.bashrc",
    "cp x ~/.zshenv",
    "mv x ~/.profile",
    "cp x ~/.bash_aliases",
    "cp x ~/.config/fish/conf.d/x.fish",
    "cp x ~/.curlrc",
    "cp x ~/.wgetrc",
    "BASH_ENV=e/x bash -c true",
    "export ENV=e/x; sh -c true",
    "ZDOTDIR=e zsh -c true",
    "env BASH_ENV=e/x bash -c true",
    # T02 bypass review: quoted and escaped names, setters, shebang scripts, moved homes, run text
    'export "BASH_ENV"=/tmp/e; bash -c true',
    "export BASH\\_ENV=/tmp/e; bash -c true",
    "read BASH_ENV <<< /tmp/e; export BASH_ENV; bash -c true",
    "printf -v BASH_ENV /tmp/e; export BASH_ENV; bash -c true",
    "BASH_ENV=/tmp/e ./run.sh",
    "HOME=/tmp/h zsh -c true",
    "XDG_CONFIG_HOME=/tmp/x fish -c true",
    "CURL_HOME=/tmp/c curl https://h/x",
    "WGETRC=/tmp/w wget https://h/x",
    "env 'BASH_FUNC_ls%%=() { id; }' bash -c ls",
    "PS4='$(id)' bash -x -c true",
    "env SHELLOPTS=xtrace bash -c true",
    'ENV=/tmp/e "bash" -i',
    "declare -n h=BASH_ENV; h=/tmp/x; bash -c :",
    "typeset -n h=HOME; h=/tmp/x; bash -lc :",
    "cp x ~/.ssh/rc",
    "cp x ~/.config/environment.d/x.conf",
]


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("X=cobot.rules; cp x ~/.claude/$X", "deny"),
        ("X=config; cp x ~/.gemini/$X/settings.json", "force_ask"),
        ("cp x ~/.gemini/config/$X", "force_ask"),
        ("tee -a ~/.bashrc", "force_ask"),
        ("BASH_ENV=e/x bash -c true", "force_ask"),
        ("cp x $DEST", "allow"),
    ],
)
def test_story3_agy_sameJudgement(rules, tmp_path, monkeypatch, command, expected):
    """Story 3 (ADR-0007): under agy, run_command reaches the same judgement; ``allow`` there is
    no opinion."""
    monkeypatch.delenv("COBOT_RULES_PROJECT_DIR", raising=False)
    home = tmp_path / "home"
    (home / ".gemini" / "config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    workspace = tmp_path / "ws"
    (workspace / ".agent").mkdir(parents=True)
    (workspace / ".agent" / "cobot.rules").write_text("")
    call = {"id": "t1", "name": "run_command", "args": {"CommandLine": command}}
    body = {"hookEventName": "PreToolUse", "toolCall": call, "workspacePaths": [str(workspace)]}
    assert json.loads(rules.gate_agy(json.dumps(body)))["decision"] == expected


@pytest.mark.parametrize("command", SOURCED_REFUSED)
def test_story2_sessionSnapshotsAndEnvFiles_areRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", SOURCED_ASKED)
def test_story2_startFilesAndShellVariables_ask(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize(
    ("tool", "path", "expected"),
    [
        ("Write", "~/.claude/shell-snapshots/snapshot-bash-1.sh", "deny"),
        ("Edit", "~/.claude/session-env/abc/hook-1.sh", "deny"),
        ("Edit", "~/.bashrc", "ask"),
        ("Write", "~/.zshrc", "ask"),
        ("Write", "~/.curlrc", "ask"),
        ("Edit", "~/notes.md", None),
    ],
)
def test_story2_fileTools_sameRows(rules, tool, path, expected):
    loaded, _, _ = rules.load_rules(None)
    assert rules.judge_file(tool, path, None, loaded, None).decision == expected


def test_story2_zdotdirTwins_followTheGatesEnvironment(rules, tmp_path, monkeypatch):
    monkeypatch.setenv("ZDOTDIR", str(tmp_path / "zsh"))
    loaded, _, _ = rules.load_rules(None)
    assert rules.judge_bash(f"cp x {tmp_path}/zsh/.zshrc", loaded, None)[0].decision == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "bash -c true",
        "cat README.md",
        "zsh -c 'echo hi'",
        "ENV=prod true",
        "echo $HOME",
        "grep HOME README.md",
    ],
)
def test_story2_frictionRows_staySilent(rules, command):
    assert decide(rules, command) is None
