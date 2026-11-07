# ADR-0004 — The project is named cobot

Status: accepted · Date: 2026-11-07 · Amends: ADR-0001 ("one plugin, `partner`")

## Context

Until 2026-11-07 the marketplace was `agentic-partner` and the plugin `partner`: a generic word
that said nothing about the field, and two names where one would do. The owner wanted a name
that reads as a technical AI assistant for architects, developers and operators at first sight.
Candidates were checked against GitHub for collisions in the Claude plugin and AI-agent space:
`techne` and `foreman` collided, `tandem` and `cadre` lacked the technical reference, `sidecar`
was crowded.

## Decision

**cobot**: the collaborative robot that works on the engineer's bench under force limits, here a
rules gate on every outward action. One word serves the repository (`YpNo/cobot`), the
marketplace, the plugin (`cobot@cobot`), the slash prefix (`/cobot:`), the agent namespace
(`cobot:`), the binaries (`cobot-memory`, `cobot-rules`, `cobot-deps`, `cobot-session`), the
environment (`COBOT_*`), the tags in every refusal (`cobot rule:`, `cobot gate:`,
`cobot session:`), the rule files (`cobot.rules`) and the state directories
(`~/.local/share/cobot`, `~/.claude/cobot`). In the protocol the assistant is "the cobot" and the
human "the owner".

## Consequences

- One breaking rename before the first user-scope install and before the switch plan, with a
  migration in `install.sh` for the state this machine already holds (spec
  `.agent/specs/rename-cobot.md`).
- Records keep their text: the journal's past entries, the earlier specs, the design inputs and
  the released changelog section still say `partner`, so history stays searchable under both
  names. ADR-0001 is read with this amendment.
- The GitHub rename keeps a redirect from the old repository name.
