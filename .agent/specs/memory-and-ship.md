# Spec — one commit per change, parked notices, promotion lint, a ship that checks its ground

size: medium-large · profile: library · owner: YpNo · date: 2026-11-18 · revision 2 · built on
`main` `97c48dc` (security auditor merged as PR 73)

## Goal

Close the memory and ship findings from the 2026-11-15/16 dogfood sessions and evals: F-37, F-41,
F-42, F-43, F-46, F-47 and F-48. Measured on `97c48dc`:

| # | today | after |
|---|---|---|
| F-41 | a verified change takes two commits (code, then a journal entry naming its sha): 4 of 7 commit asks in curriculo; `journal add` prints an error and exits 0, so `journal add … && git commit` commits anyway | one commit: the journal names the tested tree; an invalid entry exits 1 |
| F-48 | the owner approved the same `git commit` ask four times and was never shown an allow line | from the second repeat of one ask row in a session, the reason ends with the owner allow line that would lift it |
| F-48 | builders' `Noticed:` items were never filed | the report hook parks them in `.agent/noticed.md`; wrap files or drops each, and `check` names the rest |
| F-42 | `learn --promote` carried a private slug, a CI run id, a release snapshot and an unproven line into the plugin | such lines are refused and named; `reported` lines need `--allow-reported` |
| F-46 | dated lines in `skills/onboard/references/workstation.md` never reach the brief's staleness line | every skill's dated lines are scanned |
| F-47 | `init --trust-root` said `root commit added`, `check` still said untrusted, and the report named `cobot-memory trust` | both name the trust file they used; onboard re-checks and names `init --trust-root` |
| F-48 | `cobot-deps check` prints its GitHub Actions hint in a repository with no workflow (`_cobot_deps.py:522`) | only when `.github/workflows/` holds a workflow |
| F-37 | ship pinned action SHAs but left `rust-toolchain.toml` on `stable`: CI took 1.100, the proof ran 1.99 | ship flags floating toolchain channels, and lists every pin Dependabot cannot see with its update path; `cobot-deps` reports floating channels |
| F-43 | ship proposed a PR against an empty remote, and stacked `ci/` on an unmerged branch | ship reads the remote's default branch first and names the base |
| F-48 | ship installed absent audit tools globally and unpinned | absent tools are printed in the owner's install route, pinned, never run |

Unchanged: the gate's decisions; the stamp's doc-only rule (`DOC_ONLY_PREFIXES`); the existing
`verified: <commit sha>` form, still read; the protocol's paths.

## Owner's answers (2026-11-18, before drafting)

- **Stamp:** one commit, stamped by the tested tree (`verified: tree <sha>`).
- **Repeated asks:** offer the allow line after the second repeat of one row in a session.
- **Noticed items:** the report hook parks them; wrap clears them.
- **Promotion lint:** refuse, and name each refused line.

## Principles check

- **Proportionality:** medium-large, but seven small, separate changes. Most are `cobot-memory`
  and skill text; one is gate state.
- **Rules before autonomy:** nothing widens. The allow line is printed, never written; tools are
  printed, never installed; the hook writes only cobot's own memory file.
- **Proof, not promises:** each Goal row becomes a test. The skill changes get text tests, and
  ship's ground step gets an eval case.
- **Governance:**
  - decision 20 (one spec, one branch, one PR) holds;
  - decision 21 (dependency currency) gains the toolchain row;
  - decision 23 (knowledge freshness) gains every skill's lines;
  - decision 29 (install routes) applies to ship's tools.
  - A new decision, 31, records the tree stamp and the parked notices: they change the wrap
    discipline that `docs/02-design.md` and the protocol describe.
- **New dependencies:** none.
- **Delivery:** one branch `feat/memory-and-ship`, one PR; the tasks below are the commits.

## Stories and acceptance

1. **One commit per verified change (F-41).**
   - **The key:** `cobot-memory stamp --tree` prints `tree <key>`. The key is the index's tree
     (`git write-tree`) with the root entries `.agent`, `docs`, `CHANGELOG.md` and `README.md`
     removed, rebuilt with `git mktree`. `cmd_stamp` computes the same key from `HEAD^{tree}` and
     compares the strings. No object lookup is needed, so the key survives gc and holds in any
     clone (challenger 1: an unreachable written tree is pruned).
   - **Foreign mode** (`.agent` a symlink): the key is the whole tree, an exact match, as today.
   - **Readiness:** `stamp --tree` refuses (exit 1, `stamp: not ready — <reason>`) when a tracked
     file outside the doc entries has unstaged changes, or an untracked file sits outside them and
     the ignored paths: the key must be what the tests ran on.
   - **The line:** a journal stamp reads `verified: tree <key> · <commands>`, or as today
     `verified: <commit sha> · …`.
   - **`journal add`** exits 1 on an invalid entry, so a chained commit stops. `--check`
     validates without writing (a `SWITCHES["journal"]` entry).
   - **The flow**, in wrap's journal step and the build skill: stage, `stamp --tree`,
     `journal add`, `git add .agent/JOURNAL.md`, one `git commit`. In foreign mode the journal
     lives outside the tree, so there is no `git add` of it (it exits 128 there).
   - Accept:
     - one commit of code plus journal is `ok`, also after `git gc --prune=now` and in a fresh
       clone;
     - an untracked `src/x.py` gets `not ready`;
     - a later code commit is `missing`;
     - a foreign-mode change under `docs/` is `missing`;
     - the commit form stays `ok` (its existing tests pass).
