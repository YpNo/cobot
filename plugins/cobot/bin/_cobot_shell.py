"""Shell text to structure for the rules gate (.agent/specs/gate-substitution.md): which parts of
a Bash command are words of the command, which run as commands of their own, which are data.

``scan(command)`` reads the text once, modelled on bash 5.2, and returns a ``Scan``:

- ``outer``: the command with every substitution replaced by a sentinel, here-document bodies,
  comments and redirections removed (the rest of each line kept), quotes left in place for
  ``shlex``;
- ``holes``: each substitution (``$(…)``, a backtick, ``<(…)``, ``>(…)``), arithmetic
  ``$((…))``/``$[…]``, ANSI-C ``$'…'`` and locale ``$"…"`` word, ``${…}`` with an operator
  (.agent/specs/gate-findings.md), keyed by its sentinel, with its scanned body
  when it runs a command; a hole whose sentinel is not in ``outer`` (a redirection target, an
  unquoted here-document body, inside arithmetic) still runs and is judged by its body;
- ``targets``: redirection target words, for the protected-file check; ``writes``: those a
  redirection writes (``>``, ``>>``, ``>|``, ``&>``, ``<>``, ``>&`` to a word that is no file
  descriptor), for the read-only agents;
- ``error``: set on anything the scanner does not model exactly, so the caller asks.

Expansion (.agent/specs/gate-expansion.md): an unquoted brace expression is a ``brace`` hole whose
alternatives ``expand_braces`` turns into bash's words after splitting; an unquoted ``*``, ``?``
or bracket expression is a ``glob`` hole, zero or more file names. Every hole is kept in
``REGISTRY`` under a key unique in the process, so a runner's inner command, scanned again with
``issued`` keys, shares them.

Soundness target: a hole in the command's words, a substitution or a glob, is never silent where
some text in its place, for a glob some set of file names, would change which program runs, or
make a rule match the form that names what runs; brace expansion is computed, not approximated.
Code that
reaches execution from a variable's value (arithmetic on it, ``${x@P}``) is not a hole: the
caller's quoted-code rule and the ``@P`` error cover what the command text shows.
"""

from __future__ import annotations

import itertools
import re
import shlex
from dataclasses import dataclass, field

OPEN, CLOSE = "", ""  # private-use characters: never in a command, never NUL
SENTINEL_RE = re.compile(f"{OPEN}\\d+{CLOSE}")
MAX_DEPTH = 8  # nesting of substitutions before the command is refused
SPAN_LIMIT = 60
METACHARS = frozenset(" \t\n;&|()<>")
QUOTING_MODES = ("top", "sub", "arith", "param")  # where quotes quote; not inside "…" or a body
FD_PREFIX_RE = re.compile(r"(?:\d+|\{[A-Za-z_][A-Za-z0-9_]*\})$")
CAT_HEREDOC_RE = re.compile(r"^\s*cat\s*$")
WRITING_OPERATORS = frozenset({">", ">>", ">|", "&>", "&>>", "<>", ">&"})
CLOSERS = frozenset({")", "}", "done", "fi", "esac"})  # a compound command ends: it owns what follows
FD_WORD_RE = re.compile(r"^\d*-?$")  # ``>&2``, ``>&-``, ``>&3-``: a descriptor, not a file
EXPANDING_MODES = ("top", "sub")  # where bash expands braces and globs in a word
EXTGLOB_CHARS = "?*+@!"  # before ``(``: an extended glob when ``extglob`` is on
SPECIAL_PARAMETERS = "*?@#-!$"  # ``$*``, ``$?`` … : a parameter, never a glob
MAX_BRACE_WORDS = 256  # words brace expansion may build in one command before it asks
BRACKET_CODE_RE = re.compile(r"\$[({]|`")
# ``${…}`` read as a variable's value or a number: a name, positional or special parameter,
# ``#`` or ``!`` before one, a subscript; anything else holds an operator word bash expands
PLAIN_PARAMETER_RE = re.compile(r"^[#!]?(?:[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?|\d+|[*@#?$!-])$")
POSITIONAL_PARAMETERS = "*@"  # with the digits: argv a ``set``, a function or ``sh -c`` gives
VARIABLE_MODES = ("top", "sub", "dq", "param")  # where an expansion is a word of a command
NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# names the gate puts in itself, as text (``home_forms``, ``expand_pwd``); an in-command
# assignment to one adds a reading there, never replaces the gate's own value
GATE_TEXT_VARIABLES = frozenset({"HOME", "PWD"})
TEXT_PARAMETER_RE = re.compile(r"^(?:#.+|[?$#!-])$")  # a length or a status: a number, never a path
ALTERNATIVE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*|\d+):?[-+=](.*)$", re.DOTALL)
SEQUENCE_RE = re.compile(r"^(?:([-+]?\d+)\.\.([-+]?\d+)|([A-Za-z])\.\.([A-Za-z]))(?:\.\.([-+]?\d+))?$")
_COUNTER = itertools.count()  # one key space per process: inner scans share the outer holes
REGISTRY: dict[str, Hole] = {}  # every hole by key; the gate reads kinds and spans here


