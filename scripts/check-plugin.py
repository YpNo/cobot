#!/usr/bin/env python3
"""Plugin contract check (CI): SKILL.md sizes, description lengths, agent listing budget, protocol size,
knowledge lines, the two manifests, strict YAML frontmatter, the Antigravity agents.

Usage: python3 scripts/check-plugin.py [plugin dir]   exit 1 on any violation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "cobot" / "bin"))

from _cobot_agy import AGENT_TIERS, AGY_TOOLS, agent_fields  # noqa: E402

SKILL_MAX_LINES = 500
SKILL_BODY_MAX_BYTES = 24_000  # agy skips a SKILL.md whose body is larger
DESCRIPTION_MAX = 1536
SKILL_DESCRIPTIONS_TOTAL_MAX = 15000  # every model-visible skill sits in the system prompt of every turn
# knowledge skills: plugin skills are always listed and paths: does not gate them
KNOWLEDGE_DESCRIPTION_MAX = 350
AGENT_BUDGET_TOKENS = 600
PROTOCOL_MAX_CHARS = 3000  # protocol.md is injected into every session (docs/02-design.md)
KNOWLEDGE_PREFIXES = ("lang-", "expert-", "fw-")  # the prefixes _cobot_knowledge tracks for staleness
KNOWLEDGE_LINE = re.compile(r"- \[(verified|reported|assumed) \d{4}-\d{2}-\d{2} · src: ")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
# an Agent call that omits the flag may start in the background, and the skill reports before the
# agent; the desktop app has no such flag, so the skill also waits (F-35, spec builder-proof-hosts)
FOREGROUND = ("`run_in_background: false` where the host offers it", "wait for every hand-back")
CLAUDE_MANIFEST = ".claude-plugin/plugin.json"
AGY_MANIFEST = ".antigravity-plugin/plugin.json"  # agy reads it first and ignores .claude-plugin/
MANIFEST_AGREE = ("name", "version", "description", "license", "repository")
CLAUDE_AGENTS = "claude-agents"  # Claude Code's agents, listed by file; agents/ holds agy's
AGY_AGENTS = "agents"
AGENT_DEFS = "agent-defs"
# strict YAML (agy parses frontmatter with a strict parser; Claude Code tolerates more)
KEY_LINE = re.compile(r"([A-Za-z0-9_-]+):(?: (.*))?")
BLOCK_SCALAR = re.compile(r"[|>][+-]?")
PLAIN_FORBIDDEN = re.compile(r": |:$| #")  # a mapping inside a plain value, or a comment cutting it
RESERVED_START = tuple("@`%&*!")


def frontmatter_text(path: Path) -> str:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    return match.group(1) + "\n" if match else ""


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


def flow_closes_at_end(value: str) -> bool:
    """A flow collection (``[a, b]``) is the whole value: its first bracket closes on the last char."""
    depth = 0
    for index, char in enumerate(value):
        depth += (char in "[{") - (char in "]}")
        if depth == 0:
            return index == len(value) - 1
    return False


def scalar_problem(value: str) -> str | None:
    """Why a one-line value is not strict YAML, or None."""
    if not value or BLOCK_SCALAR.fullmatch(value):
        return None
    if value[0] in "\"'":
        return None if len(value) > 1 and value.endswith(value[0]) else "an unclosed quote"
    if value[0] in "[{":
        return None if flow_closes_at_end(value) else "a flow collection that is not the whole value"
    if value.startswith(RESERVED_START):
        return f"a plain value starting with {value[0]!r}"
    if PLAIN_FORBIDDEN.search(value):
        return "': ', a trailing ':' or ' #' inside a plain value"
    return None


def line_problem(line: str, mode: str) -> tuple[str | None, str]:
    """One frontmatter line in the current mode (block, plain, nested) -> (problem, next mode)."""
    stripped = line.strip()
    indented = line.startswith(" ")
    if indented and mode == "block":
        return None, mode
    if indented and mode == "plain":
        return ("': ' or ' #' in a continued value" if PLAIN_FORBIDDEN.search(stripped) else None), mode
    if indented and stripped.startswith("- "):
        return scalar_problem(stripped[2:].strip()), mode
    match = KEY_LINE.fullmatch(stripped if indented else line)
    if not match:
        return "not a `key: value` line", mode
    value = (match.group(2) or "").strip()
    next_mode = "nested" if not value else "block" if BLOCK_SCALAR.fullmatch(value) else "plain"
    return scalar_problem(value), mode if indented else next_mode


def yaml_problems(text: str) -> list[str]:
    """The strict-YAML subset cobot's frontmatter uses: ``key: value`` lines, block scalars, lists."""
    problems: list[str] = []
    mode = "nested"
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        problem, mode = line_problem(line, mode)
        if problem:
            problems.append(f"line {number}: {problem} (quote it or fold it with >-)")
    return problems


