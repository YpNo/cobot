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
  `effort`, `context: fork` + `agent`, `background`, `paths` (globs gating auto-activation of
  project and user skills; plugin skills ignore it, see 2026-11-10 below),
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

- A folder carries one marketplace name: `marketplace add <path>` for a folder already
  registered under another name answers "Marketplace '<old>' already on disk — declared in user
  settings" and registers nothing, so a rename must `marketplace remove <old>` first.
  `marketplace remove` clears `known_marketplaces.json` and the `extraKnownMarketplaces` record
  in `~/.claude/settings.json` itself; `plugins/cache/<old>/` stays behind (observed 2026-11-07,
  2.1.285).

## Hooks (verified 2026-11-07 against <https://code.claude.com/docs/en/hooks.md>, 2.1.311)
- `SubagentStop` input: common fields plus `agent_id`, `agent_type`, `agent_transcript_path`
  (`<session>/subagents/agent-<id>.jsonl`), `last_assistant_message`, `stop_hook_active`. The
  matcher is the agent type; plugin agents match their namespaced name (`^cobot:rust-builder$`).
  Internal agents fire it too with an empty `agent_type`, so anchor the matcher. Output
  `{"decision": "block", "reason": "…"}` (exit 0) or exit 2 with stderr keeps the subagent
  running with the reason as its next instruction; `stop_hook_active` true means a stop hook
  already continued it once. For a subagent that reports through `SubagentHandback`,
  `last_assistant_message` is closing text and the report is `tool_input.message` of that call
  (`PreToolUse`/`PostToolUse` matcher `SubagentHandback`). 2.1.311 fixed `SubagentStop` firing
  twice a minute per running subagent.
- `PostToolUse` on `Agent` carries `tool_response.content` (the report), `usage`, `totalTokens`,
  `modelsUsed` for foreground runs; it cannot block the tool, it can `block` the result with a
  reason. Plugin hooks run inside subagents too.
- `SubagentStart`: matcher by agent type, context-only (`hookSpecificOutput.additionalContext`),
  cannot block.
- Transcripts: `~/.claude/projects/<slug>/<session>.jsonl` (slug = cwd with non-alphanumerics →
  `-`; `CLAUDE_CONFIG_DIR` moves the root), subagents under `<session>/subagents/`, retention
  `cleanupPeriodDays` (30). The row format is documented as internal and changeable; `/usage`
  (aliases `/cost`, `/stats`) attributes the live session's cost to skills, subagents and
  plugins. Plugins may ship Workflow scripts under `workflows/`, namespaced `/<plugin>:<name>`.

