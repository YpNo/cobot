"""Makefile subset reader for the rules gate: what ``make [-C dir] [-f file] [VAR=value] <goals>``
would run, found by reading, never by running make.

Resolved: plain variables (``=``, ``:=``, ``?=``, ``+=``), ``define`` bodies through ``$(call)``,
``$(MAKE)`` (as ``make``), ``$@``, ``$$``, prerequisites that are targets, ``.DEFAULT_GOAL``.
Not resolved, so the caller keeps the command opaque: a Makefile with ``include``, a pattern,
suffix or static pattern rule, ``.SECONDEXPANSION``, ``.DEFAULT`` or ``$(eval)``; a target
defined or extended under a conditional or carrying a target-specific variable; a recipe that needs
a function (``$(shell …)``, ``$(wildcard …)``, …), a substitution reference, an unknown variable or
an automatic variable other than ``$@``.

One accepted gap: a prerequisite list that does not expand (``test: $(GO_SOURCES)`` with
``GO_SOURCES := $(shell find …)``) is taken as a list of files, which is what such lists are; a
computed prerequisite naming a target with a recipe would escape. Pattern rules, which could turn
a file into a recipe, already make the whole Makefile opaque.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

MAKEFILE_NAMES = ("GNUmakefile", "makefile", "Makefile")
ASSIGN_RE = re.compile(r"^(?:(?:override|export|private)\s+)*([^\s:#=?+!]+)\s*(::?:?=|\?=|\+=|!=|=)\s*(.*)$")
TARGET_VARIABLE_RE = re.compile(r"^[^\s=]+\s*(::?:?=|\?=|\+=|!=|=)")
CONDITIONAL_RE = re.compile(r"^(ifeq|ifneq|ifdef|ifndef)\b")
INCLUDE_RE = re.compile(r"^-?s?include\b")
NAME_RE = re.compile(r"^[\w./-]+$")  # a plain reference: no function, no substitution reference
SUFFIX_RULE_RE = re.compile(r"^\.[^./\s]+(\.[^./\s]+)?$")
HARMLESS_SPECIAL = frozenset(
    ".PHONY .DELETE_ON_ERROR .NOTPARALLEL .ONESHELL .SILENT .EXPORT_ALL_VARIABLES .PRECIOUS "
    ".INTERMEDIATE .NOTINTERMEDIATE .SECONDARY .IGNORE .LOW_RESOLUTION_TIME .POSIX .WAIT".split()
)
UNSAFE_SPECIAL = frozenset({".SECONDEXPANSION", ".DEFAULT", ".SUFFIXES"})
# make-provided variables whose value the reader cannot know
BUILTIN_VARIABLES = frozenset("CURDIR MAKEFILE_LIST MAKEFLAGS MAKECMDGOALS SHELL MAKELEVEL".split())
RECIPE_PREFIXES = "@-+ \t"
MAX_DEPTH = 12


@dataclass
class Rule:
    prereqs: str = ""
    recipe: list[str] = field(default_factory=list)
    tainted: bool = False  # defined or extended where the reader cannot follow


@dataclass
class Makefile:
    rules: dict[str, Rule] = field(default_factory=dict)
    variables: dict[str, str | None] = field(default_factory=dict)  # None: value unknowable
    order: list[str] = field(default_factory=list)
    unsafe: str | None = None  # why no target of this file can be resolved


def join_continuations(text: str) -> list[str]:
    """A backslash-newline and the indentation after it become one space, as the shell would read it.
    Only an odd run of backslashes continues the line: ``a\\\\`` then a newline ends it (spec
    gate-f63-f65, T01 review: the second line was hidden from the rows)."""
    lines: list[str] = []
    pending: str | None = None
    for line in text.split("\n"):
        line = line if pending is None else pending + " " + line.lstrip(" \t")
        run = len(line) - len(line.rstrip("\\"))
        pending = line[:-1].rstrip(" \t") if run % 2 else None
        if pending is None:
            lines.append(line)
    return lines if pending is None else [*lines, pending]


def strip_comment(line: str) -> str:
    out = []
    escaped = False
    for char in line:
        if char == "#" and not escaped:
            break
        out.append(char)
        escaped = char == "\\" and not escaped
    return "".join(out)


def parse(text: str) -> Makefile:
    """Read one Makefile. A directive the reader does not know marks the file unsafe."""
    mf = Makefile()
    lines = join_continuations(text)
    current: list[str] = []
    depth = 0
    index = 0
    while index < len(lines):
        raw = lines[index]
        index += 1
        if raw.startswith("\t") and current:  # without a rule in progress a tab line is a makefile line
            for name in current:
                mf.rules[name].recipe.append(raw[1:].lstrip(RECIPE_PREFIXES))
                mf.rules[name].tainted |= depth > 0
            continue
        line = strip_comment(raw).strip()
        if not line:
            continue
        if re.match(r"^define\b", line):
            name = line.split(None, 1)[1].split("=")[0].strip() if len(line.split(None, 1)) > 1 else ""
            body: list[str] = []
            while index < len(lines) and lines[index].strip() != "endef":
                body.append(lines[index])
                index += 1
            index += 1
            mf.variables[name] = None if depth else "\n".join(body)
            current = []
        elif CONDITIONAL_RE.match(line):
            depth += 1
        elif line == "else" or line.startswith("else "):
            pass
        elif line == "endif":
            depth = max(0, depth - 1)
        elif INCLUDE_RE.match(line):
            mf.unsafe = "include"
        elif "$(eval" in line or "${eval" in line:
            mf.unsafe = "eval"
        elif re.match(r"^(unexport|vpath|export)\b", line) and "=" not in line:
            pass
        elif line.startswith(("$(", "${")):
            pass  # $(info …), $(warning …), $(error …)
        elif match := ASSIGN_RE.match(line):
            current = []
            assign(mf, match.group(1), match.group(2), match.group(3), depth)
        elif ":" in line:
            current = rule_line(mf, line, depth)
        else:
            mf.unsafe = f"directive {line.split()[0]}"
    return mf


def assign(mf: Makefile, name: str, operator: str, value: str, depth: int) -> None:
    value = value.strip()
    if depth or operator == "!=":
        mf.variables[name] = None
    elif operator == "?=":
        mf.variables.setdefault(name, value)
    elif operator == "+=":
        previous = mf.variables.get(name, "")
        mf.variables[name] = None if previous is None else f"{previous} {value}".strip()
    elif operator == "=":
        mf.variables[name] = value
    else:  # := ::= :::= expand now, with what is defined so far
        mf.variables[name] = expand(value, mf.variables, {})


def rule_line(mf: Makefile, line: str, depth: int) -> list[str]:
    """Record a rule; return the targets the following recipe lines belong to."""
    left, _, right = line.partition(":")
    if right.startswith(":"):
        right = right[1:]
    inline = None
    if ";" in right:
        right, _, inline = right.partition(";")
    if ":" in right:
        mf.unsafe = "static pattern rule"
        return []
    targets = left.split()
    if TARGET_VARIABLE_RE.match(right.strip()):
        for name in targets:
            mf.rules.setdefault(name, Rule()).tainted = True
        return []
    recipients = []
    for name in targets:
        suffix_rule = SUFFIX_RULE_RE.match(name) and name not in HARMLESS_SPECIAL
        if "%" in name or name in UNSAFE_SPECIAL or suffix_rule:
            mf.unsafe = f"pattern or suffix rule {name}"
            return []
        if name in HARMLESS_SPECIAL:
            continue
        rule = mf.rules.setdefault(name, Rule())
        rule.prereqs = f"{rule.prereqs} {right.strip()}".strip()
        rule.tainted |= depth > 0
        if inline is not None:
            rule.recipe.append(inline.strip().lstrip(RECIPE_PREFIXES))
        if name not in mf.order:
            mf.order.append(name)
        recipients.append(name)
    return recipients


def matching_close(text: str, start: int) -> int | None:
    opener = text[start]
    closer = ")" if opener == "(" else "}"
    level = 0
    for index in range(start, len(text)):
        if text[index] == opener:
            level += 1
        elif text[index] == closer:
            level -= 1
            if level == 0:
                return index
    return None


def expand(text: str, variables: dict[str, str | None], params: dict[str, str], depth: int = 0) -> str | None:
    """Expand make references; None when a reference cannot be known from the file alone."""
    if depth > MAX_DEPTH:
        return None
    out: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char != "$":
            out.append(char)
            index += 1
            continue
        if index + 1 >= len(text):
            return None
        marker = text[index + 1]
        if marker == "$":
            out.append("$")
            index += 2
            continue
        if marker in "({":
            end = matching_close(text, index + 1)
            if end is None:
                return None
            value = reference(text[index + 2 : end], variables, params, depth)
            index = end + 1
        else:
            value = params[marker] if marker in params else reference(marker, variables, params, depth)
            index += 2
        if value is None:
            return None
        out.append(value)
    return "".join(out)


def reference(inner: str, variables: dict[str, str | None], params: dict[str, str], depth: int) -> str | None:
    if re.match(r"^call\s", inner):
        return call(inner.split(None, 1)[1], variables, params, depth)
    if not NAME_RE.match(inner):
        return None  # a function, a substitution reference, a nested reference
    if inner in params:
        return params[inner]
    if inner == "MAKE":
        return "make"
    if inner in BUILTIN_VARIABLES or inner not in variables:
        return None
    raw = variables[inner]
    return None if raw is None else expand(raw, variables, params, depth + 1)


def call(arguments: str, variables: dict[str, str | None], params: dict[str, str], depth: int) -> str | None:
    parts = [expand(part.strip(), variables, params, depth + 1) for part in arguments.split(",")]
    if any(part is None for part in parts):
        return None
    name = parts[0] or ""
    body = variables.get(name)
    if body is None:
        return None
    call_params = {str(position): value for position, value in enumerate(parts) if value is not None}
    return expand(body, variables, call_params, depth + 1)


def prerequisites(raw: str, variables: dict[str, str | None], target: str) -> list[str]:
    """The prerequisite words that can be known: literal names always, a reference only when it
    expands. A reference that does not expand is a file list (see the module note)."""
    words: list[str] = []
    for word in raw.split():
        expanded = expand(word, variables, {"@": target}) if "$" in word else word
        words.extend(part for part in (expanded or "").split() if part != "|")
    return words


def default_goal(mf: Makefile, variables: dict[str, str | None]) -> str | None:
    configured = variables.get(".DEFAULT_GOAL")
    if configured is not None:
        return expand(configured, variables, {}) or None
    if ".DEFAULT_GOAL" in variables:
        return None
    return mf.order[0] if mf.order else None


def commands(mf: Makefile, goals: list[str], overrides: dict[str, str]) -> list[str] | None:
    """The recipe lines make would run for the goals, prerequisites first; None when unknowable."""
    if mf.unsafe:
        return None
    variables: dict[str, str | None] = {**mf.variables, **overrides}
    if not goals:
        goal = default_goal(mf, variables)
        if goal is None:
            return None
        goals = [goal]
    out: list[str] = []
    seen: set[str] = set()

    def visit(name: str) -> bool:
        if name in seen:
            return True
        seen.add(name)
        rule = mf.rules.get(name)
        if rule is None:
            return True  # a file, or a goal make would refuse: nothing of its own runs
        if rule.tainted:
            return False
        for word in prerequisites(rule.prereqs, variables, name):
            if not visit(word):
                return False
        for line in rule.recipe:
            text = expand(line, variables, {"@": name})
            if text is None:
                return False
            out.extend(part.strip().lstrip(RECIPE_PREFIXES) for part in text.split("\n") if part.strip())
        return True

    return out if all(visit(goal) for goal in goals) else None


def find_makefile(folder: Path, name: str | None) -> Path | None:
    if name is not None:
        path = folder / name
        return path if path.is_file() else None
    for candidate in MAKEFILE_NAMES:
        path = folder / candidate
        if path.is_file():
            return path
    return None


def resolve(
    folder: Path, makefile: str | None, goals: list[str], overrides: dict[str, str]
) -> list[str] | None:
    path = find_makefile(folder, makefile)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return commands(parse(text), goals, overrides)
