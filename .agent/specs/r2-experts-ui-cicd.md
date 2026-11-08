# Spec — R2 slice 2: the UI/UX expert and the CI/CD family

size: large · profile: library · owner: YpNo · date: 2026-11-08 · parent: `.agent/specs/r2.md` · branch `feat/r2-experts-ui-cicd` stacked on `feat/r2-hardening`

## Goal

Two new domains join the bench as knowledge skills with their read-only audits. `expert-ui`
covers user-interface design for web interfaces and applications and for constrained devices
such as the Miyoo Mini Plus (640×480, D-pad, OnionOS themes): tokens, type scale, colour and
contrast, layout and reflow, input modes, focus, motion, component systems, device profiles,
and the procedure that turns a request into a design brief, a token sheet and screens, with
Google Stitch rendering those screens when the owner has registered its MCP server (decision 27,
ADR-0005). `expert-cicd` holds the platform-neutral delivery principles the GitHub expert
assumes (trigger matrix, aggregator, pinning, provenance, SBOM, signing, secrets, environments)
and `expert-gitlab-ci` applies them to GitLab with `glab`; `/cobot:ship` learns to pick the
platform from the remote. What does not change: every line carries a status, a source and a
date; outward actions ask; builders never commit; the agent listing stays under 600 tokens; the
SessionStart payload under 10 000 characters.

## Principles check

- Proportionality: five skills and their references, two eval cases, one `ship` step, the rule
  rows below and two small Python changes (the `gh`/`glab api` canonical form learns the implicit
  POST of `-f`/`-F`/`--field`/`--raw-field`/`--input`; `check-plugin` gains an aggregate
  description budget); no new dependency; no new agent (consults fork the existing consultant).
- Rules before autonomy, one table for both CLIs: `release create` never (`gh` already),
  `pr|mr merge` ask, `repo delete` never (the `gh` row is added), `pr|mr create|edit|update`
  with `Generated with` never, `api -X DELETE` never, `api` POST/PUT/PATCH ask including the
  implicit POST of a body flag (the blocker the challenger found: `gh api repos/o/r/issues -f
  title=x` was silent for the consultant), `glab mr create|update`, `glab ci
  run|retry|cancel|delete`, `glab variable set|delete`, `glab release delete` ask; the
  consultant's and the learner's read lists gain `glab ci status|list|get|trace|lint`,
  `glab mr view|list|diff`, `glab repo view`, `glab release list|view`,
  `glab api projects/*|groups/*|users/*` (GETs by the canonical form); `glab ci view` is an
  interactive TUI and `glab mr checks` does not exist, so neither is listed; Stitch generate and
  edit tools ask (slice 1).
- Knowledge is a skill: every version and fact in the four references comes from the two
  research deltas gathered 2026-11-08 from primary sources, persisted first as
  `.agent/knowledge/ui.md` and `.agent/knowledge/cicd.md` (task 0) so a fresh session can build
  from them; third-party facts are `reported`; nothing unreached is written.
- Proof: `check-plugin` (paths and dated lines), strict validation, markdownlint, the two eval
  cases single-arm, a dogfood audit of a real CSS file and a real `.gitlab-ci.yml` fixture.
- Delivery: tasks below are the commits; one PR with base `feat/r2-hardening`; when PR 4 merges
  GitHub retargets it to `main` (branches delete on merge, squash is off); review changes to
  slice 1 reach this branch by `git merge feat/r2-hardening`, never by a rebase of a pushed
  branch (every force push is denied).

## Stories and acceptance

