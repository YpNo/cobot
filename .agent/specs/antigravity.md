# Spec — 0.3.0: cobot under the Antigravity CLI from one tree

size: large · profile: library · owner: YpNo · date: 2026-11-12, facts re-read 2026-11-15 (agy 1.5.9)

## Goal

The owner works in the Antigravity CLI (`agy`) at work and needs cobot there. This change makes
`plugins/cobot/` install as it is in both runtimes. Claude Code keeps everything it has. Under
agy, cobot keeps four things:
- the rules gate, failing closed by its answer, since agy ignores a hook's exit code;
- the session brief;
- the skills;
- the nine agents.

What agy cannot carry is named, not hidden:
- builder proof is requested, not enforced;
- `context: fork` skills run through a subagent or are refused;
- agent-scoped rules have no agent identity to match.

Shape, facts (re-read on agy 1.5.9, 2026-11-15) and the challenged ideas from
google/elephant-goldfish-model: `docs/design-inputs/antigravity-0.3.0.md` (owner decisions 2026-11-11: 0.2.0 tagged first, 0.3.0
Antigravity only, builders allowed under agy with the gap written, grants later for both
runtimes).

What does not change:
- the rules, their precedence and the layers;
- the memory and its trust;
- the Claude Code hooks;
- the evals;
- the protocol text, which stays within 3 000 characters (the agy differences live in the agy
  brief).

## Principles check

- Proportionality: large (a second runtime, a trust boundary at its gate); the challenger runs, the
  spec is one PR.
- Rules before autonomy: the gate never widens in either runtime; under agy "no opinion" is
  `allow` (agy's defer), asks are `force_ask`, `auto_approve` is never emitted (a test scans every
  output); self-protection extends to agy's settings and `agy plugin disable|uninstall|link`.
- Knowledge is a skill: no new skill; the agy facts are dated in `docs/harnesses.md` and
  `docs/reference/antigravity-mechanics.md`.
- Proof, not promises: every story has its command; the live behaviour (hooks in subagents, fail
  open, MCP names) is proven by `scripts/spikes/smoke-agy.sh` on the owner's signed-in agy and
  recorded with the version, `not run` where it did not run.
