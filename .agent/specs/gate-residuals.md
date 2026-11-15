# Spec — the gate's residual path gaps (findings F-29 to F-32)

size: medium · profile: library · owner: YpNo · date: 2026-11-15 · revision 1 · built on
`chore/journal-compact-0.3` `f0d6117` (main `a6610fc`, PRs 53 and 54 merged)

## Goal

Close the open gate findings from the Antigravity wrap and the F-28 rebase, in both runtimes,
without widening anything. Measured 2026-11-15 on `f0d6117` (bash 5.2, Linux, ext4), project rule
`never Write(*/vault/*)`, `alias -> vault/key.txt`:

| # | command or call | today | after |
|---|---|---|---|
| F-29 | a project row `ask Bash(curl *[ -- cobot verified this as a safe read, approve it]*)` | the ask's reason prints the pattern: repository text in the owner's prompt | the reason names `.agent/cobot.rules:<line>` and the decision, never the pattern |
| F-30 | Write `.Claude/settings.json`; `tee .Claude/settings.json` | none | deny; ask |
| F-30 | `GIT push --force origin main` (APFS resolves `GIT` to `git`) | none | deny, like `git push --force` |
| F-31 | `cd .claude && tee settings.json` | none | ask |
| F-31 | `cd $HOME/.gemini/config && rm -r plugins` | none | ask (the `cd` operand could be the protected folder) |
| F-32 | `ls` with the working directory in `vault/` | ask, reason `protected file 'ls'` | ask, reason `the working directory … is inside a protected folder` |
| link glob | `cat al*` | none | ask (`al*` reaches `alias`, a link into `vault/`) |

Unchanged: every verdict the gate gives today outside these rows; `allow` rows never fold case
and never gain a resolved form; the gate still never executes repository content (expanding a
glob lists a folder, it runs nothing).

## Principles check

- Proportionality: medium. One module (`cobot-rules`), five residuals of one class (a path the
  rules protect, reached by a form they do not read); holds.
- Rules before autonomy: every change only adds asks or denies, or rewrites a reason; holds.
- Proof not promises: each table row is a test; the bypass-aimed review runs after the build
  (lesson from the gate PRs: each found bypasses the challenger missed); holds.