1. **A UI file touched loads the designer.** `expert-ui` (`paths:` `**/*.css`, `**/*.scss`,
   `**/*.tsx`, `**/*.jsx`, `**/*.vue`, `**/*.svelte`, `**/tailwind.config.*`,
   `**/*tokens*.json`, `**/Themes/**`, `**/themes/**`; no `*.html` and no bare `theme`/`skin`
   folders, which fire on docs output and unrelated trees; the body stays near 150 lines because
   `*.tsx` also loads `lang-typescript`) carries: the
   non-negotiables (WCAG 2.2 AA by criterion number, target size, focus, reflow, reduced
   motion, colour-scheme pairs, no colour-only meaning, text as text); the token discipline
   (W3C Design Tokens format, semantic over raw, one source of truth, dark and light as
   modes); the type and spacing scale; the component-system choice by stack (`lang-typescript`
   decides the framework, the expert the system: Material 3, shadcn/ui on Radix and Tailwind,
   native CSS when the stack has no framework); device profiles with their rules (`web-desktop`,
   `web-mobile`, `handheld-640x480-dpad` for OnionOS themes: pixel-grid typography, safe
   margins, focus ring as the only pointer, every action reachable by D-pad and two buttons,
   asset sizes the theme format expects); pitfalls. References: `references/web.md`
   (criteria, tokens, versions), `references/devices.md` (Miyoo Mini Plus, OnionOS themes),
   `references/stitch.md` (endpoint, header, tools, quota, `claude mcp add` line, all
   `reported` until the owner's first call), `templates/design-brief.md`,
   `templates/tokens.json` (W3C format skeleton). Acceptance: `check-plugin` passes, the
   description names the files, every version line has a source.
2. **A request to design a screen follows one procedure.** The expert's "Design" section: read
   the stack and the existing tokens; write the brief (`templates/design-brief.md`: users,
   device profile, tasks, states, constraints from CONTEXT.md); derive or extend the token
   sheet; then, when `mcp__*stitch*` tools are present, call `generate_screen_from_text` with
   the brief under the gate's `ask` (quota is the owner's, generation takes minutes), read the
   screen back with the get tool and treat the output as a sketch to adapt into the repository's
   stack, never pasted as is; without Stitch, hand-draw the layout in text (regions, order,
   states) and build from the component system. Every screen ends with the audit checklist of
   story 3. Acceptance: the section exists, names the gate behaviour and the no-Stitch path.