@dataclass(frozen=True)
class Hole:
    key: str  # the sentinel standing for it in the outer text
    span: str  # the original text, capped, for reasons and traces
    quoted: bool  # exactly one word (inside double quotes, a process substitution, ``$'…'``)
    body: Scan | None  # the command it runs; None for arithmetic, ``$'…'``, braces and globs
    value: str | None = None  # known text: a bare ``cat <<'D'`` here-document, an untranslated ``$"…"``
    kind: str = "substitution"  # or ``glob`` (file names), ``brace`` (``alternatives``), ``variable``
    alternatives: tuple[str, ...] = ()  # a brace's alternatives, scanned, quotes kept; a variable's word
    name: str = ""  # a variable's name: ``X``, ``1``, ``@``, ``_``, or ``!X``/``A[0]`` (never put in)
    operator: str = ""  # a variable's ``${…}`` operator: "" none, ``alt`` (-, :-, +, :+, =, :=) or ``other``


@dataclass(frozen=True)
class HereDoc:
    delimiter: str
    quoted: bool
    strip_tabs: bool
    body: str = ""


@dataclass(frozen=True)
class Stage:
    """One pipeline stage of this text: its list item (split on ``;``, ``&&``, ``||``, ``&`` and
    newline), its place in the pipeline, and its span in ``outer`` (spec gate-f36-f40-f44, Plan 6)."""

    item: int
    index: int
    start: int
    end: int


@dataclass(frozen=True)
class Redirect:
    """A redirection, here-document (``<<``) or here-string (``<<<``) with the stage it sits in;
    ``after_closer`` when a ``)``, ``}``, ``done``, ``fi`` or ``esac`` precedes it in that stage,
    so a compound command owns it."""

    item: int
    index: int
    operator: str
    fd: str
    target: str
    after_closer: bool


@dataclass
class Scan:
    outer: str = ""
    holes: dict[str, Hole] = field(default_factory=dict)
    targets: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)  # targets a redirection writes
    heredocs: list[HereDoc] = field(default_factory=list)
    stages: list[Stage] = field(default_factory=list)
    redirects: list[Redirect] = field(default_factory=list)
    inert_code: bool = False  # data text (a quoted here-document, a here-string) holds ``$(`` or a backtick
    error: str | None = None


class ShellError(Exception):
    """Text the scanner does not model exactly; the caller asks."""


def scan(command: str, issued: frozenset[str] = frozenset()) -> Scan:
    """Scan a whole command. Never raises: a construct outside the model sets ``error``. A sentinel
    in ``issued`` (one the gate put in a runner's inner command) stands for its registered hole;
    any other sentinel character is an error."""
    if "\0" in command or not set(OPEN + CLOSE).isdisjoint(SENTINEL_RE.sub(_drop_issued(issued), command)):
        return Scan(outer=command, error="reserved character in the command")
    scanner = _Scanner(command, 0, "top", issued)
    try:
        return scanner.run()
    except ShellError as error:
        return Scan(outer=command, error=str(error))


def _drop_issued(issued: frozenset[str]):
    return lambda match: "" if match.group() in issued and match.group() in REGISTRY else match.group()


def register(span: str, quoted: bool, kind: str) -> str:
    """A hole the gate makes after the scan (spec gate-f55: a variable read as a full hole)."""
    key = f"{OPEN}{next(_COUNTER)}{CLOSE}"
    REGISTRY[key] = Hole(key, span[:SPAN_LIMIT], quoted, None, kind=kind)
    return key


def kind_of(key: str) -> str | None:
    hole = REGISTRY.get(key)
    return hole.kind if hole else None


def join(tokens: list[str]) -> str:
    """``shlex.join`` that leaves hole sentinels bare, so scanning the text again with them issued
    gives back the same words and holes."""
    return " ".join(_join_word(token) for token in tokens)


def _join_word(token: str) -> str:
    pieces = re.split(f"({SENTINEL_RE.pattern})", token)
    joined = "".join(p if SENTINEL_RE.fullmatch(p) else shlex.quote(p) if p else "" for p in pieces)
    return joined or "''"


def expand_braces(tokens: list[str]) -> list[str]:
    """Bash's words for tokens holding brace holes: the cartesian product of the alternatives, left
    to right, nested ones recursively; a word expansion leaves empty is dropped (stricter than
    bash, which keeps a quoted one). The scanner capped the count at MAX_BRACE_WORDS."""
    out: list[str] = []
    for token in tokens:
        words = _expand_word(token)
        out.extend(words if words == [token] else [word for word in words if word])
    return out


def _expand_word(token: str) -> list[str]:
    for key in sentinels(token):
        hole = REGISTRY.get(key)
        if hole is not None and hole.kind == "brace":
            head, tail = token.split(key, 1)
            return [word for alt in hole.alternatives for word in _expand_word(head + _dequote(alt) + tail)]
    return [token]


