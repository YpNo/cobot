"""Home Assistant's secret files for the gate's read-only agents (spec expert-homeassistant).

A consultant, learner, auditor or investigator reads with an allow-listed command (``cat``,
``grep``, ``rg``, ``git show``, ``curl -s``, ``gitleaks``, ``semgrep``). These helpers say when
such a command would print ``secrets.yaml`` or a ``.storage/`` file: naming it, reading it through
a redirect, walking a tree that holds it, printing a history that tracked it, or fetching it as a
``file:`` URL. Each takes a segment's plain words (wrappers stripped, the program first) and
returns the refusal's note, or None. The main thread is not judged here.
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path

import _cobot_shell as shell
from _cobot_common import git

SECRET_FILE_NAMES = frozenset({"secrets.yaml"})
SECRET_FOLDERS = frozenset({".storage"})
SECRET_NAMES = SECRET_FILE_NAMES | SECRET_FOLDERS
WALK_LIMIT = 20_000  # entries walked per command; past it the tree counts as holding both
SKIPPED_DIRS = frozenset({".git"})

TEXT_READERS = frozenset("cat head tail less more sort uniq diff cut".split())
PATTERN_READERS = frozenset("grep egrep fgrep rg jq yq awk".split())  # first operand: a pattern
GREPS = frozenset({"grep", "egrep", "fgrep"})
PATTERN_OPTIONS = frozenset({"-e", "--regexp", "-f", "--file", "--from-file"})
PATTERN_CLUSTER_RE = re.compile(r"-[A-Za-z]*[ef].*")  # -e or -f inside a short cluster
GREP_VALUES = frozenset(
    "-e -f -m -A -B -C -d -D --regexp --file --max-count --after-context --before-context "
    "--context --directories --devices --exclude --include --exclude-dir --exclude-from --label "
    "--binary-files --color --colour".split()
)
RG_VALUES = frozenset(
    "-e -f -g -t -T -m -A -B -C -j -M -d -E -r --regexp --file --glob --iglob --type --type-not "
    "--max-count --after-context --before-context --context --threads --max-columns --max-depth "
    "--max-filesize --encoding --replace --sort --sortr --color --colors --pre --pre-glob "
    "--ignore-file --path-separator --context-separator --field-match-separator".split()
)
SEMGREP_VALUES = frozenset(
    "-c -e -l -o -j --config --pattern --lang --output --jobs --exclude --include --severity "
    "--timeout --max-target-bytes --metrics --baseline-commit".split()
)
GIT_GLOBAL_VALUES = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"})
HISTORY_VERBS = frozenset({"show", "log", "diff", "whatchanged", "grep", "cat-file"})
NO_CONTENT = frozenset(
    "--stat --shortstat --numstat --name-only --name-status --summary --dirstat --raw -s "
    "--no-patch --quiet".split()
)
LOG_PATCH_RE = re.compile(r"-p|-u|--patch.*|-U\d*|--unified.*|--cc|-c|-L.*|--full-diff")
FILE_URL_RE = re.compile(r"(?:^|=)file:", re.I)
TRACKED_SPECS = (":(glob)**/secrets.yaml", ":(glob)**/.storage/**")

NAMED = "a read-only agent reads a Home Assistant secrets file (secrets.yaml or .storage/): " \
    "report whether it is tracked with git ls-files instead"  # fmt: skip
TREE = "a recursive read or scan reaches {names} here: exclude it ({how}) or name the files to read"
HISTORY = "this history printer would show {path}, which the repository tracks or tracked: " \
    "add a pathspec that excludes it (-- . ':!*secrets.yaml' ':!*.storage/*')"  # fmt: skip
FILE_URL = "curl with a file: URL reads any local file, Home Assistant's secrets included"


def names_secret_file(word: str) -> bool:
    """``config/secrets.yaml``, ``HEAD:secrets.yaml``, ``--file=.storage/auth``, ``.storage``."""
    if shell.has_sentinel(word):
        return False
    parts = [part for part in re.split(r"[/:=]", word) if part]
    return bool(parts) and (parts[-1] in SECRET_FILE_NAMES or any(p in SECRET_FOLDERS for p in parts))


def exposure(plain: list[str], base: Path) -> str | None:
    """The note refusing a read-only agent's segment that would print a secrets file, else None."""
    if not plain:
        return None
    head, words = plain[0], plain[1:]
    if head == "curl" and any(FILE_URL_RE.search(word) for word in words):
        return FILE_URL
    if head == "git":
        return history_exposure(words, base)
    named = [w for w in words if not w.startswith("--exclude")]  # an exclusion keeps the file out
    if (head in TEXT_READERS and any(map(names_secret_file, named))) or (
        head in PATTERN_READERS and any(map(names_secret_file, without_pattern(named)))
    ):
        return NAMED
    return tree_exposure(head, words, base)