2. **The repeated ask names its allow line (F-48).**
   - **What can be offered:** only the rows in `OFFERED_ROWS`, a short list in `cobot-rules` of
     local, undoable work: `ask Bash(git commit*)`, `ask Bash(git rebase*)`. Never an agent-scoped
     row (`ask Bash(*) @consultant` would offer `allow Bash(*)`), an outward row, an install route,
     a credential printer, `agy`, an MCP row, or an owner-layer ask: the owner wrote that one, and
     deletes it (challenger 3).
   - **The counter:** the gate (Claude Code only: its payload carries `session_id`) counts asks
     per session and per row, keyed by `rule.text()`, in `data_dir().parent / "asks" /
     <session>.json`. The file holds rule texts and counts only, never command text. A
     `session_id` that is not UUID-shaped is ignored. Files older than 7 days are pruned. Writes go
     to a temp file, then a rename; a lost update between parallel hooks is harmless. The winning
     ask and the rows in `also` both count.
   - **The offer:** from the third ask of an offered row in a session, the reason ends with
     ` · to stop asking: allow Bash(<pattern>) in <owner rules path>`, where the path is
     `fixed_layer_paths()["owner"]` (it honours `CLAUDE_CONFIG_DIR` and `COBOT_RULES_OWNER`). A
     row is marked offered only when the line was printed: if the stamp suffix and `also asks`
     leave no room, the next ask tries again.
   - Accept:
     - the third `git commit -m x` in one session names `allow Bash(git commit*)`, and the fourth
       does not;
     - the third consultant `curl` names nothing, nor does a third `git push`;
     - a new session starts at zero;
     - a missing, unreadable or corrupt state file never blocks: the gate judges as before.
3. **Noticed items are parked and cleared (F-48).**
   - The report hook, after a builder report passes, runs `cobot-memory noticed add` (timeout
     5 s, under the hook's 10 s) with the `Noticed:` items on stdin. An item is a bullet under
     `Noticed:`, or the text after it on its line; `none` is no item. Items are appended to
     `.agent/noticed.md` of the session's checkout (the payload's `cwd`, not the builder's
     worktree), one dated line each, de-duplicated, only in a trusted memory. A failure never blocks
     the report.
   - `noticed.md` joins `KNOWN_AGENT_FILES`, so the brief does not list it as an extra file. It is
     committed with the journal like any memory file; wrap leaves it empty.
   - Wrap gains a step: each parked item becomes `findings add`, or is dropped with a reason;
     `noticed clear` empties the file.
   - `cobot-memory check` prints `noticed: N waiting` when the file holds items.
   - Accept:
     - a builder report with two `Noticed:` items leaves two lines;
     - `Noticed: none` leaves none;
     - an untrusted memory leaves none;
     - `check` counts them.
   - Limit: in a host where `Agent` returns "Async agent launched" (F-35), the hook sees no report
     and parks nothing; the build skill files the hand-back's items itself there.
4. **Promotion is linted (F-42).** The lint sits in `promote_entries`, so both promotion paths
   pass through it: a JSON delta, and `learn --promote <topic>` from pending lines (that path
   skips `filter_delta` and `SECRET_RE` today; the secret check moves there too). It refuses an
   entry whose claim or source holds:
   - a run id (`/actions/runs/<n>`, `/pipelines/<n>`, `/jobs/<n>`);
   - a user's home path (`/home/<x>/`, `/Users/<x>/`, a drive letter). `~/` stays allowed: it is
     generic by nature, and the plugin already ships such lines;
   - a release snapshot (`latest (release|version) is`, `as of today`);
   - an `owner/repo` slug, matched on word boundaries, whose owner is the promoting repository's
     `origin` owner or one of the owner's identities from the trust settings;
   - a `reported` status, unless `--allow-reported` is given.

   Each refused entry is named with its reason, and the rest are promoted. Project-scope entries
   and `.agent/knowledge` writes are unchanged. Accept:
   - one test per rule, through both paths;
   - a clean delta still promotes;
   - the plugin's own `~/.cargo` line passes.
