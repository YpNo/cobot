"""How an interpreter's argv hands it code (spec gate-f57, F-57): read by a table per family, never
by running the interpreter.

``read_argv`` walks an interpreter's options the way the program does: a code letter takes the
rest of its cluster or the next word (``-cprint(1)``, ``-pe x``), a value option skips its value,
and the first operand is the script, after which every word is the script's own. What the table
does not know keeps the old rule as a floor: after an unknown option, any later ``-c``, ``-e`` or
``-`` word asks. Sources, read 2026-11-23: ``node --help`` 26.13.0, ``python3 --help`` 3.13.15,
perlrun 5.44.0, ruby.1 (ruby/ruby master), php.net CLI options, docs.deno.com run/eval/repl,
bun.com/docs/cli/run, typestrong.org ts-node options, tsx's docs (a drop-in for ``node``).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

FLOOR_WORDS = frozenset({"-c", "-e", "-"})  # today's rule, kept after an option the table lacks
STDIN_PATHS = ("/dev/", "/proc/")  # an operand there is a pipe or a descriptor: code on stdin
REMOTE_PREFIXES = ("http://", "https://", "data:", "npm:", "jsr:", "blob:")
FAMILY_PATTERNS = (
    ("python", re.compile(r"python(?:\d+(?:\.\d+)?t?)?|pypy\d*(?:\.\d+)?")),
    ("node", re.compile(r"node(?:js)?\d*")),
    ("perl", re.compile(r"perl(?:\d+(?:\.\d+)*)?")),
    ("php", re.compile(r"php(?:\d+(?:\.\d+)?)?")),
    ("ruby", re.compile(r"ruby(?:\d+(?:\.\d+)?)?")),
    ("deno", re.compile(r"deno")),
    ("bun", re.compile(r"bun")),
    ("tsx", re.compile(r"tsx")),
    ("ts-node", re.compile(r"ts-node")),
)


def family(name: str) -> str | None:
    """The interpreter family a command word names (``python3.13t`` is python), else None."""
    base = os.path.basename(name).lower()
    return next((fam for fam, pattern in FAMILY_PATTERNS if pattern.fullmatch(base)), None)


@dataclass(frozen=True)
class Table:
    """One family's options. Short letters: ``code`` take code, ``value`` take a value (the rest of
    the cluster, else the next word), ``attached`` take only what follows in the cluster, matched
    by their pattern; ``asks`` run code with no value (``-i``, perl ``-c``); ``info`` print and
    exit; ``script`` take the script file. Long names the same way, ``--name=value`` or two words."""

    code: str = ""
    value: str = ""
    attached: dict[str, str] = field(default_factory=dict)
    flags: str = ""
    asks: str = ""
    info: str = ""
    script: str = ""
    purpose: str = ""  # a run with no script that reads no code (``php -S``, ``node --test``)
    code_long: frozenset[str] = frozenset()
    value_long: frozenset[str] = frozenset()
    flag_long: frozenset[str] = frozenset()
    asks_long: frozenset[str] = frozenset()
    info_long: frozenset[str] = frozenset({"--version", "--help"})
    purpose_long: frozenset[str] = frozenset()
    script_long: frozenset[str] = frozenset()


NODE = Table(
    code="ep",
    value="rC",
    flags="c",  # --check: a syntax check of the script operand
    asks="i",
    info="vh",
    code_long=frozenset({"--eval", "--print"}),
    value_long=frozenset(
        "--require --import --loader --experimental-loader --conditions --input-type --env-file "
        "--env-file-if-exists --title --watch-path --test-reporter --test-reporter-destination "
        "--test-name-pattern --test-skip-pattern --test-concurrency --redirect-warnings "
        "--inspect-port --disable-warning --diagnostic-dir --report-dir --cpu-prof-dir "
        "--heap-prof-dir --icu-data-dir --openssl-config --tls-cipher-list".split()
    ),
    flag_long=frozenset({"--check", "--watch", "--no-warnings", "--enable-source-maps", "--trace-warnings"}),
    asks_long=frozenset({"--interactive", "--run"}),  # --run: a package.json script, as ``npm run``
    info_long=frozenset({"--version", "--help", "--v8-options"}),
    purpose_long=frozenset({"--test"}),
)
TABLES: dict[str, Table] = {
    "python": Table(
        code="c",
        value="WXm",
        flags="bBdEIOPqsSuvx",
        asks="i",
        info="hV?",
        value_long=frozenset({"--check-hash-based-pycs"}),
        flag_long=frozenset({"--safe-path"}),
        info_long=frozenset({"--version", "--help", "--help-env", "--help-xoptions", "--help-all"}),
    ),
    "node": NODE,
    "tsx": NODE,
    "perl": Table(
        code="eE",
        value="IMm",
        attached={
            "i": ".*",
            "x": ".*",
            "F": ".*",
            "l": "[0-7]*",
            "0": "x[0-9A-Fa-f]*|[0-7]*",
            "C": "[0-9IOESioDALa]*",
            "d": "t?(?::.*)?",
            "D": "[0-9]*",
            "V": ":.*",
        },
        flags="anpsStTuUwWX",
        asks="c",  # a syntax check runs BEGIN and CHECK blocks
        info="vhV",
    ),
    "ruby": Table(
        code="e",
        value="CEIrX",
        attached={
            "F": ".*",
            "i": ".*",
            "K": ".?",
            "T": "[0-9]*",
            "W": "[0-9]*|:[\\w-]*",
            "x": ".*",
            "0": "x[0-9A-Fa-f]*|[0-7]*",
        },
        flags="SUacdlnpswy",
        info="vh",
        value_long=frozenset({"--encoding", "--enable", "--disable"}),
        flag_long=frozenset({"--jit", "--yjit", "--verbose", "--copyright"}),
    ),
    "php": Table(
        code="rBRE",
        value="cdtSz",
        flags="nqHswe",
        asks="a",
        info="vhim",
        script="fF",
        purpose="Sl",
        code_long=frozenset({"--run", "--process-begin", "--process-code", "--process-end"}),
        value_long=frozenset({"--php-ini", "--define", "--docroot", "--server", "--zend-extension"}),
        asks_long=frozenset({"--interactive"}),
        info_long=frozenset({"--version", "--help", "--info", "--modules", "--ini"}),
        purpose_long=frozenset({"--syntax-check", "--server"}),
        script_long=frozenset({"--file", "--process-file"}),
    ),
    "ts-node": Table(
        code="ep",
        value="rPOCID",
        flags="TsHn",
        asks="i",
        info="vh",
        code_long=frozenset({"--eval", "--print"}),
        value_long=frozenset(
            "--require --project --compiler-options --compiler --ignore --ignore-diagnostics --cwd "
            "--scope-dir --dir".split()
        ),
        asks_long=frozenset({"--interactive"}),
    ),
    "bun": Table(
        code="ep",
        value="rcd",
        info="vh",
        code_long=frozenset({"--eval", "--print"}),
        value_long=frozenset(
            "--preload --require --import --cwd --config --env-file --tsconfig-override --define".split()
        ),
        flag_long=frozenset({"--hot", "--watch", "--smol", "--bun", "--silent"}),
    ),
}
# value options whose value is code loaded before the script: remote or inline asks
PRELOAD_OPTIONS = frozenset({"-r", "--require", "--import", "--loader", "--experimental-loader", "--preload"})
# a folder of modules or a config that loads code, judged by where it lies (php -c, bun -c, ts-node
# -P, deno --config); perl and ruby -I
FILE_OPTIONS = frozenset("-I -c --config --php-ini -P --project --import-map --tsconfig".split())
# the interpreter changes into this folder before it opens the script
CHDIR_OPTIONS = {"ruby": ("-C", "-X"), "bun": ("--cwd",), "ts-node": ("--cwd", "--dir")}
# ``-MFoo`` or ``-MFoo=a,b`` names a module and words; anything else is a ``use`` list run at BEGIN
# (``-M'lib qx(x)'``, ``-MPOSIX;system(…)``; bypass review of T01)
PERL_MODULE = re.compile(r"-?[\w:]+(?:=[\w:,./-]*)?")
PHP_LOADING_SETTING = re.compile(r"(?i)auto_(?:pre|ap)pend_file|extension|preload")
DENO_SUBCOMMANDS = frozenset(
    "add approve-scripts bench check clean compile completions coverage deploy doc fmt info init install "
    "jupyter lint lsp outdated publish remove task test types uninstall update upgrade vendor".split()
)
DENO_VALUE_OPTIONS = frozenset(
    "-c --config --import-map --cert --location --seed --preload --require --ext -L --log-level".split()
)  # ``--lock``, ``--frozen``, ``--node-modules-dir``, ``--vendor``: an optional ``=`` value only
# Python modules that run code from their arguments or a prompt (Q2: the named list; docs.python.org
# timeit, code, pdb, profile, trace, asyncio, runpy, idle; ``_pyrepl`` is 3.13's REPL)
CODE_MODULES = frozenset(
    "timeit code pdb cProfile profile trace asyncio _pyrepl idlelib IPython runpy".split()
)
BUN_SUBCOMMANDS = frozenset(
    "test install add remove update outdated link unlink pm build create init upgrade publish patch "
    "audit info why".split()
)


@dataclass
class Reading:
    """What an interpreter's argv runs: inline ``code`` texts, a ``why`` to ask, the ``script``
    operand, a Python ``module`` with its arguments, and whether code comes on stdin."""

    family: str
    code: list[str] = field(default_factory=list)
    why: str | None = None
    script: str | None = None
    module: list[str] | None = None
    stdin: bool = False
    in_place: bool = False
    settled: bool = False  # an info or purpose option: no script and no stdin code
    lacks: bool = False  # a letter the table does not know, read as a flag (the floor then holds)
    loads: list[str] = field(default_factory=list)  # files a preload, include or config option names
    candidates: list[str] = field(default_factory=list)  # words after an unknown option: maybe the script
    base: str | None = None  # the folder the interpreter changes into before it opens the script
    searches: bool = False  # ``perl -S``, ``ruby -S``: the script is looked up on PATH

    def asks(self) -> str | None:
        """The reason the argv runs code the gate cannot read, else None."""
        if self.why:
            return self.why
        if self.code:
            return f"{self.family} runs inline code from its command line"
        if self.module and package(self.module[0]) in CODE_MODULES:  # ``asyncio.__main__`` too
            return f"python -m {self.module[0][:40]} runs code from its arguments or a prompt"
        if self.stdin:
            return f"{self.family} reads its code from stdin"
        return None


def read_argv(argv: list[str]) -> Reading | None:
    """The reading of an interpreter's argv (``argv[0]`` names it), else None for any other word."""
    name = family(argv[0]) if argv else None
    if name is None:
        return None
    reading = Reading(name)
    words = argv[1:]
    if name == "deno":
        return read_deno(words, reading)
    if name == "bun":
        words = bun_words(words, reading)
    elif name == "tsx" and words[:1] == ["watch"]:
        words = skip_values(words[1:], frozenset({"--include", "--exclude"}))
    if words is not None:
        read_options(words, TABLES[name], reading)
    return reading