def _dequote(alternative: str) -> str:
    """Quote removal on one alternative, which holds no unquoted blank."""
    return "".join(shlex.split(alternative)) if alternative else ""


def sentinels(text: str) -> list[str]:
    return SENTINEL_RE.findall(text)


def has_sentinel(text: str) -> bool:
    return OPEN in text


class _Scanner:
    """One level of text: ``top`` (a command), ``sub`` (until its ``)``), ``dq`` (inside double
    quotes), ``heredoc`` (an unquoted body), ``arith`` (arithmetic: no here-documents, comments
    or redirections), ``param`` (an unquoted ``${…}``: like ``arith``, but ``<(…)`` and ``>(…)``
    still run). Braces and globs expand in ``top`` and ``sub`` only."""

    def __init__(
        self, text: str, depth: int, mode: str, issued: frozenset[str], start: int = 0, in_word: bool = False
    ):
        if depth > MAX_DEPTH:
            raise ShellError(f"more than {MAX_DEPTH} nested substitutions")
        self.text, self.depth, self.mode, self.issued = text, depth, mode, issued
        self.i = start
        self.in_word = in_word  # a brace alternative: its first character does not start a word
        self.word_brace = self.word_bracket = False  # the current word holds a brace, a bracket
        self.word_product = 1  # words the current word's braces build
        self.brace_words = 0  # words built so far by braces in this text
        self.out: list[str] = []
        self.scan = Scan()
        self.parens = 0
        self.pending: list[HereDoc] = []
        self.capture: int | None = None  # start of a redirection target in ``out``
        self.capture_data = False  # the target is a here-string: data, not a file
        self.capture_operator = ""  # the operator of the pending target
        self.capture_where: tuple[int, int, str, bool] = (0, 0, "", False)  # item, stage, fd, closer
        self.item = self.stage_index = self.stage_start = 0
        self.skip_separator = False  # the second character of ``&&``, ``||`` or ``|&``

    # ------------------------------------------------------------ driver

    def run(self) -> Scan:
        while self.i < len(self.text):
            if self.step():
                break
        else:
            if self.mode == "sub":
                raise ShellError("unclosed substitution")
        self.end_capture()  # a here-document still pending has no body: bash reads nothing
        self.end_word()
        self.close_stage()
        self.scan.outer = "".join(self.out)
        return self.scan

    # ------------------------------------------------------------ lists and pipelines

    def length(self) -> int:
        return sum(len(piece) for piece in self.out)

    def close_stage(self) -> None:
        stage = Stage(self.item, self.stage_index, self.stage_start, self.length())
        self.scan.stages.append(stage)

    def separator(self, c: str) -> str | None:
        """``item`` or ``stage`` when ``c`` ends a pipeline stage here, else None."""
        if self.mode not in ("top", "sub") or c not in ";&|\n":
            return None
        if self.skip_separator:
            self.skip_separator = False
            return "rest"  # the next stage starts after this character
        if c == "\n" and "".join(self.out).rstrip(" \t").endswith(("|", "&&")):
            return None  # ``echo x |`` then a newline: the pipeline or list goes on
        following = self.text[self.i + 1 : self.i + 2]
        if c == "|":
            self.skip_separator = following in ("|", "&")
            return "item" if following == "|" else "stage"
        self.skip_separator = c == "&" and following == "&"
        return "item"

    def open_stage(self, kind: str) -> None:
        if kind == "item":
            self.item, self.stage_index = self.item + 1, 0
        elif kind == "stage":
            self.stage_index += 1
        self.stage_start = self.length()

    def after_closer(self) -> bool:
        so_far = "".join(self.out)[self.stage_start :]
        return any(word in CLOSERS for word in re.findall(r"[()]|[^\s()]+", so_far))

    def step(self) -> bool:
        """Handle the text at ``self.i``; True when this level ends."""
        c = self.text[self.i]
        if c == OPEN:
            return self.issued_hole()
        if c == "\\":
            return self.backslash()
        if c == "'" and self.mode in QUOTING_MODES:
            return self.single_quoted()
        if c == '"' and self.mode in QUOTING_MODES:
            return self.double_quoted()
        if c == "$":
            return self.dollar()
        if c == "`":
            return self.backtick()
        if self.mode in ("dq", "heredoc"):
            self.emit(c)
            self.i += 1
            return False
        return self.unquoted(c)

    def backslash(self) -> bool:
        """A backslash-newline is removed, as bash does before anything else reads the line; any
        other escape is one piece, which never starts a word or a comment."""
        pair = self.text[self.i : self.i + 2]
        if len(pair) < 2:
            raise ShellError("trailing backslash")
        if pair != "\\\n":
            self.emit(pair)
        self.i += 2
        return False

    def issued_hole(self) -> bool:
        """A sentinel ``scan`` accepted as issued: the same hole, the same word."""
        end = self.text.index(CLOSE, self.i) + 1
        key = self.text[self.i : end]
        self.scan.holes[key] = REGISTRY[key]
        self.emit(key)
        self.i = end
        return False

    def unquoted(self, c: str) -> bool:
        if c in METACHARS:
            self.end_word()
        if c in " \t\n" or c in ";&|":
            self.end_capture()
        if c == "\n":
            kind = self.separator(c)
            if kind in ("item", "stage"):
                self.close_stage()
            self.emit(c)
            if kind:
                self.open_stage(kind)
            self.i += 1
            self.read_heredocs()
            return False
        if c == "#" and self.at_word_start() and self.mode in ("top", "sub"):
            end = self.text.find("\n", self.i)
            self.i = len(self.text) if end < 0 else end
            return False
        if c in "<>" and self.mode == "param" and self.text[self.i + 1 : self.i + 2] == "(":
            self.process_substitution()
            return False
        if c in "<>&" and self.mode in ("top", "sub") and self.redirection():
            return False
        if self.mode in EXPANDING_MODES and self.expansion(c):
            return False
        if c == "(":
            return self.open_paren()
        if c == ")":
            return self.close_paren()
        if self.mode == "sub" and self.at_word_start() and self.word_is("case"):
            raise ShellError("'case' inside a substitution")
        kind = self.separator(c)
        if kind in ("item", "stage"):
            self.close_stage()
        self.emit(c)
        if kind:
            self.open_stage(kind)
        self.i += 1
        return False

    # ------------------------------------------------------------ output helpers

    def emit(self, piece: str) -> None:
        self.out.append(piece)

    def at_word_start(self) -> bool:
        return not self.in_word if not self.out else ends_word(self.out[-1])

    def word_is(self, word: str) -> bool:
        end = self.i + len(word)
        return self.text[self.i : end] == word and (end == len(self.text) or self.text[end] in METACHARS)

    def hole(
        self,
        span: str,
        quoted: bool,
        body: Scan | None,
        value: str | None = None,
        kind: str = "substitution",
        alternatives: tuple[str, ...] = (),
        name: str = "",
        operator: str = "",
    ) -> None:
        key = f"{OPEN}{next(_COUNTER)}{CLOSE}"
        hole = Hole(key, span[:SPAN_LIMIT], quoted, body, value, kind, alternatives, name, operator)
        self.scan.holes[key] = REGISTRY[key] = hole
        self.emit(key)

    def child(self, mode: str, start: int, text: str | None = None, in_word: bool = False) -> _Scanner:
        source = self.text if text is None else text
        return _Scanner(source, self.depth + 1, mode, self.issued, start, in_word)

    # ------------------------------------------------------------ braces and globs

    def end_word(self) -> None:
        """A blank or an operator ends the word: count what its braces built."""
        if self.word_product > 1:
            self.brace_words += self.word_product
            if self.brace_words > MAX_BRACE_WORDS:
                raise ShellError("brace expansion too large")
        self.word_brace = self.word_bracket = False
        self.word_product = 1

    def expansion(self, c: str) -> bool:
        """An unquoted glob character, bracket or brace in a word; True when one was read. Bash
        globs the words braces build, so a word with both a brace and a bracket is refused."""
        if c in EXTGLOB_CHARS and self.text[self.i + 1 : self.i + 2] == "(":
            raise ShellError("extended glob")
        if c in "*?":
            self.hole(c, False, None, kind="glob")
            self.i += 1
            return True
        if c in "[]":
            self.word_bracket = True
            if self.word_brace:
                raise ShellError("brackets and braces in one word")
            end = bracket_end(self.text, self.i) if c == "[" else None
            if end is None:
                return False
            self.hole(self.text[self.i : end], False, None, kind="glob")
            self.i = end
            return True
        return c == "{" and self.brace()

    def brace(self) -> bool:
        found = brace_end(self.text, self.i)
        if found is None:
            return False
        end, commas = found
        if self.word_bracket:
            raise ShellError("brackets and braces in one word")
        if commas:
            cuts = [self.i, *commas, end - 1]
            pieces = [self.text[a + 1 : b] for a, b in itertools.pairwise(cuts)]
            alternatives, count = self.alternatives(pieces)
        else:
            alternatives = sequence(self.text[self.i + 1 : end - 1])
            count = len(alternatives)
        self.word_brace = True
        self.word_product *= count
        if self.word_product > MAX_BRACE_WORDS:
            raise ShellError("brace expansion too large")
        self.hole(self.text[self.i : end], False, None, kind="brace", alternatives=alternatives)
        self.i = end
        return True

    def alternatives(self, pieces: list[str]) -> tuple[tuple[str, ...], int]:
        """Each alternative scanned as part of a word (its substitutions and globs become holes of
        their own, nested braces too) and the words they build together."""
        scanned, count = [], 0
        for piece in pieces:
            inner = self.child("top", 0, piece, in_word=True)
            result = inner.run()
            self.adopt(result)
            scanned.append(result.outer)
            count += inner.brace_words or 1
        return tuple(scanned), count

    def adopt(self, inner: Scan) -> None:
        """Holes found in arithmetic or a here-string still run: keep them for judging."""
        self.scan.holes.update(inner.holes)
        self.scan.inert_code = self.scan.inert_code or inner.inert_code

    # ------------------------------------------------------------ quotes

    def single_quoted(self) -> bool:
        end = self.text.find("'", self.i + 1)
        if end < 0:
            raise ShellError("unbalanced quote")
        self.emit(self.text[self.i : end + 1])
        self.i = end + 1
        return False

    def double_quoted(self) -> bool:
        inner = self.child("dq", self.i + 1)
        while inner.i < len(self.text) and self.text[inner.i] != '"':
            inner.step()
        if inner.i >= len(self.text):
            raise ShellError("unbalanced quote")
        self.scan.holes.update(inner.scan.holes)
        self.emit('"' + "".join(inner.out) + '"')
        self.i = inner.i + 1
        return False

    def locale(self) -> bool:
        """``$"…"``: double-quoted text a message catalogue may translate into anything, so a quoted
        hole; its value is the untranslated text when that holds no expansion or escape."""
        start = self.i
        inner = self.child("dq", self.i + 2)
        while inner.i < len(self.text) and self.text[inner.i] != '"':
            inner.step()
        if inner.i >= len(self.text):
            raise ShellError("unbalanced quote")
        self.scan.holes.update(inner.scan.holes)
        raw = self.text[start + 2 : inner.i]
        value = None if any(c in raw for c in "$`\\") else raw
        self.hole(self.text[start : inner.i + 1], True, None, value)
        self.i = inner.i + 1
        return False

    def ansi_c(self) -> bool:
        """``$'…'``: escapes the gate does not decode, so the word is computed."""
        j = self.i + 2
        while j < len(self.text) and self.text[j] != "'":
            j += 2 if self.text[j] == "\\" else 1
        if j >= len(self.text):
            raise ShellError("unbalanced quote")
        self.hole(self.text[self.i : j + 1], True, None)
        self.i = j + 1
        return False

    # ------------------------------------------------------------ dollar forms

    def dollar(self) -> bool:
        nxt = self.text[self.i + 1 : self.i + 2]
        if nxt and (nxt in POSITIONAL_PARAMETERS or nxt.isdigit()) and self.mode in VARIABLE_MODES:
            self.variable("$" + nxt, nxt)  # ``$1``, ``$@``: argv the command may set (spec gate-f55)
            self.i += 2
            return False
        if nxt and (nxt in SPECIAL_PARAMETERS or nxt.isdigit()):
            self.emit("$" + nxt)  # ``$?``, ``$$``: a parameter, not a glob, never a path
            self.i += 2
            return False
        name = NAME_RE.match(self.text, self.i + 1)
        if name and self.mode in VARIABLE_MODES and name.group() not in GATE_TEXT_VARIABLES:
            self.variable("$" + name.group(), name.group())
            self.i = name.end()
            return False
        if nxt == "'" and self.mode in QUOTING_MODES:
            return self.ansi_c()
        if nxt == '"' and self.mode in QUOTING_MODES:
            return self.locale()
        if nxt == "(":
            end = self.arith_end(self.i + 3) if self.text[self.i + 2 : self.i + 3] == "(" else None
            return self.arithmetic(self.i + 3, end, "$((") if end is not None else self.substitution()
        if nxt == "[":
            return self.bracket_arithmetic()
        if nxt == "{":
            return self.parameter()
        self.emit("$")
        self.i += 1
        return False

    def substitution(self) -> bool:
        start = self.i
        inner = self.child("sub", self.i + 2)
        body = inner.run()
        self.i = inner.i
        self.hole(self.text[start : self.i], self.mode == "dq", body, known_value(body))
        return False

    def arith_end(self, start: int) -> int | None:
        """Index after the closing ``))`` when ``$((`` is arithmetic: the depth never falls below
        two before it. None when it is a substitution whose body starts with ``(``."""
        depth, j = 2, start
        while j < len(self.text):
            c = self.text[j]
            if c == "$" and self.text[j + 1 : j + 2] == "'":
                j = skip_quoted(self.text, j + 1, escapes=True)
                continue
            if c in "'\"`\\":
                j = skip_quoted(self.text, j)
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 1:
                    return j + 2 if self.text[j + 1 : j + 2] == ")" else None
            j += 1
        return None

    def arithmetic(self, start: int, end: int, opener: str) -> bool:
        closer = "]" if opener == "$[" else "))"
        content = self.text[start : end - len(closer)]
        inner = self.child("arith", 0, content).run()
        self.adopt(inner)
        self.hole(self.text[start - len(opener) : end], self.mode == "dq", None)
        self.i = end
        return False

    def bracket_arithmetic(self) -> bool:
        depth, j = 0, self.i + 1
        while j < len(self.text):
            depth += {"[": 1, "]": -1}.get(self.text[j], 0)
            if depth == 0:
                return self.arithmetic(self.i + 2, j + 1, "$[")
            j += 1
        raise ShellError("unclosed $[")

    def parameter(self) -> bool:
        """``${…}``: no comments inside; a substitution inside is a hole; ``@P`` re-expands a
        value as a prompt, which runs ``$(…)`` held in it. One with an operator word
        (``${x:-word}``, ``${x#pat}``, ``${x@Q}``) is a hole of unknown text, quoted inside
        double quotes: the gate cannot know whether the variable is set."""
        start = self.i
        inner = self.child("dq" if self.mode == "dq" else "param", self.i + 2)
        braces = 1
        while inner.i < len(self.text):
            c = self.text[inner.i]
            if c == "}" and braces == 1:
                break
            braces += {"{": 1, "}": -1}.get(c, 0)
            inner.step()
        if inner.i >= len(self.text):
            raise ShellError("unclosed ${")
        content = "".join(inner.out)
        if content.endswith("@P"):
            raise ShellError("${…@P} prompt expansion")
        self.scan.holes.update(inner.scan.holes)
        self.i = inner.i + 1
        span = self.text[start : self.i]
        text = TEXT_PARAMETER_RE.match(content) or content in GATE_TEXT_VARIABLES
        if self.mode not in VARIABLE_MODES or text:
            self.emit("${" + content + "}")  # a length, ``${?}``: a number, never a path
        elif PLAIN_PARAMETER_RE.match(content):
            self.variable(span, content)
        else:
            alternative = ALTERNATIVE_RE.match(content)
            if alternative:
                self.variable(span, alternative.group(1), "alt", (alternative.group(2),))
            else:
                operand = NAME_RE.match(content.lstrip("#!"))
                self.variable(span, operand.group() if operand else content, "other")
        return False

    def variable(self, span: str, name: str, operator: str = "", word: tuple[str, ...] = ()) -> None:
        """A parameter expansion (spec gate-f55, story 1): the gate reads it by its class in the
        whole command, so it is a hole here, one word inside double quotes."""
        quoted = self.mode == "dq"
        self.hole(span, quoted, None, kind="variable", alternatives=word, name=name, operator=operator)

    def backtick(self) -> bool:
        j = self.i + 1
        while j < len(self.text) and self.text[j] != "`":
            j += 2 if self.text[j] == "\\" else 1
        if j >= len(self.text):
            raise ShellError("unclosed backtick")
        body_text = unescape_backtick(self.text[self.i + 1 : j], self.mode == "dq")
        body = self.child("top", 0, body_text).run()
        self.hole(self.text[self.i : j + 1], self.mode == "dq", body)
        self.i = j + 1
        return False

    # ------------------------------------------------------------ parens, process substitution

    def open_paren(self) -> bool:
        if self.text.startswith("((", self.i) and self.at_word_start():
            end = self.arith_end(self.i + 2)
            if end is not None:  # ``(( … ))``: arithmetic, where ``<<`` is a shift
                inner = self.child("arith", 0, self.text[self.i + 2 : end - 2]).run()
                self.adopt(inner)
                self.emit("((" + inner.outer + "))")
                self.i = end
                return False
        self.parens += 1
        self.emit("(")
        self.i += 1
        return False

    def close_paren(self) -> bool:
        self.end_capture()  # ``(echo x >f)``: the target ends at the paren
        if self.mode == "sub" and self.parens == 0:
            self.i += 1
            return True
        self.parens = max(0, self.parens - 1)  # a ``case`` pattern's ``)`` at the top level
        self.emit(")")
        self.i += 1
        return False

    def process_substitution(self) -> None:
        start = self.i
        inner = self.child("sub", self.i + 2)
        body = inner.run()
        self.i = inner.i
        self.hole(self.text[start : self.i], True, body)

    # ------------------------------------------------------------ redirections, here-documents

    def redirection(self) -> bool:
        """Remove a redirection operator and its target from the words; True when one was read."""
        text, i = self.text, self.i
        if text[i] in "<>" and text[i + 1 : i + 2] == "(":
            self.process_substitution()
            return True
        match = re.match(r"&>>|&>|<<<|<<-|<<|<>|<&|>&|>>|>\||<|>", text[i:])
        if not match or (text[i] == "&" and not match.group().startswith("&>")):
            return False
        operator = match.group()
        fd = self.drop_fd_prefix()
        self.i = i + len(operator)
        self.skip_blanks()
        where = (self.item, self.stage_index, fd, self.after_closer())
        if operator in ("<<", "<<-"):
            self.pending.append(self.read_delimiter(operator == "<<-"))
            self.scan.redirects.append(Redirect(where[0], where[1], operator, fd, "", where[3]))
            self.emit(" ")
            return True
        self.end_capture()
        self.emit(" ")
        self.capture = len(self.out)
        self.capture_data = operator == "<<<"
        self.capture_operator = operator
        self.capture_where = where
        return True

    def drop_fd_prefix(self) -> str:
        """Take a ``2`` or ``{fd}`` before the operator out of the words, and return it."""
        word: list[str] = []
        while self.out and self.out[-1] and not ends_word(self.out[-1]):
            word.insert(0, self.out.pop())
        joined = "".join(word)
        prefix = FD_PREFIX_RE.search(joined)
        if prefix and prefix.start() == 0:
            return joined  # ``2>``, ``{fd}>``: the number or name belongs to the operator
        self.out.extend(word)
        return ""

    def skip_blanks(self) -> None:
        while self.i < len(self.text) and self.text[self.i] in " \t":
            self.i += 1

    def end_capture(self) -> None:
        if self.capture is None:
            return
        word = "".join(self.out[self.capture :])
        del self.out[self.capture :]
        item, index, fd, closer = self.capture_where
        self.scan.redirects.append(Redirect(item, index, self.capture_operator, fd, word.strip(), closer))
        if self.capture_data:
            self.scan.inert_code = self.scan.inert_code or ("$(" in word or "`" in word)
        else:
            self.scan.targets.append(word)
            if self.capture_operator in WRITING_OPERATORS:
                fd_dup = self.capture_operator == ">&" and FD_WORD_RE.match(word.strip())
                if not fd_dup:
                    self.scan.writes.append(word.strip())
        self.capture = None
        self.emit(" ")

    def read_delimiter(self, strip_tabs: bool) -> HereDoc:
        """The delimiter word after ``<<``, with quote removal; quoted when any quote or backslash
        appears in it (``E"O"F`` is ``EOF``, quoted)."""
        word: list[str] = []
        quoted = False
        while self.i < len(self.text) and self.text[self.i] not in METACHARS:
            c = self.text[self.i]
            if c in "'\"":
                end = self.text.find(c, self.i + 1)
                if end < 0:
                    raise ShellError("unbalanced quote")
                word.append(self.text[self.i + 1 : end])
                quoted, self.i = True, end + 1
            elif c == "\\":
                word.append(self.text[self.i + 1 : self.i + 2])
                quoted, self.i = True, self.i + 2
            else:
                word.append(c)
                self.i += 1
        if not word:
            raise ShellError("here-document without a delimiter")
        return HereDoc("".join(word), quoted, strip_tabs)

    def read_heredocs(self) -> None:
        """At a newline: consume the queued here-document bodies."""
        for doc in self.pending:
            lines: list[str] = []
            while self.i < len(self.text):
                line = self.read_line(joined=not doc.quoted)
                if (line.lstrip("\t") if doc.strip_tabs else line) == doc.delimiter:
                    break
                lines.append(line.lstrip("\t") if doc.strip_tabs else line)
            body = "\n".join(lines) + ("\n" if lines else "")
            self.heredoc_body(doc, body)
        self.pending = []

    def read_line(self, joined: bool) -> str:
        """The next line of a here-document; with ``joined`` (an unquoted delimiter) a line ending
        in an odd number of backslashes continues on the next one, as bash reads it."""
        parts: list[str] = []
        while True:
            end = self.text.find("\n", self.i)
            end = len(self.text) if end < 0 else end
            line = self.text[self.i : end]
            self.i = min(end + 1, len(self.text))
            trailing = len(line) - len(line.rstrip("\\"))
            if not (joined and trailing % 2 and end < len(self.text)):
                return "".join(parts) + line
            parts.append(line[:-1])

    def heredoc_body(self, doc: HereDoc, body: str) -> None:
        self.scan.heredocs.append(HereDoc(doc.delimiter, doc.quoted, doc.strip_tabs, body))
        if doc.quoted:
            self.scan.inert_code = self.scan.inert_code or ("$(" in body or "`" in body)
            return
        self.adopt(self.child("heredoc", 0, body).run())


