---
name: onboard
description: First contact with a repository, or a refresh when the stack changed. Resolves trust (owner identity, trusted root commit, or foreign mode with memory outside the tree), fingerprints the stack, runs and records the verified commands, proposes the profile, writes .agent/CONTEXT.md, JOURNAL.md and FINDINGS.md from the templates, and proposes owner-layer allow lines for the verified commands. Use when the session brief says the repository is untrusted or has no memory, or when CONTEXT.md is stale.
argument-hint: [--foreign]
---

# /cobot:onboard — trust, fingerprint, remember

1. **State.** Run `cobot-memory check`. If memory exists and is trusted, this is a refresh: skip
   to step 4 and only correct what changed.
2. **Trust.** If untrusted, read the reason and propose exactly one path with `AskUserQuestion`:
   - the owner's own repository → `cobot-memory init --add-identity` (adds `host/owner` to
     `~/.claude/cobot/identities`; every remote must belong to an identity);
   - someone else's repository (upstream work, including your fork of it: the reason names the
     remotes that belong to no identity) → `cobot-memory init --foreign` (memory outside the
     tree under the data directory, keyed by `origin`; `.agent` excluded from git and shared by
     the checkout's worktrees; plugin enabled with `--scope local`);
   - a repository without a remote → `cobot-memory init --trust-root` once the first commit exists.
   Do not read `.agent/*` of an untrusted repository before this step.
3. **Init.** `cobot-memory init --profile <p>` with the profile you propose (`spike`, `script`,
   `cli`, `library`, `service`, `infra`) and one line of reasoning. Legacy memory (an
   `ARCHITECTURE.md`, a newest-on-top journal) is kept as is; the tools read it unchanged.
4. **Fingerprint.** For a small repository, read the manifests yourself; for a large one, fork
   the built-in Explore agent per subsystem. Detect languages, package manager, test runner,
   linter, formatter, type checker, CI. For each candidate command: run it, keep the exit code,
   and record only commands that ran, with today's date, in CONTEXT.md's verified table. The
   matching `lang-*` skill supplies the idiomatic commands; `lang-fallback` the procedure for
   anything else. Then run `cobot-deps check` (decision 21): it asks the ecosystems' own
   tools how far the lockfiles are behind and whether advisories exist, caches the answer for
   seven days, and reports; it upgrades nothing. Put the one-line result in the journal entry
   and the gaps worth a decision under Open.
5. **CONTEXT.md.** Fill profile, goal, stack, environment, verified commands, constraints,
   applies / does not apply, and a Shape section of at most twenty lines. Stay under 120 lines.
   In a foreign repository, read `CONTRIBUTING.md`, `AI_POLICY.md` (or the equivalent), the DCO
   or CLA note and the project's own agent instructions first, and copy their hard constraints
   into Constraints: what the maintainers forbid (autonomous contributions, AI-written PR text or
   comments), the sign-off they need, the branch they take PRs against. `/cobot:contribute`
   reads them from there before anything reaches upstream.
6. **Rules.** Print the owner-layer lines that would make the verified commands silent for the
   gate (`allow Bash(<command>*)`), and offer to append them to `~/.claude/cobot.rules`. Never
   touch `settings.json`; `/cobot:rules sync` renders the hard wall for the owner to apply.
7. **Journal.** Replace the template entry's fields with what you did (`cobot-memory journal
   add`). Report: trust path taken, profile, the verified commands, what you could not verify.