def pip_argv(argv: list[str]) -> list[str] | None:
    """``python -m pip …`` as the ``pip …`` it runs, else None."""
    reading = read_argv(argv)
    return pip_command(reading) if reading else None


def pip_command(reading: Reading) -> list[str] | None:
    """A reading's ``-m pip`` (or ``pip.__main__``) as the ``pip …`` it runs, else None."""
    module = reading.module
    return ["pip", *module[1:]] if module and package(module[0]) == "pip" else None


def package(module: str) -> str:
    """The top package a ``-m`` name runs from (``idlelib.pyshell``, ``pip.__main__``; bypass review
    of T03)."""
    return module.split(".", 1)[0]


def read_options(words: list[str], table: Table, reading: Reading) -> None:
    """Walk the options up to the script operand, filling ``reading``; then decide stdin."""
    index, unknown_at = 0, None
    while index < len(words) and not reading.why and reading.module is None and reading.script is None:
        word = words[index]
        if word == "--":
            reading.script = words[index + 1] if index + 1 < len(words) else None
            break
        if word == "-":
            reading.stdin = True
            break
        if not word.startswith("-") or len(word) == 1:
            reading.script = word
            break
        step = read_long(words, index, table, reading) if word.startswith("--") else None
        if step is None and not word.startswith("--"):
            step = read_cluster(words, index, table, reading)
        if step is None or reading.lacks:  # an option the table does not know: the floor holds after it
            unknown_at = index if unknown_at is None else unknown_at
            step = step or 1
        index += step
    if reading.module is not None:  # ``-m mod`` ends the options: the rest is the module's
        reading.module += words[index:]
    if unknown_at is not None:
        later = words[unknown_at + 1 :]
        if any(floor_word(word, table) for word in later):
            reading.why = reading.why or f"{reading.family} may run inline code after an unknown option"
        # the unknown option's value may have been read as the script (bypass review of T02)
        reading.candidates = [word for word in later if not word.startswith("-")]
    settle(reading)