def ends_word(piece: str) -> bool:
    """Whether an output piece ends with a blank or an operator; an escape pair (``\\ ``,
    ``\\;``) is part of a word."""
    escaped = len(piece) == 2 and piece[0] == "\\"
    return bool(piece) and piece[-1] in METACHARS and not escaped


def bracket_end(text: str, i: int) -> int | None:
    """Index after the last unquoted ``]`` of the path component a ``[`` at ``i`` opens; None when
    there is none, and bash reads the ``[`` as itself. The longest span holds every bracket form
    bash reads (``[]j]``, ``[[:alpha:]]``); a bracket never holds ``/``. A substitution inside one,
    or a brace, is refused: its code or its words would hide in the glob."""
    j, last = i + 1, None
    while j < len(text) and text[j] not in METACHARS and text[j] != "/":
        c = text[j]
        if c == "{" and text[j - 1] != "$":
            raise ShellError("brackets and braces in one word")
        if c in "\\'\"`" or text.startswith("$'", j):
            j = skip_piece(text, j)
            continue
        if c == "]":
            last = j
        j += 1
    if last is None:
        return None
    if BRACKET_CODE_RE.search(text, i, last):  # quoted or not: ``a["$(x)"]`` runs ``x``
        raise ShellError("expansion inside a bracket expression")
    return last + 1