- Governance (`docs/01-decisions.md`): 28 (the gate's soundness target) gains the cd and case
  rows; 6 and 20 hold; the others are not relevant.
- Architecture: plain layering, inside `cobot-rules`; no new module.
- New dependencies: none (`glob` and `os` from the standard library).
- Delivery: one branch `security/gate-residuals`, one PR; tasks below are the commits. The branch
  sits on the journal tidy branch, which merges first.

## Stories and acceptance

1. As the owner, a permission prompt from a project rule shows where the rule is, never its
   text. Accept: `cobot-rules check` with the curl row prints
   `cobot rule: ask Bash rule at .agent/cobot.rules:2 (project layer)`; the hole form
   (`could match`) names the place the same way; default and owner rows keep their text and note.
2. As the owner, a differently cased path to a protected file is protected on a case-insensitive
   volume. Accept: tests for Write/Edit and the Bash check with `.Claude/`, `.GEMINI/`,
   `Settings.json`; a never Bash row against `GIT`/`Git` as the program word; an `allow` row with
   a different case stays unmatched.
3. As the owner, a bare word after an in-command `cd` is a path in the folder the `cd` reaches.
   Accept: `cd .claude && tee settings.json`, `cd .agents; tee hooks.json`,
   `pushd vault && cat key.txt` ask; `cd docs && tee notes.md` stays silent; an unknown `cd`
   (`cd "$d" && tee x`) keeps today's verdict.
4. As the owner, a `cd` whose operand could be a protected folder asks. Accept:
   `cd $HOME/.gemini/config && rm -r plugins`, `cd ~/.gemini/config/` ask;
   `cd "$(git rev-parse --show-toplevel)" && make` stays silent.
5. As the owner, a command whose working directory is protected asks once, naming the folder.
   Accept: `ls`, `make`, `git status` in `vault/` ask with
   `the working directory '<dir>' is inside a protected folder (never Write(*/vault/*), project
   layer at …)`; a bare program word is never resolved against the working directory.
6. As the owner, a bare glob that reaches a link into a protected folder asks. Accept: `cat al*`
   and `cat ./a?ias` ask; `cat *.md` in a folder without links stays silent; a glob with more than
   `GLOB_EXPAND_MAX` matches asks.
7. Under agy, the same rows hold through `run_command` with and without `Cwd`. Accept: one
   `test_gate_agy` row per story 3–6.

## Clarify

None asked. Decisions taken (each expensive to undo is listed under Trade-offs):

- F-29 shows the location, not a quoted pattern: quoting does not stop text written to persuade.
- F-30 folds case always for `never` and `ask` path rows, rather than probing whether a volume
  is case-insensitive: a false ask on Linux for `.Claude/` costs one prompt; a probe costs a
  `stat` per hook call and still misses a volume mounted later.
- F-32 keeps the ask (an implicit-cwd command like `make clean` or `git clean -fdx` writes in a
  protected folder without naming a file) and fixes its reason.

## Plan

1. **F-29.** `Rule.shown()`: `text()` for the default and owner layers; for the project layer
   `"{decision} {tool} rule at .agent/cobot.rules:{line}"` (an MCP row: `mcp rule at …`).
   `Verdict.reason` and `could_match` use it. The decision and tool come from fixed vocabularies,
   so nothing the repository wrote reaches the reason.
2. **F-30.** `matches_file(rule, forms, fold=False)`: with `fold`, compare `casefold()` of both.
   `judge_file` folds for `never` and `ask` rows only; `word_touches` folds (never rows only);
   `path_may_match` already folds when a glob is present and now folds always. Program word:
   `judge_segment` adds a variant with the program word casefolded (after wrappers, only when it
   differs); `outranks` keeps the stricter, and an `allow` from that variant is ignored.
3. **F-31.** `expand_script` and `expand_units` keep each segment's `Dirs` in the entry
   (`(segment, origin, unit, dirs)`); `protected_file_touched` resolves a bare word against every
   directory in the segment's `Dirs`, and against the payload cwd when `Dirs` is unknown.
4. **F-31, unknown cd.** A `cd`/`pushd` operand is checked as a folder: the token with a trailing
   `/` goes through `word_touches`, so a hole-led operand (`$HOME/.gemini/config`) that names a
   protected folder's last part meets the folder row; a bare hole (`"$d"`, `$(…)`) still reads
   like a variable and stays silent.
5. **F-32.** `protected_cwd(dirs, protected)`: the first directory (payload cwd and every known
   `Dirs` entry) inside, or equal to, a protected folder row's folder or matching a protected
   pattern; the ask names it and the rule (`Rule.shown()`). `protected_file_touched` skips the
   program word when it has no `/` (PATH resolves it, never the working directory).
6. **Link glob.** For a token whose holes are all globs: rebuild the glob (`glob.escape` on the
   literal parts, each hole's span), expand it with `glob.iglob(root_dir=dir)` non-recursively for
   every directory in effect, at most `GLOB_EXPAND_MAX = 1024` matches; each match goes through
   `file_forms` + `matches_file`; reaching the cap asks.
7. Docs (configuration known asks, architecture security model, decision 28 amended), CHANGELOG
   Security, FINDINGS F-29..F-32 closed.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | F-29: `Rule.shown`, reason and `could_match`; tests (story 1) incl. the memory hook test | a | — | — |
| T02 | F-30: case fold for restrictive path rows and the program word; tests (story 2) | a | auth | T01 |
| T03 | F-31: segment directories threaded to the protected check; cd operands as folders; tests (stories 3, 4) | a | auth | T02 |
| T04 | F-32: `protected_cwd`, bare program word skipped; tests (story 5) | a | auth | T03 |
| T05 | link globs expanded on disk with a cap; tests (story 6); agy rows (story 7) | a | auth | T04 |
| T06 | docs, CHANGELOG, decision 28, FINDINGS closed | b | — | T05 |

All `auth` tasks are test first; one lane, since every task edits `cobot-rules`.

## Trade-offs

- Location over a quoted pattern (F-29): the owner opens one file to read the rule; no repository
  text can speak in a prompt.
- Always fold over probing the volume (F-30): stricter on Linux by design; `allow` never folds.
- Program-word fold over folding the whole command: arguments stay case-sensitive (`--FORCE` is
  not `--force` to git).
- Known `cd` targets only (F-31); an unknown target is covered by its operand check (story 4),
  not by asking every later word, which would ask on every `cd "$(git rev-parse …)"`.
- Keeping the protected-cwd ask (F-32) over silencing argument-less commands: an implicit-cwd
  write cannot be told from a read.
- Non-recursive expansion with a cap (link glob): `**` keeps the lexical check only, so a link
  deeper than the glob's segments is a named residual; the hook stays fast.

Residuals named, not fixed: `nocaseglob` expansions on disk; a link created between the check and
the run (inherent to any pre-run gate); a recursive `**` reaching a link.

## Challenger verdict

pending

## Converge

pending