def floor_word(word: str, table: Table) -> bool:
    """After an option the table lacks, its value may have been read as the script: any later word
    that is one of the family's code options asks (bypass review of T01: ``node
    --unhandled-rejections strict -p x``), so a missing entry costs friction, never a hole. A
    cluster is read in its first three letters only: further on sits an attached value
    (``-Wignore::DeprecationWarning`` holds a ``c``), so ``-bbbc`` is a residual."""
    if word in FLOOR_WORDS:
        return True
    name = word.split("=", 1)[0]
    if word.startswith("--"):
        return name in table.code_long or name in table.asks_long
    letters = word[1:4] if word.startswith("-") else ""
    return any(letter in table.code or letter in table.asks for letter in letters)


def settle(reading: Reading) -> None:
    """A bare interpreter reads code from stdin, and so does a script operand under /dev or /proc."""
    script = reading.script
    if script is not None and script.startswith(STDIN_PATHS):
        reading.stdin, reading.script = True, None
    elif script is not None and remote(script):
        reading.why = reading.why or f"{reading.family} runs remote or inline code '{script[:40]}'"
    elif script is not None and reading.searches and "/" not in script:
        reading.why = reading.why or f"{reading.family} -S runs the first '{script[:40]}' on PATH"
    bare = script is None and reading.module is None and not reading.code and not reading.settled
    if bare and not reading.why:
        reading.stdin = True


def read_long(words: list[str], index: int, table: Table, reading: Reading) -> int | None:
    """A ``--name`` or ``--name=value`` option: the words it takes, or None when unknown."""
    name, eq, value = words[index].partition("=")
    taken = 1 if eq else 2
    if not eq:
        value = words[index + 1] if index + 1 < len(words) else ""
    if name in table.code_long:
        reading.code.append(value)
    elif name in table.value_long:
        option_value(name, value, reading)
    elif name in table.script_long:
        reading.script = value
    elif name in table.asks_long:
        reading.why = f"{reading.family} {name} runs code the gate does not read"
        return 1
    elif name in table.info_long or name in table.purpose_long:
        reading.settled = True
        return 1
    elif name in table.flag_long:
        return 1
    else:
        return None
    return taken


