"""The Antigravity CLI (agy) tool and model names cobot relies on: one table, read by
scripts/sync-agents.py (the agy agents), scripts/check-plugin.py and the gate adapter.

Facts: agy 1.5.9, re-read 2026-11-15 (docs/design-inputs/antigravity-0.3.0.md). The toolset
varies by model, so a Claude tool maps to every agy tool of both file-tool families. agy's
validator accepts an unknown tool name silently, which is why check-plugin holds AGY_TOOLS.
"""

from __future__ import annotations

import json
import re

# Claude Code tool -> agy tools. Skill and Agent have no agy tool: an agy agent reads a skill
# file with view_file, and only the orchestrator delegates.
CLAUDE_TO_AGY: dict[str, tuple[str, ...]] = {
    "Read": ("view_file", "read_file"),
    "Edit": ("replace_file_content", "multi_replace_file_content", "edit_file"),
    "Write": ("write_to_file", "write_file"),
    "Bash": ("run_command", "manage_task"),  # manage_task polls an async command
    "Grep": ("grep_search",),
    "Glob": ("find_by_name", "list_dir"),
    "WebFetch": ("read_url_content",),
    "WebSearch": ("search_web",),
    "Skill": (),
    "Agent": (),
}
COMMAND_TOOLS = frozenset(CLAUDE_TO_AGY["Bash"])

READ_TOOLS = frozenset(
    {"view_file", "read_file", "list_dir", "find_by_name", "grep_search", "read_url_content", "search_web"}
    | {"view_code_item"}
)
FILE_TOOLS = frozenset(CLAUDE_TO_AGY["Edit"] + CLAUDE_TO_AGY["Write"])
ORCHESTRATION_TOOLS = frozenset(
    {"ask_question", "send_message", "list_permissions", "ask_permission", "finish", "skill_search"}
    | {"schedule", "manage_task", "manage_subagents", "invoke_subagent", "define_subagent", "run_workflow"}
)
AGY_TOOLS = READ_TOOLS | FILE_TOOLS | ORCHESTRATION_TOOLS | {"run_command", "call_mcp_tool"}

# Claude model -> agy tier. agy accepts only tiers (a model name skips the agent) and ignores
# effort, so an agent that relies on effort gets a stronger tier by name.
CLAUDE_TO_TIER: dict[str, str] = {"sonnet": "flash", "inherit": "inherit"}
TIER_BY_AGENT: dict[str, str] = {"learner": "pro"}  # effort: high under Claude Code
AGENT_TIERS = frozenset({"inherit", "flash", "pro"})  # flash_lite exists; cobot uses none of it

AGENT_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def agent_fields(text: str) -> dict[str, str | list[str]]:
    """An agy agent's frontmatter as written by sync-agents: one-line values (a double-quoted one
    is JSON) and block lists (``key:`` then ``  - item`` lines)."""
    match = AGENT_FRONTMATTER.match(text)
    fields: dict[str, str | list[str]] = {}
    key = ""
    for line in match.group(1).splitlines() if match else []:
        items = fields.get(key)
        if line.startswith("  - ") and isinstance(items, list):
            items.append(line[4:].strip())
            continue
        key, _, value = (part.strip() for part in line.partition(":"))
        fields[key] = [] if not value else json.loads(value) if value.startswith('"') else value
    return fields
