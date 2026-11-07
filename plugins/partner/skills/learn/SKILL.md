---
name: learn
description: >-
  Learn from primary sources and reproducible commands instead of guessing. Invoke when the
  session brief says a skill's knowledge is stale, when no lang-* or expert-* skill covers a
  domain, when a consult returned low confidence or a spike contradicted a skill, or when the
  owner asks a question the skills cannot answer. Forks the read-only learner agent, which
  returns a knowledge delta (claims with status, source, date and scope); the orchestrator then
  applies it with partner-memory learn, and general entries reach the plugin only through
  learn --promote.
argument-hint: <skill or topic> [question]
context: fork
agent: partner:learner
user-invocable: true
---

# /partner:learn — verify, do not guess

Read-only. Change nothing, commit nothing, write no file. Your result is the report described
in your agent instructions, with exactly one ```json fence holding the `knowledge_delta`.

## Procedure

1. **Frame.** The argument names a skill (`lang-go`, `expert-gha`, …) or a topic, and may add a
   question. Read the baseline: the skill's `SKILL.md` and `references/*.md` under
   `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/`, and `.agent/knowledge/<topic>.md` when it exists.
   No matching skill → say so in the summary; the delta then carries `topic` only, plus a
   `skeleton` block (description, `when_to_use`, `paths` globs) when the argument says
   `--new-expert`.
2. **Pick the claims.** With a question: the facts needed to answer it, each as one checkable
   sentence. Without one (a refresh): the lines that `partner-memory knowledge --stale <skill>`
   or the brief flagged — versions older than 30 days, idiom older than 90, every `reported` and
   `assumed` line. Refreshing means re-checking the same claim text: when it still holds, return
   it unchanged with today's `checked` so it is re-dated in place; when it changed, return the
   new claim with `supersedes` set to a fragment of the old one.
3. **Verify.** Primary sources first (release pages, official docs, changelogs, the registry's
   JSON, upstream code), through WebFetch or WebSearch; quote the URL that carries the fact.
   Then experiments from your read list (`<tool> --version`, `gh api repos/<o>/<r>/releases/latest`,
   `cat`, `grep` on a checkout); record the exact command as `exp: <command>`. Anything else is
   `reported` (one source, not reproduced) or `assumed` (memory). Never mark `verified` from
   memory, and never run a command the gate would have to ask about: name it under *Not covered*.
4. **Filter.** Keep an entry only if it changes a decision, a command or a version, contradicts
   or refreshes an existing line, cannot be derived from the repository or a single lookup, and
   is stable (a version, a flag, a protocol detail, a policy). No tutorials, no logs, no general
   knowledge. Fifteen entries at most; `scope: general` for what any repository can use,
   `project` for what belongs to this one.
5. **Report** per the agent format: summary, the JSON delta, not covered.

## After the fork (orchestrator)

- Dry run first: `partner-memory learn --dry-run '<json>'`; read what would be written, skipped
  and re-dated.
- Apply: `partner-memory learn '<json>'` writes project entries to `.agent/knowledge/<topic>.md`
  and keeps general ones there tagged `(general)` until promoted.
- Promote general entries when they are worth a review: `partner-memory learn --promote '<json>'`
  (the gate asks). It writes a `learn/<topic>` branch in a worktree under the data directory,
  re-dating or superseding existing lines in place and appending the rest to
  `references/learned.md`, and prints the `git push` and `gh pr create` commands for the owner.
  Nothing is pushed. With `--in-place` (CI) the lines land in the given `--source` checkout
  without a branch.
- A delta from a consult report follows the same path. An `assumed` entry may be quoted but may
  not drive a decision, a command or a version.
