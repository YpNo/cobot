"""The Antigravity CLI (agy) tool and model names cobot relies on: one table, read by
scripts/sync-agents.py (the agy agents), scripts/check-plugin.py and the gate adapter, and the
translation of one agy tool call into what the gate judges (``translate``).

Facts: agy 1.5.9, re-read 2026-11-15 (docs/design-inputs/antigravity-0.3.0.md). The toolset
varies by model, so a Claude tool maps to every agy tool of both file-tool families. agy's
validator accepts an unknown tool name silently, which is why check-plugin holds AGY_TOOLS.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

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
    | {"swarm", "post_message", "read_board", "swarm_wait"}
)
MCP_RESOURCE_TOOLS = frozenset({"list_resources", "read_resource"})
AGY_TOOLS = (
    READ_TOOLS | FILE_TOOLS | ORCHESTRATION_TOOLS | MCP_RESOURCE_TOOLS | {"run_command", "call_mcp_tool"}
)

# Explicit task-matched tiers under Antigravity (never inherit by default):
# - pro (Gemini 4 Pro family): adversarial design, security auditing, primary research, language builders
# - flash (Gemini 3.8 Flash): 8-way parallel domain checklist audits and lightweight generic tasks
CLAUDE_TO_TIER: dict[str, str] = {"sonnet": "flash", "inherit": "pro", "opus": "pro", "haiku": "flash"}
DEFAULT_AGENT_TIERS: dict[str, str] = {
    "auditor": "pro",
    "builder": "flash",
    "challenger": "pro",
    "consultant": "flash",
    "go-builder": "pro",
    "learner": "pro",
    "python-builder": "pro",
    "rust-builder": "pro",
    "terraform-builder": "pro",
    "typescript-builder": "pro",
}
TIER_BY_AGENT: dict[str, str] = DEFAULT_AGENT_TIERS
SWARM_GEMINI4_MODELS: dict[str, str] = {
    "auditor": "gemini-4-carbon-high",
    "builder": "gemini-3.8-flash-high",
    "challenger": "gemini-4-carbon-high",
    "consultant": "gemini-3.8-flash-high",
    "go-builder": "gemini-4-hydrogen-high",
    "learner": "gemini-4-argon-high",
    "python-builder": "gemini-4-hydrogen-high",
    "rust-builder": "gemini-4-hydrogen-high",
    "terraform-builder": "gemini-4-hydrogen-high",
    "typescript-builder": "gemini-4-hydrogen-high",
}
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


# agy loads hooks and plugins from these roots in every folder from the workspace up to the
# repository root (docs/reference/antigravity-mechanics.md)
CUSTOMIZATION_ROOTS = (".agents", ".agent", "_agents", "_agent")


def folders_to_root(workspace: Path) -> list[Path]:
    """The workspace and its parents up to the repository root holding ``.git``; the workspace
    alone outside a repository."""
    chain = [workspace, *workspace.parents]
    for index, folder in enumerate(chain):
        if (folder / ".git").exists():
            return chain[: index + 1]
    return [workspace]


def root_aliases(path: str, workspaces: list[str]) -> list[str]:
    """``path`` as seen through each customization root that resolves elsewhere (a symlinked
    ``.agents``, cobot's foreign-mode ``.agent``): writing the real file is writing the root's."""
    real = os.path.realpath(path)
    aliases = []
    for workspace in workspaces:
        for folder in folders_to_root(Path(workspace)):
            for root in CUSTOMIZATION_ROOTS:
                link = folder / root
                target = os.path.realpath(link)
                if target != str(link) and (real == target or real.startswith(target + "/")):
                    aliases.append(str(link) + real[len(target) :])
    return aliases


# ---------------------------------------------------------------- one tool call -> what the gate judges

NO_OPINION, ASK, DENY = "no opinion", "ask", "deny"
TARGET_FILE_TOOLS = frozenset({"write_to_file", "replace_file_content", "multi_replace_file_content"})
WRITE_TOOLS = frozenset(CLAUDE_TO_AGY["Write"])
NO_OPINION_TOOLS = READ_TOOLS | {"ask_question", "send_message", "list_permissions", "ask_permission"}
NO_OPINION_TOOLS |= {"finish", "skill_search", "post_message", "read_board", "swarm_wait"}
TASK_ACTIONS = frozenset({"list", "status", "kill"})  # manage_task without input to a running task
SUBAGENT_ACTIONS = frozenset({"list", "kill", "kill_all"})
SWARM_SAFE_ACTIONS = frozenset({"status", "models", "title", "kill"})
WORKSPACE_MODES = frozenset({"inherit", "branch", "share"})
NEW_WORKSPACE_MODES = frozenset({"branch", "share"})  # a new checkout reads the committed rules
MCP_EAGER_PREFIX = "mcp_"
HASH_SHOWN = 16
WORKFLOW_READ_MAX = 1 << 20  # a script larger than this is not hashed: named, and asked


@dataclass(frozen=True)
class Plan:
    """What the gate does with one agy call: a decision by name, or Claude-shaped calls to judge
    (the strictest verdict wins). ``at_least_ask`` floors that verdict at ask;
    ``needs_committed_rules`` asks unless every workspace's .agent/cobot.rules is committed."""

    decision: str | None = None  # NO_OPINION, ASK or DENY when decided by name
    calls: tuple[tuple[str, dict], ...] = ()
    note: str = ""
    cwd: str | None = None  # the model's Cwd: expansion only, never the project
    at_least_ask: bool = False
    needs_committed_rules: bool = False


def asks(note: str) -> Plan:
    return Plan(decision=ASK, note=note)


def command_plan(name: str, args: dict) -> Plan:
    if name == "manage_task":
        action = args.get("Action")
        if action in TASK_ACTIONS:
            return Plan(decision=NO_OPINION, note=f"manage_task {action}")
        if action != "send_input" or not isinstance(args.get("Input"), str):
            return asks(f"manage_task {action!r}")
        note = "manage_task send_input: text to a running task (a REPL, a shell) always asks"
        return Plan(calls=(("Bash", {"command": args["Input"]}),), note=note, at_least_ask=True)
    command, cwd = args.get("CommandLine"), args.get("Cwd")
    if not isinstance(command, str) or not command.strip():
        return asks("run_command without CommandLine")
    if cwd is not None and not (isinstance(cwd, str) and os.path.isabs(cwd)):
        return asks(f"run_command with a relative Cwd {str(cwd)[:60]!r}")
    return Plan(calls=(("Bash", {"command": command}),), cwd=cwd)


def file_plan(name: str, args: dict) -> Plan:
    """Both file-tool families. The path is judged as written (a ``~`` rule expands to HOME as
    given), with its parent resolved and fully resolved (a symlinked folder or file): the
    strictest form wins."""
    key = "TargetFile" if name in TARGET_FILE_TOOLS else "Path"
    path = args.get(key)
    if not isinstance(path, str) or not path:
        return asks(f"{name} without {key}")
    if not os.path.isabs(path):
        return asks(f"{name} with a relative path {path[:60]!r}")
    tool = "Write" if name in WRITE_TOOLS else "Edit"
    parent = os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path))
    forms = dict.fromkeys([os.path.normpath(path), parent, os.path.realpath(path)])
    return Plan(calls=tuple((tool, {"file_path": form}) for form in forms))


