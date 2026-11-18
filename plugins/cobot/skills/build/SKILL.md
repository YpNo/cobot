---
name: build
description: Build the tasks of a spec, or a small change without one. Routes each task to the orchestrator (risk tasks) or to a builder agent by language (cobot:rust-builder, go-builder, python-builder, typescript-builder, terraform-builder, builder), with the task text, acceptance and verified commands; runs builders in up to three worktree lanes when file sets are disjoint; verifies proof lines before accepting a report; ticks tasks in the spec; journals per task group. Use after /cobot:spec, or directly for tiny and small work.
argument-hint: <spec slug, or the small change in one sentence>
---

# /cobot:build — implement with proof

**Small or tiny work (no spec):** state the size, write a five-line plan for small, make the
change (inline, or one builder when isolation helps), run the focused check from CONTEXT.md's
verified commands, run `/code-review low` for small, then one journal line through
`cobot-memory journal add`. Stop.

**From a spec** (`.agent/specs/<slug>.md`):

1. Read the task table and the verified commands. Order tasks by `deps`.
2. For each task:
   - `risk` → you do it yourself, in the main thread, test first.
   - otherwise pick the builder by the files in scope: `Cargo.toml` or `*.rs` →
     `cobot:rust-builder`; `go.mod` or `*.go` → `cobot:go-builder`; `pyproject.toml` or `*.py`
     → `cobot:python-builder`; `package.json`, `*.ts`, `*.tsx`, `*.jsx` or `*.vue` →
     `cobot:typescript-builder`; `*.tf` → `cobot:terraform-builder`; `*.sh`, `*.bash`, `*.zsh` →
     `cobot:builder` with `lang-shell` named in the brief; else `cobot:builder`. For the
     TypeScript builder, name the framework skill in the brief from the nearest `package.json`
     dependencies: `react` → `fw-react`, `next` → `fw-next` (with `fw-react`), `vue` → `fw-vue`. A task that spans two stacks
     (headplane has `package.json` and `go.mod`) is split into one task per stack, or goes to the
     builder of the files it changes most with the other skill named in the brief. Brief = the
     task row, its acceptance, the files in scope, the verified commands, nothing more (not the
     whole spec). Every builder call sets `run_in_background: false`: step 3 needs its report.
   - Tasks with disjoint file sets and no mutual deps may run as parallel lanes: at most three
     Agent calls in one message with `isolation: worktree`. You integrate; builders never merge.
3. On each report: refuse it if `Checks:` lacks a command, an exit code or output; re-run the
   focused check yourself when in doubt. Refuse a `Deps added:` entry the spec does not name
   (decision 22). Tick the task in the spec (`[x]` or a `done` column).
   When CONTEXT.md's verified table holds only the `none yet` row (a new project), record the
   accepted task's proof commands there with their result and today's date, remove that row,
   run `cobot-memory check`, and print the owner-layer allow lines as onboard step 7 does.
   Items under `Noticed:` never go into the code. The report hook parks them in
   `.agent/noticed.md` for wrap. Where the `Agent` call came back "Async agent launched", the
   hook saw no report: pass the hand-back's items to `cobot-memory noticed add` yourself.
   Then commit the task on the spec's branch with a Conventional Commit message (one task = one
   commit, decision 20; no attribution footer, decision 18). `git commit` asks unless the owner's
   layer allows it; never push from here.
4. A builder that fails the same check twice hands back: decide yourself whether to fix inline,
   split the task, or stop and ask the owner. Never let a builder loop.
5. After a task group (a lane, or three tasks): one journal entry (`Changed / Why / Proof / Open /
   Next`) through `cobot-memory journal add`, committed with the task's code in one commit when
   it carries a stamp (`cobot-memory stamp --tree`, as wrap's journal step does).
6. Never push, tag or open anything outward from here; the PR belongs to `/cobot:wrap`.

When every task is ticked, say so and hand over to `/cobot:wrap`.
