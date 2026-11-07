# Spec — R1.1 slice 1: learning and currency

size: large · profile: library · owner: YpNo · date: 2026-11-07

## Goal

The partner stops guessing and stops rotting. A `learner` agent behind `/partner:learn` turns a
question or a stale skill into a dated, sourced knowledge delta; `partner-memory learn --promote`
carries the general part of a delta into this repository as a reviewable branch; the session brief
says how old each skill's knowledge is and how far the repository's dependencies are behind; a
weekly workflow opens the refresh PR. What does not change: no agent writes a knowledge file,
nothing outward runs without the owner, and `.agent/knowledge` stays the home of project facts.
The rest of R1.1 (ship with `expert-containers`, contribute, security-sweep, compaction, the
Python and TypeScript stacks, the terraform builder, `accepted-risks.md`, the other evals) is the
next slice.

## Principles check

- Proportionality: three scripts, one agent, one skill, one workflow; everything reads what
  exists (reference files, lockfiles, the ecosystems' own tools), nothing new is stored but a
  per-repository cache line.
- Rules before autonomy: the learner is read-only by rule; `--promote` is an `ask` action;
  experiments run under the gate; the refresh workflow pushes a branch and opens a PR, it never
  merges.
- Knowledge is a skill: deltas land in `skills/<x>/references/learned.md`, dated and sourced, or in
  `.agent/knowledge/<topic>.md`; a skill with no owner yet is a skeleton `expert-<x>` that stays
  `reported` until it has served twice.
- Proof, not promises: a `verified` line needs a primary source or a reproducible command; the
  staleness check is deterministic and offline; the dependency check quotes the tool it ran.
- Architecture: plain layering (library profile). Shared logic in `_partner_knowledge.py` and
  `_partner_deps.py`, thin CLIs in `partner-memory` and `partner-deps`; the session payload
  composes lines from the three tools through subprocess, as it already does.
- New dependencies: none. Standard library; the ecosystems' own CLIs are invoked when present and
  named in the report when absent; the Terraform registry and HashiCorp checkpoint endpoints are
  queried with `urllib`.
- Delivery: commits on `main` (no remote yet; branch-per-spec starts with the remote). Tasks below
  are the commits.

## Stories and acceptance

1. As the orchestrator, when no skill covers a domain or one is stale, I run `/partner:learn
   <topic or skill> [question]` and get back a delta whose every entry has a status, a source and a
   date. Accept: `tests/test_partner_rules.py` proves `@learner` is read-only with the consultant's
   read list; the `learn-unknown-domain` eval asserts the learner agent ran and the reply carries
   statuses and sources.
2. As the owner, general entries reach this repository through `partner-memory learn --promote`
   as a branch `learn/<topic>` in a worktree under the data directory, with the push and PR
   commands printed, never run. Accept: `tests/test_partner_knowledge.py` runs promote against a
   temporary git checkout and checks the branch, the commit, the `references/learned.md` lines,
   de-duplication across the skill's references, the 300-line cap, and the skeleton expert when no
   skill matches; `partner-rules check "partner-memory learn --promote x"` is `ask`.
3. As the orchestrator, the session brief tells me which skills carry stale knowledge
   (versions > 30 days, idiom > 90 days) and how many `reported` lines remain. Accept:
   `partner-memory knowledge --stale` lists them; `partner-session` payload carries the line;
   tests fix the thresholds and the classification.
4. As the owner, dependency currency is checked at onboard, reported in the brief from a cache,
   and refreshed before a PR. Accept: `partner-deps check` runs the ecosystem's tools (fakes on
   PATH in tests), caches by lockfile hash and date under the data directory, `partner-deps brief`
   never runs a tool; `onboard` and `wrap` name the command.
5. As the owner, a weekly workflow refreshes the stalest skills and opens one PR per skill with
   the delta. Accept: `.github/workflows/knowledge-refresh.yml` passes `zizmor` offline, is
   SHA-pinned, `permissions` minimal, budget-capped, and reuses `partner-memory knowledge --json`
   and `learn --promote --in-place`.

## Clarify

Answered from the design (§8, ADR-0002, decisions 21 and 23); no question is expensive to undo.

- Q1 Where does promote write? → a) the owner's checkout on a new branch · b) a worktree under
  the data directory · c) a patch file → **answer: b)** (the checkout may be mid-work; a
  worktree is isolated and the owner pushes it); the workflow uses `--in-place` on its own
  checkout.
- Q2 Which file in the skill? → a) guess the topical file · b) one `references/learned.md` per
  skill → **answer: b)**, the owner moves lines at review.
- Q3 Does the brief run the dependency tools? → a) yes when stale · b) never, cache only →
  **answer: b)**: the SessionStart hook has 30 s and no network promise; the brief says "stale,
  run `partner-deps check`".
- Q4 Version versus idiom line? → by the claim: a version token (`v1.2`, `1.2.3`, a 40-hex SHA,
  "current", "latest") makes it a version line (30 days); everything else is idiom (90 days).

## Plan

1. `_partner_knowledge.py`: scan dated lines across the plugin and `.agent/knowledge`, classify,
   age; map a topic to a skill; write promoted lines; create a skeleton expert; worktree and
   in-place modes. `partner-memory knowledge|learn --promote` call it.
2. `learner.md` agent and `skills/learn/SKILL.md` (fork into the learner); default rules give the
   learner the consultant's read list and make `--promote` ask; protocol and `consult-gha` speak
   the same delta (`scope: general|project`, JSON).
3. `partner-session` adds the knowledge and dependency lines.
4. `_partner_deps.py` + `partner-deps`: adapters per ecosystem, cache, `check`, `brief`, `--json`;
   wired into `onboard` and `wrap`.
