#!/usr/bin/env python3
"""Plugin contract check (CI): SKILL.md sizes, description lengths, agent listing budget, protocol size,
knowledge lines.

Usage: python3 scripts/check-plugin.py [plugin dir]   exit 1 on any violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_MAX_LINES = 500
DESCRIPTION_MAX = 1536
SKILL_DESCRIPTIONS_TOTAL_MAX = 15000  # every model-visible skill sits in the system prompt of every turn
# knowledge skills: plugin skills are always listed and paths: does not gate them
KNOWLEDGE_DESCRIPTION_MAX = 350
AGENT_BUDGET_TOKENS = 600
PROTOCOL_MAX_CHARS = 3000  # protocol.md is injected into every session (docs/02-design.md)
KNOWLEDGE_PREFIXES = ("lang-", "expert-", "fw-")  # the prefixes _cobot_knowledge tracks for staleness
KNOWLEDGE_LINE = re.compile(r"- \[(verified|reported|assumed) \d{4}-\d{2}-\d{2} · src: ")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def frontmatter(text: str) -> dict[str, str]:
    """Top-level keys; a folded or literal block (``>-``, ``|``) is joined into its key's value."""
    match = FRONTMATTER.match(text)
    fields: dict[str, str] = {}
    key = ""
    if match:
        for line in match.group(1).splitlines():
            if line.startswith(" ") and key:
                fields[key] = (fields[key] + " " + line.strip()).strip()
            elif ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                key = key.strip()
                fields[key] = "" if value.strip() in (">-", ">", "|", "|-") else value.strip()
    return fields


def listed(fields: dict[str, str]) -> int:
    """Characters a skill adds to the model's listing: description plus when_to_use, or nothing
    for a user-only skill (Claude Code drops disable-model-invocation skills from the listing)."""
    if fields.get("disable-model-invocation") == "true":
        return 0
    return len(fields.get("description", "")) + len(fields.get("when_to_use", ""))


def listing_chars(plugin: Path) -> int:
    return sum(
        listed(frontmatter(s.read_text(encoding="utf-8"))) for s in (plugin / "skills").glob("*/SKILL.md")
    )


def check(plugin: Path) -> list[str]:
    problems: list[str] = []
    skill_chars = listing_chars(plugin)
    consult = plugin / "skills" / "consult"
    for procedure in sorted(consult.rglob("*.md")) if consult.is_dir() else []:
        if KNOWLEDGE_LINE.search(procedure.read_text(encoding="utf-8")):
            problems.append(
                f"{procedure}: dated knowledge line in a consult procedure (it belongs in the expert)"
            )
    for skill in sorted((plugin / "skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        fields = frontmatter(text)
        count = len(text.splitlines())
        if count >= SKILL_MAX_LINES:
            problems.append(f"{skill}: {count} lines (max {SKILL_MAX_LINES - 1})")
        if not fields.get("name") or not fields.get("description"):
            problems.append(f"{skill}: frontmatter needs name and description")
        if len(fields.get("description", "")) > DESCRIPTION_MAX:
            problems.append(
                f"{skill}: description {len(fields['description'])} chars (max {DESCRIPTION_MAX})"
            )
        if skill.parent.name.startswith(KNOWLEDGE_PREFIXES):
            length = len(fields.get("description", ""))
            if length > KNOWLEDGE_DESCRIPTION_MAX:
                problems.append(f"{skill}: description {length} chars (max {KNOWLEDGE_DESCRIPTION_MAX})")
            if "paths" not in text.split("---")[1]:
                problems.append(f"{skill}: knowledge skill without paths:")
            refs = list(skill.parent.glob("references/*.md"))
            if refs and not any(KNOWLEDGE_LINE.search(r.read_text(encoding="utf-8")) for r in refs):
                problems.append(f"{skill.parent}: references without a dated knowledge line")
    total_chars = 0
    if skill_chars > SKILL_DESCRIPTIONS_TOTAL_MAX:
        problems.append(f"skill descriptions total {skill_chars} chars (max {SKILL_DESCRIPTIONS_TOTAL_MAX})")
    for agent in sorted((plugin / "agents").glob("*.md")):
        fields = frontmatter(agent.read_text(encoding="utf-8"))
        if not fields.get("name") or not fields.get("description"):
            problems.append(f"{agent}: frontmatter needs name and description")
        total_chars += len(fields.get("name", "")) + len(fields.get("description", ""))
    tokens = total_chars // 4
    if tokens > AGENT_BUDGET_TOKENS:
        problems.append(f"agents: listing ≈ {tokens} tokens (budget {AGENT_BUDGET_TOKENS})")
    protocol = plugin / "protocol.md"
    protocol_chars = len(protocol.read_text(encoding="utf-8")) if protocol.is_file() else 0
    if not protocol.is_file():
        problems.append("protocol.md: missing")
    elif protocol_chars > PROTOCOL_MAX_CHARS:
        problems.append(f"protocol.md: {protocol_chars} chars (max {PROTOCOL_MAX_CHARS})")
    skills = list((plugin / "skills").glob("*/SKILL.md"))
    print(
        f"agents listing ≈ {tokens} tokens; skills: {len(skills)}, listed {skill_chars} chars; "
        f"protocol {protocol_chars} chars"
    )
    return problems


def main(argv: list[str]) -> int:
    plugin = Path(argv[0]) if argv else Path("plugins/cobot")
    problems = check(plugin)
    for problem in problems:
        print(f"FAIL {problem}")
    print("plugin contract: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
