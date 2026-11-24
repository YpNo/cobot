# cobot — context

profile: library
goal: a Claude Code plugin marketplace that makes the main thread a governed orchestrator
forge: github  # YpNo/cobot
owner: YpNo · public since 0.2.0 · MIT
governance: docs/01-decisions.md
runs: host

## Stack
- Python 3.12+ stdlib for `plugins/cobot/bin/*`; POSIX sh hooks and `install.sh`; Markdown skills and agents
- pytest + pytest-cov, ruff, shellcheck, markdownlint-cli2, zizmor

## Environment
- Claude Code 2.1.311 locally, CI pins 2.1.322; hooks run as the user
- the directory marketplace serves this checkout to dogfood repos: keep it on `main`, branch in worktrees
- rtk rewrites Bash to `rtk <cmd>`; git has `safe.bareRepository = explicit`

## Verified commands
All exit 0 on 2026-11-24.

| purpose | command |
|---|---|
| tests, coverage gate (98.35 %, 6099 tests) | `uv run --no-project --python 3.13 --with pytest==9.2.0 --with pytest-cov==7.1.0 pytest --cov=plugins/cobot/bin --cov-fail-under=85` |
| lint | `uvx ruff@0.17.6 check . && uvx ruff@0.17.6 format --check .` |
| shell lint | `uvx --from shellcheck-py shellcheck install.sh plugins/cobot/hooks/*.sh scripts/*.sh scripts/spikes/*.sh plugins/cobot/evals/*/fixture.sh` |
| markdown lint | `npx --yes markdownlint-cli2@0.24.2 "**/*.md"` |
| plugin validation | `claude plugin validate plugins/cobot --strict && claude plugin validate . --strict` |
| gate dry run | `plugins/cobot/bin/cobot-rules check "<cmd>"` |
| plugin contract | `python3 scripts/check-plugin.py` |
| memory self-check | `plugins/cobot/bin/cobot-memory check` |
| agy twins in sync | `python3 scripts/sync-agents.py --check` |

## Constraints
- nothing writes to `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills`, `~/.claude/settings.json` (ADR-0003)
- the gate emits `allow` only under a session grant (ADR-0008); a failure blocks (exit 2). agy: `allow`, `force_ask` or `deny`, never `auto_approve`; a failure denies
- agents never write `.agent/`; only the orchestrator and wrap do
- commits: Conventional Commits, no Co-Authored-By; PR bodies never mention Claude Code
- coverage floor 85 % on `bin/`; check-plugin holds the size caps

## Applies / does not apply
- applies: TDD on `bin/`, SHA-pinned actions, Keep a Changelog, SemVer
- does not apply: a service deployment, a database, browser E2E

## Release checks
Verified, run at release or when agy or CI changes; the brief leaves them out.

| purpose | command | result | verified |
|---|---|---|---|
| agy validation (throwaway HOME) | `HOME=$(mktemp -d) agy plugin validate plugins/cobot` | passed, the one hooks/hooks.json warning | 2026-11-22 |
| agy staged install (throwaway HOME) | `HOME=$(mktemp -d) ./install.sh --agy` | exit 0, group cobot-<random> | 2026-11-15 |
| evals (paid, CI; the evals environment refuses feature branches) | `gh workflow run ci.yml -f evals=true [-f cases=<case>]` | 16 of 17 (run 43584857035) | 2026-11-14 |
| evals, local (paid) | `cd plugins/cobot && PATH="$PWD/bin:$PATH" claude plugin eval . --runs 1 --ablation none --no-publish --scaffold --allow-tools Bash Write Edit [--case <glob>]` | gcp-mcp-asked-once and gcp-mcp-never-again 1.00 | 2026-11-22 |

## Owner-terminal commands
Carried over, not re-run; the brief leaves them out.

| purpose | command | result | verified |
|---|---|---|---|
| reinstall into a dogfood repository (uninstall + install; `claude plugin update` ignores same-version edits) | `./install.sh --refresh /path/to/repo` | carried over, not re-run | 2026-11-08 (journal) |
| R1 spikes (owner's terminal) | `sh scripts/spikes/spike-r1.sh` | carried over, not re-run | 2026-11-06 (journal) |
| coexistence spikes (owner's terminal) | `sh scripts/spikes/spike-coexistence.sh` | carried over, not re-run | 2026-11-06 (journal) |
| agy smoke (owner's terminal, signed in, real HOME) | `./install.sh --agy && sh scripts/spikes/smoke-agy.sh` | second run: every runnable check ok; w1, m1, S4 not run | 2026-11-15 |

## Shape
- `plugins/cobot/` is the only plugin for now; domain plugins come later
- `bin/cobot-rules` (gate, `_cobot_make`), `bin/cobot-memory` (brief, learn and promote, knowledge, check, init, journal, findings; `_cobot_knowledge`), `bin/cobot-deps` (currency, `_cobot_deps`), `bin/cobot-session` (SessionStart payload)
- `hooks/` are thin shims around `bin/`; all logic is tested Python
- skills: workflow (onboard, spec, build, wrap, rules, learn, ship, contribute; onboard, rules, security-sweep user-only), knowledge (lang-*, fw-*, expert-*), the consult router (domains under `skills/consult/domains/`), security-sweep (forked)
- agents: challenger, consultant, learner, builder, rust-builder, go-builder, python-builder, typescript-builder, terraform-builder; Claude Code's in `claude-agents/`, agy's in `agents/` (written by `scripts/sync-agents.py`; edit the Claude one)
- people read `README.md`; agents and architects read `docs/architecture.md`, `docs/configuration.md`, `docs/development.md`
- design: `docs/02-design.md`; decisions: `docs/01-decisions.md`, `docs/adr/`; platform facts: `docs/reference/claude-code-mechanics.md`; open inputs: `docs/design-inputs/`; decided ones: `docs/history/`
