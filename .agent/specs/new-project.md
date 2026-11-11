# Spec — new projects: onboard, spec and build from an empty repository

size: medium · profile: library · owner: YpNo · date: 2026-11-11

## Goal

cobot assumes a codebase exists. On latex-resume-generator (2026-11-11, no commit, empty remote)
onboard could only record unknowns: it inferred the goal from the folder name, guessed the
profile, verified no command, and told the owner to re-run onboard after the first commit. The
spec that followed chose Rust and a `cli → service` profile but left CONTEXT.md saying "language
undecided", and wrote crate versions without `lang-rust`, whose `paths:` trigger cannot fire with
no `.rs` file. On the way, `cobot-memory init --help` ran `init` and wrote the three files with
the default profile. This change gives a new project its own path: cobot recognises it, onboard
asks the owner instead of fingerprinting, the first spec makes the scaffold its first task and
writes its decisions into CONTEXT.md, and build records the scaffold's proof commands as the first
verified commands. Nobody runs onboard twice. What does not change: the existing-repository path,
trust (identities, trusted roots, foreign mode), the gate's contract (one `ask` row is added), the agents, `protocol.md` (2 995 of
3 000 characters: no room, and none needed).

## Principles check

- Proportionality: one detection function, one brief line, three skill sections, CLI hygiene,
  one eval; no new agent, no new skill.
- Rules before autonomy: onboard proposes the first commit, it never makes one unasked; `git
  commit` keeps its gate `ask`.
- Knowledge is a skill: the spec loads the chosen `lang-*` skill by name instead of looking
  versions up itself. The `lang-rust` versions gap seen on latex-resume-generator (`clap`,
  `serde`, `proptest`, `tempfile`, `assert_cmd` missing) goes to the knowledge refresh, not here.
- Proof, not promises: the verified table never holds a command that did not run; on a new
  project it says so in one row until the scaffold task's proof runs.
- Governance (docs/01-decisions.md): decision 2 (one planning path) holds, the first spec is the
  plan; decision 20 (one spec, one branch, one PR) holds; decision 21 (currency at onboard) holds,
  `cobot-deps check` still runs and reports no lockfile; decision 22 (named dependencies) holds,
  the scaffold's dependencies are named in the spec; ADR-0003 (nothing writes the owner's
  `~/.claude` files) holds; the others are not relevant.
- Architecture: plain layering (the plugin's own shape).
- New dependencies: none.
- Delivery: one branch `feat/new-project`, one PR; tasks below are the commits.

## Stories and acceptance

1. As the orchestrator, `cobot-memory check` tells me whether the repository is new, in fixed
   labels only (a file name is repository content): `tree: new (no commit)`, `tree: new
   (bootstrap files only)`, `tree: existing`, `tree: inside another repository`, or `tree: not a git repository`. New is decided on
   the files alone: every tracked and untracked, non-ignored file is in the bootstrap set
   (`.agent/`, `.claude/`, and at the root only `.gitignore`, `.gitattributes`, `.editorconfig`,
   `README*`, `LICENSE*`, `CHANGELOG*`); an empty folder is new. A never-committed folder of 200
   `.rs` files is existing. A git error or timeout (`git()` returns None) reads as `existing`, never
   as new. A work tree whose `--show-toplevel` is above the working directory, with nothing tracked
   below it (a dotfiles repository at `~`), is `inside another repository`: onboard offers `git
   init` here and never writes `.agent/` at the parent's root. A bare repository is not a work
   tree (`--is-inside-work-tree`) and reads as `not a git repository`. Accept: `pytest tests/test_cobot_memory.py -k tree_` (empty repository; README and
   LICENSE committed; uncommitted source files; `docs/README.md` counts as existing; a workflow
   under `.github/` counts as existing; ignored files do not count; git failure; not a repository; a folder inside a parent repository;
   an untracked `target/` costs one line through `--directory --no-empty-directory`).
2. As the orchestrator, the session brief names the next step when there is no memory yet:
   today a trusted repository without `.agent/` gets an empty brief and nothing says onboard.
   Trusted and no CONTEXT.md → `cobot memory: none yet (new project). Ask the owner to type
   /cobot:onboard.`, or `(existing repository)`. Untrusted with no remote and no commit, inside a
   git repository → the reason reads `no remote and no commit: /cobot:onboard starts it` (no
   "new project" label: the files decide that, not the reason). Outside a git repository → `cobot memory: not a git repository`, and nothing proposes
   onboard there; `inside another repository` names the parent's root. Accept: `pytest tests/test_cobot_memory.py -k "brief_ and (noMemory or newProject
   or notARepository)"`.