def read_cluster(words: list[str], index: int, table: Table, reading: Reading) -> int | None:
    """A cluster of short letters (``-Sc x``, ``-pi.bak``): the words it takes. A letter the table
    does not know is read as a flag and marks the reading ``lacks``."""
    cluster = words[index][1:]
    position = 0
    while position < len(cluster):
        letter, rest = cluster[position], cluster[position + 1 :]
        if letter in table.code or letter in table.value or letter in table.script:
            value, taken = (rest, 1) if rest else (next_word(words, index), 2)
            short_value(letter, value, table, reading)
            return taken
        if letter in table.attached:
            match = re.match(table.attached[letter], rest)
            reading.in_place = reading.in_place or (reading.family == "perl" and letter == "i")
            reading.settled = reading.settled or letter in table.info  # ``perl -V:name``
            position += 1 + (match.end() if match else 0)
            continue
        if letter in table.asks:
            reading.why = f"{reading.family} -{letter} runs code the gate does not read"
        elif letter in table.info or letter in table.purpose:
            reading.settled = True
        elif letter not in table.flags:  # read on as a flag: ``python3 -Rc x`` still reaches the c
            reading.lacks = True
        elif letter == "S" and reading.family in ("perl", "ruby"):
            reading.searches = True
        position += 1
    return 1


def next_word(words: list[str], index: int) -> str:
    return words[index + 1] if index + 1 < len(words) else ""


def short_value(letter: str, value: str, table: Table, reading: Reading) -> None:
    """The value of a short code, value or script option."""
    if letter in table.code:
        reading.code.append(value)
    elif letter in table.script:
        reading.script = value
    elif reading.family == "python" and letter == "m":
        reading.module = [value]
    elif letter in table.purpose:
        reading.settled = True
    else:
        option_value(f"-{letter}", value, reading)


def option_value(name: str, value: str, reading: Reading) -> None:
    """A value that loads code: a remote or inline preload, a perl import list, a PHP setting
    that loads a file or an extension."""
    if name in PRELOAD_OPTIONS and remote(value):
        reading.why = f"{reading.family} {name} loads remote or inline code '{value[:40]}'"
    elif reading.family == "perl" and name in ("-M", "-m") and not PERL_MODULE.fullmatch(value):
        reading.why = f"perl {name}{value[:40]} runs code in its import list"
    elif reading.family == "php" and name == "-z":
        reading.why = "php -z loads an extension"
    elif reading.family == "php" and name in ("-d", "--define") and PHP_LOADING_SETTING.search(value):
        reading.why = f"php -d {value[:40]} loads a file or an extension"
    elif name in ("-S", "--server"):
        reading.settled = True
    elif name in CHDIR_OPTIONS.get(reading.family, ()):
        reading.base = value
    if name in FILE_OPTIONS or (name in PRELOAD_OPTIONS and path_like(value)):
        reading.loads.append(value)  # judged where the script is (bypass review of T02)


def path_like(value: str) -> bool:
    """A preload value naming a file, not a package (``-r ./x.js``, not ``-r ts-node/register``
    or ``-rjson``)."""
    return value.startswith(("/", ".", "~")) or value.endswith((".js", ".mjs", ".cjs", ".ts", ".rb", ".py"))


def skip_values(words: list[str], value_options: frozenset[str]) -> list[str]:
    """Drop leading options of a subcommand, skipping the values of ``value_options``."""
    rest = list(words)
    while rest and rest[0].startswith("-") and rest[0] not in ("-", "--"):
        name = rest[0].split("=", 1)[0]
        rest = rest[2:] if name in value_options and "=" not in rest[0] else rest[1:]
    return rest


def read_deno(words: list[str], reading: Reading) -> Reading:
    """``deno eval``, ``deno repl`` and a bare ``deno`` run code; ``deno run`` (or ``deno <file>``,
    or ``serve``) runs its script operand; other subcommands run project files."""
    rest = skip_values(words, DENO_VALUE_OPTIONS)
    sub = rest[0] if rest else ""
    if not rest:
        reading.settled = bool(words)  # ``deno --version``; a bare ``deno`` is the REPL
        reading.stdin = not words
    elif sub == "eval":
        reading.code.append(" ".join(rest[1:]))
    elif sub in ("repl", "x"):  # ``deno x``: a package's binary, as ``npx``
        reading.why = f"deno {sub} runs code the gate does not read"
    elif sub in ("run", "serve"):
        operands = skip_preloads(rest[1:], reading)
        reading.stdin = operands[:1] == ["-"]
        reading.script = operands[0] if operands and operands[0] != "-" else None
        reading.settled = not operands and not reading.stdin
        settle(reading)
    elif sub not in DENO_SUBCOMMANDS:
        reading.script = sub
        settle(reading)
    return reading


