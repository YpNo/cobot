"""The shell scanner behind the gate (.agent/specs/gate-substitution.md): words, holes, data, errors."""

from __future__ import annotations

import itertools
import re
import shlex

import _cobot_shell as sh
import pytest


@pytest.fixture(autouse=True)
def fresh_keys(monkeypatch):
    """Sentinel numbers start at 0 in every test (the scanner shares one counter per process)."""
    monkeypatch.setattr(sh, "_COUNTER", itertools.count())


def plain(text: str) -> str:
    """Outer text with sentinels shown as ``<n>`` and runs of blanks collapsed."""
    for key in sh.sentinels(text):
        text = text.replace(key, f"<{key[1:-1]}>")
    return re.sub(r"[ \t]+", " ", text).strip()


def bodies(scan: sh.Scan) -> list[str]:
    """Every command body a scan runs, depth first, outer texts collapsed."""
    found = []
    for hole in scan.holes.values():
        if hole.body is not None:
            found.append(" ".join(plain(hole.body.outer).split()))
            found.extend(bodies(hole.body))
    return found


# ---------------------------------------------------------------- quoting and comments


@pytest.mark.parametrize(
    ("command", "outer"),
    [
        ("echo 'a $(b) `c`'", "echo 'a $(b) `c`'"),
        ('echo "a \\$(b) \\`c\\`"', 'echo "a \\$(b) \\`c\\`"'),
        ("echo \\$(b)", "echo \\$(b)"),
        ("ls # don't", "ls"),
        ("echo a#b $# ${#x} ${x:- #}", "echo a#b $# ${#x} ${x:- #}"),
        ("nix develop .#dev -c cargo test", "nix develop .#dev -c cargo test"),
    ],
)
def test_scan_quotedAndCommentText_staysOutOfHoles(command, outer):
    result = sh.scan(command)
    assert result.error is None and not result.holes
    assert " ".join(result.outer.split()) == outer


def test_scan_quoteInsideComment_doesNotHideTheNextLine():
    result = sh.scan("echo x # '\ngit push --force\n# '")
    assert "git push --force" in result.outer and result.error is None


def test_scan_commentInsideSubstitution_endsAtTheLine():
    result = sh.scan("echo $(true # '\ngit push --force\n) # ')")
    assert bodies(result) == ["true git push --force"]


# ---------------------------------------------------------------- substitutions


def test_scan_substitution_becomesASplitHoleWithItsBody():
    result = sh.scan('for f in $(find .claude -type f); do cat "$f"; done')
    (hole,) = result.holes.values()
    assert not hole.quoted and hole.span == "$(find .claude -type f)"
    assert plain(result.outer) == 'for f in <0>; do cat "$f"; done'
    assert bodies(result) == ["find .claude -type f"]


def test_scan_substitutionInDoubleQuotes_isOneWord():
    result = sh.scan('VIS="$(gh repo view o/r)"')
    (hole,) = result.holes.values()
    assert hole.quoted and bodies(result) == ["gh repo view o/r"]


def test_scan_nestedSubstitutions_areScannedAtEachLevel():
    result = sh.scan('echo $(basename "$(dirname $(pwd))")')
    assert bodies(result) == ['basename "<1>"', "dirname <0>", "pwd"]


def test_scan_backtick_isUnescapedThenScanned():
    result = sh.scan('echo "`echo \\"a\\" \\`date\\``"')
    (hole,) = result.holes.values()
    assert hole.quoted
    assert bodies(result) == ['echo "a" <0>', "date"]


def test_scan_backtickClosesAtTheNextBacktick_quotesIgnored():
    assert sh.scan("echo `true '` ; git push --force ; `'`").error == "unbalanced quote"


def test_scan_escapedBacktickInDoubleQuotes_isLiteral():
    result = sh.scan('grep -n "a \\`b\\` c" f')
    assert not result.holes and result.error is None


def test_scan_ansiC_isAComputedWordWithoutBody():
    result = sh.scan("terraform $'apply'")
    (hole,) = result.holes.values()
    assert hole.quoted and hole.body is None and plain(result.outer) == "terraform <0>"