def brace_end(text: str, i: int) -> tuple[int, list[int]] | None:
    """Index after the ``}`` closing the brace at ``i`` within the word, and the indexes of its
    top-level commas; None when bash reads it as literal text: unclosed in the word, no comma and
    no sequence (``{}``, ``{a}``, ``stash@{0}``, ``{ cmd; }``). A bracket inside is refused."""
    j, depth, commas = i + 1, 1, []
    while j < len(text):
        c = text[j]
        if c in METACHARS:
            return None
        if c in "[]":
            raise ShellError("brackets and braces in one word")
        if c in "\\'\"`" or text.startswith(("$(", "${", "$'"), j):
            j = skip_piece(text, j)
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                inner = text[i + 1 : j]
                return (j + 1, commas) if commas or SEQUENCE_RE.match(inner) else None
        elif c == "," and depth == 1:
            commas.append(j)
        j += 1
    return None


def skip_piece(text: str, j: int) -> int:
    """Index after the escape, quoted run, ``$'…'``, backtick, ``$(…)`` or ``${…}`` at ``j``, read
    as the scanner reads it (escapes in ``$'…'``, substitutions nested in double quotes). An
    unclosed one is an error: reading the rest as literal text would fail open."""
    c = text[j]
    if c == "\\":
        end = j + 2
    elif text.startswith("$'", j):
        end = skip_quoted(text, j + 1, escapes=True)
    elif c in "'`":
        end = skip_quoted(text, j)
    elif c == '"':
        end = skip_double_quoted(text, j)
    else:
        end = skip_nested(text, j)
    if end > len(text):
        raise ShellError("unclosed quote or expansion")
    return end