def skip_preloads(words: list[str], reading: Reading) -> list[str]:
    """``deno run``'s options with their values; a remote preload asks."""
    rest = list(words)
    while rest and rest[0].startswith("-") and rest[0] != "-":
        name, eq, value = rest[0].partition("=")
        takes = name in DENO_VALUE_OPTIONS and not eq
        value = value or (rest[1] if takes and len(rest) > 1 else "")
        option_value(name, value, reading)
        rest = rest[2:] if takes else rest[1:]
    return rest


def bun_words(words: list[str], reading: Reading) -> list[str] | None:
    """Bun's words for the option walk, or None when nothing is left to walk: ``bun run -`` reads
    stdin, ``repl`` and ``exec`` run code, ``bun run <script>`` is judged as a runner elsewhere,
    ``bun <script>`` asks as ``pnpm <script>`` does, a bare ``bun`` prints its help."""
    head = words[0] if words else ""
    if head.startswith("-"):
        return words
    if head in ("repl", "exec"):
        reading.why = f"bun {head} runs code the gate does not read"
        return None
    if head == "run":
        tail = words[1:]
        if tail[:1] == ["-"]:
            reading.stdin = True
            return None
        script = next((word for word in tail if not word.startswith("-")), "")
        if looks_like_file(script):
            return tail
        reading.settled = True  # a package script: judged as a runner elsewhere
        return None
    if not head or head in BUN_SUBCOMMANDS:
        reading.settled = True
        return None
    if not looks_like_file(head):  # bypass review of T01: ``bun dev``
        reading.why = f"bun {head[:40]} runs a package.json script or a package's binary"
        return None
    return words


def looks_like_file(word: str) -> bool:
    """A Bun operand that names a file or a remote module, not a package script."""
    return "/" in word or "." in word or remote(word)


def remote(word: str) -> bool:
    """A URL or an inline module; schemes are read without case (``DATA:`` loads too)."""
    return word.lower().startswith(REMOTE_PREFIXES)


# ---------------------------------------------------------------- awk and sed (story 6)
# gawk manual (I/O functions, redirection), mawk 1.3.4 manual and ``mawk -W usage``, GNU sed 4.9
# ``info sed`` (Extended Commands; Multiple commands: ``e``, ``r``, ``w`` and their kin take the
# rest of the line, a ``;`` included), read 2026-11-23. gawk's option page was rate-limited: an
# option outside these tables makes every operand a program to scan.

AWK_NAMES = frozenset({"awk", "gawk", "mawk", "nawk", "original-awk"})
SED_NAMES = frozenset({"sed", "gsed"})
AWK_VALUE_OPTIONS = frozenset({"-v", "-F", "--assign", "--field-separator"})
AWK_PROGRAM_FILES = frozenset({"-f", "--file", "-E", "--exec"})
AWK_SOURCE_OPTIONS = frozenset({"-e", "--source"})
AWK_LOADERS = frozenset({"-l", "--load", "-i", "--include"})  # gawk: an extension or an awk library
AWK_TAKES_VALUE = AWK_VALUE_OPTIONS | AWK_PROGRAM_FILES | AWK_SOURCE_OPTIONS | AWK_LOADERS | {"-W"}
AWK_LONG = {
    "--assign": "-v",
    "--field-separator": "-F",
    "--file": "-f",
    "--exec": "-E",
    "--source": "-e",
    "--load": "-l",
    "--include": "-i",
}
# gawk's flags (no value or an attached one), read as flags so an abbreviation stays unique
AWK_LONG_FLAGS = frozenset(
    "--characters-as-bytes --traditional --copyright --debug --dump-variables --gen-pot --help "
    "--lint --lint-old --bignum --use-lc-numeric --non-decimal-data --optimize --no-optimize "
    "--profile --posix --re-interval --sandbox --version --pretty-print --csv --persist".split()
)
AWK_FLAGS = frozenset(f"-{letter}" for letter in "bcCdDghLMnNoOpPrsStVY") | AWK_LONG_FLAGS
AWK_ATTACHED_LETTERS = frozenset("dDLop")  # gawk ``-d[file]``, ``-o[file]``, ``-p[file]``: an attached value
# gawk flags whose ``=value`` is a file it writes (a dump, a profile, a pretty-printed program)
AWK_WRITING_FLAGS = frozenset({"--dump-variables", "--profile", "--pretty-print", "--debug"})
AWK_WRITING_LETTERS = {"-d": "--dump-variables", "-p": "--profile", "-o": "--pretty-print", "-D": "--debug"}
AWK_RUNS_RE = re.compile(r"\bsystem\s*\(|\|&|\|\s*getline\b|@\s*(?:load|include)\b|@\w+\s*\(")
AWK_REGEX_AFTER = frozenset("(,~!{};&|^?:\n=") | {""}  # a ``/`` after these opens a regex, else divides
AWK_REGEX_KEYWORDS = frozenset({"print", "printf", "return", "in", "getline", "case", "do", "else"})
AWK_STATEMENT_RE = re.compile(r"[;{}\n]")
AWK_PRINT_RE = re.compile(r"\bprintf?\b")
AWK_PIPE_RE = re.compile(r"(?<!\|)\|(?!\|)")
AWK_REDIRECT_RE = re.compile(r">>?\s*(.*)$", re.S)
AWK_STRING_RE = re.compile(r'"(\d+)"')
SED_SCRIPT_LETTERS = {"e": "script", "f": "file", "l": "value"}
SED_LONG_OPTIONS = {
    "--expression": "script",
    "--file": "file",
    "--sandbox": "sandbox",
    "--line-length": "value",
}
SED_LONG_FLAGS = frozenset(
    "--quiet --silent --debug --posix --separate --unbuffered --null-data --zero-terminated "
    "--regexp-extended --in-place --follow-symlinks --help --version".split()
)
SED_PLAIN_COMMANDS = frozenset("=dDgGhHlnNpPxzFqQLv")
# the two branches inside a custom-delimiter address exclude each other, so a run of backslashes
# reads in linear time (wrap code review: ``\x`` and 34 backslashes outran the hook's timeout)
SED_ADDRESS_RE = re.compile(r"\s*(?:\d+|\$|/(?:\\.|[^/\\\n])*/[IM]*|\\(.)(?:\\.|(?!\1)[^\\])*\1[IM]*)?")
SED_STEP_RE = re.compile(r"\s*(?:,\s*(?:\d+|\$|/(?:\\.|[^/\\\n])*/[IM]*|[+~]\d+)|~\d+)?\s*!?\s*")
SED_S_FLAGS = frozenset("gpiImMe0123456789w")
SED_LABEL_RE = re.compile(r"[ \t]*[^\s;]*")
STD_STREAMS = frozenset({"/dev/stdout", "/dev/stderr"})