def test_scan_parameterExpansion_holdsItsSubstitutions():
    result = sh.scan('echo ${x:-$(git push)} "${y:-"$(id)"}"')
    assert sorted(bodies(result)) == ["git push", "id"]


def test_scan_processSubstitution_isOneWordWithItsBody():
    result = sh.scan("diff <(a) >(b)")
    assert [h.quoted for h in result.holes.values()] == [True, True]
    assert bodies(result) == ["a", "b"]


def test_scan_processSubstitutionInDoubleQuotes_isLiteral():
    assert not sh.scan('echo "<(a)"').holes


# ---------------------------------------------------------------- arithmetic


def test_scan_arithmetic_isAHoleWithoutBody():
    (hole,) = sh.scan("echo $((1+2))").holes.values()
    assert hole.body is None and hole.span == "$((1+2))"


def test_scan_arithmeticWhoseDepthDips_isASubstitution():
    result = sh.scan("$((echo A); (git push))")
    assert bodies(result) == ["(echo A); (git push)"]


def test_scan_substitutionInsideArithmetic_isJudged():
    assert bodies(sh.scan("echo $(( a[$(id)] ))")) == ["id"]


@pytest.mark.parametrize("command", ["echo $((1<<EOF))", "echo $[1<<EOF]", "((x = 1<<EOF)); echo hi"])
def test_scan_shiftInArithmetic_isNotAHereDocument(command):
    result = sh.scan(command + "\ngit push")
    assert not result.heredocs and "git push" in result.outer


def test_scan_quotesInsideArithmetic_doNotCloseIt():
    result = sh.scan('echo $(( x + $(echo ")" \\) "(") ))')
    (outer_hole,) = [h for h in result.holes.values() if h.body is None]
    assert outer_hole.span.startswith("$((") and bodies(result) == ['echo ")" \\) "("']


def test_scan_unclosedArithmetic_isAnUnclosedSubstitution():
    assert sh.scan("echo $((1+2").error == "unclosed substitution"


def test_scan_controlOperators_stayInTheWords():
    assert " ".join(sh.scan("a && b || c & d |& e").outer.split()) == "a && b || c & d |& e"


def test_scan_unclosedBracketArithmetic_isAnError():
    assert sh.scan("echo $[1+2").error == "unclosed $["


# ---------------------------------------------------------------- here-documents


def test_scan_quotedHereDocument_bodyIsData_restOfLineKept():
    result = sh.scan("cat <<'EOF' > f; git push --force\n$(id)\nEOF\nls")
    assert plain(result.outer) == "cat ; git push --force\nls"
    assert not result.holes and result.inert_code and result.targets == ["f"]


def test_scan_unquotedHereDocument_runsItsSubstitutions():
    result = sh.scan("cat <<EOF\n$(git push --force)\nEOF")
    assert bodies(result) == ["git push --force"] and result.holes
    assert sh.has_sentinel(result.outer) is False


def test_scan_delimiterQuoteRemoval_findsTheEnd():
    result = sh.scan('cat <<E"O"F\nx\nEOF\nterraform apply')
    assert result.heredocs[0].delimiter == "EOF" and result.heredocs[0].quoted
    assert "terraform apply" in result.outer


def test_scan_dashHereDocument_stripsTabs_twoOnOneLine():
    result = sh.scan("cat <<-A <<\\B\n\tone\n\tA\ntwo\nB\necho done")
    assert [(d.delimiter, d.body) for d in result.heredocs] == [("A", "one\n"), ("B", "two\n")]
    assert "echo done" in result.outer


def test_scan_unterminatedHereDocument_readsToTheEnd():
    result = sh.scan("cat <<'EOF'\ngit push")
    assert "git push" not in result.outer and result.heredocs[0].body == "git push\n"


def test_scan_hereDocumentWithoutDelimiter_isAnError():
    assert sh.scan("cat <<").error == "here-document without a delimiter"
    assert sh.scan("cat <<'EOF").error == "unbalanced quote"


