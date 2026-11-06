#!/usr/bin/env python3
"""Plugin contract check (CI): SKILL.md sizes, description lengths, agent listing budget, knowledge lines.

Usage: python3 scripts/check-plugin.py [plugin dir]   exit 1 on any violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_MAX_LINES = 500
DESCRIPTION_MAX = 1536
AGENT_BUDGET_TOKENS = 600
KNOWLEDGE_LINE = re.compile(r"- \[(verified|reported|assumed) \d{4}-\d{2}-\d{2} · src: ")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    fields: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip()
    return fields


def check(plugin: Path) -> list[str]:
    problems: list[str] = []
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
        if skill.parent.name.startswith(("lang-", "expert-")):
            if "paths" not in text.split("---")[1]:
                problems.append(f"{skill}: knowledge skill without paths:")
            refs = list(skill.parent.glob("references/*.md"))
            if refs and not any(KNOWLEDGE_LINE.search(r.read_text(encoding="utf-8")) for r in refs):
                problems.append(f"{skill.parent}: references without a dated knowledge line")
    total_chars = 0
    for agent in sorted((plugin / "agents").glob("*.md")):
        fields = frontmatter(agent.read_text(encoding="utf-8"))
        if not fields.get("name") or not fields.get("description"):
            problems.append(f"{agent}: frontmatter needs name and description")
        total_chars += len(fields.get("name", "")) + len(fields.get("description", ""))
    tokens = total_chars // 4
    if tokens > AGENT_BUDGET_TOKENS:
        problems.append(f"agents: listing ≈ {tokens} tokens (budget {AGENT_BUDGET_TOKENS})")
    print(f"agents listing ≈ {tokens} tokens; skills: {len(list((plugin / 'skills').glob('*/SKILL.md')))}")
    return problems


def main(argv: list[str]) -> int:
    plugin = Path(argv[0]) if argv else Path("plugins/partner")
    problems = check(plugin)
    for problem in problems:
        print(f"FAIL {problem}")
    print("plugin contract: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