def strict_yaml(path: Path) -> list[str]:
    return [f"{path}: frontmatter is not strict YAML, {p}" for p in yaml_problems(frontmatter_text(path))]


def load_manifest(plugin: Path, rel: str) -> tuple[dict | None, str | None]:
    path = plugin / rel
    if not path.is_file():
        return None, f"{rel}: missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as error:
        return None, f"{rel}: not JSON ({error})"


def manifest_problems(plugin: Path) -> list[str]:
    """Both manifests exist and agree on the fields a release reads."""
    claude, claude_problem = load_manifest(plugin, CLAUDE_MANIFEST)
    agy, agy_problem = load_manifest(plugin, AGY_MANIFEST)
    problems = [p for p in (claude_problem, agy_problem) if p]
    if claude is not None and agy is not None:
        for key in MANIFEST_AGREE:
            if claude.get(key) is None or claude.get(key) != agy.get(key):
                problems.append(f"manifests disagree on {key}: {claude.get(key)!r} vs {agy.get(key)!r}")
    return problems


def listed_agents(plugin: Path) -> list[str]:
    """The ``agents`` list of the Claude Code manifest (empty when it cannot be read)."""
    claude, _ = load_manifest(plugin, CLAUDE_MANIFEST)
    agents = (claude or {}).get("agents", [])
    return agents if isinstance(agents, list) else []


def claude_agents(plugin: Path) -> list[Path]:
    """The agents Claude Code loads: the manifest's list, files that exist."""
    return [plugin / rel for rel in listed_agents(plugin) if (plugin / rel).is_file()]


def agent_list_problems(plugin: Path) -> list[str]:
    """The manifest lists exactly the files in claude-agents/ (the list replaces the folder scan)."""
    listed = listed_agents(plugin)
    if not listed:
        return [f"{CLAUDE_MANIFEST}: no `agents` list"]
    missing = [rel for rel in listed if not (plugin / rel).is_file()]
    problems = [f"{rel}: listed in {CLAUDE_MANIFEST}, no such file" for rel in missing]
    for file in sorted((plugin / CLAUDE_AGENTS).glob("*.md")):
        if f"./{CLAUDE_AGENTS}/{file.name}" not in listed:
            problems.append(f"{file}: not in the manifest's agents list")
    return problems


def twin_problems(plugin: Path) -> list[str]:
    """Every Claude Code agent has its agy twin and canonical agent-def when agent-defs/ is present."""
    claude = {p.stem for p in (plugin / CLAUDE_AGENTS).glob("*.md")}
    agy = {p.stem for p in (plugin / AGY_AGENTS).glob("*.md")}
    problems = [
        f"{plugin / CLAUDE_AGENTS / name}.md: no {AGY_AGENTS}/{name}.md (python3 scripts/sync-agents.py)"
        for name in sorted(claude - agy)
    ]
    problems += [
        f"{plugin / AGY_AGENTS / name}.md: no {CLAUDE_AGENTS}/{name}.md" for name in sorted(agy - claude)
    ]
    defs_dir = plugin / AGENT_DEFS
    if defs_dir.is_dir():
        defs = {p.stem for p in defs_dir.glob("*.md")}
        for def_file in sorted(defs_dir.glob("*.md")):
            problems.extend(strict_yaml(def_file))
        for name in sorted((claude | agy) - defs):
            problems.append(f"{defs_dir / name}.md: missing canonical definition")
        for name in sorted(defs - (claude & agy)):
            problems.append(f"{defs_dir / name}.md: out of sync (python3 scripts/sync-agents.py)")
    return problems