def mcp_names(name: str, args: dict, servers: frozenset[str]) -> list[str] | None:
    """The Claude Code names (``mcp__<server>__<tool>``) an agy MCP call may stand for. An eager
    ``mcp_<server>_<tool>`` splits at a known server, else at every ``_``; None when unknown."""
    if name in MCP_RESOURCE_TOOLS:
        server = args.get("ServerName")
        return [f"mcp__{server}__{name}"] if isinstance(server, str) and server else None
    if name == "call_mcp_tool":
        server, tool = args.get("ServerName"), args.get("ToolName")
        ok = isinstance(server, str) and isinstance(tool, str) and server and tool
        return [f"mcp__{server}__{tool}"] if ok else None
    rest = name[len(MCP_EAGER_PREFIX) :]
    known = [s for s in servers if rest.startswith(s + "_") and len(rest) > len(s) + 1]
    if known:
        server = max(known, key=len)
        return [f"mcp__{server}__{rest[len(server) + 1 :]}"]
    cuts = [i for i, char in enumerate(rest) if char == "_" and 0 < i < len(rest) - 1]
    return [f"mcp__{rest[:i]}__{rest[i + 1 :]}" for i in cuts] or None


def swarm_plan(args: dict) -> Plan:
    """Native agy swarm control: board/status/kill pass; model switches and adds force_ask."""
    action = args.get("action")
    if action in SWARM_SAFE_ACTIONS:
        return Plan(decision=NO_OPINION, note=f"swarm {action}")
    if action == "model":
        target = str(args.get("name") or "self")[:40]
        model = str(args.get("model") or "?")[:40]
        return asks(f"swarm model: switch {target} to {model}")
    if action == "add":
        ws = args.get("workspace") or "inherit"
        if ws not in WORKSPACE_MODES:
            return asks(f"swarm add: workspace {str(ws)[:60]!r} is not a known mode")
        worker = str(args.get("name") or "<unnamed>")[:40]
        model = str(args.get("model") or "inherit")[:40]
        note = f"swarm add {worker} (model={model}, workspace={ws})"
        if ws in NEW_WORKSPACE_MODES:
            return Plan(note=note, at_least_ask=True, needs_committed_rules=True)
        return asks(note)
    return asks(f"swarm {action!r}")


