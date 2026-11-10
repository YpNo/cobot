# Spec — R2 slice 4: stacks (React, Next, Vue, shell, APIs, Gitea)

size: large · profile: library · owner: YpNo · date: 2026-11-10 · 0.2.0 PR 5

## Goal

The builders and the orchestrator get senior knowledge for the stacks the owner's repositories
use and cobot does not cover yet: React, Next.js and Vue on top of `lang-typescript`, shell promoted
out of `lang-fallback`, API design and web protocols, and Gitea: how it works, how it differs from
GitHub and GitLab, how to contribute to it, and `tea` under the gate. Each skill is dogfooded on a
local repository and carries dated knowledge lines from primary sources. What does not change:
the gate's contract, the builders' count (React and Vue work stays with `typescript-builder`,
shell with `builder`), the agent listing, memory.

## Principles check

- Proportionality: knowledge skills and rules, no new binary; one consult domain and one eval.
- Knowledge is a skill, isolation is an agent: four skills, no agent.
- Evidence before structure: a framework skill ships only with a repository to dogfood it on
  (third owner review, I-8); `fw-next` has none here (Clarify Q1).
- Proof, not promises: every version and idiom line carries a status, a source and a date
  (decision 23); a skill is checked on its dogfood repository before the PR.
- Governance (docs/01-decisions.md): decision 24 (thin `fw-*` on `lang-typescript`, `lang-shell`
  promoted once server-automation is onboarded: it is) holds; decision 25 (Gitea through `tea`,
  `expert-api` for OpenAPI and web protocols; CLIs over MCP) holds; decision 23 (dated lines)
  holds; decision 22 (no unnamed dependency) is not relevant (no code dependency); the rest are
  not relevant.
- Architecture: plain layering.
- New dependencies: none.
- Delivery: one branch `feat/r2-stacks`, one PR; tasks below are the commits.

## Dogfood repositories (read 2026-11-10)

| Skill | Repository | Stack |
|---|---|---|
| `fw-react` | headplane; Valetudo | React 19.3, React Router 8, Vite 8, Tailwind 4, TypeScript 7, Vitest 5; React 19.2, TanStack Query 5 |
| `fw-vue` | gitea; demo-profil-matching | Vue 3.5, Vite 8, Vitest 5; Vue 3.5, vue-router 5 |
| `lang-shell` | server-automation (onboarded); googleapis-interceptor-envoy | shell around Ansible, installers, backups |
| `expert-api` | gitea; docs | OpenAPI files in the tree |
| `fw-next` | none (owner: build now, lines `reported`) | Next.js from its documentation |
| `expert-gitea` | docs (origin on gitea.com, `.gitea/workflows/`); gitea (the project's source) | Gitea Actions, `tea`; contributing to go-gitea/gitea |

## Stories and acceptance

1. As `typescript-builder` in a React repository, I get the React idiom (components and hooks
   rules, state and data fetching, React Router, forms, testing with Vitest and Testing Library,
   XSS through `dangerouslySetInnerHTML`), versions with dates, and a hand-off to `expert-ui`.
   Accept: `fw-react` exists, its description ≤ 350 chars names its triggers, `check-plugin`
   passes, and its commands run on headplane (`pnpm` or `npm` test and typecheck as recorded).
2. The same for Vue (Composition API and `<script setup>`, reactivity pitfalls, Pinia, vue-router,
   Vue Test Utils, `v-html`). Accept: `fw-vue` as above, checked on gitea's web sources.
3. As `builder` on shell, I get `lang-shell`: POSIX sh against bash, strict mode and its limits,
   quoting, traps and temp files, shellcheck, shfmt, bats-core, portability, CI, supply chain.
   `lang-fallback` keeps the procedure and Lua and points shell work to `lang-shell`; build
   routes `*.sh` and `*.bash` to `cobot:builder` with `lang-shell` named. Accept: shellcheck and
   shfmt commands from the skill run clean or report real findings on server-automation.
4. As the orchestrator, `expert-api` gives OpenAPI 3.x design-first, linting (Spectral or
   Redocly), versioning and deprecation, errors (RFC 9457), pagination, idempotency, auth
   (OAuth 2.x, OIDC), webhooks, SSE, WebSocket, gRPC and HTTP/2-3 choices; `/cobot:consult api`
   audits an OpenAPI document read-only. Accept: the skill, `skills/consult/domains/api.md`, the
   router's signal row, and eval `api-contract-audit` (file reads only) that passes on a single
   run.
5. As the owner, `expert-gitea` explains Gitea: architecture, features and limits against GitHub
   and GitLab (Actions compatibility, packages, mirrors, protection, webhooks, OIDC), its API,
   `tea`, gitea.com, and contributing to go-gitea/gitea (its own rules, make targets, backports).
   On a Gitea forge, `tea` writes ask and destructive or attribution forms are never run, every
   alias form included; `ship` reads `forge:` first, recognises `.gitea/` and names what Gitea
   cannot do. Accept: rules tested per alias form; read-only `tea` and detection checked on docs.
6. As `typescript-builder`, the brief names the framework skill (`fw-react`, `fw-next`, `fw-vue`)
   detected from `package.json`, and I call it first; `*.vue` and `*.jsx` route to me. Accept: build
   and the builder prompt say so; spike T00b decides whether an eval can see a subagent's Skill call.
7. `fw-next` as story 1, lines `reported` (no local Next.js repository; owner's choice).

## Clarify

- Q1 `fw-next` → a) held back until a repository uses Next.js, decision 24 noted · b) built now
  from the documentation, every line `reported` → recommended: a), the I-8 rule → **answer:** b)
  (owner, 2026-11-10)