3. As the owner, `/cobot:onboard <what the project is for>` on a new project asks instead of
   guessing: the goal is my words (from the argument, else one prose question; never the folder
   name), then one `AskUserQuestion` with profile, licence and forge (skipped when a remote names
   it); the language is not asked, the Stack section says `decided by the first spec`. It runs
   `cobot-memory init --profile <p>`, checks only what a new project needs (the runtimes present,
   `df -h .` against the 10 GB guard, `cobot-deps check`), writes CONTEXT.md with one
   verified row `| — | none yet: the first spec's scaffold task records them | — | <date> |`, skips
   the rules dry run, and ends with `/cobot:spec <goal>` as the next step. In a folder that is not a
   git repository, or inside another one, it offers `git init -b main` and runs it only on my yes;
   the default rules gain `ask Bash(git init*)` so the gate asks too. Accept: eval
   `new-project-onboard` passes a single run; `python3 scripts/check-plugin.py` exit 0.
4. As the owner of a repository with no commit, onboard makes the current branch (`main` or
   `master`, whatever `init.defaultBranch` gave) exist before any spec branch: without it, `git
   worktree add -b feat/x` infers `--orphan`, the spec branch becomes its own root, and its PR has
   no base.
   - With a remote, `git ls-remote --heads origin` first. If the remote has branches (a repository
     created with a README), it offers `git fetch origin` and `git switch <default branch>`, never
     an empty commit: unrelated roots end in a rejected push and a tempting force push.
   - If the remote is empty or there is none, it offers the empty first commit (`git commit
     --allow-empty -m "chore: initial commit"`, which the gate asks about). Without a remote it then
     runs `cobot-memory init --trust-root` (or I add a remote of mine and it takes the identity
     path); with an empty remote it says the branch must reach it (my push, which asks) before the
     first PR.
   - If the commit fails (signing, a global hook), it shows the error and gives me the command to
     run myself; it never bypasses signing or hooks (`--no-verify`, `--no-gpg-sign`, `-c
     commit.gpgsign=false`).
   - It never commits, fetches or switches without my yes. `init --trust-root` before any commit
     refuses and writes no file.

   Accept: the onboard skill text, and `pytest tests/test_cobot_memory.py -k trustRoot_` (after an
   empty commit the repository is trusted; before it, nothing is written and the line says what to
   do); `cobot-rules check "git init -b main"` prints `ask`.
5. As the owner, the first spec on a new project needs no cold read and leaves CONTEXT.md true:
   - the new-project rules apply when CONTEXT.md's Stack says `decided by the first spec` or its
     verified table holds only the `none yet` row (the brief carries no `tree:` line);
   - the language is a clarify question, counted in the five, unless the owner's request already
     names it; a profile the choice changes (`cli → service`) is updated, not asked again;
   - once the language is chosen, the spec calls the `lang-<language>` skill by name before it
     writes a version or a command;
   - it writes the decided profile, the Stack lines and the Applies lines into CONTEXT.md in the
     same step, so the build's brief is current;
   - T01 is the scaffold: manifest, toolchain pin, lint, format and test configuration, one
     passing test; its proof commands are the project's first verified commands.

   Accept: the spec skill text; `python3 scripts/check-plugin.py` exit 0 (size caps).
6. As the orchestrator in `/cobot:build`, when CONTEXT.md's verified table has no command yet, the
   proof commands of the first accepted task are recorded there with their result and date (the
   "none yet" row removed), then `cobot-memory check` runs, and the owner-layer allow lines are
   printed as onboard step 7 does. Accept: the build skill text.