def agy_agent_problems(agent: Path) -> list[str]:
    """agy skips an agent whose tools are a string or whose model is not a tier, and accepts an
    unknown tool name silently: hold all three, and keep it a subagent."""
    fields = agent_fields(agent.read_text(encoding="utf-8"))
    problems = strict_yaml(agent)
    if fields.get("name") != agent.stem:
        problems.append(f"{agent}: name {fields.get('name')!r} is not the file name")
    tools = fields.get("tools")
    if not isinstance(tools, list) or not tools:
        problems.append(f"{agent}: tools must be a YAML list")
    else:
        problems += [f"{agent}: unknown agy tool {tool}" for tool in tools if tool not in AGY_TOOLS]
    if fields.get("model") not in AGENT_TIERS:
        problems.append(
            f"{agent}: model {fields.get('model')!r} is not one of {', '.join(sorted(AGENT_TIERS))}"
        )
    if fields.get("mainAgent") != "false":
        problems.append(f"{agent}: needs mainAgent: false (a subagent, never the session's agent)")
    return problems


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


def background_spawns(plugin: Path) -> list[str]:
    """Skills whose body names one of the plugin's agents (``cobot:<agent>``) without both FOREGROUND
    strings. A text check: it cannot see a negation, a limit the spec accepts."""
    names = [a.stem for a in claude_agents(plugin)]
    if not names:
        return []
    named = re.compile(r"cobot:(" + "|".join(map(re.escape, names)) + r")\b")
    problems = []
    for skill in sorted((plugin / "skills").glob("*/SKILL.md")):
        body = FRONTMATTER.sub("", skill.read_text(encoding="utf-8"), count=1)
        if named.search(body):
            missing = [rule for rule in FOREGROUND if rule not in body]
            problems += [f'{skill}: names an agent to run but not "{rule}"' for rule in missing]
    return problems


def consult_problems(plugin: Path) -> list[str]:
    consult = plugin / "skills" / "consult"
    return [
        f"{procedure}: dated knowledge line in a consult procedure (it belongs in the expert)"
        for procedure in (sorted(consult.rglob("*.md")) if consult.is_dir() else [])
        if KNOWLEDGE_LINE.search(procedure.read_text(encoding="utf-8"))
    ]


def knowledge_problems(skill: Path, text: str, fields: dict[str, str]) -> list[str]:
    problems = []
    length = len(fields.get("description", ""))
    if length > KNOWLEDGE_DESCRIPTION_MAX:
        problems.append(f"{skill}: description {length} chars (max {KNOWLEDGE_DESCRIPTION_MAX})")
    if "paths" not in text.split("---")[1]:
        problems.append(f"{skill}: knowledge skill without paths:")
    refs = list(skill.parent.glob("references/*.md"))
    if refs and not any(KNOWLEDGE_LINE.search(r.read_text(encoding="utf-8")) for r in refs):
        problems.append(f"{skill.parent}: references without a dated knowledge line")
    return problems


def skill_problems(skill: Path) -> list[str]:
    text = skill.read_text(encoding="utf-8")
    fields = frontmatter(text)
    problems = strict_yaml(skill)
    count = len(text.splitlines())
    if count >= SKILL_MAX_LINES:
        problems.append(f"{skill}: {count} lines (max {SKILL_MAX_LINES - 1})")
    body_bytes = len(FRONTMATTER.sub("", text, count=1).encode("utf-8"))
    if body_bytes > SKILL_BODY_MAX_BYTES:
        problems.append(f"{skill}: body {body_bytes} bytes (max {SKILL_BODY_MAX_BYTES})")
    if not fields.get("name") or not fields.get("description"):
        problems.append(f"{skill}: frontmatter needs name and description")
    if len(fields.get("description", "")) > DESCRIPTION_MAX:
        problems.append(f"{skill}: description {len(fields['description'])} chars (max {DESCRIPTION_MAX})")
    if skill.parent.name.startswith(KNOWLEDGE_PREFIXES):
        problems.extend(knowledge_problems(skill, text, fields))
    return problems