## Evals
- `evals/<case>/prompt.md` (frontmatter `name`, `runs`, `max_turns`, `model`, …) +
  `evals/<case>/graders/<g>.md` (`type: regex|tool_used|tool_order|file_exists|llm|baseline`,
  `weight`). Optional `case.yaml` (`schema_version: "1.1"`, `name`), mocks in `evals/mocks/`.
  A fixture is `case.yaml` → `context.scaffold_script: fixture.sh` (a script in the case
  directory, run only with `--scaffold`, 120 s limit); `scaffold_script` is not a prompt.md key
  (loader error "unknown frontmatter key", verified 2026-11-07 on 2.1.285 against
  <https://code.claude.com/docs/en/plugin-evals.md>).
- A case's `allowed_tools` grants only the read-only set (Read, Glob, Grep, Skill, Agent, …);
  `Bash`, `Write`, `Edit`, Web* must also be granted with `--allow-tools`, else they are removed
  from the session and the model cannot call them. A grader that needs them warns "cannot pass
  with the granted tools" and the case fails every run.
- `claude plugin eval <target> --threshold 1.0 --model <pinned> --trust-plugin --json` in CI.
  Exit 0 pass, 1 below threshold. A plugin resolved from a path runs two arms by default
  (`with` the plugin, `without` as baseline, Δ reported); `--ablation none` runs one. In two-arm
  mode every `tool_used` grader on `Skill` and every `arm: with-only` grader is reported but not
  scored (a plugin-fired indicator).
- A skill with `context: fork` and `agent:` invoked through the Skill tool records a `Skill`
  call, not an `Agent` call (observed 2026-11-07: `/cobot:learn` ran the learner, Agent 0x).
  Detect it with `tool_used: Skill` + `input_match`.
- A `regex` grader's `target: trace` sees every line of the session JSON, including the
  `hook_response` line that carries the SessionStart payload (so the protocol text is in the
  trace: a pattern that only looks for a word the protocol uses passes vacuously) and every
  assistant message, not only the last. Non-ASCII is not escaped; quotes are `\"`. `flags: i`.
  With `--keep-temp` the trace is `/tmp/claude-eval-<id>/out/trace.jsonl` (the kept directory
  is read-only, `home/` and `tmp/` sealed). Verified 2026-11-07 on 2.1.311.
- An `llm` judge (haiku by default) votes 2 of 3 on prose; it failed three answers that met a
  five-clause rubric (profile-caps-size, 2026-11-07). Prefer one regex per required fact.
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
  a path marketplace: the install looked for `<repo>/cobot`. Write full `source` paths
  (`./plugins/cobot`) and omit `pluginRoot`.
- `claude plugin details <name>` only knows installed plugins; it takes no path and no `--json`.
  Measuring the token cost of a checkout in CI means registering the checkout as a path
  marketplace and installing it in the runner first.
- `claude -p` from a sandboxed subprocess cannot reuse the desktop app's credentials; nested
  sessions need the CLI's own login (`claude login`). Spikes that start Claude run from the
  owner's terminal.
- The owner's git has `safe.bareRepository = explicit`: scratch remotes are non-bare with
  `receive.denyCurrentBranch = updateInstead`.

- Spike results (owner's terminal, 2026-11-06): **A** `--plugin-dir` lists `cobot:challenger`
  beside the legacy `challenger`. **B** with `--allowedTools "Bash(git push:*)"` the gate's `ask`
  prevailed and the remote stayed unchanged; the gate log shows the **original** command
  (`git push origin main`), not the rtk-rewritten one, so hooks receive the pre-rewrite input.
  **C** is *not* proven: the model refused the force push before calling Bash, so the hook never
  saw it (one log line only). R1 re-tests `deny` with a harmless probe rule
  (`never Bash(echo cobot-deny-probe*)`) so the model does call the tool. Whether hooks fire for
  a subagent's Bash is still open (`agent` was null: main thread).
- R1 spike results (owner's terminal, 2026-11-06, `scripts/spikes/spike-r1.sh`): **D** a plugin hook's
  `permissionDecision: deny` blocks a Bash call in the main thread (the model had no reason to
  refuse `echo`). **E** the hook fires for a subagent's Bash too; the hook input carries
  `agent_type` as the **namespaced** name (`cobot:builder`), so agent scopes must match with or
  without the `cobot:` prefix. **F** a skill with `context: fork` and `agent: cobot:consultant`
  runs in that agent (`agent_type` = `cobot:consultant` in the log). In `-p` mode a Bash call the
  gate leaves silent is still denied by Claude Code's own permissions, so headless consults are
  read-only through Read/Grep only; interactive sessions prompt.
- `claude plugin eval`: an `llm` grader does not accept `target` (loader error "Unrecognized
  key(s) in object: 'target'"); `regex` graders do. A single invalid case aborts the whole run
  (exit 1) before any case executes.
- `claude plugin eval` with `--allow-tools Bash` needs the OS sandbox backend: on Linux
  `bubblewrap` and `socat` (`apt install bubblewrap socat`), otherwise every run is refused with
  "sandbox required but unavailable" and scores as failed at zero cost. Cases that only need
  `Write`/`Edit` run without it. The `gate-asks` case therefore needs the backend on the machine
  that runs it (CI's ubuntu runner has to install it too).
- The eval sandbox confines the child's writes outside the workspace: `cobot-memory init
  --foreign` ran and reported success inside a run, and the owner's `~/.local/share/cobot`
  held nothing afterwards (observed 2026-11-08, 2.1.311, bubblewrap backend). A case's `env`
  accepts `EVAL_*` names only and the child inherits an allowlist (`PATH`, locale, proxy,
  `ANTHROPIC_*`, `CLAUDE_CODE_*`, `EVAL_*`); `regex` graders read a workspace file with
  `target: {source: file, path: …}`; `tool_used input_match` is a regex over the JSON-encoded
  tool input; `--case <glob> --runs 1 --ablation none` iterates on one case.
- Eval judges (`llm`, default haiku) failed two runs whose final message plainly met the rubric
  ("I sized this as tiny"). Prefer `regex`, `tool_used`, `tool_order` and `file_exists` graders;
  keep `llm` for what cannot be matched. Traces are deleted after a run unless `--keep-temp`.

## Found while dogfooding on cartridge-os (2026-11-06, Claude Code 2.1.285)

- `claude plugin marketplace add <directory>` records the marketplace in `~/.claude/plugins/known_marketplaces.json` and in the user `settings.json` (`extraKnownMarketplaces`); a project-scope install then writes only `enabledPlugins` into the project's `.claude/settings.json`.
- An install copies the plugin to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and records `gitCommitSha` and `projectPath` in `installed_plugins.json`. `${CLAUDE_PLUGIN_ROOT}` is that versioned path, and hooks run from it.
- `claude plugin update` compares version strings only: a same-version edit in a directory marketplace reports "already at the latest version" and the cache stays stale. `uninstall` leaves the cache directory in place; the next `install` overwrites it from the checkout (`install.sh --refresh`).
- `claude plugin list` shows a project-scope plugin as enabled only when run from inside that project.
- `claude -p` in a terminal can fail with "OAuth session expired and could not be refreshed" while the desktop app's own session works; `claude login` in that terminal is the fix.
- In `claude -p` (non-interactive), a PreToolUse `ask` surfaces to the model as the tool result `This command requires approval` when it comes from Claude Code's own permission system, and as the hook's `permissionDecisionReason` (`cobot gate: opaque command '…'`) when the hook asked; neither runs the command. Verified from cartridge-os with the project-scope install on 2026-11-06.

## Found while dogfooding on headscale (2026-11-07, Claude Code 2.1.285)

- `claude plugin install --scope local` writes `enabledPlugins` into the repository's `.claude/settings.local.json` and a second entry under the same plugin key in `installed_plugins.json` (`scope: local`, its own `projectPath` and `gitCommitSha`); both scopes share one cache directory per version. headscale ignores `.claude/` in its `.gitignore`, so nothing shows in `git status`.
- From inside a repository with a local-scope install, `claude plugin list` shows both the local entry and another repository's project-scope entry; the scope line, not the position, says which applies.
- `claude -p` from a foreign checkout delivered the cobot protocol, the UNTRUSTED brief line with its reason and the five `cobot:` agents through the local-scope install; a project `.mcp.json` with unapproved servers does not block the run.
- The memory symlink lives in the main checkout; a git worktree of the same repository resolves `--git-common-dir` to it, so the worktree is trusted and shares the memory without a symlink of its own.

## Found while building the learner (2026-11-07, Claude Code 2.1.285)

- In `claude -p`, `WebFetch` and `WebSearch` are not granted unless `--allowedTools WebFetch
  WebSearch` is passed: a forked agent sees "not granted" and cannot fetch. The `learner` then
  returns an empty delta and lists the refusals, which is the designed behaviour; the
  `knowledge-refresh.yml` workflow passes the grants.
- `--allowedTools` is variadic: every argument after it is read as a tool name, including the
  prompt, and the run fails with "Input must be provided either through stdin or as a prompt
  argument". Put the prompt right after `-p` and the tool list last.
- `--plugin-dir plugins/cobot` loads the plugin for one print run: its hooks (the gate, the
  SessionStart brief), agents and skills are all active, so a checkout can probe itself without
  an install.
- `claude plugin validate --strict` accepts `context: fork` with `agent: cobot:learner` in a
  skill whose agent file is in the same plugin.

## Found while building the R2 surface (2026-11-10, Claude Code 2.1.311)

Spikes with a throwaway plugin and `claude -p --output-format stream-json`, haiku, about 0.05 USD.

- Forked skills (`context: fork`) run **one at a time**: two Skill calls in one assistant message,
  to the same skill or to two different skills, finished 11 s apart around an 8 s sleep. Two
  `Agent` calls in one message finished 1 s apart: **agents run in parallel**. Fan-out therefore
  goes through `Agent` calls (the `/cobot:consult` router), never through forked skills.
- A forked skill receives `$ARGUMENTS`, and `${CLAUDE_PLUGIN_ROOT}` is expanded in a skill body;
  a file the agent reads afterwards is raw text, so its paths must start at the plugin root.
- `paths:` gates project skills only. A plugin skill with `paths:` was listed before any matching
  file was touched; the same skill in `.claude/skills/` appeared only after a matching file was
  read. A plugin skill's description is its only trigger, and every plugin skill costs listing
  space in every session.
- `disable-model-invocation: true` removes a skill from the model's listing (the owner still
  types it); `user-invocable: false` hides it from the menu but keeps it listed.