7. As anyone typing `<bin> <command> --help` or `-h`, I get the usage on stdout, exit 0, and
   nothing runs or is written; an unknown `--flag` is refused with exit 2 and the usage; `init
   --profile` takes only the six profiles (`embedded` is a project kind in decision 19, not a
   profile, and is refused). For `cobot-memory`, `cobot-deps` and `cobot-rules`. A flag the
   tables miss would fail silently, since `cobot-session` reads stdout only: a test collects every
   `cobot-* <command> --flag` from `hooks/`, `skills/`, `.github/workflows/` and `scripts/`
   (stopping at the first quote, so an inner command's flags are not taken) and asserts each is
   accepted, and asserts `cobot-session`'s argument lists (`brief --budget`, `knowledge --brief`)
   directly, since a text grep cannot see them. Accept: `pytest tests -k
   "help_ or unknownFlag_ or profile_ or flagsInUse_"`; the latex-resume-generator case
   (`cobot-memory init --help` in an empty folder) writes no file.

## Clarify

- Q1 What counts as a new project → a) no commit, or only bootstrap files (README, LICENSE,
  `.gitignore`, `.agent/`, `.claude/`), which covers a GitHub repository created with a README ·
  b) no commit only → recommended: a) → **answer:** a) (owner, 2026-11-11); refined at pass 1: the
  files alone decide, an uncommitted codebase is existing
- Q2 No remote and no commit → a) onboard offers an empty first commit (gate asks), then
  `--trust-root` · b) onboard stops and asks the owner to commit or add a remote · c) trust a
  commit-less folder by its path → recommended: a); c) is weak, a path is not an identity →
  **answer:** a) (owner, 2026-11-11); extended at pass 1: the empty commit is offered whenever
  there is no commit, remote or not
- Q3 Who decides the language → a) onboard asks, with "the first spec decides" as an option · b)
  always the first spec → recommended: a), the answer is cheap at onboard and the spec can still
  revisit it → **answer:** b), always the first spec (owner, 2026-11-11)
- Q4 The `--help` fix → a) in this PR (T01; it broke this very path) · b) its own tiny PR first →
  recommended: a), one commit, tested apart → **answer:** a) (owner, 2026-11-11)

## Plan

1. CLI hygiene first, so the skills can rely on `--help` and on `--profile` being checked.
2. Detection in `cobot-memory` (`tree_state`), surfaced in `check` and the brief.
3. Skill text: onboard's new-project branch, the spec's new-project rules, build's first
   verified commands. `protocol.md` is untouched; onboard is user-invocable only, so the brief
   line is what reaches the model.
4. The eval, then docs.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | CLI hygiene: a per-command flag table in `cobot-memory`, `cobot-deps` and `cobot-rules`; `-h`/`--help` after any command prints usage, exit 0, before any work; unknown `--flag` exit 2; `init --profile` checked against the six profiles. Tests `help_*`, `unknownFlag_*`, `profile_*`, and `flagsInUse_*` (every flag used in docstrings, hooks, skills, workflows and scripts is accepted) | a | — | — |
| T02 | `tree_state(mem)` in `cobot-memory`: `git rev-parse --is-inside-work-tree` first (not a repository; a bare one included), `--show-toplevel` above the working directory with nothing tracked below it (inside another repository), then `git ls-files --cached --others --exclude-standard --directory --no-empty-directory` all in the bootstrap set (root-only names), None from `git()` → existing; the fixed-label `tree:` line in `check`. Tests `tree_*` | a | — | T01 |
| T03 | Brief without memory: the two `none yet` lines, `not a git repository`, the untrusted reason for a new project without remote; `init --trust-root` refuses before writing when there is no commit; `ask Bash(git init*)` in `default.rules` with a gate test; `test_brief_emptyMemory` changes from `""` to the line. Tests `brief_*noMemory*`, `brief_*newProject*`, `brief_*notARepository*`, `trustRoot_*` | a | — | T02 |
| T04 | `skills/onboard/SKILL.md`: step 1 branches on `tree: new`; the new-project steps (goal, one question round without the language, init with profile, runtimes and disk, no fingerprint, the "none yet" row, no rules dry run, next step `/cobot:spec`); no commit: `ls-remote` first, fetch and switch when the remote has branches, else the empty first commit; a failed commit is handed to the owner, never bypassed; `git init` only on the owner's yes, also inside another repository; the push of the branch named before the first PR; `argument-hint: [--foreign] [what a new project is for]`; the description names new projects | b | — | T02 |
| T05 | `skills/spec/SKILL.md` steps 1–3: new-project rules (keyed on `decided by the first spec` or the `none yet` row; no cold read, language clarify, `lang-*` by name, CONTEXT.md updated, T01 scaffold); `skills/build/SKILL.md` step 3: first verified commands and allow lines | b | — | — |
| T06 | eval `new-project-onboard`: fixture `git init`, one commit with README.md only, no remote; fixture commits with fixed author, committer and dates so the root commit, and so its `~/.claude/cobot/trusted` line, is the same every run; prompt gives goal, profile, licence and forge (`other`), and says trust the root; graders: Bash `init .*--profile`, Bash `--trust-root`, CONTEXT.md names the goal's words and `decided by the first spec`, last message names `/cobot:spec`, no AskUserQuestion, no `pyproject.toml` or `src/` written. The run leaves one line in `~/.claude/cobot/trusted` (as onboard does), said in the eval description | — | — | T04 |
| T07 | docs: README quick start (new project and existing repository), `docs/architecture.md` onboard flow, `docs/configuration.md` if a flag changed, CHANGELOG, journal, converge | — | — | T01–T06 |

