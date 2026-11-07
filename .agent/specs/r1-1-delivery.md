# Spec — R1.1 slice 2: delivery, stacks and the sweep

size: large · profile: library · owner: YpNo · date: 2026-11-07

## Goal

The partner can take a repository from "tests pass locally" to a pipeline, an image and a
reviewed upstream pull request without inventing anything: `/partner:ship` writes the trigger
matrix from the verified commands, `expert-containers` makes the image part exact,
`/partner:contribute` drives a foreign repository's PR under the maintainers' constraints,
`/partner:security-sweep` audits a whole tree read-only against the accepted risks, and the
journal stops growing without bound. Two more stacks join Rust and Go: Python and TypeScript,
each with a builder, plus a Terraform builder. What does not change: no outward action runs
without the owner, builders never commit, knowledge lines carry a status and a source, and the
agent listing stays under 600 tokens.

## Principles check

- Proportionality: skills and knowledge, two Python changes (`compact`, the risks check), one
  template per new memory file; the legacy sweep's rule packs are reused after a read, not
  rewritten.
- Rules before autonomy: ship writes files and runs local commands only; contribute proposes
  `git push` and `gh pr create` as commands; the sweep forks into the read-only consultant;
  `gh repo fork` and `git remote add` join the ask list.
- Knowledge is a skill: every version in `lang-python`, `lang-typescript` and
  `expert-containers` comes from the three research deltas gathered today, dated and sourced;
  anything not reached is `reported` or left out.
- Proof, not promises: ship runs each pipeline command locally before writing it; the sweep
  anchors every finding to a file and line; builders report commands with exit codes.
- Architecture: plain layering. `compact` is a pure function over journal text with the model
  summary as an optional input; everything else is Markdown.
- New dependencies: none.
- Delivery: commits on `main` (no remote yet); tasks below are the commits.

## Stories and acceptance

1. As the owner, `/partner:ship` turns CONTEXT.md's verified commands and the profile into
   `ci.yml` (PR: lint, type check, changed-area tests, security scan; merge: full suite and one
   artifact; aggregator `ci-ok`), `release.yml` (verify the tag's commit passed, no test rerun,
   attest, `gh release create --verify-tag`) and, for a service with a Dockerfile, an image
   workflow (buildx, metadata tags, cosign keyless, SBOM, Trivy gate). Accept: the skill names
   each job's failure prevented and what it omitted; the SHAs come from `expert-gha` references
   (re-resolved when older than 30 days); `consult-gha` runs on the result; applied to this
   repository's own `ci.yml` as the first dogfood (the double run on push plus PR is fixed).
2. As the owner, `expert-containers` loads on Dockerfiles, Containerfiles, compose files and
   Quadlet units with verified lines (engine, BuildKit, Dockerfile frontend, distroless and
   Chainguard bases, cosign, syft, Trivy, rootless Podman) and `consult-containers` audits them
   read-only (hadolint and Trivy when present, else by hand). Accept: `check-plugin` passes
   (`paths:` and dated lines); gate rows already cover `docker push`, `prune`, `login`.
3. As the owner, `/partner:contribute` in a foreign repository reads the constraints onboard
   copied (AI policy, DCO, branch), keeps or creates `.agent/UPSTREAM.md` from a template,
   requires the wrap stamp on HEAD, prepares the branch (upstream base, sign-off when the DCO
   asks), drafts the PR body into a file only when the maintainers allow AI text and otherwise
   leaves it to the owner, and prints the push and `gh pr create --repo <upstream>` commands.
   Accept: the skill text; `UPSTREAM.md` template; rules `ask Bash(gh repo fork*)`,
   `ask Bash(git remote add*)`; headscale's memory gets an `UPSTREAM.md` as the dogfood.
4. As the owner, `/partner:security-sweep` forks the consultant on the whole tree with the
   legacy rule packs (core, one per language present, infra) reduced to what still holds,
   reads `.agent/accepted-risks.md` and reports at most ten findings with severity, confidence,
   file:line, path and fix; accepted rows are listed, expired rows flagged. Accept: skill plus
   `references/` packs; `partner-memory check` warns on an expired accepted risk;
   `accepted-risks.md` template with `why · by · expires ≤ 90 days`.
5. As the owner, `partner-memory compact` folds the journal once it passes 400 lines: all
   entries but the last ten become one dated summary entry, written from a model summary when
   wrap provides one (haiku) or from a mechanical digest (date, title, first `Changed:`
   sentence) otherwise; `--dry-run` shows the fold. Accept: tests on both orderings, the
   mechanical digest, the summary input and the keep count; `check` stops saying "arrives in
   release 1.1".