def agent_problems(plugin: Path) -> tuple[list[str], int]:
    """Problems in the agents Claude Code lists, and their listing size in tokens."""
    problems: list[str] = []
    total_chars = 0
    for agent in claude_agents(plugin):
        fields = frontmatter(agent.read_text(encoding="utf-8"))
        problems.extend(strict_yaml(agent))
        if not fields.get("name") or not fields.get("description"):
            problems.append(f"{agent}: frontmatter needs name and description")
        total_chars += len(fields.get("name", "")) + len(fields.get("description", ""))
    tokens = total_chars // 4
    if tokens > AGENT_BUDGET_TOKENS:
        problems.append(f"agents: listing ≈ {tokens} tokens (budget {AGENT_BUDGET_TOKENS})")
    return problems, tokens


def protocol_problems(plugin: Path) -> tuple[list[str], int]:
    protocol = plugin / "protocol.md"
    if not protocol.is_file():
        return ["protocol.md: missing"], 0
    chars = len(protocol.read_text(encoding="utf-8"))
    if chars > PROTOCOL_MAX_CHARS:
        return [f"protocol.md: {chars} chars (max {PROTOCOL_MAX_CHARS})"], chars
    return [], chars


def policy_problems(plugin: Path) -> list[str]:
    """Policy DSL lives under policy/default.rules; agy ingests plugins/<name>/rules/* as LLM prompt rules."""
    problems: list[str] = []
    if not (plugin / "policy" / "default.rules").is_file():
        problems.append("policy/default.rules: missing")
    rules_dir = plugin / "rules"
    if rules_dir.is_dir():
        for leaked in sorted(rules_dir.rglob("*.rules")):
            rel = leaked.relative_to(plugin)
            problems.append(f"{rel}: gate policy under rules/ is ingested by agy as an LLM prompt rule")
    return problems


def check(plugin: Path) -> list[str]:
    problems = [*manifest_problems(plugin), *agent_list_problems(plugin), *background_spawns(plugin)]
    problems.extend(policy_problems(plugin))
    problems.extend(consult_problems(plugin))
    problems.extend(twin_problems(plugin))
    for agent in sorted((plugin / AGY_AGENTS).glob("*.md")):
        problems.extend(agy_agent_problems(agent))
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    for skill in skills:
        problems.extend(skill_problems(skill))
    skill_chars = listing_chars(plugin)
    if skill_chars > SKILL_DESCRIPTIONS_TOTAL_MAX:
        problems.append(f"skill descriptions total {skill_chars} chars (max {SKILL_DESCRIPTIONS_TOTAL_MAX})")
    agents, tokens = agent_problems(plugin)
    protocol, protocol_chars = protocol_problems(plugin)
    problems.extend([*agents, *protocol])
    print(
        f"agents listing ≈ {tokens} tokens; skills: {len(skills)}, listed {skill_chars} chars; "
        f"protocol {protocol_chars} chars"
    )
    return problems


INSTALL_NAME = re.compile(r"\bcobot-[0-9a-f]{16}\b")  # install.sh --agy's hook group, per install
SCANNED_SUFFIXES = frozenset({".md", ".json", ".sh", ".py", ".yml", ".yaml", ".txt", ".rules"})
SKIPPED_FOLDERS = frozenset({".git", "node_modules", "__pycache__", ".venv"})


def install_name_problems(repo: Path) -> list[str]:
    """A live hook group name written into the tree: the repository is public, and a repository's
    .agents/hooks.json naming that group with enabled false switches the owner's gate off."""
    problems = []
    for path in sorted(repo.rglob("*")):
        relative = path.relative_to(repo)
        if SKIPPED_FOLDERS & set(relative.parts) or path.suffix not in SCANNED_SUFFIXES or not path.is_file():
            continue
        for name in dict.fromkeys(INSTALL_NAME.findall(path.read_text(encoding="utf-8", errors="replace"))):
            problems.append(f"{relative}: an installed hook group name ({name}): redact it")
    return problems


def main(argv: list[str]) -> int:
    plugin = Path(argv[0]) if argv else Path("plugins/cobot")
    problems = [*check(plugin), *install_name_problems(plugin.resolve().parents[1])]
    for problem in problems:
        print(f"FAIL {problem}")
    print("plugin contract: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
