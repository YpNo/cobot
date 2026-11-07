# ADR-0001 — A blank-slate plugin marketplace with a governed orchestrator

**Status:** accepted · **Date:** 2026-11-06 · **Deciders:** Michael Lopez, Claude (orchestrator;
two architect agents and one challenger agent contributed)

## Context

A home-grown scaffold (workstation-starter `ai/`, installed as `~/.agents`) gave Claude Code five
phases, ten agents and per-repo memory files. It worked in six repositories but had grown a second
planning system (spec-kit), stale language facts, four unused commands, contradictory global
rules, and an install that silently stopped propagating edits. The owner wants one structured
cobot: Claude Code as orchestrator, dedicated experts, explicit rules before autonomy, model
routing, and quality gates on the cobot itself. See `docs/01-decisions.md` and
`docs/reference/legacy-audit.md`.

## Decision

1. **Start from a blank slate** in a public marketplace repo. Old ideas are rewritten only after
   the audit's fixes; nothing is copied.
2. **One plugin (`cobot`) in release 1**; domain plugins (`cobot-gcp`, `cobot-reverse`,
   delivery extras) are created when their content exists. Split further only on measured cost.
3. **The orchestrator is Claude Code's main thread**, shaped by a ≤ 3k-char protocol injected at
   session start. Built-ins (plan mode, task list, sessions, `/code-review`, `/security-review`,
   `/simplify`, auto-memory) are never re-implemented.
4. **Knowledge is a skill, isolation is an agent.** Experts are skills consulted through one
   read-only `consultant` agent. Agents exist only for a tool allowlist, a fresh context or a
   different model: `challenger`, `consultant`, `builder` and thin per-language builders.
5. **The conceptor is a main-thread skill** (spec, ≤ 5 clarify questions, plan, tasks) because it
   must talk to the owner; the fresh-context `challenger` supplies the independent view, and the
   owner alone may accept a BLOCKER or MAJOR objection.
6. **Rules before autonomy.** A plain rules file (`never` / `ask` / `allow`, layered, most
   restrictive wins) enforced by a `PreToolUse` gate written in Python behind a POSIX shim that
   blocks on any failure; the gate never widens permissions. The hard wall is a `permissions.deny`
   block the owner installs, emitted in both plain and `rtk`-prefixed forms.
7. **Memory is committed** (`.agent/CONTEXT.md`, `JOURNAL.md`, `specs/`) in the owner's repos and
   kept outside the tree, keyed by remote, for foreign repos; untrusted `.agent/` is never injected.
8. **Model routing by role**: owner's model for orchestration, spec, challenge and risky tasks;
   Sonnet for builders and consults; Haiku for extraction and compaction.
9. **The cobot is tested like software**: plugin evals, pytest on the gate, SHA-pinned CI,
   semantic versions, a changelog.

## Alternatives considered

| Option | Why not |
|---|---|
| Evolve the existing scaffold in place | Two sources of truth and stale content were its root defects; the owner chose a blank slate. |
| Nine plugins from day one, one agent per language and per expert | Spends agent-description budget on roles that are knowledge, not isolation; structure before evidence, the old scaffold's mistake. |
| Named expert agents | Each costs listing tokens in every session and grows with the catalogue; a forked skill into one consultant gives the same isolation. |
| Conceptor as a subagent | Cannot ask the owner the clarify questions; the challenger already provides the fresh context. |
| Rules as prose in CLAUDE.md | Not enforced; the previous scaffold's permission allowlist let `git push` through unconditionally. |
| Bash + jq gate | Compound-command parsing is where bypasses hide; `shlex`/`fnmatch` are testable and need no extra binary. |
| Workflow scripts as the orchestrator's fan-out mechanism | User opt-in per run, so the orchestrator cannot rely on them; shipped later as an optional deep review. |

## Consequences

**Good.** One install, one version, one place to edit. Every outward action is gated
deterministically and visibly. Per-session cost stays around five to six thousand tokens. Adding an
expert costs no agent budget. The cobot can be evaluated and regressed in CI.

**Costs.** The owner must apply the permission block by hand once per machine. The gate is string
and argv matching: it stops honest and careless attempts, not determined obfuscation. Foreign-mode
memory lives outside the repo and must be backed up. The legacy scaffold coexists with the cobot until
the owner triggers the switch (ADR-0003); the extra listing cost is measured during dogfood.

**Reversible.** Settings changes go through a shown diff; memory files are additive; foreign mode
is local-only; the backup restores the previous setup.