6. As the owner, `lang-python` (uv, ruff, pytest with coverage, type checker, packaging,
   idiom 3.12+, security) and `lang-typescript` (Node LTS, pnpm, strict tsconfig, vitest,
   biome or oxlint, security) exist with `references/versions.md` and `references/ci.md`, and
   `python-builder`, `typescript-builder`, `terraform-builder` agents preload them; `build`
   routes `pyproject.toml`/`*.py`, `package.json`/`*.ts`, `*.tf`. Accept: `check-plugin` and
   strict validation pass with the agents listing under 600 tokens; dogfood: `partner-rules
   check` on the skills' commands, lang-python's lint command run on dreame-vacuum, the
   lang-typescript commands checked against headplane's `package.json`.
7. As the owner, three more evals exist: `never-apply`, `builder-routing`, `proof-required`.
   Accept: the case files validate (`claude plugin eval --list` or a dry parse) and are wired
   into the eval job.

## Clarify

Answered from the design; nothing here is expensive to undo.

- Q1 Sweep fan-out? → a) one forked consultant, capped · b) orchestrator partitions and forks
  several → **answer: a)** for R1.1 (the owner's repositories are small; the consultant stops at
  ten findings and says what it did not cover); b) is the R2 deep-review workflow.
- Q2 Compaction summary source? → a) haiku through wrap, mechanical fallback · b) mechanical
  only → **answer: a)**: the skill asks the built-in Agent with `model: haiku` for the summary
  and passes it; the fallback keeps the command deterministic and testable.
- Q3 Which legacy packs? → copy the packs whose language or infra the partner covers (core, go,
  python, ts-js, rust, shell, dockerfile, terraform, github-actions), each read and trimmed of
  tool paths and dead references; java, kotlin, php stay behind until a repository needs them.
- Q4 Contribute's PR body under an AI policy? → the skill never writes prose the owner would
  submit as theirs when the policy forbids it; it prepares facts (what changed, how tested,
  issue link) in `UPSTREAM.md` and the owner writes the body.

## Plan

1. `ship` skill (main thread) + `expert-containers` + `consult-containers`.
2. `contribute` skill + `UPSTREAM.md` template + rules.
3. `security-sweep` skill + packs + `accepted-risks.md` template + the `check` warning.
4. `partner-memory compact` + tests + wrap wiring.
5. `lang-python`, `lang-typescript` from the research deltas; `python-builder`,
   `typescript-builder`, `terraform-builder`; `build` routing.
6. Evals `never-apply`, `builder-routing`, `proof-required`.
7. Dogfood: this repository's `ci.yml` through ship; headscale `UPSTREAM.md`; dreame-vacuum
   and headplane probes. Docs, changelog, journal.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `skills/ship/SKILL.md`; `expert-containers` (SKILL + references/versions.md, ci.md) and `consult-containers` from the containers delta | ship | — | research |
| T02 | `skills/contribute/SKILL.md` + `templates/UPSTREAM.md`; rules `gh repo fork`, `git remote add`; rules tests | contribute | — | — |
| T03 | `skills/security-sweep/SKILL.md` + `references/*.md` (trimmed legacy packs) + `templates/accepted-risks.md`; `partner-memory check` expiry warning + test | sweep | — | — |
| T04 | `partner-memory compact` + tests; wrap step for the haiku summary | memory | — | — |
| T05 | `lang-python` + `python-builder`; `lang-typescript` + `typescript-builder`; `terraform-builder`; `build` routing; check-plugin budget | stacks | — | research |
| T06 | evals `never-apply`, `builder-routing`, `proof-required` | evals | — | T05 |
| T07 | dogfood: split this repository's `ci.yml` into PR and merge sets with the `ci-ok` aggregator; propose the trigger fix for dreame-vacuum's `validate.yaml`; headscale `UPSTREAM.md`; dreame-vacuum and headplane probes | dogfood | — | T01 T02 T05 |
| T08 | docs (design §3, §15; README; CHANGELOG), journal | docs | — | all |

## Trade-offs

- One forked consultant for the sweep over a partitioned fan-out: fits the owner's repository
  sizes and the "delegation depth is one" rule; the cap is stated in every report.
- Mechanical compaction digest as the floor: a model summary is better prose, but a journal
  must compact even when no model is at hand (CI, a cheap session).