def skip_double_quoted(text: str, j: int) -> int:
    k = j + 1
    while k < len(text) and text[k] != '"':
        k = skip_piece(text, k) if text[k] in "\\`" or text.startswith(("$(", "${"), k) else k + 1
    return k + 1


def skip_nested(text: str, j: int) -> int:
    """``$(…)`` or ``${…}`` at ``j``: to the closer at depth zero, quotes skipped."""
    opener, closer = ("(", ")") if text[j + 1] == "(" else ("{", "}")
    depth, k = 1, j + 2
    while k < len(text):
        c = text[k]
        if c in "\\'\"`" or text.startswith(("$(", "${", "$'"), k):
            k = skip_piece(text, k)
            continue
        depth += {opener: 1, closer: -1}.get(c, 0)
        if depth == 0:
            return k + 1
        k += 1
    return k + 1


def sequence(inner: str) -> tuple[str, ...]:
    """The words of ``{x..y[..n]}``: integers (zero padded to the wider endpoint when one is
    padded) or letters; a step of 0 is 1, its sign is ignored. Letters that would build
    punctuation (``{Z..a}``) and more than MAX_BRACE_WORDS words are refused."""
    match = SEQUENCE_RE.match(inner)
    if match is None:  # brace_end matched it already
        raise ShellError("not a brace sequence")
    first, last, low, high, step_text = match.groups()
    step = abs(int(step_text)) if step_text else 1
    step = step or 1
    if first is not None:
        a, b = int(first), int(last)
    else:
        a, b = ord(low), ord(high)
    if abs(b - a) // step + 1 > MAX_BRACE_WORDS:
        raise ShellError("brace expansion too large")
    values = range(a, b + (1 if b >= a else -1), step if b >= a else -step)
    if first is None:
        words = [chr(v) for v in values]
        if not all(w.isalpha() for w in words):
            raise ShellError("brace sequence builds punctuation")
        return tuple(words)
    padded = any(re.match(r"[-+]?0\d", end) for end in (first, last))
    width = max(len(first.lstrip("+")), len(last.lstrip("+"))) if padded else 0
    return tuple(f"{v:0{width}d}" for v in values)