- Governance (`docs/01-decisions.md`):
  - **decision 1** ("Claude Code only") is amended to "Claude Code first; the Antigravity CLI
    supported from the same tree, its gaps named", through ADR-0007;
  - decisions 18 (no attribution), 20 (one spec, one PR) and 22 (no unnamed dependency) hold;
  - ADR-0003 (nothing writes the owner's `~/.claude` files) holds, and its spirit extends to
    `~/.gemini`: install writes only through `agy plugin install`;
  - the others are not relevant.
- Architecture: plain layering; one adapter function per runtime at the gate's and the session's
  edge, the policy stays single.
- New dependencies: none (standard library, POSIX sh).
- Delivery: one branch `feat/antigravity` (it carries the design input's two commits), one PR;
  tasks below are the commits.

## Stories and acceptance

1. **One tree, two validators.** As the owner, `plugins/cobot/` passes `claude plugin validate
   --strict` and `agy plugin validate` with exactly one warning (agy: `hooks/hooks.json` never
   loaded).
   - Claude Code's nine agents live in `claude-agents/`, listed by file in
     `.claude-plugin/plugin.json` `agents`; agy's nine in `agents/`.
   - `.antigravity-plugin/plugin.json` carries the same `name`, `version`, `description`,
     `license`, `repository`.
   - Accept: `python3 scripts/check-plugin.py` exit 0 with new checks:
     - the two manifests agree;
     - every `claude-agents/<n>.md` has `agents/<n>.md`;
     - agy agents name only known agy tools (a table in `check-plugin`), as a YAML list;
     - `model` is in `inherit|flash|pro` (`flash_lite` exists, unused) and `mainAgent: false`;
     - every SKILL.md body is under 24 000 bytes;
     - every frontmatter parses as strict YAML (the `onboard` `argument-hint` is quoted);
     - the agent-listing budget reads the manifest's list;
     - the manifest's `agents` list equals the files in `claude-agents/`.
   - Also: `pytest tests/test_check_plugin.py`; both validators in the full set when the
     binaries exist.
2. **Agy agents keep their limits.** As the owner, each agy agent has the tools its Claude twin
   has, mapped by one table to both agy families (the toolset varies by model): Read →
   `view_file`, `read_file`; Grep → `grep_search`; Glob → `find_by_name`, `list_dir`; Edit →
   `replace_file_content`, `multi_replace_file_content`, `edit_file`; Write → `write_to_file`,
   `write_file`; Bash → `run_command`, `manage_task` (to poll an async command); WebFetch → `read_url_content`; WebSearch → `search_web`;
   Skill and Agent have no agy tool and are dropped.
   - The consultant and the learner get no `run_command` (their `@agent` read lists cannot
     apply: no agent identity reaches agy hooks), and `commandExecutionPolicy: off`.
   - Models: `sonnet` → `flash`, `inherit` → `inherit`, except the learner → `pro`: agy ignores
     `effort`, and the learner relies on `effort: high`.
   - The agy body is the Claude body, copied by `scripts/sync-agents.py`, which rewrites the one
     line that says to call a skill "with the Skill tool" into "read
     `<plugin>/skills/<name>/SKILL.md` with `view_file`" (the orchestrator puts the absolute
     plugin path in every builder brief). agy's `skills:` preload is not relied on.
   - Named gap: without `run_command`, the agy consultant loses its read list (`git log`, `gh api`
     GET, `zizmor`), so `/cobot:consult` and security-sweep read files only under agy.
   - Accept: `pytest tests/test_agents_sync.py -k agents_`. The failure message names `python3
     scripts/sync-agents.py`; a body edit is the only change that can trip it.
3. **The gate under agy, fail closed by its answer.** As the owner, a root `hooks.json` group
   `cobot` sends every tool call (`matcher: ".*"`, `timeout: 10` set explicitly) to `sh
   ./hooks/gate-agy.sh`.

   The shim:
   - buffers stdin to a `mktemp` file, since a background job reads `/dev/null`;
   - runs `python3 -I ./bin/cobot-rules gate --runtime agy` under an internal 8 s deadline
     (`gate` gains the `runtime` option in its parser table);
   - prints `{"decision":"deny","reason":"cobot gate: …"}` with exit 0 when `python3` is
     missing, older than 3.12, exits non-zero, prints nothing, prints anything not starting with
     `{"decision"`, or times out.

   Named gap: the shim's own launch failing (no `sh`) still fails open.

   **Project folder.** agy hooks run in the plugin folder. The project layer comes from
   `workspacePaths`, never from `run_command`'s `Cwd` (model-written, present on some models) or
   the stdin `cwd`: the layers of every listed path apply, so a `Cwd: /tmp` cannot drop a project
   `never`. `Cwd`, else `cwd`, serves only Makefile, mise and package.json expansion. With no
   `workspacePaths`, a call that needs the
   project gets `force_ask`. A test proves a project-layer `never` applies whatever `Cwd` says.

   **Mapping:**
   - `run_command.CommandLine` → Bash `command`;
   - `manage_task` `Input` → Bash, never below `force_ask` (the reader may be a REPL or `ssh`);
   - `write_to_file`, `replace_file_content`, `multi_replace_file_content` (`TargetFile`) and
     `write_file`, `edit_file` (`Path`) → Write / Edit `file_path`, the parent resolved with
     `realpath`; a relative path gets `force_ask`;
   - MCP: `call_mcp_tool` `ServerName` and `ToolName` → `mcp__<server>__<tool>`. An eager
     `mcp_<rest>` is split at a known server name, read at each call from agy's MCP configuration
     and the installed plugins' servers, named `<plugin>_<server>` (files in the mechanics doc). For an unknown server it is judged at every `_` and
     the strictest verdict wins, and any split that hits a `never` denies. So
     `mcp_vertex_search_delete_index` cannot pass as a read.

   **Verdicts:** `allow` (no opinion), `force_ask` or `deny`, with the rule as `reason`.

   **Tools by name:**
   - read tools (`view_file`, `read_file`, `list_dir`, `find_by_name`, `grep_search`,
     `read_url_content`, `search_web`, `view_code_item`) and orchestration tools (`ask_question`,
     `send_message`, `list_permissions`, `ask_permission`, `finish`, `skill_search`, `schedule`
     without `TimerCondition`, `manage_task` `list|status|kill`, `manage_subagents`
     `list|kill|kill_all`) → `allow`; any other action or argument → `force_ask`;
   - `invoke_subagent` → `allow` when every spec's `Workspace` (flat args or the `Subagents`
     array) is absent or `inherit`, or `branch`/`share` while `.agent/cobot.rules` has no
     uncommitted change (a new workspace reads the committed rules), `force_ask` otherwise;
   - `run_workflow` → `force_ask`, its reason naming the `ScriptPath` file's sha256 and "workflow
     agents not proven gated" (inside a workflow agy denies an unapproved ask);
   - `define_subagent` → `deny`;
   - any other tool, or a file tool without its path argument, → `force_ask`.

   Accept:
   - `pytest tests/test_gate_agy.py`:
     - a payload per tool;
     - every failure path of the shim run as a subprocess (empty, garbage, timeout, exit 1);
     - project-layer rules through `workspacePaths`;
     - each MCP split, with `never mcp__gcp-*` rows and read names;
     - a corpus test that no output contains `auto_approve`;
     - the Claude Code gate tests unchanged;
   - shellcheck on the shim.