- Legacy packs copied and trimmed rather than rewritten: they were reviewed once already; the
  risk is stale tool advice, handled by the trim and by dated lines where a version appears.
- `oxlint`/`oxfmt` beside biome in `lang-typescript`: headplane uses oxc; the skill names both
  and recommends one per repository, never two.

## Challenger verdict

SOUND WITH CHANGES (2026-11-07), fourteen points, folded as follows:

1. Compaction and the brief: the summary entry carries the newest folded date and sits where
   the folded entries were, so the brief is unchanged by a fold (tested).
2. Re-folds merge the previous summary's lines instead of digesting them again, and `Open:`
   items travel with the digest (tested).
3. The stamp predicate in contribute: equality with HEAD in foreign mode; in committed mode the
   diff from the stamp to HEAD may touch only `.agent/**`, docs, changelog and README.
4. The ci.yml double run does not exist (both triggers filter on `main`); T07 restated as the
   PR-versus-merge split with the aggregator; dreame-vacuum's bare triggers become a proposed
   patch for the owner.
5. Ship refuses in foreign mode and patches existing workflows after a consult-gha audit,
   never rewrites them.
6. Accepted risks: rows keyed by rule, file and symbol; `partner-memory risks add` writes them
   (the consultant is read-only); the report ends with the commands the orchestrator may run
   after the owner's yes.
7. Scanner allow rows for the consultant, read-only forms only (`npm audit fix` and `docker
   build .` still ask); hook tests.
8. Name: `security-sweep` kept. `onboard`, `build`, `wrap` and `ship` already share names with
   the legacy set under the `/partner:` namespace, the protocol lists the legacy skills the
   partner replaces, and the switch removes them; `security-sweep` joins that line. Accepted
   deviation, not a rename.
9. Routing on the task's files (extension, nearest manifest), tie → ask; a mixed-repository
   case is named in `build`.
10. Changed-area tests: `vitest run --changed` named; Python runs the full suite with the reason.
11. Release check filtered to the merge run of `ci.yml` with `actions: read` and an
    `environment: release`.
12. `--scaffold` added to the eval job; fixtures through `scaffold_script`; proof-required uses
    a pasted report.
13. Contribute resolves the upstream through `gh repo view --json parent`; the advisory remote
    is never a candidate; DCO through `git rebase --signoff` (asks).
14. Budget: `builder`'s description trimmed (listing 528 tokens of 600); only `verified` lines
    may become pins; §15 records three evals in this slice (foreign-onboard and actions-pinning
    deferred to R2) and that the sweep runs at the consultant's `medium` effort until a
    per-skill effort override exists.

## Converge

2026-11-07. Story 1: `ship` written with the profile table, the trigger matrix, the challenger
step and the report; this repository's `ci.yml` gained the `ci-ok` aggregator and PR-only
cancellation (zizmor offline: no new finding); the full ship run on a third-party repository
waits for the first service repository. Story 2: `expert-containers` (39 dated lines, 9 action
SHAs resolved today) and `consult-containers` pass check-plugin and strict validation. Story 3:
`contribute` with the stamp predicate, the parent resolved by `gh repo view`, the DCO note and
the AI-policy stop; headscale's external memory holds its `UPSTREAM.md` (no DCO, acknowledged
contribution model, AI policy); rules for `gh repo fork` and `git remote add|set-url` tested.
Story 4: `security-sweep` with the nine ported packs (355 rule ids, none dropped), the risk key
rule+file+symbol, `partner-memory risks add|list` and the `check` warning, scanner allow rows
tested; a live sweep is owed on the next real audit. Story 5: `compact` tested on both
orderings, with a summary and without, re-folding, the brief unchanged, `Open:` carried.
Story 6: both language skills built from the research deltas (every line verified or marked),
three builders (listing 528 of 600 tokens), routing by files in scope; the gate now resolves
`uv run`, `pnpm|npm|yarn run <script>` (hooks included), the pnpm and yarn shorthand, npm's
aliases and `exec`, so headplane's `pnpm run typecheck`, `pnpm test:unit` and `pnpm run lint
--fix` go silent while `pnpm dev` (a script regex) and `pnpm run deploy` (a push) ask (F-10
fixed); dreame-vacuum's workflows are a proposed patch (F-11), its code is upstream's. Story 7:
three eval cases with `scaffold_script` fixtures and `--scaffold` in the eval job; they run on
dispatch once the remote exists. Suite: 539 tests, 98 % coverage; ruff, shellcheck,
markdownlint, check-plugin, strict validation clean.
