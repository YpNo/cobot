"""Dated knowledge lines: scan, classify, age, and promote. Standard library only.

A knowledge line is ``- [status YYYY-MM-DD · src: source] claim`` (design section 8). Lines live in
the plugin's skills (``SKILL.md`` and ``references/*.md``) and in ``.agent/knowledge/<topic>.md``.

Decision 23 sets the staleness thresholds. A *version* line is one whose claim states what is
current: it carries a version token (``1.2``, ``v7``, a commit SHA) together with a currency word
(current, latest, supported, released, ships, bundles, ...), or it sits in a ``versions``,
``actions`` or ``ci`` reference file without a history word (since, stable in, introduced). It is
stale after 30 days. Every other line is *idiom* and is stale after 90 days; "edition 2024 stable
since 1.85.0" is history, not currency. A line unchecked for 180 days is due for re-verification
or removal at consolidation.

Promotion carries general entries into the agentic-partner checkout. An entry whose claim is
already known re-dates the existing line where it is; an entry with ``supersedes`` (a fragment of
the old claim) replaces that line; everything else is appended to ``references/learned.md``. A
skeleton expert is created only when the delta carries a ``skeleton`` block.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from _partner_common import config_dir, plugin_root

VERSION_DAYS = 30
IDIOM_DAYS = 90
DROP_DAYS = 180
REFERENCES_CAP = 300  # dated lines per skill, across SKILL.md and references/
BRIEF_MAX = 220
LINE_RE = re.compile(
    r"^(\s*)- \[(verified|reported|assumed) (\d{4}-\d{2}-\d{2})(?: · src: ([^\]]*))?\] (.*)$"
)
VERSION_TOKEN_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)*\b|\b[0-9a-f]{40}\b")
CURRENCY_RE = re.compile(
    r"\b(?:current|latest|newest|supported|released|ships|bundles|preinstalled|default)\b|\bis the\b", re.I
)
HISTORY_RE = re.compile(
    r"\b(?:since|stable in|introduced|added in|deprecated in|removed in)\b|\(\w{3} \d{4}\)", re.I
)
VERSION_FILES = frozenset({"versions", "actions", "ci"})
KNOWLEDGE_SKILL_PREFIXES = ("lang-", "expert-", "consult-")
STATUSES = ("verified", "reported", "assumed")
MARKETPLACE = "agentic-partner"


@dataclass(frozen=True)
class Line:
    skill: str
    file: Path
    number: int
    status: str
    checked: date
    source: str
    claim: str
    indent: str = ""

    @property
    def kind(self) -> str:
        if not VERSION_TOKEN_RE.search(self.claim) or HISTORY_RE.search(self.claim):
            return "idiom"
        if CURRENCY_RE.search(self.claim) or self.file.stem in VERSION_FILES:
            return "version"
        return "idiom"

    @property
    def threshold(self) -> int:
        return VERSION_DAYS if self.kind == "version" else IDIOM_DAYS

    def age(self, today: date) -> int:
        return (today - self.checked).days

    def stale(self, today: date) -> bool:
        return self.age(today) > self.threshold


@dataclass(frozen=True)
class Summary:
    skill: str
    total: int
    stale: int
    stale_version: int
    reported: int
    assumed: int
    oldest: date | None
    due: int  # unchecked for DROP_DAYS or more

    def as_dict(self) -> dict:
        return {
            "skill": self.skill,
            "lines": self.total,
            "stale": self.stale,
            "stale_version": self.stale_version,
            "reported": self.reported,
            "assumed": self.assumed,
            "oldest": self.oldest.isoformat() if self.oldest else None,
            "due": self.due,
        }


def parse_line(skill: str, file: Path, number: int, text: str) -> Line | None:
    match = LINE_RE.match(text.rstrip())
    if not match:
        return None
    indent, status, checked, source, claim = match.groups()
    try:
        when = date.fromisoformat(checked)
    except ValueError:
        return None
    return Line(skill, file, number, status, when, (source or "").strip(), claim.strip(), indent)


def scan_file(skill: str, file: Path) -> list[Line]:
    try:
        text = file.read_text(encoding="utf-8")
    except OSError:
        return []
    found = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = parse_line(skill, file, number, raw)
        if line:
            found.append(line)
    return found


def skill_files(folder: Path) -> list[Path]:
    files = [folder / "SKILL.md"] if (folder / "SKILL.md").is_file() else []
    files.extend(sorted((folder / "references").glob("*.md")))
    return files


def scan_skill(folder: Path) -> list[Line]:
    lines: list[Line] = []
    for file in skill_files(folder):
        lines.extend(scan_file(folder.name, file))
    return lines


def scan_plugin(plugin: Path) -> dict[str, list[Line]]:
    """Every knowledge skill that carries dated lines, by skill name."""
    found: dict[str, list[Line]] = {}
    for folder in sorted((plugin / "skills").glob("*/")):
        if folder.name.startswith(KNOWLEDGE_SKILL_PREFIXES):
            lines = scan_skill(folder)
            if lines:
                found[folder.name] = lines
    return found


def scan_memory(memory_dir: Path) -> dict[str, list[Line]]:
    """``.agent/knowledge/<topic>.md`` files, keyed ``knowledge/<topic>``."""
    found: dict[str, list[Line]] = {}
    for file in sorted((memory_dir / "knowledge").glob("*.md")):
        name = f"knowledge/{file.stem}"
        lines = scan_file(name, file)
        if lines:
            found[name] = lines
    return found


def summarise(skill: str, lines: list[Line], today: date) -> Summary:
    stale = [line for line in lines if line.stale(today)]
    return Summary(
        skill=skill,
        total=len(lines),
        stale=len(stale),
        stale_version=sum(1 for line in stale if line.kind == "version"),
        reported=sum(1 for line in lines if line.status == "reported"),
        assumed=sum(1 for line in lines if line.status == "assumed"),
        oldest=min((line.checked for line in lines), default=None),
        due=sum(1 for line in lines if line.age(today) >= DROP_DAYS),
    )


def summaries(groups: dict[str, list[Line]], today: date) -> list[Summary]:
    return [summarise(name, lines, today) for name, lines in groups.items()]


def describe(summary: Summary, today: date) -> str:
    parts = [f"{summary.total} line(s)"]
    if summary.stale:
        idiom = summary.stale - summary.stale_version
        kinds = ", ".join(
            k
            for k in (
                f"{summary.stale_version} version" if summary.stale_version else "",
                f"{idiom} idiom" if idiom else "",
            )
            if k
        )
        parts.append(f"{summary.stale} stale ({kinds})")
    if summary.reported:
        parts.append(f"{summary.reported} reported")
    if summary.assumed:
        parts.append(f"{summary.assumed} assumed")
    if summary.due:
        parts.append(f"{summary.due} due for re-verification (>= {DROP_DAYS} days)")
    age = (
        f"oldest {summary.oldest.isoformat()} ({(today - summary.oldest).days} days)"
        if summary.oldest
        else "undated"
    )
    return f"{summary.skill}: {', '.join(parts)}; {age}"


def report(items: list[Summary], today: date, stale_only: bool = False, as_json: bool = False) -> str:
    shown = [s for s in items if s.stale or s.reported or s.assumed] if stale_only else items
    if as_json:
        return json.dumps([s.as_dict() for s in shown], indent=1)
    if not shown:
        return "knowledge: nothing stale" if stale_only else "knowledge: no dated lines found"
    lines = [describe(s, today) for s in shown]
    lines.append(
        f"thresholds: version lines {VERSION_DAYS} days, idiom {IDIOM_DAYS} days, "
        f"re-verify or drop at {DROP_DAYS}"
    )
    return "\n".join(lines)


def brief_line(items: list[Summary], today: date) -> str:
    """One line for the session brief: the stale skills, the reported count, or 'fresh'."""
    stale = sorted((s for s in items if s.stale), key=lambda s: (-s.stale, s.skill))
    reported = sum(s.reported for s in items)
    oldest = min((s.oldest for s in items if s.oldest), default=None)
    if not items or oldest is None:
        return "knowledge: no dated lines"
    if not stale:
        text = f"knowledge: fresh (oldest {(today - oldest).days} days)"
    else:
        named = ", ".join(f"{s.skill} ({s.stale})" for s in stale[:4])
        more = f" +{len(stale) - 4} more" if len(stale) > 4 else ""
        text = f"knowledge: stale -> {named}{more}; refresh with /partner:learn <skill>"
    if reported:
        text += f"; {reported} reported line(s)"
    return text[:BRIEF_MAX]


# ---------------------------------------------------------------- lines and claims


def claim_key(text: str) -> str:
    """Normalised claim for de-duplication; the ``(general)`` tag is not part of the claim."""
    text = re.sub(r"\s*\(general\)\s*$", "", text.strip())
    return re.sub(r"\W+", " ", text.lower()).strip()


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def format_line(entry: dict, today: date, tag_general: bool = True, indent: str = "") -> str:
    """The dated line; a ``]`` in the source would end the bracket early, so it becomes ``)``."""
    source = one_line(str(entry.get("source", ""))).replace("]", ")") or "unsourced"
    scope = " (general)" if tag_general and entry.get("scope") in ("general", "plugin") else ""
    checked = entry.get("checked") or today.isoformat()
    return f"{indent}- [{entry['status']} {checked} · src: {source}] {one_line(entry['claim'])}{scope}"


@dataclass
class Index:
    """Dated lines of a set of files, by normalised claim, for re-dating and superseding."""

    files: list[Path]
    dry: bool = False
    lines: list[Line] = field(default_factory=list)

    def __post_init__(self) -> None:
        for file in self.files:
            self.lines.extend(scan_file("", file))

    def by_claim(self, claim: str) -> Line | None:
        key = claim_key(claim)
        return next((line for line in self.lines if claim_key(line.claim) == key), None)

    def by_fragment(self, fragment: str) -> Line | str | None:
        """The one line whose claim contains the fragment; a message when it is ambiguous."""
        needle = fragment.strip().lower()
        hits = [line for line in self.lines if needle and needle in line.claim.lower()]
        if len(hits) > 1:
            return f"supersedes '{fragment[:40]}' matches {len(hits)} lines"
        return hits[0] if hits else None

    def replace(self, old: Line, text: str) -> Line | None:
        new = parse_line(old.skill, old.file, old.number, text)
        if new is None:
            return None
        if not self.dry:
            rows = old.file.read_text(encoding="utf-8").splitlines()
            rows[old.number - 1] = text
            old.file.write_text("\n".join(rows) + "\n", encoding="utf-8")
        self.lines = [new if line is old else line for line in self.lines]
        return new

    def add(self, file: Path, text: str) -> None:
        line = parse_line("", file, 0, text)
        if line:
            self.lines.append(line)


def newer(entry: dict, known: Line, today: date) -> bool:
    """An entry re-dates a known line when it was checked later or its status changed."""
    checked = entry.get("checked")
    when = date.fromisoformat(checked) if checked else today
    return when > known.checked or entry["status"] != known.status


def place(entry: dict, index: Index, today: date, tag_general: bool) -> tuple[str, str, Path | None]:
    """Where an entry goes: ``("redated"|"superseded"|"new"|"skipped", line or reason, file)``."""
    claim = entry["claim"].strip()
    known = index.by_claim(claim)
    if known:
        if not newer(entry, known, today):
            return "skipped", f"already known: {claim[:50]}", None
        text = format_line({**entry, "claim": known.claim}, today, False, known.indent)
        index.replace(known, text)
        return "redated", text.strip(), known.file
    fragment = str(entry.get("supersedes", "")).strip()
    if fragment:
        old = index.by_fragment(fragment)
        if isinstance(old, str):
            return "skipped", old, None
        if old:
            tag = " (general)" if old.claim.endswith("(general)") else ""
            text = format_line(entry, today, False, old.indent) + tag
            index.replace(old, text)
            return "superseded", text.strip(), old.file
    return "new", format_line(entry, today, tag_general), None


# ---------------------------------------------------------------- promote


SKELETON_TEMPLATE = "skills/learn/templates/expert-SKILL.md"
LEARNED_HEADER = (
    "# {skill} — learned lines\n\n"
    "Promoted by `partner-memory learn --promote`; move a line to its topical file at review.\n"
    "Format: `- [status YYYY-MM-DD · src: <url or exp: command>] claim`.\n"
)


@dataclass
class Promotion:
    skill: str
    created: bool
    written: list[str]
    skipped: list[str]
    files: list[Path]
    redated: int = 0
    superseded: int = 0
    branch: str | None = None
    worktree: Path | None = None
    commit: str | None = None

    @property
    def changed(self) -> int:
        return len(self.written) + self.redated + self.superseded

    def lines(self) -> list[str]:
        out = [
            f"promote: {self.skill}{' (new skeleton expert)' if self.created else ''}, "
            f"{len(self.written)} new, {self.redated} re-dated, {self.superseded} superseded"
        ]
        out.extend(f"  + {line}" for line in self.written)
        out.extend(f"  - {reason}" for reason in self.skipped)
        out.extend(f"  file: {file}" for file in self.files)
        if self.worktree:
            out.append(f"  worktree: {self.worktree} on {self.branch} ({self.commit or 'no new commit'})")
            out.append(f"  to open the PR: git -C {self.worktree} push -u origin {self.branch}")
            out.append(
                f"  then: gh pr create --head {self.branch} "
                f"--title 'docs(knowledge): {self.skill} learns {self.changed} line(s)' --fill"
            )
        return out


def source_checkout(explicit: str | None = None) -> Path | None:
    """The agentic-partner checkout promote writes to: ``--source``, ``$PARTNER_SOURCE``, the
    checkout this plugin runs from (``--dev``), or the directory Claude Code recorded when the
    marketplace was added (``known_marketplaces.json``). A GitHub-sourced install has none."""

    def valid(candidate: str | os.PathLike | None) -> Path | None:
        return (
            Path(candidate).resolve()
            if candidate and (Path(candidate) / "plugins" / "partner" / "skills").is_dir()
            else None
        )

    if explicit:
        return valid(explicit)
    found = valid(os.environ.get("PARTNER_SOURCE"))
    if found is None and len(plugin_root().parents) > 1:
        found = valid(plugin_root().parents[1])
    if found is None:
        found = valid(marketplace_path())
    return found


def marketplace_path() -> str | None:
    record = config_dir() / "plugins" / "known_marketplaces.json"
    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    source = (data.get(MARKETPLACE) or {}).get("source") or {}
    return source.get("path") if source.get("source") == "directory" else None


def skill_name(topic: str, requested: str | None, plugin: Path) -> tuple[str, bool]:
    """The skill a general entry belongs to and whether it exists: the requested name, or an
    exact ``lang-<topic>`` / ``expert-<topic>`` / ``<topic>`` match."""
    for name in [requested] if requested else [f"lang-{topic}", f"expert-{topic}", topic]:
        if name and (plugin / "skills" / name / "SKILL.md").is_file():
            return name, True
    return (requested or f"expert-{topic}"), False


def skeleton(plugin: Path, skill: str, topic: str, meta: dict, today: date) -> Path:
    folder = plugin / "skills" / skill
    folder.mkdir(parents=True, exist_ok=True)
    text = (plugin / SKELETON_TEMPLATE).read_text(encoding="utf-8")
    text = (
        text.replace("{{SKILL}}", skill)
        .replace("{{TOPIC}}", topic)
        .replace("{{DATE}}", today.isoformat())
        .replace("{{DESCRIPTION}}", str(meta["description"]).strip())
        .replace(
            "{{WHEN}}", str(meta.get("when_to_use") or f"when {topic} is read, changed or discussed").strip()
        )
        .replace("{{PATHS}}", "\n".join(f'  - "{p}"' for p in meta["paths"]))
    )
    (folder / "SKILL.md").write_text(text, encoding="utf-8")
    return folder


def skeleton_problem(meta: dict | None, topic: str) -> str | None:
    if not meta:
        return f'no skill matches \'{topic}\': set "skill" in the delta, or a "skeleton" with description and paths'  # noqa: E501
    missing = [key for key in ("description", "paths") if not meta.get(key)]
    if missing or not isinstance(meta.get("paths"), list):
        return f"skeleton needs {', '.join(missing) or 'paths as a list'}"
    return None


def write_lines(plugin: Path, topic: str, entries: list[dict], delta: dict, today: date) -> Promotion | str:
    name, exists = skill_name(topic, delta.get("skill"), plugin)
    if not exists:
        problem = skeleton_problem(delta.get("skeleton"), topic)
        if problem:
            return f"promote: {problem}"
        skeleton(plugin, name, topic, delta["skeleton"], today)
    folder = plugin / "skills" / name
    index = Index(skill_files(folder))
    room = REFERENCES_CAP - len(index.lines)
    result = Promotion(name, not exists, [], [], [folder / "SKILL.md"] if not exists else [])
    touched: list[Path] = []
    for entry in entries:
        kind, text, file = place(entry, index, today, tag_general=False)
        if kind == "skipped":
            result.skipped.append(text)
        elif kind == "redated":
            result.redated += 1
            touched.append(file)
        elif kind == "superseded":
            result.superseded += 1
            touched.append(file)
        elif room <= 0:
            result.skipped.append(
                f"over the {REFERENCES_CAP}-line cap of {name}, consolidate first: {entry['claim'][:50]}"
            )
        else:
            room -= 1
            result.written.append(text)
            index.add(folder / "references" / "learned.md", text)
    if result.written:
        target = folder / "references" / "learned.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file():
            head = target.read_text(encoding="utf-8").rstrip("\n") + "\n"
        else:
            head = LEARNED_HEADER.format(skill=name).rstrip("\n") + "\n\n"  # a blank line before the list
        target.write_text(head + "\n".join(result.written) + "\n", encoding="utf-8")
        touched.append(target)
    for file in touched:
        if file not in result.files:
            result.files.append(file)
    return result


def git(args: list[str], cwd: Path) -> tuple[int, str]:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30, check=False)  # noqa: S603,S607
    return out.returncode, (out.stdout + out.stderr).strip()


def base_ref(source: Path) -> str:
    code, out = git(["symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], source)
    return out if code == 0 and out else "HEAD"


def worktree_for(source: Path, topic: str, worktrees: Path, today: date) -> tuple[Path, str] | str:
    """A worktree on ``learn/<topic>``; reused when it exists, dated when only the branch does."""
    branch = f"learn/{topic}"
    folder = worktrees / topic
    git(["worktree", "prune"], source)
    if folder.is_dir():
        code, out = git(["rev-parse", "--abbrev-ref", "HEAD"], folder)
        if code == 0 and out == branch:
            return folder, branch
        return f"promote: {folder} exists but is not on {branch}; remove it first"
    if git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], source)[0] == 0:
        branch = f"{branch}-{today.isoformat()}"
        folder = worktrees / f"{topic}-{today.isoformat()}"
    worktrees.mkdir(parents=True, exist_ok=True)
    code, out = git(["worktree", "add", "-b", branch, str(folder), base_ref(source)], source)
    if code != 0:
        return f"promote: git worktree add failed: {out[-300:]}"
    return folder, branch


def promote(
    source: Path, topic: str, entries: list[dict], delta: dict, today: date, in_place: bool, worktrees: Path
) -> Promotion | str:
    if not (source / "plugins" / "partner" / "skills").is_dir():
        return f"promote: {source} is not an agentic-partner checkout (no plugins/partner/skills)"
    if in_place:
        return write_lines(source / "plugins" / "partner", topic, entries, delta, today)
    if git(["rev-parse", "--git-dir"], source)[0] != 0:
        return f"promote: {source} is not a git checkout; use --in-place to write without a branch"
    placed = worktree_for(source, topic, worktrees, today)
    if isinstance(placed, str):
        return placed
    folder, branch = placed
    result = write_lines(folder / "plugins" / "partner", topic, entries, delta, today)
    if isinstance(result, str):
        return result
    result.worktree, result.branch = folder, branch
    if result.changed or result.created:
        for file in result.files:
            git(["add", str(file.relative_to(folder))], folder)
        message = f"docs(knowledge): {result.skill} learns {result.changed} line(s) on {topic}"
        code, out = git(["commit", "-q", "-m", message], folder)
        if code != 0:
            return f"promote: commit failed in {folder}: {out[-300:]}"
        result.commit = git(["rev-parse", "--short", "HEAD"], folder)[1]
    return result
