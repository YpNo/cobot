# Spec — Host-agnostic core, pure packaging, explicit Gemini tiers, and agy 1.5.11 alignment

size: large · profile: library · owner: YpNo · date: 2026-11-19 · rebased onto `main` `356b6ff` (`feat/agy-agnostic`: `e7b45cb`..`4a847ff` + adaptations)

## Goal

Keep Claude Code as the full reference host while making `cobot` genuinely host-agnostic in source
and native to Antigravity CLI (`agy >= 1.5.11`): zero context leakage, zero validation warnings on
the installed bundle, XDG owner configuration for agy-only machines, task-matched Gemini model
tiers with owner/project overrides, execution-mode-aware gating (`ask` vs `force_ask`), and
coverage of `agy 1.5.11` `swarm` and MCP resource tools.

## Root causes identified on `agy 1.5.11`

Live probing (`agy plugin install`, `agy plugin list --json`, `agy plugin validate --strict`) and
code inspection exposed six gaps in the single-tree 0.3.0 baseline (`ADR-0007`):

1. **`rules/default.rules` prompt pollution.** `agy` loads files under `plugins/<name>/rules/` as
   system-prompt instructions (truncated at 24 KB from a 20k-token budget). Putting cobot's
   internal policy DSL (`plugins/cobot/rules/default.rules`) there leaked ~24 KB of `never`/`ask`
   patterns into every `agy` turn (`"rules": ["default.rules"]`).
2. **Claude-coupled prompt & config vocabulary.** `protocol.md`, workflow `SKILL.md` files, and
   `cobot-session` hardcoded `/cobot:<skill>`, `cobot:<agent>`, `Explore`, `isolation: worktree`,
   `/code-review`, `/security-review`, `view_file` (absent on Gemini 4 Carbon in main thread, which
   exposes `read_file`/`write_file`/`edit_file`), and `~/.claude/cobot*` owner paths.
3. **Suboptimal agent tiers under `agy`.** Mapping Claude `sonnet` to `flash` forced all six
   builders and `consultant` onto `flash`, while owner intent called for explicit task-matched
   Gemini tiers rather than blanket `inherit`.
4. **Over-aggressive `force_ask` breaking `auto` and `accept-edits` modes.** Emitting `force_ask`
   for every `ASK` bypassed `agy`'s per-session *Always Allow* cache even for local repeatable dev
   steps (`git commit`, `uvx`, `npx`, `uv add`, opaque `make`).
5. **Unmapped `agy 1.5.11` tools.** `swarm`, `post_message`, `read_board`, `swarm_wait`,
   `list_resources`, and `read_resource` fell through as unknown tools.
6. **Lost scanner/history signal in read-only sweeps.** Because `agy` subagent hooks omit agent
   identity, `auditor`/`consultant` lack `run_command`; the main-thread router has `run_command`
   under the gate and can run read-only scanners and `git log` itself and pass outputs as data.

## Owner decisions (2026-11-18 / 2026-11-19)

Recorded in [ADR-0008](../../docs/adr/0008-host-agnostic-core-and-agy-modes.md) and Decision 33 of
[docs/01-decisions.md](../../docs/01-decisions.md):

1. **Packaging architecture — Option C (canonical core + pure per-host build).**
   - Rejected keeping a mixed single-tree install (fails `agy plugin validate --strict` and risks
     cross-host directory collisions) and rejected committing two duplicated `plugins/cobot*`
     copies in git.
   - Adopted one canonical source tree (`plugins/cobot/`) holding host-neutral `agent-defs/*.md`,
     shared `skills/`, `bin/`, and `policy/default.rules` (`rules/` forbidden by `check-plugin.py`).
     `scripts/package-plugin.py --host agy|claude --out <dir>` stages pure, host-clean bundles
     used by `install.sh --agy` (with randomized hook group renaming `cobot-<hex>`) and by
     `release.yml` (`cobot-agy.zip`, `cobot-claude.zip`).
2. **Owner configuration path.**
   - Default to `$COBOT_CONFIG_DIR`, else `$CLAUDE_CONFIG_DIR/cobot`, else existing
     `~/.claude/cobot*` (100% backward compatible), else `$XDG_CONFIG_HOME/cobot` (`~/.config/cobot/`).
   - Protect `~/.config/cobot/*` and `~/.config/cobot.rules` with `never` rules in `policy/default.rules`.
