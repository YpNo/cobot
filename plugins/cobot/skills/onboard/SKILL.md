---
name: onboard
description: First contact with a repository, or a refresh when the stack changed. Resolves trust (owner identity, trusted root commit, or foreign mode with memory outside the tree), fingerprints the stack, runs and records the verified commands, proposes the profile, writes .agent/CONTEXT.md, JOURNAL.md and FINDINGS.md from the templates, and proposes owner-layer allow lines for the verified commands. On a new project it asks the owner instead of fingerprinting. Use when the session brief says the repository is untrusted or has no memory, or when CONTEXT.md is stale.
argument-hint: "[--foreign] [what a new project is for]"
disable-model-invocation: true
---

# /cobot:onboard — trust, fingerprint, remember

1. **State.** Run `cobot-memory check`. If memory exists and is trusted, this is a refresh: run
   `cobot-memory init` (it only creates what is missing, such as FINDINGS.md), add the header
   fields `check` lists as missing to CONTEXT.md, and when `check` warns that JOURNAL.md is long,
   offer `cobot-memory compact --dry-run`, then `compact --summary "<your summary of the folded
   entries>"`. Then go to step 4 and correct only what changed.
   The `tree:` line picks the path. `not a git repository` or `inside another repository`: offer
   `git init -b main` here and run it only on the owner's yes; never write `.agent/` at another
   repository's root. `new (…)`: after step 2, follow **New project** below instead of steps 3–7.