@dataclass
class Program:
    """What an awk or sed program does beyond its text: a ``why`` to ask, and the literal files it
    writes (judged as redirect targets are)."""

    why: str | None = None
    writes: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)  # program files (``-f``): judged where they lie

    def write(self, target: str) -> None:
        """sed and awk take ``~`` literally: a folder named ``~`` where the command runs."""
        target = target.strip()
        if target and target not in STD_STREAMS:
            self.writes.append(f"./{target}" if target.startswith("~") else target)


def read_program(argv: list[str]) -> Program | None:
    """The awk or sed program in ``argv`` (``busybox awk`` too), else None for any other command."""
    words = argv[1:] if argv and os.path.basename(argv[0]) == "busybox" else argv
    name = os.path.basename(words[0]).lower() if words else ""
    if name in AWK_NAMES:
        return read_awk(words[1:])
    if name in SED_NAMES:
        return read_sed(words[1:])
    return None


def read_awk(words: list[str]) -> Program:
    """awk's options, then its program: the first operand unless ``-f``, ``-e`` or ``-E`` gave one.
    An option the gate does not know may take a value, so every operand is then scanned."""
    program, texts, index, unsure, from_file = Program(), [], 0, False, False
    while index < len(words) and words[index].startswith("-") and words[index] not in ("-", "--"):
        options, taken = awk_options(words, index)
        for name, value in options:
            if name == "-W" and "exec".startswith(value or "-"):  # mawk ``-W exec file``: the last option
                value, taken = next_word(words, index + taken - 1), taken + 1
                name = "-E"
            elif name == "-W" and value:  # gawk ``-W source=…``: the POSIX form of a long option
                name, value = awk_options([f"--{value}"], 0)[0][0]
            name = AWK_WRITING_LETTERS.get(name, name) if value else name
            if name in AWK_WRITING_FLAGS:
                program.write(value)  # a dump or a profile lands in the file it names
            elif name in AWK_LOADERS and value != "inplace":  # ``-i inplace`` edits in place, judged apart
                program.why = f"awk {name} loads code the gate does not read"
            elif name in AWK_PROGRAM_FILES:
                from_file = True
                awk_program_file(value, program)
            elif name in AWK_SOURCE_OPTIONS:
                texts.append(value)
            elif name.startswith("--") and value and name not in AWK_LONG_FLAGS:  # unknown, with a value
                program.why = program.why or f"awk {name[:30]} is an option the gate does not read"
            elif name not in AWK_TAKES_VALUE and name not in AWK_FLAGS:
                unsure = True
        index += taken
    operands = words[index + (words[index : index + 1] == ["--"]) :]
    if unsure:
        texts += operands
    elif operands and not texts and not from_file:
        texts.append(operands[0])
    for text in texts:
        scan_awk(text, program)
    return program


def awk_program_file(path: str, program: Program) -> None:
    """``-f``, ``-E`` or ``-W exec``: stdin asks, a file is judged where it lies (as a script is)."""
    if stdin_file(path):
        program.why = program.why or "awk reads its program from stdin"
    else:
        program.files.append(path)