def redirect_exposure(targets: list[str]) -> str | None:
    """A redirection that reads or writes a secrets file (``cat < secrets.yaml``)."""
    return NAMED if any(map(names_secret_file, targets)) else None


def without_pattern(words: list[str]) -> list[str]:
    """The words of a pattern reader less its first operand, unless an option carries the pattern
    (``-e``, ``--regexp=``, ``-netoken``): that operand is a pattern or a program, not a file."""
    if any(w.split("=", 1)[0] in PATTERN_OPTIONS or PATTERN_CLUSTER_RE.fullmatch(w) for w in words):
        return words
    first = next((i for i, w in enumerate(words) if not w.startswith("-")), None)
    return words if first is None else words[:first] + words[first + 1 :]


def operands(words: list[str], values: frozenset[str], pattern_first: bool) -> list[str]:
    """The operands past the options (and past a pattern operand), with option values skipped."""
    out: list[str] = []
    given = False
    index = 0
    while index < len(words):
        word = words[index]
        if word == "--":
            out.extend(words[index + 1 :])
            break
        if word.startswith("--"):
            name = word.split("=", 1)[0]
            given = given or name in PATTERN_OPTIONS
            index += 2 if name in values and "=" not in word else 1
            continue
        if word.startswith("-") and len(word) > 1:
            index += 1 + cluster_takes_next(word, values)
            given = given or bool(PATTERN_CLUSTER_RE.fullmatch(word))
            continue
        out.append(word)
        index += 1
    return out[1:] if pattern_first and not given and out else out


def cluster_takes_next(word: str, values: frozenset[str]) -> int:
    """1 when a short cluster ends in an option whose value is the next word (``-A`` in ``-nA 3``)."""
    for position, letter in enumerate(word[1:], start=1):
        if f"-{letter}" in values:
            return int(position == len(word) - 1)
    return 0


def option_values(words: list[str], names: frozenset[str]) -> list[str]:
    """Every value given to the named options: ``--x=v``, ``--x v``, ``-g v`` and ``-gv``."""
    found: list[str] = []
    index = 0
    while index < len(words) and words[index] != "--":
        word = words[index]
        name, eq, value = word.partition("=")
        if word.startswith("--") and name in names:
            found.append(value) if eq else found.extend(words[index + 1 : index + 2])
            index += 1 if eq else 2
        elif word in names:
            found.extend(words[index + 1 : index + 2])
            index += 2
        elif word[:2] in names and len(word) > 2 and not word.startswith("--"):
            found.append(word[2:])
            index += 1
        else:
            index += 1
    return found


def tree_exposure(head: str, words: list[str], base: Path) -> str | None:
    """A recursive grep, any rg, a semgrep scan or a verbose gitleaks over a tree holding them."""
    if head in GREPS and recursive_grep(words):
        roots = operands(words, GREP_VALUES, pattern_first=True)
        left = unexcluded(
            secret_names_under(roots or ["."], base),
            option_values(words, frozenset({"--exclude"})),
            [d.rstrip("/") for d in option_values(words, frozenset({"--exclude-dir"}))],
        )
        how = "--exclude=secrets.yaml --exclude-dir=.storage"
    elif head == "rg":
        raw = option_values(words, frozenset({"-g", "--glob", "--iglob"}))
        globs = [g[1:].rstrip("/") for g in raw if g.startswith("!")]
        roots = operands(words, RG_VALUES, pattern_first=True)
        left = unexcluded(secret_names_under(roots or ["."], base), globs, globs)
        how = "-g '!secrets.yaml' -g '!.storage'"
    elif head == "semgrep":
        rest = words[1:] if words[:1] in (["scan"], ["ci"]) else words
        excluded = [e.rstrip("/") for e in option_values(rest, frozenset({"--exclude"}))]
        roots = operands(rest, SEMGREP_VALUES, pattern_first=False)
        left = unexcluded(secret_names_under(roots or ["."], base), excluded, excluded)
        how = "--exclude=secrets.yaml --exclude=.storage"
    elif head == "gitleaks" and verbose_unredacted(words):
        roots = option_values(words, frozenset({"-s", "--source"}))
        left = secret_names_under(roots or ["."], base)
        how = "--redact"
    else:
        return None
    return TREE.format(names=" and ".join(sorted(left)), how=how) if left else None


def recursive_grep(words: list[str]) -> bool:
    return any(
        w in ("--recursive", "--dereference-recursive", "--directories=recurse")
        or (re.fullmatch(r"-[A-Za-z]+", w) is not None and bool({"r", "R"} & set(w[1:])))
        for w in words
    )


def verbose_unredacted(words: list[str]) -> bool:
    verbose = any(w in ("-v", "--verbose") for w in words)
    return verbose and not any(w.split("=", 1)[0] == "--redact" for w in words)