4. **Self-protection for agy.** As the owner, the default rules deny:
   - editing or writing `~/.gemini/antigravity-cli/settings*.json`, `~/.gemini/config/**` (hooks,
     `config.json` enablement, MCP servers, every installed plugin), `~/.gemini/jetski/**`
     (command sidecars, access grants), and in every customization root (`.agents`, `.agent`,
     `_agents`, `_agent`, at any depth) `hooks.json`, `plugins.json`, `skills.json` and
     `plugins/**`: a hook or plugin there runs outside the gate and may answer `auto_approve`;
   - `agy plugin*` and `agy plugins*` `disable`, `uninstall` and `link` forms naming cobot.

   They ask on every `agy` invocation (`ask Bash(agy*)`, reason "may replace or bypass the cobot
   gate": `agy plugin install` replaces in place, a nested `agy -p` is outside the gate) and on
   `install.sh`. A default rule cannot carve out the read forms, so the
   README proposes the owner line `allow Bash(agy plugin validate*)`.

   Accept: `pytest tests/test_cobot_rules.py -k agySelf`, with `cobot-rules check` rows for each
   form, the `plugins` alias included.
5. **The agy brief.** As the model under agy, the session starts with `cobot-session start
   --runtime agy`, which:
   - prints one `injectSteps` system message, not `userMessage`, which agy presents as the owner's
     own words: committed memory must not read as the owner's instruction. One documented shape,
     one constant: `{"injectSteps":[{"systemMessage":{"systemMessage":…}}]}`;
   - briefs the project through `workspacePaths[0]` (hooks run in the plugin folder), and says
     "project unknown" without it.

   Order: the protocol, then the agy section (at most 1 200 characters), then the rule counts and
   the memory brief, whose budget shrinks by the agy section, so the cap never cuts the agy part.
   The agy section holds:
   - the absolute plugin and `bin/` paths, and how to call `cobot-memory`, `cobot-rules` and
     `cobot-deps` through them (agy puts nothing on PATH);
   - Claude tool names to agy's (Agent → `invoke_subagent`, AskUserQuestion → `ask_question`,
     Skill → read the skill file, or the `/name` command);
   - the owner types onboard, rules and security-sweep;
   - security-sweep and learn run through `invoke_subagent` or not at all, never inline;
   - builder proof is requested, not enforced;
   - children receive the workspace's AGENTS.md and GEMINI.md;
   - builders' tool calls are not proven gated, until the smoke says otherwise.

   The serialised JSON stays within 10 000 characters. A hook failure prints the protocol alone.

   Accept: `pytest tests/test_cobot_session.py -k agy` (shape, serialised length, section
   order, bin path, `workspacePaths`, the error path).
6. **Install at work.** As the owner:
   - `./install.sh --agy` runs `agy plugin validate` on `plugins/cobot`, then `agy plugin install
     "$root/plugins/cobot"`;
   - the same command refreshes (agy replaces the copy atomically and restores the previous one
     on failure; never uninstall first); the README says to run it with no agy session open, and
     a failed install is loud; `--agy` is a modifier, not the last-wins action;
   - `./install.sh --check` reports agy's plugin state when `agy` is on PATH;
   - the README says to clone at a release tag.

   ADR-0003 holds: nothing else is written. Accept: `pytest tests/test_install.py -k agy`, with
   `agy` faked on PATH, argv recorded, both flag orders and the failed-install path.