def skip_quoted(text: str, j: int, escapes: bool | None = None) -> int:
    """Index after a quoted run (``'``, ``"``, a backtick, or ``$'`` with ``escapes``) or an escape
    starting at ``j``, for paren counting only, as bash's matched-pair reader skips them."""
    c = text[j]
    if c == "\\":
        return j + 2
    escapes = c in '"`' if escapes is None else escapes
    end = j + 1
    while end < len(text) and text[end] != c:
        end += 2 if escapes and text[end] == "\\" else 1
    return end + 1


def unescape_backtick(body: str, in_double_quotes: bool) -> str:
    """Inside backticks a backslash quotes only ``\\``, ``` ` ```, ``$`` (and ``"`` inside double quotes)."""
    special = "\\`$" + ('"' if in_double_quotes else "")
    out: list[str] = []
    j = 0
    while j < len(body):
        if body[j] == "\\" and body[j + 1 : j + 2] and body[j + 1] in special:
            out.append(body[j + 1])
            j += 2
        else:
            out.append(body[j])
            j += 1
    return "".join(out)


def known_value(body: Scan) -> str | None:
    """The text a bare ``cat <<'D'`` ⏎ … ⏎ ``D`` prints: one here-document, quoted or free of
    expansions, and nothing else in the body."""
    if body.error or body.holes or body.targets or len(body.heredocs) != 1:
        return None
    if not CAT_HEREDOC_RE.match(body.outer):
        return None
    doc = body.heredocs[0]
    if not doc.quoted and any(c in doc.body for c in "$`\\"):
        return None
    return doc.body.rstrip("\n")