def unexcluded(found: set[str], file_globs: list[str], dir_globs: list[str]) -> set[str]:
    """The names found that no exclusion glob covers: files against one list, folders the other."""
    return {
        name
        for name in found
        if not any(fnmatch.fnmatch(name, g) for g in (file_globs if name in SECRET_FILE_NAMES else dir_globs))
    }


def secret_names_under(roots: list[str], base: Path) -> set[str]:
    """Which of secrets.yaml and .storage the roots hold, walking at most WALK_LIMIT entries; past
    the limit both count as found, so a huge tree is refused rather than read blind."""
    found: set[str] = set()
    seen = 0
    for root in roots:
        if shell.has_sentinel(root):
            return set(SECRET_NAMES)  # a glob or a variable: the gate cannot know what it holds
        found |= {part for part in Path(root).parts if part in SECRET_NAMES}
        path = Path(os.path.expanduser(root))
        path = path if path.is_absolute() else base / path
        if path.is_file():
            found |= {path.name} & SECRET_FILE_NAMES
            continue
        for _, dirnames, filenames in os.walk(path):
            seen += len(dirnames) + len(filenames)
            if seen > WALK_LIMIT:
                return set(SECRET_NAMES)
            found |= (SECRET_FOLDERS & set(dirnames)) | (SECRET_FILE_NAMES & set(filenames))
            dirnames[:] = [d for d in dirnames if d not in SKIPPED_DIRS | SECRET_FOLDERS]
    return found


def history_exposure(words: list[str], base: Path) -> str | None:
    """A git verb that prints file content over a history that tracks or tracked a secrets file,
    with no pathspec keeping it out. ``git -C <dir>`` moves the base."""
    while words and words[0].startswith("-"):
        option = words[0].split("=", 1)[0]
        takes = option in GIT_GLOBAL_VALUES and "=" not in words[0]
        if option == "-C" and len(words) > 1:
            base = base / words[1]
        words = words[2:] if takes else words[1:]
    if not words or words[0] not in HISTORY_VERBS | {"blame"}:
        return None
    if any(map(names_secret_file, words[1:])):
        return NAMED
    if words[0] in ("cat-file", "blame") or not prints_content(words[0], words[1:]):
        return None  # cat-file and blame name their object: judged by name above
    paths = tracked_secret_paths(base)
    exposed = [p for p in paths if not scoped_out(words[1:], p)]
    return HISTORY.format(path=exposed[0]) if exposed else None


def prints_content(verb: str, words: list[str]) -> bool:
    if verb == "grep":
        return True
    if verb in ("log", "whatchanged"):
        return any(LOG_PATCH_RE.fullmatch(w.split("=", 1)[0] if w.startswith("--") else w) for w in words)
    return not any(w.split("=", 1)[0] in NO_CONTENT for w in words)


def tracked_secret_paths(base: Path) -> list[str]:
    """The secrets files this repository's history or index holds, by path; [] outside a repo."""
    history = git(["log", "--all", "--format=", "--name-only", "--", *TRACKED_SPECS], base) or ""
    staged = git(["ls-files", "--", *TRACKED_SPECS], base) or ""
    return sorted({line for line in (history + "\n" + staged).splitlines() if line.strip()})


def scoped_out(words: list[str], path: str) -> bool:
    """Whether the command's pathspecs (after ``--``) or ``rev:path`` operands keep ``path`` out."""
    specs = words[words.index("--") + 1 :] if "--" in words else []
    excludes = [exclude_pattern(s) for s in specs if exclude_pattern(s) is not None]
    if any(fnmatch.fnmatch(path, pattern) for pattern in excludes):
        return True
    positives = [s for s in specs if exclude_pattern(s) is None]
    named = [w.split(":", 1)[1] for w in words if ":" in w and not w.startswith(("-", ":"))]
    scopes = positives + named
    return bool(scopes) and not any(spec_covers(spec, path) for spec in scopes)


def exclude_pattern(spec: str) -> str | None:
    """``:!x``, ``:^x``, ``:(exclude)x`` and ``:(exclude,glob)x`` give ``x``; others give None."""
    match = re.fullmatch(r":(?:[!^]|\((?:[a-z]+,)*exclude(?:,[a-z]+)*\))(.*)", spec)
    return match.group(1) if match else None


def spec_covers(spec: str, path: str) -> bool:
    """Whether a positive pathspec could name ``path``: a magic or wildcard spec counts."""
    stripped = spec.rstrip("/")
    if spec.startswith(":") or stripped in ("", ".", "*"):
        return True
    if any(c in spec for c in "*?["):
        return fnmatch.fnmatch(path, spec)
    return path == stripped or path.startswith(stripped + "/")
