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
    --unhandled-rejections strict -p x``), so a missing entry costs friction, never a hole."""
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
        return tail if looks_like_file(script) else settled(reading)
    if not head or head in BUN_SUBCOMMANDS:
        return settled(reading)
    if not looks_like_file(head):  # bypass review of T01: ``bun dev``
        reading.why = f"bun {head[:40]} runs a package.json script or a package's binary"
        return None
    return words


def settled(reading: Reading) -> None:
    """Nothing to walk: the reading runs no code of its own."""
    reading.settled = True


def looks_like_file(word: str) -> bool:
    """A Bun operand that names a file or a remote module, not a package script."""
    return "/" in word or "." in word or remote(word)


def remote(word: str) -> bool:
    """A URL or an inline module; schemes are read without case (``DATA:`` loads too)."""
    return word.lower().startswith(REMOTE_PREFIXES)
