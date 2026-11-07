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

- Proportionality: five skills and their references, two eval cases, one `ship` step and a
  handful of rule rows; no Python beyond none; no new dependency; no new agent (consults fork the
  existing consultant).
- Rules before autonomy: `glab mr create`, `glab release create`, `glab ci run|retry|cancel`,
  `glab variable set|delete` ask; `glab mr merge` and `glab repo delete` never; the consultant's
  read list gains `glab ci lint|status|view|trace`, `glab mr view|list|diff|checks`,
  `glab repo view`, `glab api` GETs; Stitch generate and edit tools ask (slice 1).
- Knowledge is a skill: every version and fact in the four references comes from the two
  research deltas gathered 2026-11-08 from primary sources; third-party facts are `reported`;
  nothing unreached is written.
- Proof: `check-plugin` (paths and dated lines), strict validation, markdownlint, the two eval
  cases single-arm, a dogfood audit of a real CSS file and a real `.gitlab-ci.yml` fixture.
- Delivery: tasks below are the commits; one PR with base `feat/r2-hardening` until PR 4 merges,
  then rebased on `main`.

## Stories and acceptance

1. **A UI file touched loads the designer.** `expert-ui` (`paths:` `**/*.css`, `**/*.scss`,
   `**/*.tsx`, `**/*.jsx`, `**/*.vue`, `**/*.svelte`, `**/*.html`, `**/tailwind.config.*`,
   `**/*tokens*.json`, `**/theme/**`, `**/themes/**`, `**/skin/**`) carries: the
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
   stylesheet's colour pairs (the WCAG relative-luminance formula, written in the skill so the
   consultant computes rather than guesses), target sizes, focus styles (`:focus-visible`,
   never `outline: none` without replacement), reflow at 320 px, `prefers-reduced-motion` and
   `prefers-color-scheme` handling, semantic HTML and ARIA misuse, text in images, token drift
   (raw colours beside tokens), and for the handheld profile the pixel-grid, margin and asset
   checks. Ten findings at most with file, line, criterion number and fix; knowledge_delta as
   in the other consults. Acceptance: the eval `ui-contrast` (fixture page with `#777` on
   `#fff` body text and a `#0a0` link on white): the report names `1.4.3`, the ratio
   `4.48:1` (±0.05) and the file.
4. **The delivery principles exist once.** `expert-cicd` (`paths:` `.gitlab-ci.yml`,
   `**/.gitlab-ci*.yml`, `.gitea/workflows/**`, `.woodpecker*`, `azure-pipelines.yml`,
   `bitbucket-pipelines.yml`, `.circleci/**`, `Jenkinsfile`; GitHub stays with `expert-gha`):
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
   `references/versions.md`. `consult-gitlab-ci`: read-only audit (`glab ci lint` when
   available, else by hand) against the non-negotiables. `/cobot:ship` step 1 reads the remote
   host: GitLab (`gitlab.com` or `glab repo view` answers) → `.gitlab-ci.yml` from the
   snippets; GitHub → as today; other → the core principles and a note. Rules as listed above.
   Acceptance: eval `gitlab-ci-shape` (fixture Python library with a GitLab remote and a
   verified `pytest` command): after `/cobot:ship`, the file target `.gitlab-ci.yml` matches
   `workflow:` and `rules:`, an `image:` pinned by `@sha256:`, `interruptible: true`, a
   `pytest` job and no `only:`; the gate dry run shows `glab mr create` asks and
   `glab mr merge` denied.

## Tasks

1. `expert-ui` skill, references and templates from the UI research delta; `consult-ui`.
2. `expert-cicd` from the CI/CD research delta; `expert-gha` links to it.
3. `expert-gitlab-ci`, `consult-gitlab-ci`, the `glab` rule rows and consultant read list,
   `ship` platform step; tests for the rules.
4. Evals `ui-contrast` and `gitlab-ci-shape`; run both single-arm.
5. Design §4 roles table, README, changelog, journal; mechanics reference if anything new.

## Risks

- Knowledge rot: UI facts move slowly, GitLab monthly; the brief flags version lines after 30
  days and the weekly refresh (when the owner enables it) re-verifies them.
- Skill count grows from 19 to 24: each description stays under the contract's length and the
  SessionStart payload is measured after the change.
- Stitch facts are `reported`; the expert's no-Stitch path is the default until verified.
- `glab` is not installed on this machine: the rules are tested through the gate's dry run and
  `consult-gitlab-ci` says what it could not run.

## Out of scope

Framework skills (slice 4), Gitea (slice 4), Jenkins or Azure specifics beyond the principles,
a design-system generator, publishing anything to Stitch or Figma on the cobot's own
initiative.