def subagent_plan(args: dict) -> Plan:
    """``Workspace`` is a mode, in the flat call or in each item of ``Subagents``."""
    specs = args.get("Subagents") if "Subagents" in args else [args]
    if not isinstance(specs, list) or not specs or not all(isinstance(s, dict) for s in specs):
        return asks("invoke_subagent: unknown call shape")
    modes = {spec.get("Workspace") or "inherit" for spec in specs}
    if "Subagents" in args and args.get("Workspace"):  # a top-level mode may be the default
        modes.add(args["Workspace"])
    unknown = modes - WORKSPACE_MODES
    if unknown:
        return asks(f"invoke_subagent: Workspace {sorted(map(str, unknown))[0][:60]!r} is not a known mode")
    if modes & NEW_WORKSPACE_MODES:
        note = "invoke_subagent in a new workspace: it reads the committed .agent/cobot.rules"
        return Plan(note=note, needs_committed_rules=True)
    return Plan(decision=NO_OPINION, note="invoke_subagent in the inherited workspace")


def script_named(script_path: str) -> str:
    """The script file as the owner should see it: a relative path is the hook's folder (the
    plugin), not the workflow's, so it is named, never hashed; only a small regular file is read."""
    shown = script_path[-60:]
    if not os.path.isabs(script_path):
        return f"{shown} (a relative path)"
    try:
        if not os.path.isfile(script_path) or os.path.getsize(script_path) > WORKFLOW_READ_MAX:
            return f"{shown} (not a small regular file)"
        return f"{shown} sha256 {hashlib.sha256(Path(script_path).read_bytes()).hexdigest()[:HASH_SHOWN]}"
    except OSError as error:
        return f"{shown} unreadable ({type(error).__name__})"


def workflow_plan(args: dict) -> Plan:
    """A workflow runs Python and starts main agents whose calls are not proven gated: always ask,
    naming what would run (both forms when both are given)."""
    script_path, script = args.get("ScriptPath"), args.get("Script")
    parts = [script_named(script_path)] if isinstance(script_path, str) and script_path else []
    if isinstance(script, str):
        parts.append(f"inline script sha256 {hashlib.sha256(script.encode()).hexdigest()[:HASH_SHOWN]}")
    return asks(f"run_workflow {' and '.join(parts) or 'no script'}; workflow agents not proven gated")


def translate(name: str, args: dict, servers: frozenset[str]) -> Plan:
    """The plan for one agy tool call; anything this table does not know asks."""
    if name in NO_OPINION_TOOLS:
        return Plan(decision=NO_OPINION, note=f"{name}: read or orchestration tool")
    if name in {"run_command", "manage_task"}:
        return command_plan(name, args)
    if name in FILE_TOOLS:
        return file_plan(name, args)
    if name == "schedule":
        timed = args.get("TimerCondition")
        return (
            asks("schedule with a TimerCondition (a command)")
            if timed
            else Plan(decision=NO_OPINION, note="schedule without a TimerCondition")
        )
    if name == "manage_subagents":
        action = args.get("Action")
        return (
            Plan(decision=NO_OPINION) if action in SUBAGENT_ACTIONS else asks(f"manage_subagents {action!r}")
        )
    if name == "invoke_subagent":
        return subagent_plan(args)
    if name == "swarm":
        return swarm_plan(args)
    if name == "run_workflow":
        return workflow_plan(args)
    if name == "define_subagent":
        return Plan(decision=DENY, note="define_subagent: a child that may run without cobot")
    if name in MCP_RESOURCE_TOOLS or name == "call_mcp_tool" or name.startswith(MCP_EAGER_PREFIX):
        names = mcp_names(name, args, servers)
        return Plan(calls=tuple((n, {}) for n in names)) if names else asks(f"{name}: unknown MCP call")
    return asks(f"{name[:60]}: a tool cobot does not know")


def config_servers(path: Path, prefix: str = "") -> set[str]:
    """Server names of one MCP configuration file; none when it cannot be read (an unknown
    server is judged at every split, the strictest way)."""
    try:
        servers = json.loads(path.read_text(encoding="utf-8")).get("mcpServers") or {}
    except (OSError, ValueError, AttributeError):
        return set()
    return {f"{prefix}{name}" for name in servers} if isinstance(servers, dict) else set()


def root_servers(root: Path) -> set[str]:
    """One customization root's MCP servers: its own configuration, and each plugin's as
    ``<plugin>_<server>`` (agy 1.2.2+)."""
    servers = config_servers(root / "mcp_config.json")
    for plugin in sorted((root / "plugins").glob("*/")) if (root / "plugins").is_dir() else []:
        for file in ("mcp_config.json", "mcp.json"):
            servers |= config_servers(plugin / file, f"{plugin.name}_")
    return servers


def known_servers(home: Path, workspaces: list[str] = ()) -> frozenset[str]:
    """agy's MCP servers: ~/.gemini/config and every customization root from each workspace up to
    its repository root, so a known prefix never hides a longer server a workspace plugin adds."""
    servers = root_servers(home / ".gemini" / "config")
    for workspace in workspaces:
        for folder in folders_to_root(Path(workspace)):
            for root in CUSTOMIZATION_ROOTS:
                servers |= root_servers(folder / root)
    return frozenset(servers)