5. `knowledge-refresh.yml`; `learn-unknown-domain` eval; `install.sh` records the source checkout
   for promote.
6. Docs: design §3, §7, §8, §15; README; CHANGELOG; F-02 through a live `/partner:learn`.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `_partner_knowledge.py` scan + staleness; `partner-memory knowledge [--stale] [--json] [--brief] [skill]`; tests | knowledge | — | — |
| T02 | `learn --promote [--source DIR] [--in-place]`: mapping, `learned.md`, dedupe, cap, skeleton expert, worktree branch and commit; `install.sh` writes `~/.claude/partner/source`; rule `ask`; tests | knowledge | — | T01 |
| T03 | `agents/learner.md`, `skills/learn/SKILL.md`, learner read list in `default.rules`, protocol and `consult-gha` delta alignment; rules tests | learner | — | — |
| T04 | `_partner_deps.py` + `partner-deps check|brief`; cache; adapters (cargo, go, npm, pnpm, uv, poetry, terraform); tests with fake tools | deps | — | — |
| T05 | `partner-session` carries the knowledge and deps lines; onboard and wrap wiring; tests | session | — | T01 T04 |
| T06 | `knowledge-refresh.yml` (zizmor clean), `learn-unknown-domain` eval | ci | — | T02 T03 |
| T07 | docs, changelog, journal; live `/partner:learn` on the three reported lines (F-02) | docs | — | all |

## Trade-offs

- A worktree for promote over a branch in the owner's checkout: one more directory under the data
  dir, but never a surprise `git switch` under the owner's feet.
- The dependency check shells out to ecosystem tools rather than reading registries itself: exact
  and maintained upstream, at the price of "tool not installed" reports; only Terraform queries
  the registry directly because no read-only CLI exists for it.
- `cargo update --dry-run` as the fallback when `cargo-outdated` is absent reports compatible
  bumps only; the report says so.
- Staleness classified by the claim text, not by file: a heuristic, but one that does not depend
  on how a skill names its files.

## Challenger verdict

SOUND WITH CHANGES (2026-11-07), eleven points, all folded:

1. Staleness: a version token alone flagged history ("edition 2024 stable since 1.85.0"). Now a
   version line needs a token plus a currency word, or a `versions`/`actions`/`ci` file, and no
   history word; counts per skill are reported, not a boolean.
2. Promote appended only, so a refreshed line never lost its old date. Now an identical claim is
   re-dated in place, `supersedes` replaces the old line, the rest goes to `learned.md`; the
   workflow skips a skill whose `learn/<skill>` branch already exists.
3. Workflow: in print mode an `ask` is a refusal, so the learner never runs `--promote`; the
   workflow extracts the delta and runs `learn --promote --in-place` in a shell step, runs the
   plugin checks itself (a `GITHUB_TOKEN` push triggers no CI), takes an optional PAT, caps two
   skills per run.
4. Cache key without an origin remote: `host/owner/repo`, else the root commit, else a path hash.
5. `partner-deps` runs repository-directed code: `cargo-outdated` and `cargo-deny` binaries
   called directly (no alias), `GOTOOLCHAIN=local`, `npm_config_ignore_scripts`, exit 1 with
   parseable JSON is success, output scrubbed with the secret pattern, "no installed tree" when
   every npm row is MISSING.
6. Source checkout from `known_marketplaces.json` (Claude Code already records the directory);
   `install.sh` writes nothing new.
7. Promote twice: worktree pruned and reused, dated branch when only the branch exists, base on
   `origin/HEAD` when known.
8. No skeleton by accident: the delta names `skill`, or carries a `skeleton` block with
   description and paths; otherwise promote refuses and says so.
9. Drift: the learner read list already existed (T03 is the agent, the skill and the ask rule);
   reference headers now state the 30/90-day classes; decision 21's "at session start when
   stale" is implemented as the brief reading the cache and naming the command, because the
   SessionStart hook has 30 s and no network promise; "served twice" is the owner's review flip.
10. Session payload reserves room for the two new lines and shares one deadline.
11. Eval runs offline against read-list commands and asserts the learner ran, the delta carries
    statuses and sources, and nothing was written.

## Converge

2026-11-07. Story 1: `tests/test_partner_rules.py::test_gate_agentScope_learnerSharesTheReadListAndStaysReadOnly`
passes; eval `learn-unknown-domain` written (runs on dispatch, paid). Story 2:
`tests/test_partner_knowledge.py` (promote worktree, reuse, dated branch, refusals, re-date,
supersede, skeleton rules, 300-line cap, source resolution) passes; `partner-rules check
"partner-memory learn --promote x"` is `ask`. Story 3: `partner-memory knowledge --stale` and the
session payload tests pass; thresholds and classes fixed by tests, including every history line
of the real skills reading as idiom. Story 4: `tests/test_partner_deps.py` (seven adapters on fake
tools, cache states, scrubbing, broken adapter) passes; run live on cartridge-os (2 of 55
behind, 0 advisories), headplane (go 1 of 3, pnpm absent) and headscale (brief: not checked);
onboard and wrap name the command. Story 5: `knowledge-refresh.yml` passes `zizmor --offline
--persona auditor` with one low finding (the same pinned `npm install -g` as `ci.yml`), secrets
in the `knowledge-refresh` environment, permissions commented, budget `$3`, two skills per run;
it cannot run until the remote exists. Live learner probe in print mode without tool grants
returned an empty delta and named the refusals (the right behaviour); a second run with
`--allowedTools WebFetch WebSearch` is recorded in the journal.