# ---------------------------------------------------------------- redirections


@pytest.mark.parametrize(
    ("command", "outer", "targets"),
    [
        ("cargo 2>/dev/null publish", "cargo publish", ["/dev/null"]),
        ("</dev/null terraform apply", "terraform apply", ["/dev/null"]),
        ("echo x>file 2> err {fd}>log &>all", "echo x", ["file", "err", "log", "all"]),
        ("make 2>&1 >>out", "make", ["1", "out"]),
        ("cmd >| f <> g", "cmd", ["f", "g"]),
    ],
)
def test_scan_redirection_leavesTheWords_keepsTheTarget(command, outer, targets):
    result = sh.scan(command)
    assert " ".join(result.outer.split()) == outer and result.targets == targets


def test_scan_processSubstitutionAsTarget_isStillJudged():
    result = sh.scan("while read l; do echo $l; done < <(find . -name x)")
    assert bodies(result) == ["find . -name x"] and "<" not in result.outer


def test_scan_hereString_isData_itsSubstitutionsRun():
    result = sh.scan('tee <<< "$(id)" x')
    assert bodies(result) == ["id"] and not result.targets
    assert sh.scan("read x <<< '$(id)'").inert_code


# ---------------------------------------------------------------- known value


@pytest.mark.parametrize(
    ("command", "value"),
    [
        ("git commit -m \"$(cat <<'EOF'\nit's done)\nEOF\n)\"", "it's done)"),
        ('x "$(cat <<EOF\nplain text\n\nEOF\n)"', "plain text"),
        ('x "$(cat <<-EOF\n\tindented\n\tEOF\n)"', "indented"),
        ('x "$(cat <<EOF\n$HOME\nEOF\n)"', None),
        ('x "$(cat <<EOF f\nbody\nEOF\n)"', None),
        ("x \"$(sed s/a/b/ <<'EOF'\nbody\nEOF\n)\"", None),
        ('x "$(cat)"', None),
    ],
)
def test_scan_knownValue_onlyForABareCatHereDocument(command, value):
    (hole,) = sh.scan(command).holes.values()
    assert hole.value == value


# ---------------------------------------------------------------- errors


@pytest.mark.parametrize(
    ("command", "error"),
    [
        ("echo 'unbalanced", "unbalanced quote"),
        ('echo "unbalanced', "unbalanced quote"),
        ("echo $'unbalanced", "unbalanced quote"),
        ("echo $(date", "unclosed substitution"),
        ("echo `date", "unclosed backtick"),
        ("echo ${x", "unclosed ${"),
        ("echo $(case x in a) git push;; esac)", "'case' inside a substitution"),
        ("cat <(case x in x) git push --force;; esac)", "'case' inside a substitution"),
        ('echo "${x@P}"', "${…@P} prompt expansion"),
        ("echo " + "$(" * 10 + ")" * 10, "more than 8 nested substitutions"),
        ("echo ", "reserved character in the command"),
        ("echo \0", "reserved character in the command"),
    ],
)
def test_scan_outsideTheModel_setsError(command, error):
    assert sh.scan(command).error == error


def test_scan_caseAtTheTopLevel_isNotAnError():
    result = sh.scan("case x in a) git push;; esac")
    assert result.error is None and "git push" in result.outer


def test_scan_caseInsideBackticks_isScannedWhole():
    assert bodies(sh.scan("echo `case x in a) git push;; esac`")) == ["case x in a) git push;; esac"]


def test_unescapeBacktick_quotesOnlyItsSpecialCharacters():
    assert sh.unescape_backtick('\\\\ \\` \\$ \\" \\n', False) == '\\ ` $ \\" \\n'
    assert sh.unescape_backtick('\\"', True) == '"'


# ---------------------------------------------------------------- code review, 2026-11-13


def test_scan_backslashNewline_isRemoved():
    assert " ".join(sh.scan("git pu\\\nsh --force").outer.split()) == "git push --force"


def test_scan_trailingBackslash_isAnError():
    assert sh.scan("echo a\\").error == "trailing backslash"


