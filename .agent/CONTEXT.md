# cobot — context

profile: library          # spike | script | cli | library | service | infra
goal: a Claude Code plugin marketplace that makes the main thread a governed orchestrator
owner: YpNo (Michael Lopez) · public · MIT

## Stack
- Python 3.12+ standard library only for `plugins/cobot/bin/*` (no runtime deps)
- POSIX sh for hooks and `install.sh`; Markdown for skills and agents
- pytest + pytest-cov, ruff, shellcheck, markdownlint-cli2, zizmor; `claude plugin validate --strict`

## Environment
- Claude Code 2.1.285 locally (npm latest 2.1.318); hooks run as the user
- owner's git: `safe.bareRepository = explicit`; rtk PreToolUse hook rewrites Bash to `rtk <cmd>`

## Verified commands
| purpose | command | verified |
|---|---|---|
| unit tests + coverage gate | `uv run --no-project --python 3.13 --with pytest==9.2.0 --with pytest-cov==7.1.0 pytest --cov=plugins/cobot/bin --cov-fail-under=85` | 2026-11-06 |
| lint | `uvx ruff@0.17.4 check . && uvx ruff@0.17.4 format --check .` | 2026-11-06 |
| shell lint | `uvx --from shellcheck-py shellcheck install.sh plugins/cobot/hooks/*.sh scripts/*.sh` | 2026-11-06 |
| markdown lint | `npx --yes markdownlint-cli2@0.21.0 "**/*.md"` | 2026-11-06 |
| plugin validation | `claude plugin validate plugins/cobot --strict && claude plugin validate . --strict` | 2026-11-06 |
| gate dry run | `plugins/cobot/bin/cobot-rules check "<cmd>"` | 2026-11-06 |
| plugin contract (sizes, descriptions, agent budget, knowledge lines) | `python3 scripts/check-plugin.py` | 2026-11-06 |
| reinstall into a dogfood repository | `./install.sh --refresh /path/to/repo` (uninstall + install; `claude plugin update` ignores same-version edits) | 2026-11-06 |
| memory self-check | `plugins/cobot/bin/cobot-memory check` | 2026-11-06 |
| evals (paid sessions, owner's terminal) | `cd plugins/cobot && claude plugin eval . --runs 1 --ablation none --no-publish --allow-tools Bash Write Edit` | 2026-11-06 |
| R1 spikes (owner's terminal) | `sh scripts/spike-r1.sh` | 2026-11-06 |
| coexistence spikes (owner's terminal) | `sh scripts/spike-coexistence.sh` | 2026-11-06 |

## Constraints
- nothing writes to `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills`, `~/.claude/settings.json` (ADR-0003)
- the gate never emits `allow`; any failure blocks (exit 2 in the shim)
- agents never write `.agent/`; only the orchestrator and wrap do
- commits: Conventional Commits, no Co-Authored-By; PR bodies never mention Claude Code
- coverage floor 85 % on `bin/`; SKILL.md < 500 lines; agent descriptions ≤ 600 tokens in total

## Applies / does not apply
- applies: TDD on `bin/`, SHA-pinned actions, Keep a Changelog, SemVer
- does not apply: a service deployment, a database, browser E2E

## Shape
- `plugins/cobot/` is the only plugin for now; domain plugins come later
- `bin/cobot-rules` (gate, `_cobot_make`), `bin/cobot-memory` (brief, learn and promote, knowledge, check, init, journal, findings; `_cobot_knowledge`), `bin/cobot-deps` (currency, `_cobot_deps`), `bin/cobot-session` (SessionStart payload)
- `hooks/` are thin shims around `bin/`; all logic is tested Python
- skills: workflow (onboard, spec, build, wrap, rules, learn, ship, contribute), knowledge (lang-*, expert-*), consults (consult-*, security-sweep; forked)
- agents: challenger, consultant, learner, builder, rust-builder, go-builder, python-builder, typescript-builder, terraform-builder
- design: `docs/02-design.md`; decisions: `docs/adr/`; platform facts: `docs/reference/claude-code-mechanics.md`
