# ADR-0002 — Experts learn through a filtered knowledge delta, never by writing files

Status: accepted · Date: 2026-11-06 · Supersedes: none · Related: ADR-0001 decision 4

## Context

The owner asked for a learner / teacher capability: when no expert covers a domain, or an expert
meets something it does not know, the partner must learn from primary sources and from its own
experiments instead of guessing, and every expert must update its knowledge when it discovers or
validates something. The owner also warned against writing everything down: knowledge must stay
relevant and small. ADR-0001 fixed "knowledge is a skill", builders never write `.agent/`, and
the orchestrator owns memory writes.

## Decision

1. **Learning is a protocol every expert follows, plus one agent for the no-expert case.** A
   consultant report may carry a `knowledge_delta`; the `learner` agent (sonnet, read-only by
   rule, invoked through `/partner:learn <topic>`) produces one when no `expert-*` or `lang-*`
   skill matches, a consult returns low confidence, or a spike contradicts a skill.
2. **Agents return deltas, the orchestrator applies them** through `partner-memory learn`, which
   filters, deduplicates, refuses secret-like strings and prints the diff. No agent edits a
   knowledge file.
3. **Three statuses, provenance on every line.** `verified` (dated primary source, or an
   experiment that ran under the rules gate), `reported` (one source, not reproduced), `assumed`
   (model memory). A decision, command or version may not rest on an `assumed` entry.
4. **Two layers.** General knowledge lives in the plugin (`skills/<expert>/references/`) and
   changes through a reviewed pull request opened by `learn --promote` (an `ask` action).
   Repository- or device-specific knowledge lives in `.agent/knowledge/<topic>.md`, committed
   with the repository (or in the external memory directory for foreign repos).
5. **The relevance filter is the design, not a hint.** An entry is written only if it changed a
   decision, command or design in the session or contradicts an existing entry; is not
   derivable from the repository or a single lookup; and is stable. Caps: 80 lines per topic
   file; entries unchecked for 180 days are re-verified or dropped at consolidation. No logs,
   transcripts, tutorials or evidence dumps: evidence is a link or a one-line reproducible
   command.

## Alternatives considered

| Option | Why not |
|---|---|
| A learner agent that writes skill files directly | Breaks "the orchestrator owns memory", bypasses the filter, and a web-fed agent writing instructions is a prompt-injection path |
| One shared knowledge base outside skills | Loses path-gated loading; experts would load everything or nothing |
| Learn into auto-memory | Per-machine, unversioned, not shared with the plugin's other users or the repo's future sessions |
| No filter, keep everything with dates | The old scaffold's rot: stale facts that still look authoritative |

## Consequences

Knowledge is reviewable in git, dated, and attributable. The cost is one more structured field in
consult reports and a promote flow that needs the owner's yes. Experiments spend tokens and time;
they are reserved for claims that will drive a decision.
