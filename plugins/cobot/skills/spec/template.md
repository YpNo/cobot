# Spec — {{TITLE}}

size: {{SIZE}} · profile: {{PROFILE}} · owner: {{OWNER}} · date: {{DATE}}

## Goal

<one paragraph: what changes for whom, and what does not change>

## Principles check

<proportionality, rules before autonomy, knowledge is a skill, proof not promises: one line each where relevant>

- Governance (<path from CONTEXT.md, or none>): <each principle: holds | not relevant | violated → Clarify>
- Architecture: <hexagonal | plain layering | host project's> because <criterion: profile, adapters, test substitutes, or contribution>
- New dependencies: <none | name — why, and what the standard library or an existing dependency lacks>
- Experts: <domain → the `expert-*` or `lang-*` skill read | domain → none: facts below are questions, /cobot:learn proposed>
- Delivery: one branch `<type>/<slug>`, one PR; tasks below are the commits

## Stories and acceptance

1. As <who>, <what>. Accept: <observable check, with the command that proves it>.

## Trust boundaries

<each boundary the change creates or alters: network listeners and routes, subprocess and shell-out sites, filesystem paths built from input, deserialisation, crypto and randomness, authn and authz decisions, logging sinks, secrets read, held or forwarded, privilege lines (a role, a token scope, a sandbox, the gate)>

| entry or crossing | guard | story |
|---|---|---|
| <where untrusted input enters, or what crosses a privilege line> | <the check that refuses it> | <the story whose acceptance is a negative test> |

<or one line instead of the table: none: <why>, a reason the challenger can check>

## Clarify

<≤ 5 questions, each with options and a recommended default; answers written here once given>

- Q1 <question> → a) … · b) … → recommended: a) because … → **answer:** <pending>

## Plan

<the ordered steps, with the trade-offs you took>

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | <one task: files, change, the focused check that proves it> | <lane> | <risk or —> | — |

## Trade-offs

- <what was chosen over what, and why>

## Challenger verdict

pending

## Converge

pending