@pytest.mark.parametrize("command", ["true\\ #;terraform apply", "echo a\\;#x; ls"])
def test_scan_hashAfterAnEscape_isNotAComment(command):
    assert "#" in sh.scan(command).outer


def test_scan_processSubstitutionInsideParameter_runs():
    assert bodies(sh.scan("echo ${x:->(terraform apply)} ${y:-<(ls)}")) == ["terraform apply", "ls"]


def test_scan_closingParen_endsARedirectionTarget():
    result = sh.scan("(echo x >~/.claude/settings.json)")
    assert result.targets == ["~/.claude/settings.json"] and result.outer.rstrip().endswith(")")


def test_scan_hereDocumentDelimiter_joinsContinuationLines():
    result = sh.scan("cat <<E\nE\\\n\nterraform apply\nE")
    assert "terraform apply" in result.outer
    quoted = sh.scan("cat <<'E'\nE\\\n\nterraform apply\nE")
    assert "terraform apply" not in quoted.outer


@pytest.mark.parametrize(
    "command", ["(echo $((echo `(`) ; git push ; (true)))", "(echo $((echo $'\\'(') ; git push ; (true)))"]
)
def test_scan_backtickAndAnsiInsideDollarParens_doNotCountParens(command):
    assert "git push" in bodies(sh.scan(command))[0]


# ---------------------------------------------------------------- brace and glob expansion (gate-expansion)


def words(command: str) -> list[str]:
    """bash's words for a command without operators: scanned, split, braces expanded, each hole
    shown as ``<kind:span>``."""
    result = sh.scan(command)
    assert result.error is None, result.error
    shown = []
    for word in sh.expand_braces(shlex.split(result.outer)):
        for key in sh.sentinels(word):
            hole = sh.REGISTRY[key]
            word = word.replace(key, f"<{hole.kind}:{hole.span}>")
        shown.append(word)
    return shown


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("cargo {publish,}", ["cargo", "publish"]),
        ("{terraform,} apply", ["terraform", "apply"]),
        ("p {,}", ["p"]),
        ("p a{,}b", ["p", "ab", "ab"]),
        ("p {a,b}{c,d}", ["p", "ac", "ad", "bc", "bd"]),
        ("p {a,{b,c}d}e", ["p", "ae", "bde", "cde"]),
        ("p {{a,b}}", ["p", "{a}", "{b}"]),
        ("p {a,b}}", ["p", "a}", "b}"]),
        (
            "p {1..3} {a..c} {1..7..3} {7..1..2} {1..4..0}",
            ["p", "1", "2", "3", "a", "b", "c", "1", "4", "7"] + ["7", "5", "3", "1", "1", "2", "3", "4"],
        ),
        ("p {05..1..2} {1..-01} {+1..2}", ["p", "05", "03", "01", "001", "000", "-01", "1", "2"]),
        ('p "{a,b}" \\{a,b} {a\\,b} {"a b",c}', ["p", "{a,b}", "{a,b}", "{a,b}", "a b", "c"]),
        (
            "p {} {a} {a,b {a..} stash@{0} ${x:-{a,b}}",
            ["p", "{}", "{a}", "{a,b", "{a..}", "stash@{0}", "${x:-{a,b}}"],
        ),
        ("p {~,x}/a {$,}x", ["p", "~/a", "x/a", "$x", "x"]),
        ("p {a,b", ["p", "{a,b"]),
        ('p {$(echo ")"),b}', ["p", '<substitution:$(echo ")")>', "b"]),
        ("p {$(echo x),y}", ["p", "<substitution:$(echo x)>", "y"]),
        ("cargo publis? publi[s]h *.py", ["cargo", "publis<glob:?>", "publi<glob:[s]>h", "<glob:*>.py"]),
        ("p settings.[]j]son a[[:alpha:]]b", ["p", "settings.<glob:[]j]>son", "a<glob:[[:alpha:]]>b"]),
        (
            "p ~/.[c]laude/settings.jso[n] ~/.claude[/]x",
            ["p", "~/.<glob:[c]>laude/settings.jso<glob:[n]>", "~/.claude[/]x"],
        ),
        ("p {a,b}*", ["p", "a<glob:*>", "b<glob:*>"]),
        ("[ -f x ] [[ ]]", ["[", "-f", "x", "]", "[[", "]]"]),
        ("echo $* $? $# $@ $1 \"*\" '?' \\*", ["echo", "$*", "$?", "$#", "$@", "$1", "*", "?", "*"]),
    ],
)
def test_expandBraces_andGlobHoles_matchBash(command, expected):
    assert words(command) == expected


