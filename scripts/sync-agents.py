#!/usr/bin/env python3
"""Write the Antigravity agents (agents/<n>.md) from the Claude Code agents (claude-agents/<n>.md).

The body is copied; the frontmatter is agy's (tools as a YAML list, a model tier, not a main
agent); a few body lines that name Claude-only mechanisms are rewritten. Edit claude-agents/,
then run this script.

Usage: python3 scripts/sync-agents.py [--check] [plugin dir]
  --check   write nothing; exit 1 and name the stale agents when agents/ differs
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "bin"))

from _cobot_agy import CLAUDE_TO_AGY, CLAUDE_TO_TIER, COMMAND_TOOLS, TIER_BY_AGENT  # noqa: E402
from _cobot_agy import agent_fields as agy_fields  # noqa: E402, F401  (tests read the output)

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
NO_COMMANDS = frozenset({"consultant", "learner", "auditor"})  # their read lists cannot reach agy hooks
SKILL_READ = "under the plugin path in your brief with `view_file`"
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
    """The one-line ``key: value`` fields of a Claude Code agent."""
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


def agy_tier(name: str, model: str) -> str:
    if model not in CLAUDE_TO_TIER:
        raise ValueError(f"{name}: no agy tier for model {model}")
    return TIER_BY_AGENT.get(name, CLAUDE_TO_TIER[model])


def preloaded(fields: dict[str, str]) -> list[str]:
    return [s.strip() for s in fields.get("skills", "").strip("[]").split(",") if s.strip()]


def agy_body(name: str, body: str, skills: list[str]) -> str:
    for pattern, replacement in REWRITES:
        body = pattern.sub(replacement, body)
    preload = "Under Antigravity no skill is preloaded: before you write code, read"
    reads = "".join(f"{preload} `skills/{s}/SKILL.md` {SKILL_READ}.\n\n" for s in skills)
    if name in NO_COMMANDS:
        reads = NO_COMMANDS_LINE + reads
    header = f"<!-- generated from claude-agents/{name}.md by scripts/sync-agents.py; edit that file -->\n\n"
    return header + reads + body.lstrip("\n")


def render(text: str, name: str) -> str:
    """The agy agent for one Claude Code agent's text."""
    fields = claude_fields(text)
    lines = [
        "---",
        f"name: {fields['name']}",
        f"description: {json.dumps(fields['description'], ensure_ascii=False)}",
    ]
    lines += ["tools:", *(f"  - {t}" for t in agy_tools(name, fields.get("tools", "")))]
    lines += [f"model: {agy_tier(name, fields.get('model', 'inherit'))}", "mainAgent: false"]
    if name in NO_COMMANDS:
        lines.append('commandExecutionPolicy: "off"')
    body = FRONTMATTER.sub("", text, count=1)
    return "\n".join(lines) + "\n---\n" + agy_body(name, body, preloaded(fields))


def sync(plugin: Path, check: bool) -> list[str]:
    """Names whose agy agent is stale or orphaned; written unless ``check``."""
    target = plugin / "agents"
    wanted = {
        p.stem: render(p.read_text(encoding="utf-8"), p.stem) for p in (plugin / "claude-agents").glob("*.md")
    }
    current = {p.stem: p.read_text(encoding="utf-8") for p in target.glob("*.md")} if target.is_dir() else {}
    stale = sorted(n for n in wanted.keys() | current.keys() if wanted.get(n) != current.get(n))
    if not check:
        target.mkdir(exist_ok=True)
        for name in stale:
            if name in wanted:
                (target / f"{name}.md").write_text(wanted[name], encoding="utf-8")
            else:
                (target / f"{name}.md").unlink()
    return stale


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
