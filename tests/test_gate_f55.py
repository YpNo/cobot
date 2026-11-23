"""A shell variable is a hole, not text (spec gate-f55, story 1, F-55).

The scanner emits a ``variable`` hole for ``$NAME``, ``${NAME}``, the positional parameters,
``$_``, ``${!…}`` and subscripts. The gate reads each one by its class in the whole command:
a value the command spells out is put in, a value it computes is a full hole (never spared,
pathlike), and an inherited name or run-time data is spared as a whole word, as ``$(…)`` is.
"""

from __future__ import annotations

import json

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