@pytest.mark.parametrize(
    ("command", "error"),
    [
        ("cargo publi{[,x}s{],y}h", "brackets and braces in one word"),
        ("cat settings.[{j],x}son", "brackets and braces in one word"),
        ("cat a]{b,c}", "brackets and braces in one word"),
        ("cat {b,c}x]", "brackets and braces in one word"),
        ("cargo +(publish)", "extended glob"),
        ("cargo @(publish) ?(a) *(b)", "extended glob"),
        ("!(zzz) apply", "extended glob"),
        ("if !(grep -q x f); then :; fi", "extended glob"),
        ('echo a["$(git push)"]', "expansion inside a bracket expression"),
        ("echo a[`git push`]", "expansion inside a bracket expression"),
        ("echo a[${x}]", "expansion inside a bracket expression"),
        ("echo {1..300}", "brace expansion too large"),
        ("echo " + "{a,b}" * 9, "brace expansion too large"),
        ("echo {a,b}{c,d} " * 70, "brace expansion too large"),
        ("echo {1..99999999999}", "brace expansion too large"),
        ("echo {Z..b}", "brace sequence builds punctuation"),
    ],
)
def test_scan_expansionOutsideTheModel_isAnError(command, error):
    assert sh.scan(command).error == error


def test_scan_braceWithAnUnclosedSubstitution_isRefusedByTheSubstitution():
    assert sh.scan("p {$(x,b}").error == "unclosed quote or expansion"


def test_scan_negatedSubshellWithABlank_staysCommands():
    assert sh.scan("! (git push)").error is None


def test_scan_globInsideQuotesOrArithmeticOrParameter_isNoHole():
    assert not sh.scan('echo "*" "$((2*3))" ${x#*} $((4*(5)))').holes.keys() - {
        k for k, h in sh.REGISTRY.items() if h.kind == "substitution"
    }


def test_scan_substitutionAfterABracket_endsTheBracketAndRuns():
    assert bodies(sh.scan("echo a[$(git push)]")) == ["git push"]


def test_scan_braceAlternative_runsItsSubstitution():
    assert bodies(sh.scan("p {$(git push),y}")) == ["git push"]


def test_scan_braceAlternative_hashIsNotAComment():
    assert words("p {#,a}") == ["p", "#", "a"]


def test_scan_redirectionTargetGlob_isAHoleInTheTarget():
    (target,) = sh.scan("echo x > ~/.claude/settings.js?").targets
    assert sh.kind_of(sh.sentinels(target)[0]) == "glob"


def test_join_leavesSentinelsBare_andScanAcceptsThemIssued():
    first = sh.scan("uv run pytest tests/test_*.py")
    tokens = shlex.split(first.outer)[2:]
    text = sh.join(tokens)
    key = sh.sentinels(text)[0]
    assert text == f"pytest tests/test_{key}.py"
    assert sh.join([f"a b{key}"]) == f"'a b'{key}"
    again = sh.scan(text, frozenset({key}))
    assert again.error is None and again.holes[key] is first.holes[key]
    assert shlex.split(again.outer) == tokens
    assert sh.join(["a b", ""]) == shlex.join(["a b", ""])


def test_scan_sentinelNotIssued_isAnError():
    key = sh.sentinels(sh.scan("ls *").outer)[0]
    assert sh.scan(f"ls {key}").error == "reserved character in the command"
    assert sh.scan(f"ls {key}", frozenset({"9"})).error == "reserved character in the command"
    assert sh.scan("ls ", frozenset({key})).error == "reserved character in the command"
