"""Token usage per session, model and agent type from the local Claude Code transcripts (design §10).

The transcript row format is documented as internal and changeable: only `assistant` rows with a
`message.usage` object are read, one per request (`requestId`, else `message.id`), and the rows
skipped are counted. Subagent transcripts live under `<session>/subagents/agent-<id>.jsonl` with
their type in the sibling `agent-<id>.meta.json`. Message text is never read.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
ORCHESTRATOR = "orchestrator"
MAX_LINES = 40


def projects_root() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude"
    return Path(base) / "projects"


def project_slug(repo_root: Path) -> str:
    """Claude Code's folder name for a working directory: every non-alphanumeric character becomes '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(repo_root))


def project_folders(repo_root: Path) -> list[Path]:
    """The project folder and its worktree folders (`<slug>--claude-worktrees-*`)."""
    slug = project_slug(repo_root)
    root = projects_root()
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.iterdir() if p.is_dir() and (p.name == slug or p.name.startswith(slug + "--"))
    )


@dataclass
class Totals:
    requests: int = 0
    tokens: Counter = field(default_factory=Counter)

    def add(self, usage: dict) -> None:
        self.requests += 1
        for key in USAGE_KEYS:
            value = usage.get(key)
            if isinstance(value, int):
                self.tokens[key] += value


@dataclass
class Report:
    folders: list[str] = field(default_factory=list)
    sessions: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    models: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    agents: dict[str, Totals] = field(default_factory=lambda: defaultdict(Totals))
    calls: Counter = field(default_factory=Counter)  # "Skill:<name>" / "Agent:<type>"
    first: str = ""
    last: str = ""
    skipped: int = 0

    def as_dict(self) -> dict:
        def totals(table: dict[str, Totals]) -> dict:
            return {k: {"requests": v.requests, **v.tokens} for k, v in sorted(table.items())}

        return {
            "folders": self.folders,
            "from": self.first,
            "to": self.last,
            "sessions": totals(self.sessions),
            "models": totals(self.models),
            "agents": totals(self.agents),
            "calls": dict(sorted(self.calls.items())),
            "skipped_rows": self.skipped,
        }


def agent_type_of(transcript: Path) -> str:
    meta = transcript.with_suffix(".meta.json")
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        return str(data.get("agentType") or "subagent")
    except (OSError, ValueError):
        return "subagent"


def note_calls(report: Report, message: dict) -> None:
    content = message.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        name, inputs = block.get("name"), block.get("input") or {}
        if name == "Skill" and isinstance(inputs, dict):
            report.calls[f"Skill:{inputs.get('skill', '?')}"] += 1
        elif name == "Agent" and isinstance(inputs, dict):
            report.calls[f"Agent:{inputs.get('subagent_type', 'general-purpose')}"] += 1


def read_transcript(path: Path, report: Report, session: str, agent: str, since: str, seen: set[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            report.skipped += 1
            continue
        if not isinstance(row, dict) or row.get("type") != "assistant":
            continue
        message = row.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("usage"), dict):
            report.skipped += 1
            continue
        stamp = str(row.get("timestamp") or "")
        if since and stamp[:10] < since:
            continue
        if agent == ORCHESTRATOR:
            note_calls(report, message)
        key = str(row.get("requestId") or message.get("id") or "")
        if key and key in seen:
            continue  # a request streams several rows carrying the same usage
        seen.add(key)
        usage = message["usage"]
        for table, name in (
            (report.sessions, session),
            (report.models, str(message.get("model") or "?")),
            (report.agents, agent),
        ):
            table[name].add(usage)
        if stamp:
            report.first = min(report.first or stamp, stamp)
            report.last = max(report.last, stamp)


def collect(repo_root: Path, since: str = "", session_filter: str = "") -> Report:
    report = Report()
    for folder in project_folders(repo_root):
        report.folders.append(folder.name)
        for transcript in sorted(folder.glob("*.jsonl")):
            session = transcript.stem
            if session_filter and not session.startswith(session_filter):
                continue
            seen: set[str] = set()
            read_transcript(transcript, report, session, ORCHESTRATOR, since, seen)
            for sub in sorted((folder / session / "subagents").glob("agent-*.jsonl")):
                read_transcript(sub, report, session, agent_type_of(sub), since, seen)
    return report


def fmt(n: int) -> str:
    return f"{n / 1000:.0f}k" if n >= 10_000 else str(n)


def row(name: str, t: Totals) -> str:
    k = t.tokens
    head = f"  {name[:34]:<34} {t.requests:>5}  in {fmt(k['input_tokens']):>6}"
    created, read = fmt(k["cache_creation_input_tokens"]), fmt(k["cache_read_input_tokens"])
    cache = f"  cache+ {created:>6}  cache= {read:>7}"
    return f"{head}{cache}  out {fmt(k['output_tokens']):>6}"


def render(report: Report) -> str:
    if not report.folders:
        return "cobot-usage: no transcripts for this repository under " + str(projects_root())
    lines = [f"cobot-usage: {', '.join(report.folders)} · {report.first[:10]} → {report.last[:10]}"]
    lines.append(f"{'':2}{'per session':<34} {'reqs':>5}")
    lines += [
        row(name, t)
        for name, t in sorted(report.sessions.items(), key=lambda kv: -kv[1].tokens["output_tokens"])
    ]
    lines.append("  per model")
    lines += [row(name, t) for name, t in sorted(report.models.items())]
    lines.append("  per agent type")
    lines += [row(name, t) for name, t in sorted(report.agents.items(), key=lambda kv: -kv[1].requests)]
    if report.calls:
        calls = ", ".join(f"{k} ×{v}" for k, v in sorted(report.calls.items(), key=lambda kv: -kv[1])[:12])
        lines.append(f"  calls: {calls}")
    if report.skipped:
        lines.append(f"  skipped rows: {report.skipped} (format drift or non-usage rows)")
    if len(lines) > MAX_LINES:
        lines = lines[: MAX_LINES - 1] + [f"  … {len(lines) - MAX_LINES + 1} more lines; use --json"]
    return "\n".join(lines)
