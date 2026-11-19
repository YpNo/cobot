---
name: rules
description: Inspect and dry-run the cobot rules gate. show lists the merged never/ask/allow rules with their layer; check "<cmd>" gives the decision for a command (add --tool Edit or --agent consultant); explain "<cmd>" lists every matching rule per segment; sync [--runtime claude|agy] renders permissions.deny, ask (agy local dev) and owner allow lines as a diff against settings.json for the owner to apply by hand. Use when a command was denied or asked, before adding a rule, or when setting up a machine.
argument-hint: show | check "<cmd>" | explain "<cmd>" | sync [--runtime claude|agy]
disable-model-invocation: true
---

# /cobot:rules

Run `cobot-rules` with the given arguments and relay the output without interpretation beyond
one line of context:

- `show` → the layers in effect (default, owner `~/.config/cobot/cobot.rules` or `~/.claude/cobot.rules`,
  project `.agent/cobot.rules`), their counts, every rule with provenance.
- `check "<cmd>" [--tool T] [--agent A]` → `deny`, `ask` or `none`, with the winning rule and layer.
- `explain "<cmd>"` → each segment after normalisation and every rule that matched it; a mise
  task, a `make` target, a `bash -c` string or an entry wrapper (`distrobox enter … --`, `docker exec`) appears as
  the commands behind it (`cargo test --workspace  <- mise run test`).
- `sync [--runtime claude|agy] [--settings PATH]` → the JSON fragment and a unified diff against
  Claude's `~/.claude/settings.json` or Antigravity's `~/.gemini/antigravity-cli/settings.json`.
  Show it; the owner applies it. You never edit `settings.json` (the gate denies it, and the owner's trust depends on it).

Precedence, when asked: `never` in any layer wins and cannot be relaxed; an `allow` from the owner
layer (or an agent-scoped one from the default layer) silences the gate, after which the host's
own permissions decide; `ask` from any layer prompts (under Antigravity, local repeatable dev asks emit session-cacheable `ask` while outward/destructive asks emit `force_ask`); the project layer may only tighten.

To loosen a default `ask` the owner adds an `allow` line to `~/.config/cobot/cobot.rules` (or `~/.claude/cobot.rules`); to tighten a
repository, add `never` or `ask` lines to `.agent/cobot.rules`. Rules are one per line:
`decision Tool(pattern) [@agent]`.