5. **Every skill's dated lines are scanned (F-46).** `scan_plugin` reads every skill folder, and
   `check-plugin`'s caps keep their prefixes. The brief's line names the skill (`onboard (2
   stale)`). Its hint is `/cobot:learn <topic>` for a knowledge skill, and `edit its references
   (a cobot PR)` for any other. Accept: a test with a stale line in a non-knowledge skill's
   reference finds it and gives that hint.
6. **Trust writes show where they went (F-47).** The root cause was a command run where
   `CLAUDE_CONFIG_DIR` differed (challenger 5).
   - `init --trust-root` prints the trust file's path: `root commit added to <path>`.
   - `cobot-memory trust` and `check` print the file they read when they say untrusted.
   - A command cobot names for the owner to run carries `CLAUDE_CONFIG_DIR=<path>` in front when
     that variable is set: `trust_not_recorded`'s line and onboard's.
   - Onboard step 2 re-runs `check` after `init`. If it still says untrusted after
     `root commit added`, it reports both paths and names that prefixed
     `cobot-memory init --trust-root`, never `cobot-memory trust`.
   - Accept: the outputs hold the path, the prefix appears only when the variable is set (tests),
     and the onboard text test names the command.
7. **`cobot-deps` reads the ground ship needs (F-37, F-48).**
   - The Actions hint prints only when `.github/workflows/` holds a `*.yml` or `*.yaml`.
   - A `toolchain` row lists floating channels, read from files only and never by running a tool.
     A channel floats when it names no exact release: `stable`, `beta`, `nightly` without a date,
     `latest`, `lts`, `lts/<codename>`, `node`, or a major alone (`3`, `20`). The files:
     - `rust-toolchain.toml` (`channel`) and `rust-toolchain`;
     - `.nvmrc` and `.node-version`;
     - `.python-version` (a major alone floats; `3.12` is the minor and passes);
     - `.tool-versions` and mise's `mise.toml`, `.mise.toml`, `.config/mise.toml` and
       `mise/config.toml`, in both the string and the `{ version = … }` table form;
     - `go.mod`: the `go` and `toolchain` lines are minimums. With no `toolchain` line the row
       says that CI's setup-go and a local `GOTOOLCHAIN=auto` may pick newer patches; it is a
       note, not a float.
   - Accept: one test per file kind and form (F-37's `rust stable` in `.tool-versions`
     included), a pinned file reports nothing, and no workflow means no hint.
