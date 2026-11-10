# Spec — R2 surface: one consult command, user-only skills, shorter descriptions

size: medium · profile: library · owner: YpNo · date: 2026-11-10 · 0.2.0 PR 4

## Goal

Fewer commands to learn and a skill listing that survives Claude Code's budget, without losing
an audit or a rule. The seven `consult-<domain>` skills become one `/cobot:consult <domain>`;
`onboard`, `rules` and `security-sweep` stop being model-invocable; expert and language skill
descriptions are capped. `/cobot:consult` becomes a router that spawns one `cobot:consultant`
agent per domain in one message, so audits run in parallel, and spec and wrap use the same
command. Nothing changes
in the audits' procedures, the consultant agent, the gate or memory.

## Principles check

- Proportionality: skill text, one contract script, one knowledge constant, eval prompts; no new
  code path in the gate or memory.
- Knowledge is a skill, isolation is an agent: domain procedures stay skill text; the consultant
  stays the one read-only agent.
- Proof, not promises: the parallelism claim in spec and wrap was false (spike below); it is
  replaced by a mechanism that was measured.
- Governance (docs/01-decisions.md): decision 2 (one planning path) holds; decision 27 (`consult-ui`
  with Stitch) and decision 28 (cloud experts as skill pairs, `consult-gcp|kubernetes|service-mesh`)
  are amended in wording only (the consult command takes the domain as an argument; the pairs,
  their scope and ADR-0006's no-plugin rule hold); decision 18 (rules `ship` and `contribute`
  enforce) holds because neither becomes user-only; every other decision is not relevant.
- Architecture: plain layering (library profile, no adapters).
- New dependencies: none.
- Delivery: one branch `feat/r2-surface`, one PR; tasks below are the commits.

## Spike (2026-11-10, Claude Code 2.1.311, haiku, about 0.03 USD)

A throwaway plugin with one forked skill (`context: fork`, its agent sleeps 8 s and prints the
time), driven by `claude -p --output-format stream-json`. Both calls verified in one assistant
message.

| Two calls in one message | Gap between results |
|---|---|
| the same forked skill twice | 11 s: sequential |
| two different forked skills | 11 s: sequential |
| two `Agent` calls to the same agent | 1 s: parallel |

Forked skills run one at a time whether or not they are the same skill, so merging the consults
costs no parallelism; spec and wrap never had it. `Agent` calls do run in parallel, so the
consult command is a router (not a forked skill) that spawns the consultant agents itself.

## Stories and acceptance

1. As the owner, I type `/cobot:consult gha` (or `gitlab-ci`, `containers`, `gcp`, `kubernetes`,
   `service-mesh`, `ui`, with an optional path) and get the same audit as before. Accept: each
   domain procedure is the old skill body with paths from the plugin root; `claude plugin
   validate --strict` passes; the four consult evals pass on a single run.
2. As the owner, `/cobot:consult` with no domain audits every domain detected here, one
   consultant per domain in one message, each under its own ten-finding cap; an unknown domain
   lists the known ones. Accept: new eval `consult-fan-out` (a workflow and a Dockerfile; graded
   `tool_used Agent input_match consultant` min 2) passes on a single run.
3. As the orchestrator in spec and wrap, I call `/cobot:consult <domains>` for the relevant
   domains and the consultants run in parallel. Accept: spec, wrap, the protocol and the
   consultant agent say so; story 2's eval proves the fan-out.
4. As the owner, the model no longer fires `onboard`, `rules` or `security-sweep` on its own.
   Accept: `disable-model-invocation: true` on the three; the protocol points the model to the
   `cobot-rules check` binary and says owner-typed skills are proposed, never improvised; the
   untrusted brief asks the owner to type `/cobot:onboard`; `foreign-onboard`'s prompt starts with
   the slash command and passes on a single run.
5. As every session, the skill listing is smaller and each expert keeps its triggers. Accept:
   `python3 scripts/check-plugin.py` counts only model-visible skills (description plus
   `when_to_use`), enforces 350 chars for `expert-*` and `lang-*`, and reports the new total; no
   dated knowledge line lives under `skills/consult/`.

## Clarify

- Q1 The old `/cobot:consult-<domain>` names → a) removed, the changelog marks it breaking and
  names the new form · b) kept as thin alias skills → recommended: a), since aliases cost listing
  space and 0.x allows it → **answer:** a) (owner, 2026-11-10)
- Q2 Parallel audits in spec and wrap → a) spawn `cobot:consultant` agents, one per domain, in one
  message · b) keep sequential consult calls and stop claiming parallelism → recommended: a), the
  only mechanism measured to run in parallel → **answer:** a) (owner, 2026-11-10), realised as
  the router of challenger point 1
