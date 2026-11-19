# Spec — Host-agnostic core, pure packaging, explicit Gemini tiers, and agy 1.5.11 alignment

size: large · profile: library · owner: YpNo · date: 2026-11-19 · built on `main` `97c48dc` (`feat/agy-agnostic`: `cb3d187`..`b5a4adb`)

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

Recorded in [ADR-0008](../../docs/adr/0008-host-agnostic-core-and-agy-modes.md) and Decision 31 of
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

All eight tasks landed on `feat/agy-agnostic`:

| Task | Scope | Commit | Primary files |
|---|---|---|---|
| **T01** | Move `rules/default.rules` → `policy/default.rules`; create pure packager & hook-group randomizer; wire `install.sh --agy` and `check-plugin.py` | `cb3d187` | `plugins/cobot/policy/default.rules`, `scripts/package-plugin.py`, `scripts/check-plugin.py`, `install.sh`, `bin/cobot-rules` |
| **T02** | Host-agnostic XDG `~/.config/cobot/` with `~/.claude/cobot*` fallback and self-protection rules | `9524e65` | `bin/_cobot_common.py`, `bin/cobot-rules`, `bin/cobot-env`, `policy/default.rules` |
| **T03** | Canonical `agent-defs/*.md`, symmetric `sync-agents.py`, explicit Gemini tiers (`pro`/`flash`), multi-level model overrides, `read_file` in `agy` toolset | `eb729d8` | `plugins/cobot/agent-defs/*.md`, `scripts/sync-agents.py`, `bin/_cobot_agy.py`, `bin/_cobot_common.py`, `scripts/package-plugin.py`, `scripts/check-plugin.py` |
| **T04** | Split `ask` (local repeatable dev) vs `force_ask` under `agy` and add `cobot-rules sync --runtime agy` | `d41c6b2` | `bin/cobot-rules`, `tests/test_gate_agy.py`, `tests/test_cobot_rules.py` |
| **T05** | Govern `agy 1.5.11` `swarm`, board tools (`post_message`, `read_board`, `swarm_wait`), and `list_resources`/`read_resource` | `ade5185` | `bin/_cobot_agy.py`, `bin/cobot-rules`, `tests/test_gate_agy.py` |
| **T06** | Neutralize `protocol.md`, `cobot-session` (+ agy host adapter & active model overrides), and 10 workflow `SKILL.md` files | `715b43f` | `plugins/cobot/protocol.md`, `bin/cobot-session`, `plugins/cobot/skills/*/SKILL.md`, `tests/test_cobot_session.py` |
| **T07** | Write ADR-0008, update `antigravity-mechanics.md`, `release.yml`, `README.md`, `architecture.md`, `configuration.md`, `CHANGELOG.md` | `7df290d` | `docs/adr/0008-*.md`, `docs/reference/antigravity-mechanics.md`, `.github/workflows/release.yml`, `README.md`, `docs/*.md`, `CHANGELOG.md` |
| **T08** | Update `smoke-agy.sh` (pure bundle check + gate mode probe), update `harnesses.md` (`1.5.11` validate/install ok) and `JOURNAL.md`, run full verification | `b5a4adb` | `scripts/spikes/smoke-agy.sh`, `docs/harnesses.md`, `.agent/JOURNAL.md` |

## Verification & known gaps

- Passed on `b5a4adb`: `ruff` check & format, `shellcheck`, `check-plugin.py`, `sync-agents.py --check`,
  `markdownlint-cli2` (145 files), `cobot-memory check`, targeted `agy`/session/plugin tests, and
  throwaway-HOME `./install.sh --agy` + `agy plugin validate --strict` (0 warnings, `rules 0`,
  `skills 30`, `agents 10`, `hooks 1`).
- Full `pytest --cov=plugins/cobot/bin --cov-fail-under=85` reached **98.25%** coverage with 4
  pre-existing macOS environment failures in `tests/test_cobot_rules.py` (line 694 `/etc` symlink
  to `/private/etc`; lines 3841 and 3913 APFS case-insensitive `Dockerfile` vs `dockerfile`).
- Live signed-in `smoke-agy.sh` (real HOME) and live `swarm`/subagent runs remain `not run` inside
  the sandboxed workspace until executed in the owner's terminal (`./install.sh --agy && sh scripts/spikes/smoke-agy.sh`).
