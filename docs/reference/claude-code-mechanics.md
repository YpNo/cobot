# Claude Code mechanics that shape this design (verified 2026-11-06)

Verified against code.claude.com docs by a research agent on 2026-11-06 (Claude Code ~2.1.318).
Summarised fetches; items marked *unverified* must be re-checked before relying on them.

## Plugins and marketplace
- Plugin root: `.claude-plugin/plugin.json` (only `name` required), `skills/<n>/SKILL.md`,
  `agents/*.md`, `hooks/hooks.json`, `.mcp.json`, `workflows/`, `bin/` (added to PATH),
  `settings.json`, `commands/` (legacy, still works; use skills). Subfolders of `agents/`
  become part of the agent name.
- A `CLAUDE.md` at the plugin root is **not loaded**. Instructions live in skills, path-scoped
  rules, or a SessionStart hook (`additionalContext`, capped at 10 000 chars).
- Plugin `settings.json` keeps only `agent` and `subagentStatusLine`. **Plugins cannot ship
  permission rules.** Enforcement from a plugin = hooks (run as the user). A hard guarantee
  needs `permissions.deny` in user or project settings.
- Marketplace: `.claude-plugin/marketplace.json` with `name`, `owner.name`, `plugins[]`
  (`name`, `source` such as `"./plugins/x"`, optional `version`, `category`, `tags`,
  `dependencies`, `defaultEnabled`). Install: `claude plugin marketplace add owner/repo`,
  `claude plugin install name@marketplace --scope user|project|local`. Validate with
  `claude plugin validate <path> --strict`. Auto-update is off for GitHub marketplaces.
- Enablement: `enabledPlugins` in `~/.claude/settings.json` (user), `.claude/settings.json`
  (project), `.claude/settings.local.json` (local). Local > project > user.
- Component path keys in plugin.json must start with `./`; `agents`/`commands` keys replace
  the folder scan, `skills` adds to it. `themes`/`monitors` moved under `experimental`.

## Subagents (`agents/*.md`)
- Required `name`, `description`. Honoured for plugin agents: `tools` (allowlist),
  `disallowedTools`, `model` (`sonnet|opus|haiku|fable|<id>|inherit`), `effort`
  (`low..max`), `skills` (preloaded, first 32), `memory` (`user|project|local`),
  `isolation: worktree`, `maxTurns`, `background`, `omitClaudeMd`, `color`.
- **Ignored for plugin agents:** `permissionMode`, `hooks`, `mcpServers`, `initialPrompt`.
  Read-only = `tools: Read, Grep, Glob` (no other mechanism).
- Subagents do not inherit the parent's skills or auto-memory (forks do). Omit `Agent` from
  `tools` to stop nesting. Default spawn depth 3. Combined agent descriptions budget ≈ 15 000
  tokens: every installed agent costs context in every session.
- Fork subagent inherits the whole conversation; cannot fork again.

## Skills (`SKILL.md`)
- Fields: `name`, `description`, `when_to_use`, `argument-hint`, `disable-model-invocation`,
  `user-invocable`, `allowed-tools` (grants, does not restrict), `disallowed-tools`, `model`,
  `effort`, `context: fork` + `agent`, `background`, `paths` (globs gating auto-activation),
  `hooks`, `shell`, `metadata`.
- `description` + `when_to_use` truncated at 1 536 chars in the listing. Keep SKILL.md under
  500 lines; detail in sibling files loaded on demand; `scripts/` executed, not loaded.
- Plugin skill names: `/<plugin>:<skill>`.

## Hooks
- 33 events. Blocking ones that matter here: `PreToolUse`, `UserPromptSubmit`, `Stop`,
  `SubagentStop`, `PreCompact`, `WorktreeCreate`. `PostToolUse` cannot block.
- Handlers: `command`, `prompt`, `agent`, `http`, `mcp_tool`. `if` uses permission-rule syntax
  (`Bash(git push *)`), documented as best-effort. Exit 2 = block (stderr is the reason);
  JSON `hookSpecificOutput.permissionDecision: allow|deny|ask|defer`, `additionalContext`.
- Plugin hooks live in `hooks/hooks.json`, merge with user/project hooks, use
  `${CLAUDE_PLUGIN_ROOT}`, fire from session load.

## Memory and instructions
- `.claude/rules/*.md` (project) and `~/.claude/rules/` (user): rules with `paths:` load only
  when matching files are touched; without `paths:` they load at launch. *Unverified whether a
  plugin can ship rules.*
- Auto memory `~/.claude/projects/<project>/memory/`, `MEMORY.md` index (first 200 lines /
  25 KB loaded). Agents may have their own memory via `memory:`.
- `AGENTS.md` is read when no CLAUDE.md exists (v2.1.277+).

## Evals
- `evals/<case>/prompt.md` (frontmatter `name`, `runs`, `max_turns`, `model`, …) +
  `evals/<case>/graders/<g>.md` (`type: regex|tool_used|tool_order|file_exists|llm|baseline`,
  `weight`). Optional `case.yaml` (`schema_version: "1.1"`), mocks in `evals/mocks/`.
- `claude plugin eval <target> --threshold 1.0 --model <pinned> --trust-plugin --json` in CI.
  Exit 0 pass, 1 below threshold. `--ablation with-without` measures the plugin's delta.
- `/skill-doctor` = context-cost / usage report, not a linter.

## Workflow tool
- User opt-in per run (keyword, "run a workflow", or a skill that says so). Scripts are JS with
  `agent()`, `pipeline()`, `parallel()`, `phase()`, schemas, `model`/`effort` per agent,
  `agentType` to use a plugin agent, `isolation: 'worktree'`. Saved workflows resolve from
  `.claude/workflows/` and a plugin's `workflows/`, invoked by name.

## Not verified (re-check before relying on it)
Version computation when `version` omitted · hook event list came from a summarised fetch ·
whether plugin agents can spawn subagents · `@import` depth limit · plugin-shipped rules ·
eval exit code 2 for partial runs.

## Found while building R0 (2026-11-06, Claude Code 2.1.285)
- `marketplace.json` `metadata.pluginRoot` is **not applied** when `claude plugin install` resolves
  a path marketplace: the install looked for `<repo>/partner`. Write full `source` paths
  (`./plugins/partner`) and omit `pluginRoot`.
- `claude plugin details <name>` only knows installed plugins; it takes no path and no `--json`.
  Measuring the token cost of a checkout in CI means registering the checkout as a path
  marketplace and installing it in the runner first.
- `claude -p` from a sandboxed subprocess cannot reuse the desktop app's credentials; nested
  sessions need the CLI's own login (`claude login`). Spikes that start Claude run from the
  owner's terminal.
- The owner's git has `safe.bareRepository = explicit`: scratch remotes are non-bare with
  `receive.denyCurrentBranch = updateInstead`.

- Spike results (owner's terminal, 2026-11-06): **A** `--plugin-dir` lists `partner:challenger`
  beside the legacy `challenger`. **B** with `--allowedTools "Bash(git push:*)"` the gate's `ask`
  prevailed and the remote stayed unchanged; the gate log shows the **original** command
  (`git push origin main`), not the rtk-rewritten one, so hooks receive the pre-rewrite input.
  **C** is *not* proven: the model refused the force push before calling Bash, so the hook never
  saw it (one log line only). R1 re-tests `deny` with a harmless probe rule
  (`never Bash(echo partner-deny-probe*)`) so the model does call the tool. Whether hooks fire for
  a subagent's Bash is still open (`agent` was null: main thread).
