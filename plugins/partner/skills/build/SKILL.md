---
name: build
description: Build the tasks of a spec, or a small change without one. Routes each task to the orchestrator (risk tasks) or to a builder agent by language (partner:rust-builder, partner:go-builder, partner:builder), with the task text, acceptance and verified commands; runs builders in up to three worktree lanes when file sets are disjoint; verifies proof lines before accepting a report; ticks tasks in the spec; journals per task group. Use after /partner:spec, or directly for tiny and small work.
argument-hint: <spec slug, or the small change in one sentence>
---

# /partner:build — implement with proof

**Small or tiny work (no spec):** state the size, write a five-line plan for small, make the
change (inline, or one builder when isolation helps), run the focused check from CONTEXT.md's
verified commands, run `/code-review low` for small, then one journal line through
`partner-memory journal add`. Stop.

**From a spec** (`.agent/specs/<slug>.md`):

1. Read the task table and the verified commands. Order tasks by `deps`.
2. For each task:
   - `risk` → you do it yourself, in the main thread, test first.
   - otherwise pick the builder: `Cargo.toml` in scope → `partner:rust-builder`; `go.mod` →
     `partner:go-builder`; else `partner:builder`. Brief = the task row, its acceptance, the files
     in scope, the verified commands, nothing more (not the whole spec).
   - Tasks with disjoint file sets and no mutual deps may run as parallel lanes: at most three
     Agent calls in one message with `isolation: worktree`. You integrate; builders never merge.
3. On each report: refuse it if `Checks:` lacks a command, an exit code or output; re-run the
   focused check yourself when in doubt. Refuse a `Deps added:` entry the spec does not name
   (decision 22). Tick the task in the spec (`[x]` or a `done` column).
   Items under `Noticed:` go to `partner-memory findings add`, never into the code.
   Then commit the task on the spec's branch with a Conventional Commit message (one task = one
   commit, decision 20; no attribution footer, decision 18). `git commit` asks unless the owner's
   layer allows it; never push from here.
4. A builder that fails the same check twice hands back: decide yourself whether to fix inline,
   split the task, or stop and ask the owner. Never let a builder loop.
5. After a task group (a lane, or three tasks): one journal entry (`Changed / Why / Proof / Open /
   Next`) through `partner-memory journal add`.
6. Never push, tag or open anything outward from here; the PR belongs to `/partner:wrap`.

When every task is ticked, say so and hand over to `/partner:wrap`.
