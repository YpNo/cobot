# ADR-0003 — The cobot installs beside the legacy scaffold; the switch is a separate, owner-triggered step

Status: accepted · Date: 2026-11-06 · Amends: ADR-0001 consequences ("the legacy scaffold must be
removed before dogfood")

## Context

Design v1 planned an R0 that unlinked the legacy agents and skills from `~/.claude` and cut the
global CLAUDE.md before any dogfood. The owner decided otherwise: the old scaffold stays in place
until the new cobot is built and proven, the repository must ship its own install methods, and
the switch happens at a moment the owner picks, because it could disturb work in flight.

## Decision

1. **Nothing in R0–R1.1 writes to `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills`
   or `~/.claude/settings.json`.** The `permissions.deny` hard wall is rendered as a diff by
   `/cobot:rules sync` and applied only when the owner says so.
2. **Three install paths ship in this repository**, in `install.sh` and the README:
   `--dev` (a `claude --plugin-dir <repo>/plugins/cobot` alias, session-only, nothing written),
   `--project` (marketplace add from GitHub or the local path, then
   `claude plugin install cobot@cobot --scope project`, or `--scope local` in a
   foreign repo), and `--user` (reserved for the switch). `--check` reports legacy presence and
   name overlaps; `--uninstall` reverses `--project` and `--user`.
3. **Coexistence rules.** Every plugin skill and agent is namespaced (`/cobot:*`,
   `cobot:*`) and shares no name with the legacy set. The SessionStart protocol states in one
   line that, when the cobot is loaded, its skills replace `/onboard /design /build /wrap /ship`
   and the legacy router instruction is skipped. `cobot-memory` reads the legacy `.agent/`
   files unchanged, in either journal order, so dogfood repositories need no migration.
4. **The switch is documented in `docs/03-switch-plan.md`** and runs only on the owner's word:
   backup, `--user` install, unlink, CLAUDE.md cut to the RTK section, rules sync, a
   workstation-starter pull request replacing `ai/`, then a fresh-session check.

## Consequences

Dogfood sessions carry both instruction sets for a while; the extra listing cost (legacy agent
descriptions) and any instruction conflict are measured, not assumed. Two spikes join the day-one
list: `--plugin-dir` loads hooks, agents and namespaced skills; and the gate's `ask` prevails over
the legacy settings' unconditional `allow` for `git push`. If the second fails, the owner applies
the deny block early for `never` rules only.