3. **`/cobot:consult-ui` audits read-only.** Fork of the consultant: inventory (stylesheets,
   tokens, components, pages, theme files), then the checks: contrast ratios computed from the
   stylesheet's colour pairs (the WCAG relative-luminance formula as one `jq -n` expression
   written in the skill, `jq` being on the consultant's read list, so the consultant computes
   rather than guesses; the two reference values are `#777777` on `#ffffff` = 4.48:1, which
   fails 1.4.3 by 0.02, and `#00aa00` on `#ffffff` = 3.11:1), target sizes, focus styles (`:focus-visible`,
   never `outline: none` without replacement), reflow at 320 px, `prefers-reduced-motion` and
   `prefers-color-scheme` handling, semantic HTML and ARIA misuse, text in images, token drift
   (raw colours beside tokens), and for the handheld profile the pixel-grid, margin and asset
   checks. Ten findings at most with file, line, criterion number and fix; knowledge_delta as
   in the other consults. Acceptance: the eval `ui-contrast` (fixture page with `#777777`
   body text and a `#00aa00` link on white): the trace (not the orchestrator's paraphrase)
   carries `1.4.3`, `4.4[5-9]|4.5[0-2]` and `3.1[0-2]` with the file name.
4. **The delivery principles exist once.** `expert-cicd` (`paths:` `.gitea/workflows/**`,
   `.woodpecker*`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, `.circleci/**`,
   `Jenkinsfile`; GitHub stays with `expert-gha` and GitLab with `expert-gitlab-ci`, both of
   which link to the core instead of loading twice):
   the trigger matrix (decision 17) stated platform-neutrally, one aggregator as the only
   required check, cheap checks first, the same commands as local, pin everything by digest or
   full SHA, least privilege and short-lived credentials (OIDC), environments with approvals
   for anything that publishes, provenance (SLSA levels and what each needs), SBOM (SPDX,
   CycloneDX), signing (Sigstore), caching keyed on lockfiles, timeouts and concurrency,
   secrets never in logs, reproducible builds, DORA metrics as the measure; a "what each
   platform calls it" table (GitHub, GitLab, Gitea). Acceptance: `expert-gha` links to it for
   principles and loses nothing; dated lines for every version.
5. **GitLab is a first-class platform.** `expert-gitlab-ci` (`paths:` `.gitlab-ci.yml`,
   `**/.gitlab-ci*.yml`, `.gitlab/**`): keywords and shapes (`workflow:rules` against duplicate
   pipelines, `rules:` with `if`/`changes`/`exists`, `needs:` DAG, `include:component` and the
   catalog, `id_tokens` for OIDC, `cache:key:files`, `artifacts:reports`, `interruptible`,
   `resource_group`, `environment` tiers, `release:` with `release-cli`, `image@sha256`,
   `default:`, `!reference`, `CI_JOB_TOKEN` allowlist, protected and masked variables, the
   security templates and their tiers, `only/except` deprecated), the `glab` commands, pitfalls;
   `references/snippets.md` with the ci and release pipelines in the trigger-matrix shape;
   `references/versions.md` with dated rows including one image digest
   (`python:3.13-slim@sha256:…`, resolved today from the registry, copied by `ship` while under
   30 days old, never invented). `consult-gitlab-ci`: read-only audit (`glab ci lint` when
   available, else by hand) against the non-negotiables. `/cobot:ship` step 1 detects the forge
   offline, in order: `.gitlab-ci.yml` or `.gitlab/` present → GitLab; `.github/` present →
   GitHub; remote host containing `gitlab` → GitLab; `github.com` → GitHub; else ask the owner
   once and record `forge:` in CONTEXT.md (the onboard template gains the field). Step 3's
   verification uses `glab ci status|get` on GitLab. Rules as listed above. Acceptance: eval
   `gitlab-ci-shape` (fixture Python library with a GitLab remote, a journal stamp on HEAD and
   `python3 -m unittest` as the verified command, which runs in the sandbox without a download):
   after `/cobot:ship`, the file target `.gitlab-ci.yml` matches `workflow:` and `rules:`, the
   exact digest of the versions row, `interruptible: true`, a `unittest` job and no `only:`; the
   gate dry run shows `glab mr create` asks and `glab release create` denied.

## Tasks

0. Persist the two research deltas as `.agent/knowledge/ui.md` and `.agent/knowledge/cicd.md`;
   the API canonical form (implicit POST, `glab`), the rule table for both CLIs, the read
   lists, the `check-plugin` aggregate description budget; tests.
1. `expert-ui` skill, references and templates from the UI delta; `consult-ui`.
2. `expert-cicd` from the CI/CD delta; `expert-gha` links to it.
3. `expert-gitlab-ci`, `consult-gitlab-ci`, the `ship` forge step and `glab` verification, the
   `forge:` field in the onboard template.
4. Evals `ui-contrast` and `gitlab-ci-shape`; run both single-arm.
5. Design §4 roles table, README, changelog, journal; mechanics reference if anything new.

## Risks

- Knowledge rot: UI facts move slowly, GitLab monthly; the brief flags version lines after 30
  days and the weekly refresh (when the owner enables it) re-verifies them.
- Skill count grows from 19 to 24. The SessionStart payload does not depend on it; the skill
  listing in the system prompt does (`check-plugin` measured folded descriptions as two
  characters until this slice fixed its parser: 19 descriptions are ≈ 11 400 chars, 22 are
  13 049). The five new descriptions are capped (consults ≤ 350 chars, experts ≤ 600) and
  `check-plugin` fails the build when the listing total passes 15 000 chars.
- Stitch facts are `reported`; the expert's no-Stitch path is the default until verified.
- `glab` is not installed on this machine: the rules are tested through the gate's dry run and
  `consult-gitlab-ci` says what it could not run.

## Challenger

SOUND WITH CHANGES (2026-11-08), one blocker, four majors, five minors, all folded: the `api`
read rows let a body flag post silently (canonical form fixed for `gh` and `glab`); the
research deltas lived only in this session (task 0 persists them); the GitLab eval would have
needed an invented digest (a dated row the snippet copies); the contrast computation was not
deterministic under the read list (one `jq` expression, graded on the trace); the `glab` rows
contradicted the `gh` rows (one table); "rebased on main" was a force push; the budget that
grows is the skill listing, not the SessionStart payload; the globs were too broad and
case-blind; forge detection depended on the network; `.gitlab-ci.yml` loaded two experts.
Checked clear: Stitch under the slice-1 rules, no new agent, the ship step structure, the
check-plugin contract, decisions 20 and 25, the grader types.

## Out of scope

Framework skills (slice 4), Gitea (slice 4), Jenkins or Azure specifics beyond the principles,
a design-system generator, publishing anything to Stitch or Figma on the cobot's own
initiative.
