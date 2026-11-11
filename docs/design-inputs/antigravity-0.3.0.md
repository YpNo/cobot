# Antigravity support for 0.3.0, and what elephant-goldfish-model teaches

Status: input for the 0.3.0 spec (2026-11-11). It replaces the shape of `owner-ideas-03.md` §3
(written 2026-11-09 from the documentation only); §3's challenge points still hold where this
file does not contradict them.

## What was asked

The owner needs cobot under the Antigravity CLI (`agy`) at work, quickly, and named
[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model) (EGM) as a
source of ideas and tools, every finding challenged before it is taken. EGM ships one plugin to
Claude Code, Codex, Cursor, Copilot, OpenCode and Antigravity.

## Facts, read 2026-11-11

From `agy` 1.5.3 on this machine (`agy --help`, `agy plugin validate --strict` on throwaway
fixtures), antigravity.google/docs and the changelog (1.5.5 is the newest release on the web;
`agy changelog` lists a 1.5.6).

| Area | Fact | Consequence for cobot |
|---|---|---|
| Manifest | `plugin.json` at the plugin root, or `.antigravity-plugin/plugin.json` (wins), or `.gemini-plugin/`; a plugin with only `.claude-plugin/` fails `validate` but `install` converts it | `.antigravity-plugin/plugin.json` can sit beside `.claude-plugin/plugin.json` in `plugins/cobot/` |
| Layout | `skills/<n>/SKILL.md`, `agents/<n>.md` or `agents/<n>/agent.md`, **root** `hooks.json`, `mcp_config.json`, `rules/`, `scripts/` | Claude Code reads `hooks/hooks.json`, agy a root `hooks.json`: both can coexist |
| Skills | same format; Claude-only keys (`paths`, `context: fork`, `user-invocable`, `disable-model-invocation`, `argument-hint`, `allowed-tools`) pass `--strict` silently; each skill becomes a `/name` command; EGM records a 24 000-byte body limit | the 30 skills load as they are (largest is 16 956 bytes); onboard, rules and security-sweep become model-invocable under agy |
| Agents | `tools` must be a YAML list (a string is an error and the agent is skipped); `model` only `inherit`, `flash`, `pro` (`sonnet` is an error); also `commandExecutionPolicy` (off, auto, eager, sandbox) | cobot's nine agents (`tools: Read, Grep, Glob` strings, `model: sonnet`) are skipped as written: the one real conflict |
| Hook events | `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop` | no `SubagentStop`; the report check has nothing to block on |
| PreToolUse | stdin `toolCall{name,args}`, `workspacePaths`, `cwd` (1.5.4+); answers `decision` = allow, auto_approve, deny, ask, force_ask, deny_unless_prior_grant | the gate maps the call to its own tool shape and answers `deny` or `ask`, never `allow` |
| **Exit codes** | **a non-zero exit is logged and ignored: the call goes through (fail open)** | cobot's contract (any failure blocks) needs the adapter to catch everything and print `deny` with exit 0; a missing `python3` still fails open |
| PostToolUse | returns `{}`; cannot block | the builder report check degrades to `PostInvocation` steering (`injectSteps`): proof is asked for, not enforced |
| Tool names | `run_command`, `view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `list_dir`, `find_by_name`, `grep_search`, `read_url_content`, `invoke_subagent` … | one mapping table, used by the agents and by the gate |
| Env | `PLUGIN_ROOT`, `PLUGIN_DATA` (1.5.3+), but `validate` 1.5.3 warns on `${PLUGIN_ROOT}`: hooks run in the plugin folder, use `./bin/…` | `_cobot_common.plugin_root` falls back to the script's own folder (it already does) |
| Settings | `~/.gemini/antigravity-cli/settings.json` `permissions.{allow,ask,deny}` with `command(prefix)`, `command(regex:…)`, `mcp(srv/tool)`; deny > ask > allow | a second `sync` renderer, later |
| Install | official marketplace (sign-in) or a GitHub URL (it clones; no ref or subpath option documented) or a local folder; workspace `.agents/plugins/`, global `~/.gemini/config/plugins/<name>/` | install from a local clone at a tag: `agy plugin install ./cobot/plugins/cobot`; the URL form needs the plugin at a repository root |
| Discovery | `.agent/` is a legacy path, scanned one level deep, `.agents/` the current one | cobot's memory folder: `check` warns if `.agent/skills`, `.agent/rules` or `.agent/workflows` ever appears |
| Import | `agy plugin import claude` reads Claude Code's installed plugins, turns `hooks/hooks.json` into agy hooks (`Bash` → `run_command`, `${CLAUDE_PLUGIN_ROOT}` expanded) | a free second path, worth a spike, not a design |
| Tests | no eval harness; `agy -p --output-format json` for scripted runs; EGM tests with fixtures in a temporary HOME | a smoke script is the floor |
| Unknown | whether PreToolUse fires for a **subagent's** tool call; private-repository install | spike S3 decides whether builders may run under agy at all |

## Shape: one tree, read by both (proven by validation, 2026-11-11)

EGM does not generate an Antigravity copy: agy installs the plugin folder and reads the shared
`skills/` and `agents/`. Its one generated copy (`distributions/claude/`, committed and
byte-checked in CI) broke `main` and every open PR when a README change was not regenerated
(EGM PR #208, `docs/designs/claude_release_branch_distribution.md`). cobot's 2026-11-09 plan was
exactly that committed copy, and it is dropped.

Spikes on a scratch copy of `plugins/cobot/` (`agy plugin validate`, `claude plugin validate
--strict`, and one `claude --plugin-dir … -p` listing of the agent types):

| Spike | Result |
|---|---|
| S0 the plugin as it is | agy: "no plugin.json … looks like a Claude Code plugin"; 0 agents |
| S1 `.antigravity-plugin/plugin.json` + a root `hooks.json` | 29 skills: `onboard`'s `argument-hint: [--foreign] [what a new project is for]` is not valid YAML (two flow sequences; Claude Code's parser tolerates it, agy skips the skill; quoting fixes it). All nine agents skipped (`tools` is a string). Hook shape: tool events take `{"matcher", "hooks": [...]}`, the others a flat list of commands, all under a named group; `hooks/hooks.json` is reported "never loaded" (a warning, so `--strict` fails on it for good) |
| S2a agy adapters as `agents/<n>/agent.md` | agy loads them; **Claude Code loads them too**, as `cobot:challenger:challenger` (subfolders join the name): rejected, it would list nine broken agents and spend the listing budget |
| S2b Claude Code's agents moved to `claude-agents/*.md`, listed by file in `.claude-plugin/plugin.json` `"agents": [...]` (a folder string is refused: "must end with .md"); agy adapters at `agents/<n>.md` | `claude plugin validate --strict` passes; Claude Code lists exactly the nine `cobot:*` agents with their own tools (the custom list **replaces** `agents/`); agy validates 30 skills, the adapter and the hooks, one warning |

So (as folded after the challenge below):

- `plugins/cobot/` stays the only tree, installed as it is by both runtimes. It gains
  `.antigravity-plugin/plugin.json` (`name` and `version` equal to `.claude-plugin/plugin.json`,
  a test keeps them so) and a root `hooks.json` for agy; Claude Code keeps `hooks/hooks.json`.
  Every reader of `agents/` (`check-plugin`'s listing budget, `install.sh` overlap report,
  `test_cli_flags`, the mechanics note) reads the manifest's `agents` list instead.
- **Agents**: Claude Code's nine move to `claude-agents/` and are listed by file in
  `.claude-plugin/plugin.json`; the canonical text stays there, so the primary runtime pays no
  extra read. `agents/<n>.md` holds one agy agent each: agy's `tools` list mapped from the Claude
  list by one table and checked against agy's known tool names (an unknown name may hang the
  subagent), a model tier (`sonnet` → `flash`, `inherit` → `inherit`), `mainAgent: false`, and the
  body. EGM goes the other way (canonical in `agents/`, Claude adapters reading
  `${CLAUDE_PLUGIN_ROOT}/agents/…`); cobot keeps Claude Code primary. The agy body is either a
  pointer to the canonical file through the absolute plugin path the agy brief gives (if S3
  shows a subagent can read it) or a copy written by `scripts/sync-agents.py`, with a per-agent
  test that fails naming that command: a body edit is the only change that can trip it, not a
  README edit (EGM's failure mode).
- **Read-only agents under agy**: the documented payload carries no agent identity, so the
  gate's `@consultant` and `@learner` rows (read lists, secret reads denied) cannot apply. Their
  agy versions get no `run_command` at all (`commandExecutionPolicy: off`, read tools only)
  until S3 finds an identity field.
- **The gate under agy**, through a shell shim like `gate.sh`: `sh ./hooks/gate-agy.sh` runs
  `python3 -I ./bin/cobot-rules gate --runtime agy` under an internal deadline below the 10 s
  hook timeout and prints `{"decision":"deny","reason":…}` with exit 0 when `python3` is missing,
  too old, exits non-zero, prints nothing or times out: agy ignores a hook's exit code, so a
  failure must still say deny. The adapter reads `toolCall`, maps `run_command` → Bash, the file
  tools → Edit/Write, MCP tools → MCP (their agy name form is checked in S3 against the `never
  mcp__gcp-*` rows), and answers:
  - **no opinion** → `{"decision":"allow"}`, which in agy means "defer to the next hook or the
    default policy" (Claude Code's silence); **`auto_approve` is never emitted** (it is agy's
    widening value). The contract reads "the gate never widens" in both runtimes;
  - **ask** → `force_ask`, since agy's `ask` respects a cached "Always Allow";
  - **deny** → `deny` with the rule as the reason.

  The matcher is `.*`: agy's read-only tools by name (`view_file`, `list_dir`, `find_by_name`,
  `grep_search`, `read_url_content`, `search_web`) get no opinion; any other or unknown tool, and
  a file tool whose path argument cannot be found, gets `force_ask`; `define_subagent` (a child
  that may run without cobot's customisations) gets `deny`.
- **Self-protection**: the default rules gain `never` rows for edits of
  `~/.gemini/antigravity-cli/settings.json` and for `agy plugin disable|uninstall cobot`, as they
  protect `~/.claude/settings*.json` today. The owner rules layer and the identities stay under
  `~/.claude/` even on a machine with agy only.
- **Commands in skills**: Claude Code puts `bin/` on PATH; agy does not, and agy does not expand
  `${CLAUDE_PLUGIN_ROOT}` in skill text. The agy brief (`SessionStart` `injectSteps`) states the
  absolute `bin/` path and how to call `cobot-memory`, `cobot-rules` and `cobot-deps` through it;
  S3 runs `/cobot:onboard` end to end to prove it.
- **Skills agy cannot honour**: `context: fork` (security-sweep, learn) would run inline, and
  user-only skills (onboard, rules, security-sweep) become model-invocable. The agy brief says the
  owner types those three and that security-sweep and learn run through `invoke_subagent` or are
  refused, never run inline (EGM's own rule: stop rather than simulate a fresh reviewer). agy also
  injects the workspace's AGENTS.md and GEMINI.md into children (EGM issue #237), so the
  challenger's `omitClaudeMd` isolation does not carry over: said in the agy brief.
- **Builder proof** under agy: `PostInvocation` steers ("the report lacks command and exit
  code: send it back"); README and the agy brief say it is requested, not enforced.
- **Install at work**: from a clone at a release tag, `agy plugin install <clone>/plugins/cobot`
  (user scope); a refresh is uninstall then install. The repository must be reachable from work:
  public (the 0.2.0 cut) or a work mirror. Install by URL needs the plugin at a repository root,
  which cobot's is not. The facts above are re-read on the work machine's `agy` version (1.5.6
  here by now) and recorded in `docs/harnesses.md` (E7).
- No generator and no dist folder. A release ZIP with `SHA256SUMS` and attestation (E3, E6) is a
  later convenience, not a need.

## What EGM offers, challenged

| # | Idea (EGM path) | Take? | Why |
|---|---|---|---|
| E1 | Thin per-host agent adapters over canonical persona text (`.claude-plugin/agents/*.md` → `agents/*.md`) | **inverted** | cobot keeps the canonical text with Claude Code (primary, no extra read); the agy agent points to it or carries a synced copy |
| E2 | No committed generated copy (`claude_release_branch_distribution.md`) | **yes** | their own failure, the exact plan cobot had |
| E3 | Packer refusals: allowlist, required files, no symlinks or path escape, manifest references inside the bundle, reproducible ZIP (`scripts/pack_plugin.py`) | **later** | only if a release ZIP is added; the tree is installed as it is |
| E4 | Skill body size test (`tests/unit/test_skill_load_limits.py`, 24 000 bytes on agy) | **yes** | one line in `check-plugin`; cobot is at 16 956 |
| E5 | Manifest drift test (`test_compatibility_metadata_matches_root`) | **yes** | two manifests now |
| E6 | Draft-only, attested release with `SHA256SUMS` (`release.yml`) | **later** | cobot's release ships no artifact today; with B it would |
| E7 | Harness record: install, workflow and isolation results per host version and date (`TESTING.md`), "write `not run` for a check you did not run" | **yes** | `docs/harnesses.md`, the agy smoke result with the version |
| E8 | Review loop: converged = two clean rounds, cap 5, a failed reviewer is `not run`, never zero findings (`skills/egm-review-loop`) | **one rule** | "a reviewer that did not run is `not run`" goes into wrap and spec; the loop itself overlaps the challenger's passes |
| E9 | Drift report: docs against code, divergences only (`skills/egm-drift-report`) | **later** | overlaps spec converge and knowledge staleness; a wrap check could use it |
| E10 | Document standards handed to reviewers as a named target (`resources/document_standards`) | **later** | the challenger could get the spec template as its standard; not needed for agy |
| E11 | `test_scenarios.yaml` per skill | **no** | no runner exists (EGM says so); cobot's evals run |
| E12 | One question at a time, design-only, a synthesizer that writes files (`execution_instructions.md`) | **no** | against cobot's batched clarify, build path and "agents never write `.agent/`" |
| E14 | No subagent tool → stop, never simulate a fresh reviewer inline (`skills/egm-review`) | **yes** | the agy rule for `context: fork` skills |
| E13 | Copying EGM text | **no** | Apache-2.0 into MIT needs the licence and notices per file; ideas are reimplemented, nothing copied |

## Spikes left (the owner's terminal, signed in; before the spec is built)

- S3 `agy -p` in a temporary HOME with the plugin installed from a scratch copy: the gate hook
  fires on `run_command` and denies `git push --force`; it fires inside an `invoke_subagent`
  child; a hook that exits 1 lets the call through (confirms fail open); `injectSteps` carries a
  6 000-character brief; an adapter agent can read `claude-agents/<n>.md`.
- S4 `agy plugin import claude` on this machine: what it carries of cobot (a free second path).

## Challenger verdict

2026-11-11, one pass: **SOUND WITH CHANGES**, fifteen points, all folded above. BLOCKER: the gate
failed open whenever `python3` itself fails (agy ignores exit codes) → a shell shim that prints
deny; `bin/` is not on PATH under agy and skill text is not expanded → the agy brief gives the
absolute path. MAJOR: agy's `allow` is Claude Code's silence and `auto_approve` is the widening
value → contract "never widens", `auto_approve` never emitted; `ask` respects cached grants →
`force_ask`; the matcher missed tools and a missing path passed → `.*`, unknown asks,
`define_subagent` denied; agent-scoped rules vanish without an agent identity → no
`run_command` for the read-only agents; agy's settings and `agy plugin disable` were ungated →
`never` rows; E1 was the inverse of EGM's direction → trade-off recorded; fork and user-only
skills degrade silently → routed or refused, E14 added. MINOR: readers of `agents/` move to the
manifest list; agy tool names checked; `mainAgent: false`; facts re-read on the work machine's
version; the owner layer stays under `~/.claude`.

## Open questions for the owner

1. 0.2.0: cut it now (public, so work can reach the repository) with `/cobot:ship` and the paid
   eval run carried into 0.3.0, or hold 0.2.0 until both are done?
2. 0.3.0 scope: Antigravity only, with session grants, debug and cobot-reverse moved to 0.4.0, or
   Antigravity first inside a larger 0.3.0?
3. Builders under agy if S3 shows subagent calls are not gated: main thread only (no builders)
   under agy, or builders allowed with the risk written down?
4. Session grants under agy: agy's `allow` defers and only `auto_approve` stops a prompt, so a
   granted command would need cobot to emit the widening value. Leave grants Claude Code only
   in 0.3.0?