- Q3 Description cap for `expert-*` and `lang-*` → a) 350 characters, triggers kept · b) 420, the
  experts' cap from ADR-0006 → recommended: a), the simplicity review's figure; slice 4 adds six
  skills → **answer:** a) (owner, 2026-11-10), subject to the `paths:` spike (T00)

## Plan

The contract check moves first, so every later commit is measured by it. The consult skill
lands with its domain files moved by `git mv` from the old skill bodies (history kept), then the
call sites, then the user-only switch, then the caps. The dated lines in `consult-gha` move to
`expert-gha/references/` so staleness tracking keeps seeing them, and `KNOWLEDGE_SKILL_PREFIXES`
drops `consult-`.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T00 | spike, one run: a plugin skill whose only trigger is `paths:`; it decides whether T06 may drop globs from descriptions | a | — | — |
| T01 | `scripts/check-plugin.py`: count only skills without `disable-model-invocation: true`, description plus `when_to_use`; cap `expert-*` and `lang-*` at 350; fail on a dated knowledge line under `skills/consult/`; tests in `tests/test_check_plugin.py` | a | — | — |
| T02 | `skills/consult/SKILL.md` as a router (not forked): domain list, detection signals, one `cobot:consultant` Agent per domain in one message with the absolute plugin root and the paths in scope; `skills/consult/domains/<domain>.md` moved from the seven `consult-*` bodies with paths from the plugin root; `consult-gha`'s dated lines merged into `expert-gha`; `KNOWLEDGE_SKILL_PREFIXES` without `consult-`, with its test | a | — | T01 |
| T03 | call sites: `spec`, `wrap`, `ship`, `expert-ui`, `expert-containers`, `protocol.md`, `agents/consultant.md` use `/cobot:consult <domains>`; `_cobot_deps` hint and its test; `scripts/spikes/spike-r1.sh` | a | — | T02 |
| T04 | evals: the four consult cases take the domain argument; new `consult-fan-out`; `never-apply`'s terraform grader matches the command field only | a | — | T02 |
| T05 | `onboard`, `rules`, `security-sweep` user-only; the protocol's dry run through `cobot-rules check` and "owner-typed skills are proposed, never improvised"; the untrusted brief asks the owner to type `/cobot:onboard`; `foreign-onboard` prompt starts with `/cobot:onboard --foreign` | a | — | T01 |
| T06 | the 14 `expert-*` and `lang-*` descriptions under 350 with their triggers (globs kept if T00 fails, reference pointers moved to the body); `learn/templates/expert-SKILL.md` skeleton within the cap | a | — | T00, T01 |
| T07 | docs: README command row, `docs/architecture.md`, CONTEXT.md, decisions 27 and 28, ADR-0005 and ADR-0006 notes, design §3, §4 and §11, the spike in `docs/reference/claude-code-mechanics.md`; changelog (breaking: command form), journal, this spec's converge | a | — | T03–T06 |
| T08 | proof runs (paid, owner's OK): `claude plugin eval --runs 1 --ablation none` for the four consult cases, `consult-fan-out` and `foreign-onboard` | a | — | T07 |

## Trade-offs

- One command with an argument over seven commands: the listing and the menu stop growing per
  domain; the price is an argument grammar and a no-argument listing mode.
- A router over a forked skill: one prompt shape for the owner, spec and wrap, parallel because
  `Agent` calls are; the router runs in the main thread, so its few lines of instructions enter
  the orchestrator's context.
- Hard caps over judgment: 350 characters forces trigger-first descriptions; a skill whose
  trigger cannot fit keeps it in `paths:` or its body.

## Challenger verdict

2026-11-10: **SOUND WITH CHANGES**, nine points, all folded. MAJOR: two mechanisms for one audit
(→ the router, T02); relative paths in moved bodies resolve differently per route (→ paths from
the plugin root, absolute root in the prompt); `paths:` appears not to trigger plugin skills (→
T00 before T06); story 3 accepted on prose (→ `consult-fan-out`, T08). MINOR: `never-apply`
would count a `cobot-rules` dry run as a terraform call (→ T04); prose paths into user-only skills
invite improvisation (→ T05); `when_to_use` bypasses the cap (→ T01); old names in the consultant
agent, CONTEXT.md, design §3 and §11, the mechanics reference (→ T03, T07); a duplicate zizmor
line (→ merged in T02). Checked clear: the listing drops `disable-model-invocation` skills and
keeps `user-invocable: false`; the Agent route keeps the consultant's tools, `@consultant` scope,
ten-finding cap and delta format; knowledge refresh never names consult; decision 18 holds.

## Converge

pending