3. **Mode-aware gate granularity & `sync --runtime agy`.**
   - Under `agy`, emit `ask` (honoring session *Always Allow* in `auto`/`accept-edits`/`default`)
     only when every matching ask in a command is a local repeatable dev rule or opaque local dev
     runner (`make`, `just`, `uvx`, `npx`, `npm run`).
   - Emit strict `force_ask` (ignoring *Always Allow*) for outward, destructive, credential,
     privilege, `run_workflow`, `swarm add`/`model`, shell-wrapper, and mixed calls.
   - Keep `never` as `deny` and never emit `auto_approve`.
   - Provide `cobot-rules sync --runtime agy` printing `~/.gemini/antigravity-cli/settings.json`
     diff blocks without editing host settings (ADR-0003).
4. **Explicit task-matched Gemini tiers + overrides (not blanket `inherit`).**
   - Owner rejected defaulting every agent to `inherit`: `agents/*.md` uses `pro` for `challenger`,
     `auditor`, `learner`, and the 5 language builders (`rust-`, `go-`, `python-`, `typescript-`,
     `terraform-builder`), and `flash` for `consultant` (parallel domain checklists) and generic
     `builder`.
   - Runtime/owner/project overrides resolve in order: trusted `.agent/models.json` <
     `~/.config/cobot/models.json` < `--models <file>` < `COBOT_AGENT_MODELS` (including `*`/global
     keys and dynamic `invoke_subagent(Model=...)`). `swarm` roles map to Gemini 4 `Carbon` /
     `Hydrogen` / `Argon` / `Flash`.

## Implementation plan (`T01` → `T08`, TDD)

All eight tasks landed on `feat/agy-agnostic` (rebased onto `main` `356b6ff`):

| Task | Scope | Commit | Primary files |
|---|---|---|---|
| **T01** | Move `rules/default.rules` → `policy/default.rules`; create pure packager & hook-group randomizer; wire `install.sh --agy` and `check-plugin.py` | `e7b45cb` | `plugins/cobot/policy/default.rules`, `scripts/package-plugin.py`, `scripts/check-plugin.py`, `install.sh`, `bin/cobot-rules` |
| **T02** | Host-agnostic XDG `~/.config/cobot/` with `~/.claude/cobot*` fallback and self-protection rules | `b916c95` | `bin/_cobot_common.py`, `bin/cobot-rules`, `bin/cobot-env`, `policy/default.rules` |
| **T03** | Canonical `agent-defs/*.md`, symmetric `sync-agents.py`, explicit Gemini tiers (`pro`/`flash`), multi-level model overrides, `read_file` in `agy` toolset | `ec0ace3` | `plugins/cobot/agent-defs/*.md`, `scripts/sync-agents.py`, `bin/_cobot_agy.py`, `bin/_cobot_common.py`, `scripts/package-plugin.py`, `scripts/check-plugin.py` |
| **T04** | Split `ask` (local repeatable dev) vs `force_ask` under `agy` and add `cobot-rules sync --runtime agy` | `4f7fcb8` | `bin/cobot-rules`, `tests/test_gate_agy.py`, `tests/test_cobot_rules.py` |
| **T05** | Govern `agy 1.5.11` `swarm`, board tools (`post_message`, `read_board`, `swarm_wait`), and `list_resources`/`read_resource` | `5e23672` | `bin/_cobot_agy.py`, `bin/cobot-rules`, `tests/test_gate_agy.py` |
| **T06** | Neutralize `protocol.md`, `cobot-session` (+ agy host adapter & active model overrides), and 10 workflow `SKILL.md` files | `934dc40` | `plugins/cobot/protocol.md`, `bin/cobot-session`, `plugins/cobot/skills/*/SKILL.md`, `tests/test_cobot_session.py` |
| **T07** | Write ADR-0008, update `antigravity-mechanics.md`, `release.yml`, `README.md`, `architecture.md`, `configuration.md`, `CHANGELOG.md` | `dbb5f7a` | `docs/adr/0008-*.md`, `docs/reference/antigravity-mechanics.md`, `.github/workflows/release.yml`, `README.md`, `docs/*.md`, `CHANGELOG.md` |
| **T08** | Update `smoke-agy.sh` (pure bundle check + gate mode probe), update `harnesses.md` (`1.5.11` validate/install ok) and `JOURNAL.md` | `24636d3` | `scripts/spikes/smoke-agy.sh`, `docs/harnesses.md`, `.agent/JOURNAL.md` |

