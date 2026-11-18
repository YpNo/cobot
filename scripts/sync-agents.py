#!/usr/bin/env python3
"""Generate host-specific agents (claude-agents/<n>.md and agents/<n>.md) from canonical
host-neutral definitions in agent-defs/<n>.md (or fallback claude-agents/<n>.md in fixtures).

Edit plugins/cobot/agent-defs/<n>.md, then run:
  python3 scripts/sync-agents.py [--check] [plugin dir]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "bin"))

from _cobot_agy import AGENT_TIERS, CLAUDE_TO_AGY, CLAUDE_TO_TIER, COMMAND_TOOLS, TIER_BY_AGENT  # noqa: E402
from _cobot_agy import agent_fields as agy_fields  # noqa: E402, F401  (tests read the output)

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
NO_COMMANDS = frozenset({"consultant", "learner", "auditor"})  # their read lists cannot reach agy hooks
SKILL_READ = "under the plugin path in your brief with `read_file` (or `view_file`)"
NO_COMMANDS_LINE = (
    "Under Antigravity you have no command tool: read files and pages only, and say in your report "
    "what a command would have settled.\n\n"
)
REWRITES = (
    (
        re.compile(r"call it with the Skill tool(?: \([^)]*\))?"),
        f"read its `skills/<name>/SKILL.md` {SKILL_READ}",
    ),
    (
        re.compile(r"a report without this shape is sent back by the hook\."),
        "no hook checks this shape under Antigravity: the orchestrator does.",
    ),
)


def claude_fields(text: str) -> dict[str, str]:
    """The one-line ``key: value`` fields of an agent definition."""
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError("no frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def agy_tools(name: str, claude_tools: str) -> list[str]:
    tools: list[str] = []
    for tool in (t.strip() for t in claude_tools.split(",") if t.strip()):
        if tool not in CLAUDE_TO_AGY:
            raise ValueError(f"{name}: no agy tool for Claude tool {tool}")
        tools.extend(t for t in CLAUDE_TO_AGY[tool] if t not in tools)
    return [t for t in tools if not (name in NO_COMMANDS and t in COMMAND_TOOLS)]


def agy_tier(name: str, fields: dict[str, str]) -> str:
    explicit = fields.get("agy_model")
    if explicit:
        if explicit not in AGENT_TIERS:
            raise ValueError(f"{name}: invalid agy_model {explicit!r}")
        return explicit
    model = fields.get("model", fields.get("claude_model", "inherit"))
    if model not in CLAUDE_TO_TIER:
        raise ValueError(f"{name}: no agy tier for model {model}")
    return TIER_BY_AGENT.get(name, CLAUDE_TO_TIER[model])


def preloaded(fields: dict[str, str]) -> list[str]:
    return [s.strip() for s in fields.get("skills", "").strip("[]").split(",") if s.strip()]


def agy_body(name: str, body: str, skills: list[str], source_dir: str) -> str:
    for pattern, replacement in REWRITES:
        body = pattern.sub(replacement, body)
    preload = "Under Antigravity no skill is preloaded: before you write code, read"
    reads = "".join(f"{preload} `skills/{s}/SKILL.md` {SKILL_READ}.\n\n" for s in skills)
    if name in NO_COMMANDS:
        reads = NO_COMMANDS_LINE + reads
    header = f"<!-- generated from {source_dir}/{name}.md by scripts/sync-agents.py; edit that file -->\n\n"
    return header + reads + body.lstrip("\n")


def render(text: str, name: str, source_dir: str = "claude-agents") -> str:
    """Render the Antigravity agent (agents/<n>.md) from canonical or Claude source."""
    fields = claude_fields(text)
    lines = [
        "---",
        f"name: {fields['name']}",
        f"description: {json.dumps(fields['description'], ensure_ascii=False)}",
        "tools:",
        *(f"  - {t}" for t in agy_tools(name, fields.get("tools", ""))),
        f"model: {agy_tier(name, fields)}",
        "mainAgent: false",
    ]
    if name in NO_COMMANDS:
        lines.append('commandExecutionPolicy: "off"')
    body = FRONTMATTER.sub("", text, count=1)
    return "\n".join(lines) + "\n---\n" + agy_body(name, body, preloaded(fields), source_dir)


def render_claude(text: str) -> str:
    """Render the Claude Code agent (claude-agents/<n>.md) from canonical agent-defs/<n>.md."""
    fields = claude_fields(text)
    lines = [
        "---",
        f"name: {fields['name']}",
        f"description: {fields['description']}",
        f"tools: {fields['tools']}",
        f"model: {fields.get('claude_model', fields.get('model', 'inherit'))}",
    ]
    if effort := fields.get("claude_effort", fields.get("effort")):
        lines.append(f"effort: {effort}")
    if skills := fields.get("skills"):
        lines.append(f"skills: {skills}")
    if fields.get("omit_instructions") == "true" or fields.get("omitClaudeMd") == "true":
        lines.append("omitClaudeMd: true")
    if color := fields.get("color"):
        lines.append(f"color: {color}")
    body = FRONTMATTER.sub("", text, count=1).lstrip("\n")
    return "\n".join(lines) + "\n---\n\n" + body


def reconcile_dir(target: Path, wanted: dict[str, str], check: bool) -> set[str]:
    current = {p.stem: p.read_text(encoding="utf-8") for p in target.glob("*.md")} if target.is_dir() else {}
    stale = {n for n in wanted.keys() | current.keys() if wanted.get(n) != current.get(n)}
    if not check and stale:
        target.mkdir(exist_ok=True)
        for name in sorted(stale):
            if name in wanted:
                (target / f"{name}.md").write_text(wanted[name], encoding="utf-8")
            else:
                (target / f"{name}.md").unlink()
    return stale


def sync(plugin: Path, check: bool) -> list[str]:
    """Names whose generated host agents are stale or orphaned; written unless ``check``."""
    defs_dir = plugin / "agent-defs"
    if defs_dir.is_dir():
        defs = {p.stem: p.read_text(encoding="utf-8") for p in defs_dir.glob("*.md")}
        wanted_claude = {name: render_claude(text) for name, text in defs.items()}
        wanted_agy = {name: render(text, name, source_dir="agent-defs") for name, text in defs.items()}
        stale = reconcile_dir(plugin / "claude-agents", wanted_claude, check)
        stale |= reconcile_dir(plugin / "agents", wanted_agy, check)
        return sorted(stale)

    wanted = {
        p.stem: render(p.read_text(encoding="utf-8"), p.stem) for p in (plugin / "claude-agents").glob("*.md")
    }
    return sorted(reconcile_dir(plugin / "agents", wanted, check))


def main(argv: list[str]) -> int:
    check = "--check" in argv
    rest = [a for a in argv if a != "--check"]
    plugin = Path(rest[0]) if rest else Path(__file__).resolve().parents[1] / "plugins" / "cobot"
    stale = sync(plugin, check)
    if check and stale:
        print(f"agents/ is out of date for {', '.join(stale)}: run `python3 scripts/sync-agents.py`")
        return 1
    print(("written: " if stale and not check else "in sync: ") + (", ".join(stale) or "all"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
