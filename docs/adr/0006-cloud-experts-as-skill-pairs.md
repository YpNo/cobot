# ADR-0006 — Google Cloud, Kubernetes and the service mesh as skill pairs, not a `cobot-gcp` plugin

Status: accepted · Date: 2026-11-08 · Relates to: decision 28, decisions 25 and 26, ADR-0001 (one plugin, domain plugins later), ADR-0005 (experts as skills)

## Context

The design (§3, §12, §15) and ADR-0001 reserved a domain plugin named `cobot-gcp` for the
Google Cloud expert and gave the criterion for a domain plugin: a repository outside the domain
should not pay for what the domain needs, "each with its own `.mcp.json`". R2 slice 3 brings the
Google Cloud, Kubernetes and service-mesh experts. It ships no MCP server (decisions 25 and 26:
CLIs over MCP, because the gate judges argv) and no agent (every consult forks the consultant).
A path-gated skill costs one listing line until its files are touched. The listing total is
capped at 15 000 characters by `check-plugin`; 24 skills used 13 782 before this slice.

A second plugin would add a marketplace entry and `plugin.json`, a second `check-plugin` and
validation target in CI and `install.sh`, a cross-plugin `agent: cobot:consultant` reference
whose behaviour is unverified (the mechanics reference records same-plugin forks only), and an
eval that could not load the consultant without the first plugin installed. It would buy one
thing: a listing the owner could leave disabled on repositories without Google Cloud.

## Decision

1. `expert-gcp` + `consult-gcp`, `expert-kubernetes` + `consult-kubernetes` and
   `expert-service-mesh` + `consult-service-mesh` are skill pairs inside `plugins/cobot`, in
   the shape of `expert-gha` + `consult-gha`.
2. A domain plugin is created the day it carries a cost a repository outside the domain should
   not pay: an MCP server or an agent. It then holds the server and that agent, not the skills.
   `cobot-gcp` keeps its name for that day.
3. The listing budget is paid with description caps: experts at most 420 characters, consults
   270, and the eight longest existing descriptions trimmed to 600 with their triggers intact.
   The total lands near 14 900 of 15 000; slice 4 argues its own room in its spec (one `consult`
   skill with an `argument-hint` replacing seven `consult-<x>` entries, further trims, or a
   higher cap).
4. The legacy `gcd-universe` user skill is superseded by `expert-gcp/references/universe.md`,
   its facts re-verified against the provider 8.x documentation and the Cloud Foundation
   Fabric source on 2026-11-08; `lang-terraform` hands a `google` provider to `expert-gcp`.

## Consequences

- Design §3, §12 and §15 and the R2 umbrella spec read `cobot-gcp` as the future server
  plugin, not as this slice's deliverable.
- The gate gains the cloud read lists for the read-only agents and a marker that disables an
  agent-scoped allow whenever a segment could execute repository content (spec
  `.agent/specs/r2-cloud.md`, story 7).
- Six skills join the bench; the agent listing stays at 528 tokens.

## Amendment (2026-11-10)

`.agent/specs/r2-surface.md` merges the seven `consult-<x>` skills into one `/cobot:consult`
router that spawns one `cobot:consultant` per domain in one message; the procedures live in
`skills/consult/domains/<x>.md`. Decision point 3's caps change: `expert-*` and `lang-*` descriptions are capped at 350 characters, the consult caps fall away with the consult skills, and the budget counts only model-visible skills. Points 1, 2 and 4 hold: no `cobot-gcp` plugin until a server or an agent needs one.