## Post-rebase adaptations (`main` `356b6ff` — PRs #74 & #75)

Rebasing `feat/agy-agnostic` onto PR #74 (`memory-and-ship`, Decision 31) and PR #75
(`builder-proof-hosts`, Decision 32) required five targeted parity and conflict adaptations:

1. **Repeated-ask owner allow suggestion in `gate_agy` (`cobot-rules`).**
   - `main` wired `with_offer()` only into Claude Code's `gate()` using `session_id`.
   - Extracted `_judge_plan_with_rules()` (keeping `judge_plan() -> Verdict` unchanged) and wired
     `with_offer(reason, verdict, payload.get("conversationId"), rules)` into `gate_agy()` when
     `name == "run_command"` and `verdict.decision == ASK`, suggesting `allow Bash(git commit*)`
     or `allow Bash(git rebase*)` in `~/.config/cobot/cobot.rules` (or legacy path) from ask #3.
2. **Host-agnostic `COBOT_CONFIG_DIR` prefix in `cobot-memory` & `onboard/SKILL.md`.**
   - `main`'s `config_prefix()` checked only `CLAUDE_CONFIG_DIR`; updated it to check
     `COBOT_CONFIG_DIR` before `CLAUDE_CONFIG_DIR` so `trust not recorded:` owner commands preserve
     XDG/custom `COBOT_CONFIG_DIR` runs. Updated `skills/onboard/SKILL.md` to document both.
3. **`FOREGROUND` dual-host invariant + `stamp --tree` + `noticed` in workflow skills.**
   - Resolved T06 conflicts in `build`, `wrap`, `ship`, `spec`, `consult`, and `security-sweep` by
     keeping both invariants required by `scripts/check-plugin.py` / `tests/test_workflow_skills.py`
     (``"`run_in_background: false` where the host offers it"`` + `"wait for every hand-back"`),
     alongside `agy` (`invoke_subagent`, `Workspace="share"`, `plan` mode), `cobot-memory stamp --tree`,
     `UNPROVEN:`, and `/ship` ground checks (`cobot-deps check` toolchain pins + `git ls-remote`).
4. **Builder proof & `Noticed:` under `agy` (no hook intercept on tool outputs).**
   - Verified in `agy 1.5.11` (`hooks.md`): `PostToolUse` omits tool output (`tool_response`) and
     `SubagentHandback` does not exist. Documented this in `docs/reference/antigravity-mechanics.md`
     and updated `skills/build/SKILL.md` so the orchestrator verifies proof and calls
     `cobot-memory noticed add` manually for both `invoke_subagent` and `swarm` workers.
5. **Decision numbering sync (`Decision 31` → `Decision 33`).**
   - PR #74 and PR #75 claimed Decisions 31 and 32 in `docs/01-decisions.md`; renumbered this
     feature's decision to **Decision 33** across `docs/01-decisions.md`, `CHANGELOG.md`,
     `.agent/CONTEXT.md`, and this spec.

## Verification & known gaps

- Passed on rebased branch: `ruff` check & format, `shellcheck`, `check-plugin.py`,
  `sync-agents.py --check`, `markdownlint-cli2`, `cobot-memory check`, targeted `agy`/workflow/memory
  tests (`test_gate_agy.py`, `test_workflow_skills.py`, `test_check_plugin.py`, `test_cobot_memory.py`
  except macOS `\xff` filename), and throwaway-HOME `./install.sh --agy` + `agy plugin validate --strict`
  (0 warnings, `rules 0`, `skills 30`, `agents 10`, `hooks 1`).
- macOS APFS/symlink environment failures in untouched Linux-assumed upstream tests: 4 in
  `tests/test_cobot_rules.py` (line 694 `/etc` symlink; lines 3841 and 3913 case-insensitive
  `Dockerfile`) and 1 in `tests/test_cobot_memory.py` (`test_stampReadiness_nonUtf8Name_noCrash`,
  APFS `[Errno 92]` on raw `\xff` filename).
- Live signed-in `smoke-agy.sh` (real HOME) and live `swarm`/subagent runs remain `not run` inside
  the sandboxed workspace until executed in the owner's terminal (`./install.sh --agy && sh scripts/spikes/smoke-agy.sh`).
