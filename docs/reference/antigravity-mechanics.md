# Antigravity CLI mechanics that shape cobot (verified 2026-11-19, agy 1.5.11)

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
  (probe). cobot keeps both canonical manifests equal (`check-plugin`, `release.yml`) and stages
  pure host bundles with `scripts/package-plugin.py` (`--host agy|claude`) so each install holds
  only its host's manifest, agents, and hook file (`agy plugin validate --strict` exits 0 with
  0 warnings).
- Rules: any file under `rules/` is ingested into the session prompt (`agy plugin list --json`
  reports `rules: N`), so gate policy files must not live under `rules/` (cobot uses
  `policy/default.rules`).
- Agents: `agents/<n>.md` (synced from `agent-defs/<n>.md`); `tools` must be a YAML list (a string
  skips the agent); `model` is strictly the tier enum `inherit`, `flash_lite`, `flash` or `pro`
  (probe 1.5.11: concrete IDs such as `gemini-4-carbon-high` fail `Invalid model tier` and skip the
  agent); `effort` is ignored; an unknown tool name passes validate silently (probe). Also
  `mainAgent`, `commandExecutionPolicy` (`off`, `auto`, `eager`, `sandbox`). Concrete Gemini 4
  model IDs (`gemini-4-carbon-{low,medium,high}`, `gemini-4-hydrogen-*`, `gemini-4-argon-*`,
  `gemini-3.8-flash-*`, `gemini-pro-orchestrator`) apply to `swarm(action="add", model=...)`.
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
- A hook that exits non-zero: on 1.5.3 the call ran (spike, live docs); on 1.5.9 a workspace
  hook printing deny and exiting 1 blocked the call with "JSON hook … failed" (smoke `h1`).
  cobot's shim still prints a deny with exit 0 on every failure, which holds either way.
- Hook groups from every source merge by **name**: a workspace `.agents/hooks.json` group named
  like the plugin's with `"enabled": false` switches the plugin's group off (smoke `h2`).
  Workspace hooks ran before the plugin's (`h1`). cobot's answer: `install.sh --agy` names the
  group `cobot-<random>` per install, and the brief warns on workspace hooks and plugins.
  A workspace hook's `auto_approve` did not override cobot's `deny` (smoke `h3`); the order in
  which agy runs workspace and plugin hooks varied between runs (`h1`).
- Print mode (`agy -p`) denies an ask it cannot prompt for ("headless mode cannot prompt"), so
  a `force_ask` is a deny there (smoke `w1`, `b1`).
- `run_command` saw the checkout's `.git` read-only (a `git push` could not update its
  remote-tracking ref) (smoke `h2`).
- `SessionStart` answers `{"injectSteps": [{"systemMessage": {"systemMessage": "…"}}]}`; no size
  limit is documented (docs, live). A user-message step would read as the owner's own words.
- `PreToolUse` fires for an `invoke_subagent` child's calls (smoke `g2`). *smoke*: inside
  `run_workflow` (`call_tool` runs pre-tool hooks and an unapproved ask is denied: docs); not
  reached in print mode, which denies the asked `run_workflow` itself.

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
  `ScriptPath`, Python; 1.5.9+), `schedule` (`TimerCondition` runs a command), `swarm` (`status`,
  `models`, `add`, `model`, `kill`, `title`), `post_message`, `read_board`, `swarm_wait`,
  `ask_question`, `send_message`, `list_permissions`, `ask_permission`, `finish`,
  `skill_search` (live 1.5.11; docs; changelog).
- MCP: lazy `call_mcp_tool` (`ServerName`, `ToolName`, `Arguments`), resource tools
  `list_resources` / `read_resource` (`ServerName`), or eager `mcp_<server>_<tool>`; a plugin's
  servers are named `<plugin>_<server>` (changelog 1.2.2; observed live on `dak_bigquery`).
  Configuration: `~/.gemini/config/mcp_config.json` and each installed plugin's
  `~/.gemini/config/plugins/<p>/mcp_config.json` or `mcp.json`.
- The cobot tables: `plugins/cobot/bin/_cobot_agy.py`.

## Install and settings

- `agy plugin install <folder>` copies into `~/.gemini/config/plugins/<name>/`, replaces an
  installed copy in place and restores it on failure (changelog 1.4.8, 1.5.6); `agy plugins`
  is an alias of `agy plugin`; `link <mp> <target>` links a marketplace (`agy plugin --help`).
- Settings: `~/.gemini/antigravity-cli/settings.json` `permissions.{allow,ask,deny}` with
  `command(prefix)`, `command(regex:…)`, `write_file(path)`, `mcp(srv/tool)`; deny > ask > allow
  (live docs). cobot writes none of it (`cobot-rules sync --runtime agy` renders a diff only).
- Execution modes: `auto`, `accept-edits`, `plan`, and `default` respect `PreToolUse` `deny`,
  `force_ask` (prompts every call), and `ask` (honors session *Always Allow* cache).
- Command sidecars and access grants live under `~/.gemini/jetski/` (report; spec pass 3).