7. **Memory beside agy's discovery.** As the orchestrator, `cobot-memory check` warns when
   `.agent/` holds `skills`, `rules`, `workflows`, `plugins`, `hooks.json`, `plugins.json` or
   `skills.json`: `.agent/` is also an agy customization root, so agy loads them.
   - Accept: `pytest tests/test_new_project.py -k agyLegacy` (or the memory tests).
8. **The record.** As the owner, the change carries:
   - ADR-0007 (decision 1 amended);
   - `docs/reference/antigravity-mechanics.md` (dated facts, sources);
   - `docs/harnesses.md`: one row per runtime and version, with install, gate, brief and agents
     marked `ok`, `fails` or `not run`;
   - a README Antigravity section with the named gaps;
   - `docs/architecture.md` and `docs/configuration.md` rows;
   - the CHANGELOG;
   - in wrap and spec, the line "a reviewer that did not run is `not run`, never clean" (E8);
   - version 0.3.0 in both manifests and the marketplace;
   - `release.yml` checks that the two manifests agree with the tag.

   `scripts/spikes/smoke-agy.sh` runs in the owner's terminal, signed in, with their real HOME.
   It works only inside a scratch git repository it creates, whose `origin` is a local bare
   repository (a forced push can harm nothing). It uses `agy -p --output-format json` with a
   print timeout and never `--dangerously-skip-permissions`. It checks:
   - the gate denies `git push --force` in the main thread and inside an `invoke_subagent`
     child;
   - a throwaway workspace hook in the scratch repo's `.agents/hooks.json` that prints
     `{"decision":"deny"}` and then exits 1, removed after: if the call runs, agy ignores a
     failing hook's output;
   - inside a `run_workflow`, a `call_tool` and an `agent()` attempting `git push --force`;
   - a `branch` child after an uncommitted `.agent/cobot.rules` line;
   - a workspace hook named `cobot` with `"enabled": false` (a name clash) cannot disable the gate;
   - the brief arrives as a system message;
   - an MCP call's name form;
   - `/cobot:onboard` reaches `cobot-memory check` through the brief's path.

   S4 (`agy plugin import claude`) writes the real `~/.gemini`, so it is `not run` unless the
   owner asks. The results go into `docs/harnesses.md`.

   Accept: markdownlint; `sh -n` and shellcheck on the smoke script; the harness row is filled
   from a run or says `not run`.

## Clarify

The four questions that were expensive to undo were asked and answered on 2026-11-11 (design
input, Owner decisions). Decided here without asking:
- the agy agent body is a synced copy, not a pointer: no subagent read is proven, and a copy works
  without one;
- `install.sh --agy` covers install and refresh (one command), user scope only;
- the PostInvocation hook is dropped: it sees neither a subagent's report nor a tool result, so
  proof lives in the brief.

## Plan

