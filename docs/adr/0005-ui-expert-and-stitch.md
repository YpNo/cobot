# ADR-0005 — A UI/UX expert, with Google Stitch reachable through MCP under the gate

Status: accepted · Date: 2026-11-08 · Relates to: decision 27, ADR-0001 (experts as skills)

## Context

The owner's work includes web interfaces and applications and user interfaces for constrained
devices such as the Miyoo Mini Plus (640×480, D-pad, OnionOS themes). No expert covered design:
tokens, type scales, accessibility, input modes, component systems, small-screen readability.
Google Stitch generates screens from text and exposes an MCP server (`stitch.googleapis.com/mcp`,
API key header `X-Goog-Api-Key`, around fifteen tools: projects, screens, design systems; the
generate and edit tools take minutes and spend the owner's quota). Its documentation page does
not render for a fetch; the facts come from Google's codelab and third-party write-ups and are
therefore `reported`.

## Decision

1. `expert-ui` is a knowledge skill like the others: every claim carries a status, a source and a
   date; device profiles are part of it; `consult-ui` is the read-only audit by the consultant.
2. The expert works without Stitch. It produces the design brief, the token sheet and the review
   from the repository and the request; Stitch, when the owner has registered it, renders
   screens from that brief.
3. Stitch is the owner's: registered at user scope with `claude mcp add stitch --transport http
   https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: …" -s user`, never shipped in the
   plugin's `.mcp.json` (the key and the quota belong to the owner, and a failing server at
   plugin load would cost every session). The gate's default layer asks on `mcp__*__generate*`
   and `mcp__*__edit*` whatever the server's name; list and get tools stay silent.
4. Design §12's rule stands for code and repositories: outward writes go through `git` and `gh`.
   Design artefacts in the owner's own SaaS account are the one MCP write the protocol allows,
   under `ask`.

## Consequences

- R2 slice 2 builds `expert-ui` and `consult-ui`; the learner's first live Stitch call turns the
  `reported` endpoint and tool list into `verified` lines.
- The rules gate gains two patterns; nothing else in the plugin depends on Stitch.
- An eval for the expert waits until the knowledge lines exist.

## Amendment (2026-11-10)

`.agent/specs/r2-surface.md` merges the seven `consult-<x>` skills into one `/cobot:consult`
router that spawns one `cobot:consultant` per domain in one message; the procedures live in
`skills/consult/domains/<x>.md`. The UI audit is `/cobot:consult ui`; Stitch, the expert and the gate rules are unchanged.