2. **Trust.** If untrusted, read the reason and propose exactly one path with `AskUserQuestion`:
   - the owner's own repository → `cobot-memory init --add-identity` (adds `host/owner` to
     `~/.claude/cobot/identities`; every remote must belong to an identity);
   - someone else's repository (upstream work, including your fork of it: the reason names the
     remotes that belong to no identity) → `cobot-memory init --foreign` (memory outside the
     tree under the data directory, keyed by `origin`; `.agent` excluded from git and shared by
     the checkout's worktrees; plugin enabled with `--scope local`);
   - a repository without a remote → `cobot-memory init --trust-root` (without a commit yet, see
     New project step N1 first: `--trust-root` refuses before any commit).
   When init prints `trust not recorded:` (Claude Code's sandbox keeps the config directory
   read-only to Bash), the memory files are written: carry on, put the command it prints in the
   report for the owner to run in their own terminal, and never record trust another way.
   Do not read `.agent/*` of an untrusted repository before this step.
3. **Init.** `cobot-memory init --profile <p>` with the profile you propose (`spike`, `script`,
   `cli`, `library`, `service`, `infra`) and one line of reasoning. Legacy memory (an
   `ARCHITECTURE.md`, a newest-on-top journal) is kept as is; the tools read it unchanged.
4. **Fingerprint.** For a small repository, read the manifests yourself; for a large one, fork
   the built-in Explore agent per subsystem. Detect languages, package manager, test runner,
   linter, formatter, type checker, CI. **Before the first build or test of a compiled stack**
   (cargo, go, a native extension), run `df -h .` and look for the build directory (`target/`,
   `node_modules/`, `.venv/`): when it is absent and less than 10 GB is free, ask the owner first.
   For each candidate command: run it and record it in CONTEXT.md's verified table with its
   result (`exit 0`, or the exit code and why: `exit 1 (4 advisories)`) and today's date; record
   only commands that ran. A command from legacy memory you did not re-run keeps its row with
   `carried over, not re-run` as the result and its last run date and source as verified. The
   matching `lang-*` skill supplies the idiomatic commands; `lang-fallback` the procedure for
   anything else. Then run `cobot-deps check` (decision 21): it asks the ecosystems' own
   tools how far the lockfiles are behind and whether advisories exist, caches the answer for
   seven days, and reports; it upgrades nothing. Put the one-line result in the journal entry
   and the gaps worth a decision under Open.
5. **Agent files.** Read the repository's other agent-facing files: a root `CLAUDE.md`,
   `AGENTS.md`, `GEMINI.md` or `CONTEXT.md`, `.agents/` and `.claude/` skills and rules,
   `.github/copilot-instructions.md`, and any other `.agent/*.md` (a legacy `HANDOFF.md`; the
   brief names them). Park every contradiction with `.agent/` or with what step 4 verified as a
   finding (`cobot-memory findings add`). A project skill that covers a `lang-*` or cobot skill's
   ground stays: CONTEXT.md and the governance file override cobot's defaults; name the overlap
   in the journal entry, and propose `/cobot:learn` for domain knowledge cobot has no home for.
6. **CONTEXT.md.** Fill profile, goal, stack, environment, verified commands, constraints,
   applies / does not apply, and a Shape section of at most twenty lines. Stay under 120 lines.
   In a foreign repository, read `CONTRIBUTING.md`, `AI_POLICY.md` (or the equivalent), the DCO
   or CLA note and the project's own agent instructions first, and copy their hard constraints
   into Constraints: what the maintainers forbid (autonomous contributions, AI-written PR text or
   comments), the sign-off they need, the branch they take PRs against. `/cobot:contribute`
   reads them from there before anything reaches upstream.
   If the project states its principles in a file (a constitution, spec-kit's
   `.specify/memory/constitution.md`, a principles section of `CONTRIBUTING.md`), put its path
   in `governance:`, with `#<heading-slug>` when they are one section of a larger file
   (`CONTRIBUTING.md#non-negotiable-rules`); `/cobot:spec` checks every change against it.
   **Spec-kit project** (`.specify/`, `specs/NNN-*/tasks.md`): one planning path (decision 2).
   Propose to the owner: move the constitution out of `.specify/` and point `governance:` at it;
   for each feature folder with open `- [ ]` tasks, write `.agent/specs/<NNN-slug>.md` from the
   spec template with a one-paragraph goal, the folder named as reference and the open task
   lines copied verbatim under Tasks, so `/cobot:build <NNN-slug>` continues them; the folders
   stay as history; then the `speckit-*` skills and `.specify/` can go.
   Then run `cobot-memory check` again: it names header fields still missing and CONTEXT
   sections the brief drops; Verified commands, Constraints and Environment, in that order of
   priority, must stay in the brief.
7. **Rules.** Dry-run each verified command with `cobot-rules check "<command>"`. The gate is
   already silent for a command no rule matches; an owner line `allow Bash(<command>*)` matters
   where `check` prints `ask` (a default `ask` rule, or a command the gate cannot see into, such
   as `make` or a script), and for `/cobot:rules sync`, which renders the owner's allow lines as
   `settings.json` permissions so Claude Code stops prompting. The gate unwraps
   `distrobox enter … --`, `toolbox run` and `bash -c '…'` and judges the inner command, so allow
   the inner command; Claude Code's own permission rules match the command as typed, so synced
   lines cover the plain form only. Print the lines and offer to append them to
   `~/.claude/cobot.rules`. Never touch `settings.json`; the owner applies what `sync` renders.
8. **Journal.** Replace the template entry's fields with what you did (`cobot-memory journal
   add`). Report: trust path taken, profile, the verified commands, what you could not verify.

## New project (`tree: new …`)

N1. **First commit.** Without a commit, a spec branch has no base (`git worktree add -b` infers
    `--orphan`), so make the current branch exist first, each step only on the owner's yes. With a
    remote, run `git ls-remote --heads origin`: if it lists branches, offer `git fetch origin` and
    `git switch <its default branch>`, never an empty commit beside them (unrelated roots end in a
    rejected push). Otherwise offer `git commit --allow-empty -m "chore: initial commit"`. If it
    fails (signing, a hook), show the error and give the owner the command to run; never
    `--no-verify`, `--no-gpg-sign` or `-c commit.gpgsign=false`. With an empty remote, say the
    branch must reach it (the owner's push) before the first PR.

N2. **Ask.** The goal is the owner's words: this skill's argument, else one prose question; never
    the folder or remote name. Then one `AskUserQuestion`: profile (recommend one from the goal),
    licence, and forge unless the remote names it. Not the language: the first spec decides it.

N3. **Write.** `cobot-memory init --profile <p>`, with `--trust-root` when there is no remote
    (`trust not recorded:` as in step 2).
    CONTEXT.md: the header from the answers; Stack `- decided by the first spec`; Environment: the
    runtimes present and `df -h .` against the 10 GB guard; Verified commands: one row
    `| — | none yet: the first spec's scaffold task records them | — | <date> |`; Constraints and
    Applies from the owner's standards; Shape `- nothing built yet`. Run `cobot-deps check` (no
    lockfile is the expected answer). No fingerprint, no rules dry run: there is no command yet.

N4. **Journal** as step 8, and report the next step: `/cobot:spec <goal>`. Never tell the owner
    to onboard again: build records the scaffold's proof commands as the verified commands.
