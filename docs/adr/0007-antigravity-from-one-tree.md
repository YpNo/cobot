# ADR-0007 — The Antigravity CLI supported from the same tree, its gaps named

Status: accepted · Date: 2026-11-15 · Amends: decision 1 · Relates to: ADR-0001 (one plugin),
ADR-0003 (nothing writes the owner's files), spec `.agent/specs/antigravity.md`

## Context

Decision 1 (2026-11-06) kept Antigravity and Gemini out of scope: Claude Code only. The owner
now works in the Antigravity CLI (`agy`) at work and needs cobot there (owner decisions
2026-11-11, `docs/design-inputs/antigravity-0.3.0.md`). agy 1.5 reads a plugin folder close to
Claude Code's: the same skill format, agents with a stricter frontmatter, a root `hooks.json`,
and a second manifest folder (`.antigravity-plugin/`) that wins over `.claude-plugin/`. Its
hooks differ where the gate is concerned: a hook that fails is logged and ignored, so the call
runs; `allow` defers, `auto_approve` widens, `ask` respects a cached grant; the payload carries
no agent identity, and hooks run in the plugin folder with nothing on PATH.

## Decision

1. Decision 1 reads: **Claude Code first; the Antigravity CLI supported from the same tree,
   its gaps named.** Claude Code pays nothing for it: no extra read, no changed hook, no changed
   protocol text.
2. One tree, `plugins/cobot/`: Claude Code's agents in `claude-agents/`, listed in its manifest;
   agy's in `agents/`, written by `scripts/sync-agents.py` and checked by `check-plugin`;
   skills shared; each runtime its own hook file (`hooks/hooks.json`, root `hooks.json`).
3. One policy, one adapter per runtime at its edge: `cobot-rules gate --runtime agy` and
   `cobot-session start --runtime agy` translate agy's payloads; the rules, their layers and
   their precedence do not change.
4. Fail closed by output, not by exit code: the agy shim prints a deny with exit 0 on every
   failure it can see. Under agy the gate answers `allow` (no opinion), `force_ask` or `deny`,
   never `auto_approve`.
5. Self-protection follows the runtime: agy's settings, config, grants and every customization
   root's hook and plugin files are `never` rows in the default layer, shared by both runtimes.
6. ADR-0003 extends to `~/.gemini`: `install.sh --agy` writes only through `agy plugin install`.

## Consequences

- Named gaps under agy, in the README and the agy brief: builder proof is requested, not
  enforced (no hook sees a subagent's report); agent-scoped rules have no identity to match, so
  the consultant and the learner run without a command tool; a missing `sh` still fails open;
  whether the gate fires inside an `invoke_subagent` child or a workflow agent is proven by the
  smoke run (`docs/harnesses.md`), not assumed.
- Every agy fact the design relies on is dated in `docs/reference/antigravity-mechanics.md` and
  re-read when agy's version moves.
- A body edit to a Claude agent needs `python3 scripts/sync-agents.py`; CI fails until it runs.
- agy merges hook groups by name across sources, so a repository's committed `.agents/hooks.json`
  could switch off a group named `cobot` (smoke `h2`, 2026-11-15). `install.sh --agy` installs a
  staged copy whose group is `cobot-<16 random hex>`, new at each install; a bare `agy plugin
  install` of the checkout keeps the guessable name. The agy brief names any workspace
  `hooks.json`, `plugins.json` or `plugins/` from the workspace up to the repository root. An
  upstream issue asks agy to namespace a plugin's hook groups as it does its tools and skills.
- Session grants, the debug path and cobot-reverse are 0.4.0, for both runtimes.