8. **Ship checks its ground (F-37, F-43, F-48).** Ship's ground step:
   - **Toolchains:** names each floating channel from `cobot-deps` and proposes a pin. It lists
     every pin Dependabot cannot see (a binary with its sha256, `install-action` tool versions, a
     scanner's version, a container digest), each with its update path.
   - **The remote:**
     - Read `git remote get-url origin` first: no origin is named as such.
     - Then `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes' timeout 20 git
       ls-remote --symref origin HEAD`. That form is silent under the gate and cannot hang on a
       credential prompt.
     - Exit 0 with no output is an empty remote; a failure (exit 128, or the timeout) is
       `unreachable`, never empty. Either is named before any push or PR is proposed, with the
       first push to propose for an empty remote.
     - The report names the base branch, says when the work sits on an unmerged branch, and says
       who commits ship's output.
   - **Absent tools:** an absent audit tool is printed in the owner's install route
     (`cobot-env`, decision 29) and never run. Its version comes from a verified knowledge line
     or a release resolved today, and the source is named; with neither, ship names the tool
     without a version and says so. A job that needs the tool installs it in CI.
   - Accept: ship's text tests name each rule.
9. **The `ship-ground` eval.**
   - The scaffold has `rust-toolchain.toml` on `stable` and an empty bare remote at
     `.git/remote.git` (inside the workspace, invisible to the stamp's readiness check). It
     writes `.agent/CONTEXT.md` with `forge: github` (a local-path origin defeats forge
     detection), with trust seeded as `gitlab-ci-shape` does.
   - Graders:
     - a regex on `last_message` for `rust-toolchain` near `stable`;
     - a regex for the empty remote;
     - `tool_used Bash input_match "ls-remote"`.
   - Run once locally with `--scaffold`.

## Plan

1. **`cobot-memory`:**
   - `stamp --tree`;
   - the tree form in `STAMP_RE` and `cmd_stamp`;
   - `journal add` exit codes and `--check`;
   - `noticed add|list|clear`, and the `check` line;
   - the trust paths in `init`, `trust` and `check`;
   - the promotion lint in `filter_delta`'s promote path;
   - `scan_plugin` over every skill folder.
2. **`cobot-rules`:**
   - `ask_offer()` in `gate()`: the state file under `data_dir()`, written atomically (a temp
     file, then a rename) and wrapped so that any error is ignored;
   - `report()` hands `Noticed:` items to `cobot-memory noticed add` (a subprocess, as
     `stamp_suffix` does).
3. **`_cobot_deps.py`:** the workflow test for the hint, and `toolchain_row()`.
4. **Skills:** wrap (journal, noticed), build (one commit, async hand-back Noticed), onboard
   step 2, ship (ground). The protocol's stamp line, if it names two commits.
5. **Eval** `ship-ground`, run once locally.
6. **Docs:** decision 31, `docs/02-design.md` (wrap, stamp), `docs/configuration.md` (the
   offered line, `noticed.md`), CHANGELOG. F-37, F-41, F-42, F-43, F-46, F-47 and F-48 closed.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | tree stamp, `journal add` exit and `--check`, wrap and build text (story 1) | a | — | — |
| T02 | noticed: hook, `cobot-memory noticed`, `check`, wrap step (story 3) | a | — | T01 |
| T03 | repeated-ask offer in the gate (story 2) | b | auth | — |
| T04 | promotion lint, every skill scanned, trust paths (stories 4, 5, 6) | c | — | — |
| T05 | `cobot-deps` hint and toolchain row; ship ground text (stories 7, 8) | d | — | — |
| T06 | eval `ship-ground`, one local run (story 9) | d | — | T05 |
| T07 | docs, decision 31, CHANGELOG, findings closed | a | — | all |

## Trade-offs

- **A keyed tree over amending a commit:** an amend rewrites the sha the journal would need to
  name. The key is known before the commit, needs no stored object, and holds in any clone. Its
  cost: a stamp no longer names a commit, so `git show <stamp>` does not work. The commit form
  stays readable for that.
- **The gate counts asks, not approvals:** the hook never learns whether the owner said yes. A
  third ask of one row is the signal; a denied ask that is retried counts too, harmless because
  the line is only printed.
- **Parking in a file, not in FINDINGS.md:** a Noticed item is a lead, not yet a finding. Wrap
  decides with the owner, so FINDINGS.md holds no noise.
- **Promotion lint refuses rather than redacts:** a rewritten line is a claim nobody checked.

## Not in scope

- F-35 (hosts without `run_in_background`), F-39 (Home Assistant expert), F-49 (trust boundaries
  in `/cobot:spec`): their own specs.
- Refreshing `lang-rust`'s stable version line: `/cobot:learn rust` does it, and story 5 makes the
  brief name stale lines.

## Clarify

Asked 2026-11-18 in one call; the owner took every recommended option (above).

## Challenger verdict

**Pass 1, 2026-11-18: SOUND WITH CHANGES** (5 MAJOR, 7 MINOR), all folded in revision 2. The
MAJOR points were reproduced by hand on `97c48dc`:

| # | level | point | fold |
|---|---|---|---|
| 1 | MAJOR | a written tree is unreachable and `git gc --prune=now` deletes it (verified) | story 1, keyed tree via `git mktree`, string compare |
| 2 | MAJOR | `git add .agent/JOURNAL.md` exits 128 in foreign mode; doc-only rule dropped there | story 1, foreign flow, whole-tree key |
| 3 | MAJOR | an offer could name `allow Bash(*)` from `ask Bash(*) @consultant` (verified rows 608–609) | story 2, `OFFERED_ROWS` only |
| 4 | MAJOR | `~/` refuses shipped lines; `promote <topic>` skips the lint and `SECRET_RE` (verified) | story 4, lint in `promote_entries` |
| 5 | MAJOR | naming `init --trust-root` repeats F-47 when `CLAUDE_CONFIG_DIR` differs; hard-coded owner path | stories 2, 6, prefixed command and `fixed_layer_paths` |
| 6–12 | MINOR | state path, UUID, pruning, row key, offer marking; `noticed.md` listing and item shape; toolchain forms; unreachable remote and prompts; eval fixture; brief wording; T05 size | stories 2, 3, 5, 7, 8, 9, tasks |

Checked clear: `git diff` accepts a raw tree; the gate is silent on `git write-tree`,
`stamp --tree`, `git ls-remote …` and `noticed clear`; the payload carries `session_id`; hooks run
outside the Bash sandbox; merges need a new stamp as today; F-35 is scoped as written.

## Converge

Built 2026-11-18 on `feat/memory-and-ship`, each task one commit with its journal entry under the
tree stamp it introduced: T01 c78ef75, T02 67688e9, T03 0f56141, T04 68d2795, T05 ad689ec, T06
8193dee, T07 the docs commit. Decision 31. Every story's acceptance holds; `ship-ground` scored
1.00 in one local run. Deviations:
- `cobot-deps` also reports a cache it cannot write (the eval sandbox needed it);
- the go.mod row is a note, not a float;
- the eval's trust seed was not seen in the local run (ship reported it; no grader reads it).

F-37, F-41, F-42, F-43, F-46, F-47 and F-48 are closed.