Lanes: a (`bin/`, `tests/`) and b (skills) touch disjoint files.

## Trade-offs

- A `tree:` line in `check` over a new CONTEXT.md header field: a header field would be listed as
  missing in every existing repository's `check`, and the state changes by itself at the first
  real commit.
- Files over commits: GitHub and GitLab offer a README and a licence at creation, and those
  repositories are as new as an empty one; an uncommitted codebase is not.
- Build records the first verified commands over a second onboard: the scaffold's proof already
  ran them, with exit codes; onboarding again would re-run them for nothing.
- No protocol line: 5 characters of room, and the brief line reaches every session anyway.
- The lang-rust versions gap is not fixed here: it is knowledge, and the weekly refresh or
  `/cobot:learn` owns it.

## Challenger verdict

Pass 1 (2026-11-11, challenger): **UNSOUND**, ten points, all folded without changing an owner
answer. BLOCKER: with an owner-owned empty remote and no commit (the motivating case) `main` is
unborn, `git worktree add -b` infers `--orphan` and the spec's PR has no base → the empty first
commit is offered whenever there is no commit, and the push of `main` is named (story 4; Q2's
answer extended to the remote case). MAJOR: "no commit" made an uncommitted codebase new → files
alone decide (story 1, Q1's "no source yet"); a folder outside git read as new and could lead to a
`git init` in `~` → `not a git repository`, `git init` only on the owner's yes (stories 1–3); a
flag missing from the new tables would empty every brief silently → `flagsInUse_` test (story 7).
MINOR: git failure reads as existing; the eval names the forge and clears its `trusted` lines;
`init --trust-root` refuses before writing; the spec's new-project trigger is the Stack line or
the `none yet` row; fixed labels and root-only names in `tree:`; `embedded` is not a profile.

Pass 2 (2026-11-11, challenger): **SOUND WITH CHANGES**, nine points from the folds, all folded.
MAJOR: an empty commit beside a remote that has commits splits history and invites a force push
→ `ls-remote` first, fetch and switch instead (story 4); a folder inside a parent repository (a
dotfiles repository at `~`) would get `.agent/` written at the parent's root → `inside another
repository`, `git init` offered (stories 1–3). MINOR: the flag collector asserts
`cobot-session`'s argument lists and stops at quotes; a failed commit is handed to the owner,
never bypassed; `git init` gets an `ask` row (the gate had none); the untrusted reason drops the
"new project" label; the eval's forge is `other` and its root commit is deterministic, so the
`trusted` file keeps one line; the branch may be `master`; `--directory --no-empty-directory`
keeps `ls-files` short.

## Converge

pending
