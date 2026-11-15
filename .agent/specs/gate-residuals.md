# Spec — the gate's residual path gaps (findings F-29 to F-32)

size: medium · profile: library · owner: YpNo · date: 2026-11-15 · revision 2 (challenger pass folded) · built on
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
| HOME | `tee $HOME/.gemini/config/settings.json` · `rm -r $HOME/.gemini/config` · `cd $HOME/.gemini/config && rm -r plugins` | none: `$HOME` stays literal text, so every `~/` row is beaten by writing `$HOME/` | ask, like the `~/` form |
| F-31 | `cd .claude && tee settings.json` · `cd .claude && echo x > settings.json` · `cd .agents && tee plugins/x.sh` | none | ask |
| F-31 | `cd "$d" && tee settings.json` (unknown target, or `CDPATH` from the owner's profile) | none | ask: the word's last part matches a protected row's |
| parent | `rm -r ~/.gemini` (the parent of a protected folder) | none | ask |
| F-30 | `mv ~/.GEMINI ~/g` · `NOHUP GIT push --force` · `BASH -c "git push --force"` | none · none · ask (opaque) | ask · deny · deny |
| F-32 | `ls` with the working directory in `vault/` | ask, reason `protected file 'ls'` | ask, reason `the working directory … is inside a protected folder` |
| link glob | `cat al*` · `cat [[:alpha:]]lias` · `echo x > al*` · `shopt -s dotglob; cat *` reaching `.k -> vault/key.txt` | none | ask (the glob reaches a link into `vault/`) |

Unchanged: every verdict the gate gives today outside these rows; `allow` rows never fold case
and never gain a resolved form; the gate still never executes repository content (expanding a
glob lists a folder, it runs nothing).

## Principles check

- Proportionality: medium. One module (`cobot-rules`), five residuals of one class (a path the
  rules protect, reached by a form they do not read); holds.
- Rules before autonomy: every change only adds asks or denies, or rewrites a reason; holds.
- Proof not promises: each table row is a test; the bypass-aimed review runs after the build
  (lesson from the gate PRs: each found bypasses the challenger missed); holds.
- Governance (`docs/01-decisions.md`): no decision changes (the protected-file check's reach is
  documented in `docs/configuration.md` and the architecture security model); 6 and 20 hold;
  the others are not relevant.
- Architecture: plain layering, inside `cobot-rules`; no new module.
- New dependencies: none (`glob` and `os` from the standard library).
- Delivery: one branch `security/gate-residuals`, one PR; tasks below are the commits. The branch
  sits on the journal tidy branch, which merges first.

## Stories and acceptance

1. As the owner, a permission prompt from a project rule shows where the rule is, never its
   text. Accept: `cobot-rules check` with the curl row prints
   `cobot rule: ask Bash rule at .agent/cobot.rules:2 (project layer)`; the hole form
   (`could match`) names the place the same way; a project rule with an unknown tool name
   (`ask Approve-it(x)`) shows `tool`, not the name; default and owner rows keep text and note.
2. As the owner, a differently cased path or program reaches the same rules on a
   case-insensitive volume. Accept: Write/Edit and the shell check with `.Claude/`, `.GEMINI/`,
   `Settings.json`; `GIT`, `Git`, `/usr/bin/GIT`, `NICE GIT`, `NOHUP GIT`, `ENV GIT`, `FOO=1 GIT`
   and `BASH -c "git push --force"` deny like the lower-case form; `mv ~/.GEMINI ~/g` asks;
   `--FORCE` keeps its case; an `allow` row with a different case stays unmatched.
3. As the owner, `$HOME/` and `${HOME}/` at the start of a word read as `~/`, unless the command
   assigns `HOME`. Accept: the HOME rows of the table ask (file words, redirect targets, `cd`
   operands); `HOME=/tmp/h; tee $HOME/.gemini/config/x` keeps today's verdict for the literal.
4. As the owner, every relative word after an in-command `cd` is a path in each folder the `cd`
   may reach, redirect targets included. Accept: the F-31 rows ask; `cd docs && tee notes.md`,
   `cd docs; cat README.md`, `cd .claude && ls`, `cd "$(git rev-parse --show-toplevel)" && ls`
   stay silent.
5. As the owner, after a `cd` whose target the gate cannot know, a word whose last part matches
   the last part of a protected file row asks. Accept: `cd "$d" && tee settings.json`,
   `cd "$d" && echo x > hooks.json` ask; `cd "$d" && tee notes.md` stays silent.
6. As the owner, deleting the parent of a protected folder asks. Accept: `rm -r ~/.gemini`,
   `rm -rf "$HOME/.gemini"`, `rmdir ~/.gemini/config` ask; `rm -r ~/.cache/x` stays silent.
7. As the owner, a command whose working directory is protected asks once, naming the folder.
   Accept: `ls`, `make`, `git status` in `vault/` ask with
   `the working directory '<dir>' is inside a protected folder (<Rule.shown()>, project layer)`;
   a bare program word is never resolved against the working directory.
8. As the owner, a bare glob that reaches a link into a protected folder asks, and checking it
   never risks the hook's timeout. Accept: the link-glob rows ask; `cat *.md` in a folder without
   links stays silent; `cat /*/*/*/*/*/*/*/*/*/*.zzz; git push --force origin main` is denied in
   under one second; a scan past its entry cap or deadline asks.
9. Under agy, the same rows hold through `run_command` with and without `Cwd`. Accept: one
   `test_gate_agy` row per story 3–8.

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
   `"{decision} {tool} rule at .agent/cobot.rules:{line}"`, the tool only when it is one the gate
   judges (`FILE_TOOLS`, `Bash`, `mcp`), else `tool`. `Verdict.reason` and `could_match` use it.
2. **F-30.** `matches_file(rule, forms, fold)`: `never` and `ask` rows compare `casefold()`;
   `allow` never folds; the shell check and `path_may_match` fold always (never rows only).
   `program_folded`: lower the program word and each wrapper before it, re-stripping until the
   program is lower case; judged beside the segment, so `outranks` keeps the stricter.
   `relocates`, `protected_anchors` and the customization-root check compare without case;
   `expand_segment` also expands the folded segment, so `BASH -c` is read like `bash -c`.
3. **HOME.** `home_read(token)`: a leading `$HOME/`, `${HOME}/` (or the bare word) becomes `~`
   unless the script assigns `HOME` (`HOME_UNKNOWN_RE`, like `PWD_UNKNOWN_RE`); `file_forms`,
   `path_may_match`, the anchors check and `cd_target` read both forms (the literal and HOME's),
   which can only add asks. `cd_target` also reads a leading `~/` as HOME, beside the literal.
4. **F-31.** Entries carry each segment's `Dirs` (`(segment, origin, unit, dirs)`);
   `protected_file_touched` resolves every relative word against each directory in it (the
   payload cwd when it holds none). `Reached.paths` (redirect and runner targets) resolve
   against every directory the script visits (`anywhere`) and the payload cwd.
5. **Unknown cd.** When a segment's `Dirs` is unknown, or a relative `cd` led to it (`CDPATH`
   in the owner's profile may send it elsewhere), a relative word also asks when its last part
   matches, without case, the last part of a protected row that is not a folder row.
6. **Parent deletion.** `rm`, `rmdir`, `unlink`, `shred`, `trash` and `git rm` join the anchor
   check: a word that is a protected folder's anchor (a parent below HOME) asks.
7. **F-32.** `protected_cwd`: the payload cwd and every known directory in effect, inside or
   equal to a protected folder row's folder or matching a protected pattern; the ask names the
   directory and `Rule.shown()`. A program word without `/` is never resolved (PATH finds it).
8. **Link glob.** `glob_links(token, dirs)`: for a token whose holes are all globs, `expanduser`
   then walk the literal prefix to the first segment with a hole, `os.scandir` that directory
   only, and for each **symlink** entry whose name meets the segment's `path_glob` form
   (dotfiles included; `[…]` and POSIX classes read as one segment hole) put the link's
   `realpath` in place and check the rest lexically (`path_may_match`). Regular files are
   already covered lexically. At most `GLOB_ENTRIES_MAX = 4096` entries and
   `GLOB_DEADLINE = 0.25` s per command; past either, ask.
9. Docs (configuration Rules and known asks, architecture security model), CHANGELOG Fixed,
   FINDINGS F-29..F-32 closed, the residuals named.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | F-29: `Rule.shown`, reason and `could_match`; tests (story 1) incl. the memory hook test | a | — | — |
| T02 | F-30: case fold for restrictive path rows and the program word; tests (story 2) | a | auth | T01 |
| T03 | HOME read as `~` in words, globs, anchors and `cd` targets; tests (story 3) | a | auth | T02 |
| T04 | F-31: directories threaded to the protected check, redirect targets, unknown-cd last parts; tests (stories 4, 5) | a | auth | T03 |
| T05 | parent deletion and F-32 protected cwd; tests (stories 6, 7) | a | auth | T04 |
| T06 | link globs through `os.scandir` with an entry cap and a deadline; tests (story 8); agy rows (story 9) | a | auth | T05 |
| T07 | docs, CHANGELOG, FINDINGS closed | b | — | T06 |

All `auth` tasks are test first; one lane, since every task edits `cobot-rules`.

## Trade-offs

- Location over a quoted pattern (F-29): the owner opens one file to read the rule; no repository
  text can speak in a prompt.
- Always fold over probing the volume (F-30): stricter on Linux by design; `allow` never folds.
- Program-word fold over folding the whole command: arguments stay case-sensitive (`--FORCE` is
  not `--force` to git).
- An unknown `cd` target asks only for words whose last part names a protected file (story 5),
  not for every later word, which would ask on every `cd "$(git rev-parse …)"`.
- Keeping the protected-cwd ask (F-32) over silencing argument-less commands: an implicit-cwd
  write cannot be told from a read.
- Symlink entries of one directory, with a cap and a deadline (link glob), over expanding the
  glob: regular files are already judged lexically, and a glob with no match can take longer
  than the hook's timeout (challenger: 25 s and counting for `/*/*/*/*/*/*/*/*/*/*.zzz`).
- HOME only among plain variables: it is the one whose value the gate knows; other variables stay
  the residual decision 28 names.

Residuals named, not fixed: a link reached after a second hole segment (`*/d*/key.txt`); a link
created between the check and the run (inherent to any pre-run gate); a variable other than HOME
naming a protected path; `.agent/cobot.rules:<line>` names the main checkout's file from a
worktree and does not say which workspace under agy.

## Challenger verdict

Pass 1, 2026-11-15: **SOUND WITH CHANGES**, eleven points, each reproduced with `cobot-rules
check`; all folded.

- BLOCKER `$HOME/` stays literal, so `tee $HOME/.gemini/config/settings.json` and
  `rm -r $HOME/.gemini/config` beat every `~/` row (re-checked: none) → plan 3, story 3.
- BLOCKER redirect targets carry no directory, so `cd .claude && echo x > settings.json` stays
  silent → plan 4 (`Reached.paths` against every visited directory).
- BLOCKER a match cap does not bound work: a glob with no match can outlast the hook timeout →
  plan 8 (symlink entries of one directory, entry cap, deadline, ask past either).
- MAJOR Python glob syntax differs from bash (`[[:alpha:]]`, `[^x]`, dotglob, `~`) → plan 8 uses
  `path_glob`'s over-approximation, dotfiles included, `expanduser` first.
- MAJOR relative words with a `/` need the `cd` directory too → plan 4 (every relative word).
- MAJOR the fold misses a cased wrapper, `relocates` and the anchors, and `BASH -c` → plan 2.
- MAJOR an unknown `cd` (or `CDPATH` from the owner's profile) leaves bare names unchecked →
  plan 5.
- MINOR story 7's reason used a project pattern → `Rule.shown()`.
- MINOR rows that proved nothing (`cd ~/.gemini/config/` asks today; `make` is opaque) →
  replaced; `echo x > al*` added.
- MINOR the tool name is free text in a project row; the place is ambiguous in a worktree and
  under agy → plan 1 maps the tool; the ambiguity is a named residual.
- MINOR `rm -r ~/.gemini` (a protected folder's parent) is silent → plan 6, story 6.

## Bypass review

2026-11-15, independent reviewer on `f0d6117..3b7dc9a`, every row reproduced old against new:

- BLOCKER (a regression of this branch) the program-word skip also skipped a `for`, `select` or
  `case` head and `flock`'s file: `for f in settings.json; do cp /tmp/evil "$f"; done` in
  `~/.claude` went from ask to none → the skip is removed; `protected_cwd` names the folder.
- BLOCKER a glob naming a protected folder as a `cd` target, a move, a link or a deletion
  (`cd ~/.gemini/conf* && tee x`) → a whole-folder word with glob holes is judged by the names it
  expands to (a glob expands only to existing names), within the scan budget.
- MAJOR a bare `cd`; `~+`, `~-`, `~N`; deletion and relocation behind wrappers and assignments
  (`nice rm -r ~/.gemini`) and through globs on the parent (`rm -r ~/.gem*`); `CDPATH` set in the
  command; a link or `..` after the glob segment (`a*/l/config/x`) → each folded with a test.
- MINOR nocaseglob, globs after an unknown `cd`, the protected-cwd reason cut by agy before the
  rule → folded. Pre-existing gaps outside the claims → F-33 (find -delete, tar -C, …) and F-34
  (project text on stderr).

Residuals added: a `CDPATH` set only in the owner's shell profile; a hung network mount can block
the scan past its deadline (`resolved_prefix` shares it since F-28); over its budget the ask names
the token, not the budget.

## Converge

2026-11-15: stories 1–9 pass as tests (`-k "projectRow or caseFold or homeVariable or cdWalk or
cdOperand or cdUnknown or parentDeletion or protectedCwd or linkGlob or bypassFold"` in
`test_cobot_rules`, the residual rows in `test_gate_agy`); the bypass review's rows are tests;
a noise check against `main` changes only `cd docs && tee settings.json` and a deletion of a glob
naming the protected folder; latency 165 → 174 ms per check.