def awk_options(words: list[str], index: int) -> tuple[list[tuple[str, str]], int]:
    """The options a word holds, as (short or long name, value), and the words they take: a long
    name by unique prefix (``--sou=…`` is ``--source``, as getopt reads it), a cluster letter by
    letter (``-bl x`` is ``-b -l x``)."""
    word, following = words[index], next_word(words, index)
    if word.startswith("--"):
        name, eq, value = word.partition("=")
        full = long_name(name, AWK_LONG.keys() | AWK_LONG_FLAGS)
        short = AWK_LONG.get(full or "")
        if short is None:
            return [(full or name, value)], 1
        return ([(short, value)], 1) if eq else ([(short, following)], 2)
    options: list[tuple[str, str]] = []
    for position, letter in enumerate(word[1:], start=1):
        name, rest = f"-{letter}", word[position + 1 :]
        if name in AWK_TAKES_VALUE:
            return [*options, (name, rest or following)], 1 if rest else 2
        if letter in AWK_ATTACHED_LETTERS:  # ``-pprof``: the rest is the file, not more letters
            return [*options, (name, rest)], 1
        options.append((name, ""))
    return options, 1


def long_name(name: str, known: frozenset[str] | set[str]) -> str | None:
    """The long option a name is, or uniquely abbreviates; None when unknown or ambiguous."""
    if name in known:
        return name
    matches = [option for option in known if option.startswith(name)]
    return matches[0] if len(matches) == 1 else None


def stdin_file(path: str) -> bool:
    return path == "-" or path.startswith(STDIN_PATHS)


def scan_awk(text: str, program: Program) -> None:
    """Strings, regexes and comments set aside, an awk program that calls ``system``, pipes into or
    out of a command, loads code or makes an indirect call asks; ``print > "file"`` writes the file,
    a computed target asks."""
    code, strings = strip_awk(text)
    if AWK_RUNS_RE.search(code):
        program.why = program.why or "awk runs a command or loads code"
    for statement in AWK_STATEMENT_RE.split(code):
        found = AWK_PRINT_RE.search(statement)
        if found:
            print_target(statement[found.end() :], strings, program)


def strip_awk(text: str) -> tuple[str, list[str]]:
    """The program with each string as ``"N"`` (its index in the list), each regex as ``/R/`` and
    comments gone, so ``"|"`` and ``/a|b/`` read as no pipe."""
    out, strings, index, last, word = [], [], 0, "", ""
    while index < len(text):
        char = text[index]
        if char == '"':
            end = closing(text, index, '"')
            strings.append(text[index + 1 : end])
            out.append(f'"{len(strings) - 1}"')
            index, last, word = end + 1, '"', ""
        elif char == "/" and (last in AWK_REGEX_AFTER or word in AWK_REGEX_KEYWORDS):
            index, last, word = closing(text, index, "/") + 1, "/", ""
            out.append("/R/")
        elif char == "#":
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline
        else:
            out.append(char)
            index += 1
            if char not in " \t":
                word = word + char if char.isalnum() or char == "_" else ""
                last = char
    return "".join(out), strings


def closing(text: str, start: int, quote: str) -> int:
    """The index of the quote that closes the one at ``start``: backslash escapes skipped, and for a
    regex its bracket expressions too (``/[/]/``: mawk and nawk take the ``/`` inside)."""
    index = start + 1
    while index < len(text) and text[index] != quote:
        if quote == "/" and text[index] == "[":
            index = bracket_end(text, index)
            continue
        index += 2 if text[index] == "\\" else 1
    return min(index, len(text))


def bracket_end(text: str, start: int) -> int:
    """The index after a bracket expression (``[]x]`` and ``[^]x]`` hold their first ``]``)."""
    index = start + 1
    index += text[index : index + 1] == "^"
    index += text[index : index + 1] == "]"
    while index < len(text) and text[index] != "]":
        index += 2 if text[index] == "\\" else 1
    return index + 1


def print_target(rest: str, strings: list[str], program: Program) -> None:
    """After ``print``: into ``|`` asks; into ``>`` or ``>>`` a single string is a write target and
    anything else asks. A ``>`` inside parentheses is a comparison."""
    top = top_level(rest)
    if AWK_PIPE_RE.search(top):
        program.why = program.why or "awk prints into a command"
        return
    redirect = AWK_REDIRECT_RE.search(top)
    if not redirect:
        return
    literal = AWK_STRING_RE.fullmatch(redirect.group(1).strip())
    if literal:
        program.write(strings[int(literal.group(1))])
    else:
        program.why = program.why or "awk prints into a file it computes"


def top_level(statement: str) -> str:
    """The statement with everything inside parentheses blanked."""
    depth, out = 0, []
    for char in statement:
        depth += char == "("
        out.append(char if depth == 0 else " ")
        depth -= char == ")" and depth > 0
    return "".join(out)


def read_sed(words: list[str]) -> Program:
    """sed's options (``-e``, ``-f``, ``--expression``, ``--file``, clusters), then its script: the
    first operand unless one was given. ``--sandbox`` refuses ``e``, ``r`` and ``w``: silent."""
    program, scripts, operands, index, given = Program(), [], [], 0, False
    while index < len(words):  # GNU getopt reads options after operands too (T04 review)
        word = words[index]
        if word == "--":
            operands += words[index + 1 :]
            break
        if not word.startswith("-") or word == "-":
            operands.append(word)
            index += 1
            continue
        kind, value, taken = sed_option(words, index)
        if kind == "sandbox":
            return Program()
        if kind == "script":
            scripts.append(value)
        elif kind == "file" and stdin_file(value):
            program.why = program.why or "sed reads its script from stdin"
        elif kind == "file":
            program.files.append(value)
        given = given or kind in ("script", "file")
        index += taken
    if not given and operands:
        scripts.append(operands[0])
    for script in scripts:
        scan_sed(script, program)
    return program


