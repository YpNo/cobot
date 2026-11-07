---
name: rules
description: Inspect and dry-run the partner rules gate. show lists the merged never/ask/allow rules with their layer; check "<cmd>" gives the decision for a command (add --tool Edit or --agent consultant); explain "<cmd>" lists every matching rule per segment; sync renders the permissions.deny hard wall (plain and rtk forms) and the owner's allow lines as a diff against ~/.claude/settings.json for the owner to apply by hand. Use when a command was denied or asked, before adding a rule, or when setting up a machine.
argument-hint: show | check "<cmd>" | explain "<cmd>" | sync
---

# /partner:rules

Run `partner-rules` with the given arguments and relay the output without interpretation beyond
one line of context:

- `show` → the layers in effect (default, owner `~/.claude/partner.rules`, project
  `.agent/partner.rules`), their counts, every rule with provenance.
- `check "<cmd>" [--tool T] [--agent A]` → `deny`, `ask` or `none`, with the winning rule and layer.
- `explain "<cmd>"` → each segment after normalisation and every rule that matched it; a mise
  task, a `make` target, a `bash -c` string or an entry wrapper (`distrobox enter … --`, `docker exec`) appears as
  the commands behind it (`cargo test --workspace  <- mise run test`).
- `sync [--settings PATH]` → the JSON fragment and a unified diff. Show it; the owner applies it.
  You never edit `settings.json` (the gate denies it, and the owner's trust depends on it).

Precedence, when asked: `never` in any layer wins and cannot be relaxed; an `allow` from the owner
layer (or an agent-scoped one from the default layer) silences the gate, after which Claude Code's
own permissions decide; `ask` from any layer prompts; the project layer may only tighten.

To loosen a default `ask` the owner adds an `allow` line to `~/.claude/partner.rules`; to tighten a
repository, add `never` or `ask` lines to `.agent/partner.rules`. Rules are one per line:
`decision Tool(pattern) [@agent]`.