- Q2 Gitea → a) `tea` rules and `forge: gitea` now, proven by dry runs as `glab` was · b) held back
  until the owner runs a Gitea server → recommended: a) → **answer:** the owner wants to understand
  how Gitea works, how it differs from GitLab and GitHub, and how to contribute to the project
  (2026-11-10): `expert-gitea` with `tea` rules and `forge: gitea`; the owner's docs repository is on
  gitea.com
- Q3 `expert-api` audit → a) an `api` consult domain and one eval · b) the expert only →
  recommended: a), an OpenAPI document is a natural audit target → **answer:** a) (owner,
  2026-11-10)

## Plan

Research first, in parallel, one agent per skill, from primary sources only (release pages,
official documentation), returning dated lines; then one commit per skill with its
`references/versions.md`; then routing and builders; then docs. The listing grows by about
2 100 characters (8 142 → about 10 300 of 15 000).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T00 | research through parallel `Agent` calls (forked skills run one at a time), one per area, primary sources, dated lines with status and source: React and React Router; Next.js; Vue, Pinia, vue-router; shell tools; OpenAPI and web protocols; Gitea, its Actions, its API, `tea` with its alias table, contributing to go-gitea | — | — | — |
| T00b | spike, one run: does a subagent's Skill call appear in an eval trace a `tool_used` grader reads | — | — | — |
| T01 | knowledge prefixes gain `fw-` in `check-plugin` and `_cobot_knowledge` (cap, `paths:`, dated references, staleness, `skill_name` tries `fw-<topic>`), with tests | a | — | — |
| T02 | `lang-shell` from `lang-fallback`'s shell section and its versions lines, plus the research; zsh owned by `lang-shell`; `lang-fallback` keeps the procedure and Lua, its description loses the shell triggers | a | — | T00, T01 |
| T03 | `fw-react`, `fw-next` (lines `reported`), `fw-vue`, each with `references/versions.md`; build routes `*.vue`, `*.jsx` to `typescript-builder` and names the framework skill in the brief from `package.json`; the builder prompt calls it first | b | — | T00, T01 |
| T04 | `expert-api`, `skills/consult/domains/api.md` (generated specs and Swagger 2.0 detected, inventory by grep, findings on the source annotations), router signal rows `**/*openapi*.{json,y*ml}`, `**/swagger*.json`, the consult description, eval `api-contract-audit` | c | — | T00, T01 |
| T05 | `expert-gitea`; `tea` rows per alias form (never: release create, repo delete, `api` DELETE, attribution in PR text; ask: PR create, merge, review, approve, reject, comment, issue create and edit), `tea` in `API_CLIS` if it takes `-X`; the `glab mr new` gap closed; `ship` reads `forge:` first, recognises `.gitea/`, names Gitea's limits; tests per form | c | — | T00, T01 |
| T06 | dogfood, read-only, exact commands: headplane `react-router`-free checks (lint and tests as its scripts allow without writing), demo-profil-matching (Vue), server-automation (`shellcheck`; `shfmt` and `bats` recorded missing if absent), docs (`tea` read commands if installed, forge detection), gitea (api domain inventory) | — | — | T02–T05 |
| T07 | docs: README rows, `docs/architecture.md`, CONTEXT.md, decisions 24 and 25 notes, design §15; changelog, journal, converge | — | — | T06 |
| T08 | single paid runs: `api-contract-audit`, and the framework eval if T00b allows | — | — | T07 |

## Trade-offs

- Thin framework skills over fat ones: the TypeScript ground stays in `lang-typescript`; a
  framework skill holds only what differs.
- No new builder: framework work is TypeScript work; build names the framework skill and the
  builder calls it first.
- Plugin skills are always listed (spike 2026-11-10), so each new skill costs its description in
  every session; six skills at about 340 characters each (8 142 → about 10 300 of 15 000).

## Challenger verdict

2026-11-10: **SOUND WITH CHANGES**, ten points, all folded. BLOCKER: `fw-*` outside every
knowledge check (→ T01). MAJOR: nothing makes the builder load a framework skill (→ story 6,
T00b); `*.vue` not routed to the TypeScript builder (→ T03); `tea` aliases and `tea api` escape
prefix rows, and `glab mr new` already does (→ T05, research in T00); the ask/never split was
looser than gh and glab (→ T05); `ship` assumes GitHub or GitLab and the owner does have a Gitea
target (→ T05, T06 on docs); the api targets are generated, large and mostly Swagger 2.0 (→ T04).
MINOR: dogfood commands must be exact and read-only (→ T06); the shell move was half-specified
(→ T02); lanes, T08 and the consult description (→ table).

## Converge

2026-11-10: stories 1–7 built. T08 skipped by the owner's choice: `api-contract-audit` first runs
in the full paid eval run on `main` before the 0.2.0 tag.

- T00 research through six parallel agents, primary sources; tea turned out archived
  (2026-10-29), so the gate and the expert lead with gt, its successor; Gitea is 28.x now.
- T00b: an eval's `tool_used` grader sees a subagent's Skill call (spike, 0.003 USD).
- Dogfood, read-only: `vue-tsc --noEmit` exit 0 on demo-profil-matching; `oxlint` on headplane
  (one existing warning); `shellcheck` on server-automation's ten scripts, exit 0, no finding;
  gitea's two generated documents (Swagger 2.0 and OpenAPI 3.0.3, 35k and 37k lines) detected with
  their Makefile targets; docs detected as Gitea (`.gitea/workflows`, gitea.com origin). Two
  command lessons folded (oxlint, `vue-tsc -b` writes). shfmt, bats, gt, tea, spectral and redocly
  are not installed here: recorded, not installed.
- Not proven yet: `api-contract-audit` on a live model (T08); a builder loading a framework skill
  on a live model (T08, an eval would need a builder run).
