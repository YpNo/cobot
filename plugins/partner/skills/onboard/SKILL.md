---
name: onboard
description: First contact with a repository, or a refresh when the stack changed. Resolves trust (owner identity, trusted root commit, or foreign mode with memory outside the tree), fingerprints the stack, runs and records the verified commands, proposes the profile, writes .agent/CONTEXT.md, JOURNAL.md and FINDINGS.md from the templates, and proposes owner-layer allow lines for the verified commands. Use when the session brief says the repository is untrusted or has no memory, or when CONTEXT.md is stale.
argument-hint: [--foreign]
---

# /partner:onboard — trust, fingerprint, remember

1. **State.** Run `partner-memory check`. If memory exists and is trusted, this is a refresh: skip
   to step 4 and only correct what changed.
2. **Trust.** If untrusted, read the reason and propose exactly one path with `AskUserQuestion`:
   - the owner's own repository → `partner-memory init --add-identity` (adds `host/owner` to
     `~/.claude/partner/identities`; every remote must belong to an identity);
   - someone else's repository (upstream work) → `partner-memory init --foreign` (memory outside the
     tree under the data directory, `.agent` excluded from git; plugin enabled with `--scope local`);
   - a repository without a remote → `partner-memory init --trust-root` once the first commit exists.
   Do not read `.agent/*` of an untrusted repository before this step.
3. **Init.** `partner-memory init --profile <p>` with the profile you propose (`spike`, `script`,
   `cli`, `library`, `service`, `infra`) and one line of reasoning. Legacy memory (an
   `ARCHITECTURE.md`, a newest-on-top journal) is kept as is; the tools read it unchanged.
4. **Fingerprint.** For a small repository, read the manifests yourself; for a large one, fork
   the built-in Explore agent per subsystem. Detect languages, package manager, test runner,
   linter, formatter, type checker, CI. For each candidate command: run it, keep the exit code,
   and record only commands that ran, with today's date, in CONTEXT.md's verified table. The
   matching `lang-*` skill supplies the idiomatic commands; `lang-fallback` the procedure for
   anything else.
5. **CONTEXT.md.** Fill profile, goal, stack, environment, verified commands, constraints,
   applies / does not apply, and a Shape section of at most twenty lines. Stay under 120 lines.
6. **Rules.** Print the owner-layer lines that would make the verified commands silent for the
   gate (`allow Bash(<command>*)`), and offer to append them to `~/.claude/partner.rules`. Never
   touch `settings.json`; `/partner:rules sync` renders the hard wall for the owner to apply.
7. **Journal.** Replace the template entry's fields with what you did (`partner-memory journal
   add`). Report: trust path taken, profile, the verified commands, what you could not verify.