def sed_option(words: list[str], index: int) -> tuple[str, str, int]:
    """An option's kind (``script``, ``file``, ``sandbox``, ``value`` or ``flag``), value and words."""
    word, following = words[index], next_word(words, index)
    if word.startswith("--"):
        name, eq, value = word.partition("=")
        kind = SED_LONG_OPTIONS.get(long_name(name, SED_LONG_OPTIONS.keys() | SED_LONG_FLAGS) or "", "flag")
        return kind, value or following, 1 if eq or kind in ("flag", "sandbox") else 2
    for position, letter in enumerate(word[1:], start=1):
        if letter in SED_SCRIPT_LETTERS:
            rest = word[position + 1 :]
            return SED_SCRIPT_LETTERS[letter], rest or following, 1 if rest else 2
        if letter == "i":  # ``-i[SUFFIX]``: the rest is the suffix
            break
    return "flag", "", 1


def scan_sed(script: str, program: Program) -> None:
    """Each command after its address: ``e`` (the command or the flag of ``s``) asks; ``w``, ``W``
    and the ``w`` flag write the rest of the line. An unknown command asks."""
    position = 0
    while position < len(script):
        position = SED_STEP_RE.match(script, SED_ADDRESS_RE.match(script, position).end()).end()
        if position >= len(script):
            return
        command = script[position]
        position = sed_command(command, script, position + 1, program)
        if position < 0:
            return


def sed_command(command: str, script: str, position: int, program: Program) -> int:
    """The position after one command, or -1 once the script cannot be read further."""
    if command in "{};\n" or command in SED_PLAIN_COMMANDS:
        return position
    if command == "e":
        program.why = program.why or "sed runs a command (e)"
        return line_end(script, position)
    if command in "wW":
        end = line_end(script, position)
        program.write(script[position:end])
        return end
    if command in "aic":
        return text_end(script, position)
    if command in "rR#":
        return line_end(script, position)
    if command in ":btTv":
        return label_end(script, position)
    if command in "sy":
        return sed_parts(command, script, position, program)
    program.why = program.why or f"sed command '{command}' the gate does not read"
    return -1


def sed_parts(command: str, script: str, position: int, program: Program) -> int:
    """``s`` or ``y`` with any delimiter; then ``s``'s flags: ``e`` asks, ``w`` writes the rest of
    the line."""
    delimiter = script[position : position + 1]
    if not delimiter or delimiter in "\\\n":
        program.why = program.why or f"sed {command} with a delimiter the gate does not read"
        return -1
    position = part_end(script, part_end(script, position + 1, delimiter) + 1, delimiter) + 1
    while command == "s" and position < len(script) and script[position] in SED_S_FLAGS:
        flag = script[position]
        position += 1
        if flag == "e":
            program.why = program.why or "sed runs the pattern space as a command (the e flag)"
        if flag == "w":
            end = line_end(script, position)
            program.write(script[position:end])
            return end
    return position


def part_end(script: str, position: int, delimiter: str) -> int:
    """The index of the delimiter that ends one part of ``s`` or ``y`` (escapes skipped)."""
    while position < len(script) and script[position] != delimiter:
        position += 2 if script[position] == "\\" else 1
    return min(position, len(script))


def line_end(script: str, position: int) -> int:
    """The end of the line: a newline, or ``" ; "``. The splitter now keeps a quoted newline as it
    is (spec gate-f63-f65, story 3), so ``" ; "`` is only a guess kept for safety: a false ask at
    worst."""
    newline = script.find("\n", position)
    newline = len(script) if newline < 0 else newline
    split = script.find(" ; ", position, newline)  # bounded: linear over a long script (wrap review)
    return newline if split < 0 else split


def text_end(script: str, position: int) -> int:
    """``a``, ``i`` and ``c`` text: to the end of the line, and on past each line ending in an odd
    run of ``\\`` (``foo\\\\`` ends the text). A ``\\`` before a blank may be what the splitter left
    of ``\\`` and a newline, so the text ends there too: a false ask at worst."""
    end = line_end(script, position)
    while end < len(script) and odd_backslashes(script, end):
        end = line_end(script, end + 1)
    escaped = script.find("\\ ", position, end)
    return escaped + 2 if escaped >= 0 else end


def odd_backslashes(text: str, end: int) -> bool:
    """An odd run of backslashes just before ``end``, counted back without copying the text."""
    start = end
    while start > 0 and text[start - 1] == "\\":
        start -= 1
    return (end - start) % 2 == 1


def label_end(script: str, position: int) -> int:
    """A label (``b``, ``t``, ``T``, ``:``) or ``v``'s version: blanks before it skipped, then up to
    a blank, a ``;`` or the line's end (``:a e x`` runs ``e x``: T04 review)."""
    return SED_LABEL_RE.match(script, position).end()
