"""The shell scanner behind the gate (.agent/specs/gate-substitution.md): words, holes, data, errors."""

from __future__ import annotations

import re

import _cobot_shell as sh
import pytest


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
