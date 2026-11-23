# ADR-0008 — Host-agnostic core, pure packaging, explicit Gemini tiers, and agy mode alignment

Status: accepted · Date: 2026-11-19 · Amends: ADR-0007 · Relates to: ADR-0001 (one plugin),
ADR-0003 (host boundary)

## Context

Running `agy plugin validate --strict` and live `agy 1.5.11` probes against the single-tree layout
of ADR-0007 exposed four structural gaps:

1. Antigravity ingests files under `rules/` as always-on system-prompt rules, so placing
   `default.rules` in `rules/` leaked raw policy lines into every session context (`rules: 1`), and
   mixing `.claude-plugin/` + `claude-agents/` + `hooks/hooks.json` in one installed directory
   coupled both hosts.
2. Owner state defaulted unconditionally to `~/.claude/cobot*` even on Antigravity-only machines.
3. Antigravity agents inherited the caller's session model (`model: inherit`), instead of selecting
   an explicit Gemini tier matched to each agent's cognitive load with owner/project overrides.
4. Under Antigravity, the gate collapsed every prompt into `force_ask`, bypassing `agy`'s
   per-session *Always Allow* cache even on local repeatable dev steps (`git commit`, `uv add`,
   `make`, `uvx`) across `auto`, `accept-edits`, and `default` modes. Native `1.5.11` tools
   (`swarm`, `post_message`, `read_board`, `swarm_wait`, `list_resources`, `read_resource`) were
   also unclassified.

## Decision

1. **Canonical core + pure per-host build (Option C).** One source tree (`plugins/cobot/`) holds
   host-neutral `agent-defs/*.md`, shared `skills/`, and `policy/default.rules` (enforced by
   `check-plugin.py`, with `rules/*.rules` forbidden). `scripts/package-plugin.py` stages pure,
   warning-free `agy` (`install.sh --agy`, `cobot-agy.zip`) and `claude` (`cobot-claude.zip`)
   bundles stripping host-foreign files and randomizing the `agy` hook group name.
2. **Host-agnostic owner config.** `_cobot_common` resolves `COBOT_CONFIG_DIR` >
   `CLAUDE_CONFIG_DIR/cobot` > existing `~/.claude/cobot*` > `$XDG_CONFIG_HOME/cobot`
   (`~/.config/cobot`), with zero breaking change for existing Claude Code setups.
3. **Explicit task-matched Gemini tiers + multi-level overrides.** Under `agy`, default `agents/*.md`
   tiers match the task rather than `inherit`: `pro` for `challenger`, `auditor`, `learner`, and
   the five language builders; `flash` for `consultant` (parallel domain checklists) and `builder`.
   Overrides merge in order: trusted `.agent/models.json` < `~/.config/cobot/models.json` <
   `--models <file>` < `COBOT_AGENT_MODELS` (including global overrides and dynamic
   `invoke_subagent(Model=...)`). `/swarm` roles map to Gemini 4 `Neon` (`*-builder` code),
   `Carbon` (`challenger`/`auditor` advisor), `Hydrogen` (`consultant`/`builder` medium), and
   `Argon` (`learner`). A proportional Advisor gate consults `challenger` (`pro`/Carbon) before
   freezing medium/large plans, after hitting the exact same error twice, or before closing small+
   work (never on tiny).
4. **Mode-aware `ask` vs `force_ask` and `1.5.11` tools.** Under `agy`, `cobot-rules gate` emits
   `ask` (respecting *Always Allow* per session) only when every matching ask in a command is a
   local repeatable dev rule or opaque local dev runner (`make`, `just`, `uvx`, `npx`, `npm run`),
   and `force_ask` for all outward, destructive, privilege, credential, `swarm add/model`, and
   mixed calls. `cobot-rules sync --runtime agy` renders `~/.gemini/antigravity-cli/settings.json`
   diff fragments (`command(...)`, `write_file(...)`, `mcp(srv/tool)`).

## Consequences

- `agy plugin validate --strict` passes with zero warnings on staged `agy` bundles (`rules: 0`).
- New Antigravity-only installations write `~/.config/cobot/*` while existing `~/.claude/cobot*`
  users keep working unchanged.
- `cobot-session` appends an Antigravity host adapter (`read_file`, unprefixed `/<skill>` and
  `TypeName`, `Workspace="share"`, `plan` mode respect, Gemini 4 model routing) and prints any
  active `models.json` / `COBOT_AGENT_MODELS` overrides in both runtimes.