T01 (the tree split) first; then the safety-carrying parts test first (gate, shim,
self-protection, brief); install, memory, sync; docs and the smoke script; the owner's smoke run
fills the harness record before the PR.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | Tree split: `git mv agents/*.md claude-agents/`; `.claude-plugin/plugin.json` `agents` list; `.antigravity-plugin/plugin.json`; quote `onboard`'s `argument-hint`; `check-plugin`, `install.sh` `report_overlaps`, `test_cli_flags` and the mechanics note read the manifest list; the new `check-plugin` checks (manifest agreement, strict YAML frontmatter, 24 000-byte skill bodies). Proof: `python3 scripts/check-plugin.py`; `pytest tests/test_check_plugin.py tests/test_cli_flags.py`; `claude plugin validate plugins/cobot --strict` | — | — | — |
| T02 | `scripts/sync-agents.py` and the nine agy agents in `agents/`: tool map, model map, `mainAgent: false`, `commandExecutionPolicy: off` and no `run_command` for consultant and learner, bodies copied; `check-plugin` agy-agent checks (known tools, YAML list, tier). Proof: `pytest tests/test_agents_sync.py`; `agy plugin validate plugins/cobot` (one warning) | a | — | T01 |
| T03 | Gate adapter `cobot-rules gate --runtime agy` (project layer from `workspacePaths`, `Cwd` for expansion only, payload mapping incl. `manage_task`, verdicts, read and orchestration tools, `define_subagent` deny, missing path asks, MCP split at the known server, else strictest; `invoke_subagent` `Workspace` outside `inherit|branch|share` asks; `run_workflow` asks; both file-tool families) and `hooks/gate-agy.sh` (stdin buffered, deadline, every failure or non-JSON → deny, exit 0); root `hooks.json` group `cobot` with PreToolUse `.*`, `timeout: 10`, and SessionStart. Proof: `pytest tests/test_gate_agy.py`; shellcheck | b | **risk** (trust boundary) | T01 |
| T04 | Default rules: never Edit/Write of agy's settings, `~/.gemini/config/**`, `~/.gemini/jetski/**`, and `hooks.json`, `plugins.json`, `skills.json`, `plugins/**` in every customization root (`.agents`, `.agent`, `_agents`, `_agent`); never `agy plugin(s) disable|uninstall|link` of cobot; `ask Bash(agy*)` and `install.sh`. Proof: `pytest tests/test_cobot_rules.py -k agySelf` | b | — | T03 |
| T05 | `cobot-session start --runtime agy`: `systemMessage` step, project from `workspacePaths`, agy section after the protocol with the brief budget reduced, serialised cap, the error path. Proof: `pytest tests/test_cobot_session.py -k agy` (or the session tests in `test_cobot_memory.py`) | a | — | T01 |
| T06 | `install.sh --agy` as a modifier, validate then install (it also refreshes), never uninstall first, loud failed install; `--check` agy state; `cobot-memory check` legacy-folder warning. Proof: `pytest tests/test_install.py -k agy`; `pytest -k agyLegacy`; shellcheck `install.sh` | a | — | T01 |
| T07 | Version 0.3.0 in both manifests and the marketplace, `release.yml` manifest-agreement check; docs: ADR-0007, decision 1 note, `docs/reference/antigravity-mechanics.md`, `docs/harnesses.md`, README section, architecture and configuration rows, CHANGELOG, the E8 line in wrap and spec; `scripts/spikes/smoke-agy.sh` (scratch repo, local bare remote, real HOME, no skip-permissions flag, S4 `not run`). Proof: markdownlint, shellcheck, `check-plugin` | — | — | T02–T06 |
| T08 | The owner's smoke run on a signed-in agy; results into `docs/harnesses.md`; any gap it shows becomes a fold or a named gap in README and the brief before the PR | — | — | T07 |

Lanes after T01: a (agents, sync, session, install, memory) and b (`cobot-rules`, the shim,
`hooks.json`, default rules) touch disjoint files. T03 stays with the orchestrator (risk).

## Trade-offs

- One tree over a generated distribution: EGM's committed copy broke their `main`; the agent
  folder split costs one manifest list and nine small files.
- Canonical agent text with Claude Code over EGM's direction (canonical in `agents/`, Claude
  adapters reading it): Claude Code is the primary runtime and pays no extra read; agy gets a
  synced copy checked per file.
- Fail closed by output over trusting exit codes: agy fails open on any non-zero exit, so the
  shim's last word is always a deny line.
- `force_ask` over `ask`: an agy "Always Allow" must not silence a cobot ask.
- No PostInvocation proof hook: it sees no report; a hook that cannot check would only add noise.
- Session grants, the debug path and cobot-reverse are 0.4.0 (owner).

## Challenger verdict

Pass 3 (2026-11-15, the agy 1.5.9 fold): **SOUND WITH CHANGES**, nine folded. BLOCKER: `.agent`,
`_agents`, `_agent` are customization roots too; `config.json`, sidecars, other plugins were open.
MAJOR: `send_input` floors at `force_ask`; workflow `finish` and smoke rows. Six MINOR folded.
Passes 1 and 2 (2026-11-12): SOUND WITH CHANGES, twelve and seven points folded (BLOCKER: hooks or
plugins written outside the gate); in full in the 2026-11-12 journal entry.

## Converge

pending
