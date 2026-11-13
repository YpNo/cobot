"""Shell text to structure for the rules gate (.agent/specs/gate-substitution.md): which parts of
a Bash command are words of the command, which run as commands of their own, which are data.

``scan(command)`` reads the text once, modelled on bash 5.2, and returns a ``Scan``:

- ``outer``: the command with every substitution replaced by a sentinel, here-document bodies,
  comments and redirections removed (the rest of each line kept), quotes left in place for
  ``shlex``;
- ``holes``: each substitution (``$(…)``, a backtick, ``<(…)``, ``>(…)``), arithmetic
  ``$((…))``/``$[…]`` and ANSI-C ``$'…'`` word, keyed by its sentinel, with its scanned body
  when it runs a command; a hole whose sentinel is not in ``outer`` (a redirection target, an
  unquoted here-document body, inside arithmetic) still runs and is judged by its body;
- ``targets``: redirection target words, for the protected-file check;
- ``error``: set on anything the scanner does not model exactly, so the caller asks.

Soundness target: a hole in the command's words is never silent where some text in its place
would change which program runs, or make a rule match the form that names what runs. Code that
reaches execution from a variable's value (arithmetic on it, ``${x@P}``) is not a hole: the
caller's quoted-code rule and the ``@P`` error cover what the command text shows.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field

OPEN, CLOSE = "", ""  # private-use characters: never in a command, never NUL
SENTINEL_RE = re.compile(f"{OPEN}\\d+{CLOSE}")
MAX_DEPTH = 8  # nesting of substitutions before the command is refused
SPAN_LIMIT = 60
METACHARS = frozenset(" \t\n;&|()<>")
QUOTING_MODES = ("top", "sub", "arith", "param")  # where quotes quote; not inside "…" or a body
FD_PREFIX_RE = re.compile(r"(?:\d+|\{[A-Za-z_][A-Za-z0-9_]*\})$")
CAT_HEREDOC_RE = re.compile(r"^\s*cat\s*$")


@dataclass(frozen=True)
class Hole:
    key: str  # the sentinel standing for it in the outer text
    span: str  # the original text, capped, for reasons and traces
    quoted: bool  # exactly one word (inside double quotes, a process substitution, ``$'…'``)
    body: Scan | None  # the command it runs; None for arithmetic and ``$'…'``
    value: str | None = None  # the text a bare ``cat <<'D'`` here-document prints


@dataclass(frozen=True)
class HereDoc:
    delimiter: str
    quoted: bool
    strip_tabs: bool
    body: str = ""


@dataclass
class Scan:
    outer: str = ""
    holes: dict[str, Hole] = field(default_factory=dict)
    targets: list[str] = field(default_factory=list)
    heredocs: list[HereDoc] = field(default_factory=list)
    inert_code: bool = False  # data text (a quoted here-document, a here-string) holds ``$(`` or a backtick
    error: str | None = None


class ShellError(Exception):
    """Text the scanner does not model exactly; the caller asks."""


def scan(command: str) -> Scan:
    """Scan a whole command. Never raises: a construct outside the model sets ``error``."""
    if OPEN in command or CLOSE in command or "\0" in command:
        return Scan(outer=command, error="reserved character in the command")
    scanner = _Scanner(command, 0, itertools.count(), "top")
    try:
        return scanner.run()
    except ShellError as error:
        return Scan(outer=command, error=str(error))


def sentinels(text: str) -> list[str]:
    return SENTINEL_RE.findall(text)


def has_sentinel(text: str) -> bool:
    return OPEN in text


class _Scanner:
    """One level of text: ``top`` (a command), ``sub`` (until its ``)``), ``dq`` (inside double
    quotes), ``heredoc`` (an unquoted body), ``arith`` (arithmetic: no here-documents, comments
    or redirections), ``param`` (an unquoted ``${…}``: like ``arith``, but ``<(…)`` and ``>(…)``
    still run)."""

    def __init__(self, text: str, depth: int, counter: itertools.count, mode: str, start: int = 0):
        if depth > MAX_DEPTH:
            raise ShellError(f"more than {MAX_DEPTH} nested substitutions")
        self.text, self.depth, self.counter, self.mode = text, depth, counter, mode
        self.i = start
        self.out: list[str] = []
        self.scan = Scan()
        self.parens = 0
        self.pending: list[HereDoc] = []
        self.capture: int | None = None  # start of a redirection target in ``out``
        self.capture_data = False  # the target is a here-string: data, not a file

    # ------------------------------------------------------------ driver

    def run(self) -> Scan:
        while self.i < len(self.text):
            if self.step():
                break
        else:
            if self.mode == "sub":
                raise ShellError("unclosed substitution")
        self.end_capture()  # a here-document still pending has no body: bash reads nothing
        self.scan.outer = "".join(self.out)
        return self.scan

    def step(self) -> bool:
        """Handle the text at ``self.i``; True when this level ends."""
        c = self.text[self.i]
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

    def unquoted(self, c: str) -> bool:
        if c in " \t\n" or c in ";&|":
            self.end_capture()
        if c == "\n":
            self.emit(c)
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
        if c == "(":
            return self.open_paren()
        if c == ")":
            return self.close_paren()
        if self.mode == "sub" and self.at_word_start() and self.word_is("case"):
            raise ShellError("'case' inside a substitution")
        self.emit(c)
        self.i += 1
        return False

    # ------------------------------------------------------------ output helpers

    def emit(self, piece: str) -> None:
        self.out.append(piece)

    def at_word_start(self) -> bool:
        return not self.out or ends_word(self.out[-1])

    def word_is(self, word: str) -> bool:
        end = self.i + len(word)
        return self.text[self.i : end] == word and (end == len(self.text) or self.text[end] in METACHARS)

    def hole(self, span: str, quoted: bool, body: Scan | None, value: str | None = None) -> None:
        key = f"{OPEN}{next(self.counter)}{CLOSE}"
        self.scan.holes[key] = Hole(key, span[:SPAN_LIMIT], quoted, body, value)
        self.emit(key)

    def child(self, mode: str, start: int, text: str | None = None) -> _Scanner:
        source = self.text if text is None else text
        return _Scanner(source, self.depth + 1, self.counter, mode, start)

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
        if nxt == "'" and self.mode in QUOTING_MODES:
            return self.ansi_c()
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
        value as a prompt, which runs ``$(…)`` held in it."""
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
        self.emit("${" + content + "}")
        self.i = inner.i + 1
        return False

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
        self.drop_fd_prefix()
        self.i = i + len(operator)
        self.skip_blanks()
        if operator in ("<<", "<<-"):
            self.pending.append(self.read_delimiter(operator == "<<-"))
            self.emit(" ")
            return True
        self.end_capture()
        self.emit(" ")
        self.capture = len(self.out)
        self.capture_data = operator == "<<<"
        return True

    def drop_fd_prefix(self) -> None:
        word: list[str] = []
        while self.out and self.out[-1] and not ends_word(self.out[-1]):
            word.insert(0, self.out.pop())
        joined = "".join(word)
        prefix = FD_PREFIX_RE.search(joined)
        if prefix and prefix.start() == 0:
            return  # ``2>``, ``{fd}>``: the number or name belongs to the operator
        self.out.extend(word)

    def skip_blanks(self) -> None:
        while self.i < len(self.text) and self.text[self.i] in " \t":
            self.i += 1

    def end_capture(self) -> None:
        if self.capture is None:
            return
        word = "".join(self.out[self.capture :])
        del self.out[self.capture :]
        if self.capture_data:
            self.scan.inert_code = self.scan.inert_code or ("$(" in word or "`" in word)
        else:
            self.scan.targets.append(word)
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
