"""Editors and debuggers, newlines, loader variables and dotglob (spec gate-f63-f65: F-63, F-64,
F-65, F-70).

Each Goal row is measured on ``3e83cc6`` with the owner and project layers empty; the friction
rows stay silent. Fixtures hold no secret-shaped literal: ``x`` stands for any value. ``\\n``
inside a quoted row is a newline the shell passes in the word.
"""

from __future__ import annotations

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


def assert_all(rules, commands, expected, cwd=None):
    wrong = {command: decide(rules, command, cwd) for command in commands}
    wrong = {command: got for command, got in wrong.items() if got != expected}
    assert not wrong, wrong


# ---------------------------------------------------------------- story 3: newlines (F-64)

NEWLINE_DENY = [
    # row 1: an escaped backslash, then a newline, is a separator; the next line is a command
    "echo a\\\\\nrm -rf /",
    "bash -c 'echo a\\\\\nrm -rf /'",
    "echo a\\\\\ngit push --force origin main",
]
NEWLINE_ASK = [
    # row 2: a quoted newline stays a newline, so an awk comment ends at it
    "awk '#x\nBEGIN{system(\"x\")}'",
    "gawk '#x\n@load \"x\"'",
]
NEWLINE_UNCHANGED_DENY = [
    "bash -c 'echo a\nrm -rf /'",
    "r\\\nm -rf /",
    "# it's\nrm -rf /",
]
NEWLINE_UNCHANGED_ASK = [
    "sed 's/a/b/\\\ne' f",
    "git commit -m 'a\nb'",
    "gh pr create --body 'a\nb'",
    "python3 -c 'x=1\ny'",
]
NEWLINE_FRICTION = [
    'echo "a\nb"',
    "sed -n 'p\nw out' f",
    "cat <<'EOF'\nrm -rf /\nEOF",
    'bash -c "echo a\\\nrm -rf /"',  # bash joins it into ``echo arm -rf /``
]


def test_story3_escapedBackslashThenNewline_isASeparator(rules, project):
    assert_all(rules, NEWLINE_DENY, "deny")


def test_story3_quotedNewline_reachesTheReader(rules, project):
    assert_all(rules, NEWLINE_ASK, "ask")


def test_story3_unchangedDenies_stayDenied(rules, project):
    assert_all(rules, NEWLINE_UNCHANGED_DENY, "deny")


def test_story3_unchangedAsks_stayAsks(rules, project):
    assert_all(rules, NEWLINE_UNCHANGED_ASK, "ask")


def test_story3_friction_staysSilent(rules, project):
    assert_all(rules, NEWLINE_FRICTION, None)


@pytest.mark.parametrize(
    ("text", "words"),
    [
        ("echo 'a\nb'", ["echo", "a\nb"]),  # single quotes keep the newline
        ('echo "a\nb"', ["echo", "a\nb"]),  # double quotes too
        ("echo 'a\\\nb'", ["echo", "a\\\nb"]),  # single quotes keep both characters
        ('echo "a\\\nb"', ["echo", "ab"]),  # double quotes drop a backslash-newline
        ("ec\\\nho x", ["echo", "x"]),  # outside quotes it joins the words
    ],
)
def test_story3_shellItems_readsNewlinesAsBash(rules, text, words):
    assert rules.shell_items(text) == [words]


def test_story3_unquotedNewline_separates(rules):
    assert rules.shell_items("a\nb") == [["a"], ";", ["b"]]
    assert rules.shell_items("a\\\\\nb") == [["a\\"], ";", ["b"]]


# T01 review: forms the gate read differently from bash, each a never row hidden
REVIEW_DENY = [
    "sh -c 'echo a\\\\\nrm -rf /'",
    'bash -c "echo a\\\\\\\\\nrm -rf /"',  # the inner string is ``a\\``, then a new line
    'bash -c "# it\'s\nrm -rf /"',
]
# in double quotes \$ is $ to bash: the inner string holds an ANSI-C quote, then a command. A body
# holding an ANSI-C quote is opaque (command_parts takes expansion holes only), so it asks
REVIEW_ASK = [
    "bash -c \"echo \\$'it\\\\'s'; git push --force origin main #'\"",
    "bash -c \"echo \\$'it\\\\'s'\ngit push --force origin main #'\"",
]


def test_story3_review_innerStringsReadAsBash(rules, project):
    assert_all(rules, REVIEW_DENY, "deny")


def test_story3_review_ansiQuoteInAnInnerString_asks(rules, project):
    assert_all(rules, REVIEW_ASK, "ask")


def test_story3_review_doubleQuotedEscapedDollar_isADollar(rules):
    assert rules.shell_items("echo \"\\$x\" '\\$y'") == [["echo", "$x", "\\$y"]]


def test_story3_review_backtickInDoubleQuotes_isNotSilent(rules, project):
    command = "bash -c \"echo \\`echo '\\`\ngit push --force origin main\n#'\""
    assert decide(rules, command) in ("ask", "deny")


def test_story3_review_makefileEvenBackslashes_endTheLine(rules, project):
    (project / "Makefile").write_text("b:\n\techo a\\\\\n\tgit push --force origin main\n")
    assert decide(rules, "make b") == "deny"


def test_story3_review_makefileContinuation_staysOneLine(rules, project):
    (project / "Makefile").write_text("b:\n\techo a \\\n\t  b\n")
    assert decide(rules, "make b") is None
