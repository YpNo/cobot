# Antigravity CLI mechanics that shape cobot (verified 2026-11-15, agy 1.5.9)

What cobot relies on under the Antigravity CLI (`agy`), each with its source. Re-read when agy's
version moves; the design input (`docs/design-inputs/antigravity-0.3.0.md`) keeps the 1.5.3
facts and the owner's session report. Sources:
- **docs**: the built-in docs under `~/.gemini/antigravity-cli/builtin/skills/` (`hooks.md`,
  `run-workflow/SKILL.md`);
- **live**: antigravity.google/docs/hooks and /permissions;
- **changelog**: `agy changelog`;
- **probe**: `agy plugin validate` on a copy, with a throwaway HOME.

Facts still to prove live are marked *smoke*: `scripts/spikes/smoke-agy.sh` fills
`docs/harnesses.md`.

## Plugin layout

- Manifest: `.antigravity-plugin/plugin.json` wins over `plugin.json` and `.claude-plugin/`
  (probe). cobot keeps both manifests with the same name, version, description, license and
  repository; `check-plugin` and `release.yml` hold them equal.
- Agents: `agents/<n>.md`; `tools` must be a YAML list (a string skips the agent); `model` is
  `inherit`, `flash_lite`, `flash` or `pro`, and a model name or `sonnet` skips the agent;
  `effort` is ignored; an unknown tool name passes validate silently (probe). Also
  `mainAgent`, `commandExecutionPolicy` (`off`, `auto`, `eager`, `sandbox`).
- Skills: the Claude Code format; Claude-only keys pass; each skill is also a `/name` command;
  a body over 24 000 bytes is a problem (probe; EGM). Skill text is not expanded:
  `${CLAUDE_PLUGIN_ROOT}` stays literal.
- Hooks: a root `hooks.json`, named groups (`{"cobot": {...}}`); `hooks/hooks.json` is "never
  loaded" (the one validate warning cobot accepts). Hooks run in the folder holding
  `hooks.json`, through `sh -c`, with `PLUGIN_ROOT` and `PLUGIN_DATA` in the environment, not
  substituted into `command` (docs). Default timeout 30 s.
- Discovery: `.agents/`, `.agent/` (legacy, one level deep), `_agents`, `_agent` are
  customization roots: hooks, plugins and skills found there load (docs; spec pass 3).

## Hooks

- Events: `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`,
  `Stop`; no `SubagentStop` (docs). `PreToolUse` and `PostToolUse` are grouped with a
  `matcher` regex; the others are flat lists of handlers, their matcher ignored (docs).
- Common stdin: `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`,
  `modelName`, `lastUserInput`, `hookEventName`, `cwd` (the agent's working directory, 1.5.4+);
  no agent identity (docs, live).
- `PreToolUse` stdin adds `toolCall {id, name, args}`; the answer is `decision`: `allow` defers
  to the next hook or the default policy, `auto_approve` widens, `ask` respects a cached grant,
  `force_ask` does not, `deny` blocks (live; the built-in docs abridge `allow`).
- **A hook that exits non-zero is logged and ignored: the call runs** (1.5.3 spike, live). cobot's
  shim therefore prints a deny with exit 0 on every failure. *smoke*: the hook's output is
  ignored too when it exits 1.
- `SessionStart` answers `{"injectSteps": [{"systemMessage": {"systemMessage": "…"}}]}`; no size
  limit is documented (docs, live). A user-message step would read as the owner's own words.
- *smoke*: whether `PreToolUse` fires for an `invoke_subagent` child's calls and inside
  `run_workflow` (`call_tool` runs pre-tool hooks and an unapproved ask is denied: docs).

## Tools

- Commands: `run_command` (`CommandLine`, an optional `Cwd` on some models), `manage_task`
  (`list`, `status`, `kill`, `send_input` with `Input`) (live; report).
- Files, two families by model: `view_file` (`AbsolutePath`), `write_to_file`,
  `replace_file_content`, `multi_replace_file_content` (`TargetFile`); `read_file`,
  `write_file`, `edit_file` (`Path`) (live; report; validate's matcher hints name both).
- Reads: `list_dir`, `find_by_name`, `grep_search` (left the default baseline in 1.5.9,
  available when listed: changelog), `read_url_content`, `search_web`, `view_code_item`.
- Orchestration: `invoke_subagent` (`Workspace` = `inherit`, `branch` or `share`, flat or in a
  `Subagents` array), `manage_subagents`, `define_subagent`, `run_workflow` (`Script` or
  `ScriptPath`, Python; new in 1.5.9), `schedule` (`TimerCondition` runs a command),
  `ask_question`, `send_message`, `list_permissions`, `ask_permission`, `finish`,
  `skill_search` (live; docs; changelog).
- MCP: lazy `call_mcp_tool` (`ServerName`, `ToolName`, `Arguments`) or eager
  `mcp_<server>_<tool>`; a plugin's servers are named `<plugin>_<server>` (changelog 1.2.2).
  Configuration: `~/.gemini/config/mcp_config.json` and each installed plugin's
  `~/.gemini/config/plugins/<p>/mcp_config.json` or `mcp.json`. *smoke*: the name form seen.
- The cobot tables: `plugins/cobot/bin/_cobot_agy.py`.

## Install and settings

- `agy plugin install <folder>` copies into `~/.gemini/config/plugins/<name>/`, replaces an
  installed copy in place and restores it on failure (changelog 1.4.8, 1.5.6); `agy plugins`
  is an alias of `agy plugin`; `link <mp> <target>` links a marketplace (`agy plugin --help`).
- Settings: `~/.gemini/antigravity-cli/settings.json` `permissions.{allow,ask,deny}` with
  `command(prefix)`, `command(regex:…)`, `mcp(srv/tool)`; deny > ask > allow (live). cobot
  writes none of it.
- Command sidecars and access grants live under `~/.gemini/jetski/` (report; spec pass 3).
