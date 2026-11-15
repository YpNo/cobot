# Spec — deletes, folder options and project text on stderr (findings F-33, F-34)

size: small-medium · profile: library · owner: YpNo · date: 2026-11-15 · revision 2 (challenger pass folded) · built on
`main` `8ceaf95` (gate-residuals merged as PR 57)

## Goal

Close the two findings the gate-residuals bypass review recorded, in both runtimes. Measured
2026-11-15 on `8ceaf95` (HOME with `~/.gemini/config/plugins`, an empty project layer):

| # | command | today | after |
|---|---|---|---|
| F-33 | `find ~/.gemini -delete` · `find ~ -name .gemini -exec rm -r {} +` · `find ~/.gemini -execdir rm {} ;` | none | ask |
| F-33 | `gio trash ~/.gemini` · `gio move ~/.gemini /tmp/g` | none | ask |
| F-33 | `rm -r ~` (HOME, an ancestor of every protected folder) | none | ask |
| F-33 | `tar -C ~/.gemini -xf e.tar config/x` · `tar --directory=$HOME/.gemini -xf e.tar` | none | ask |
| F-33 | `unzip -d ~/.gemini e.zip` · `git -C ~/.gemini apply p` · `patch -d ~/.gemini -p1 -i p` | none | ask |
| F-34 | a project row `ask Bash(x` (unreadable) or `allow Bash(y)` | stderr: `cobot gate: project:8: unreadable rule ignored: <the line>` | stderr: `cobot gate: project:8: unreadable rule ignored` |

Already asking and unchanged: a folder option or `find` start inside a protected folder
(`tar -xf e.tar -C ~/.gemini/config`, `find ~/.gemini/config -delete`). Silent and unchanged:
`find . -name '*.pyc' -delete`, `find src -type f -delete`, `tar -C src -xf a.tar`,
`git -C src status`, `unzip -d out a.zip`.

## Principles check

- Proportionality: small-medium, one module; holds. Rules before autonomy: adds asks only; holds.
- Proof not promises: each row a test, both runtimes; the bypass-aimed review after the build.
- Governance (`docs/01-decisions.md`): no decision changes; the reach is documented in
  `docs/configuration.md`. Architecture: plain layering inside `cobot-rules`. New dependencies:
  none. Delivery: one branch `security/gate-f33-f34`, one PR; tasks are the commits.

## Stories and acceptance

1. As the owner, a deletion that takes a protected folder with it asks: `rm`, `rmdir`, `unlink`,
   `shred`, `trash`, `git rm`, `gio trash|remove`, and `find` with `-delete`, `-exec`, `-execdir`,
   `-ok` or `-okdir` (its start paths are the deleted trees), when a word is a protected folder,
   its parent below HOME, HOME or `/`. Accept: the F-33 delete rows ask; `find . -name '*.pyc'
   -delete` and `rm -r build` stay silent.
2. As the owner, a folder an option names as the place a command writes is checked like a `cd`
   target, and the command's relative words resolve in it: `tar -C|--directory`, `unzip -d`,
   `git -C`, `patch -d|--directory`, separate, `=` and attached forms, `$HOME` and `~` read.
   Accept: the F-33 option rows ask; `tar -C src -xf a.tar`, `git -C src status`,
   `unzip -d out a.zip` stay silent.
3. As the owner, no project text reaches stderr. Accept: both project warnings end at
   `ignored`; default and owner warnings keep the line.
4. Under agy, the same rows hold through `run_command`. Accept: one `test_gate_agy` row per story.

## Clarify

None asked. `find … -exec <anything>` counts as a deletion of its start paths: the command it
runs is not followed, and from HOME or `/` it reaches every protected folder.

## Plan

1. `reaches_protected(form, anchors)`: the form is an anchor, or an ancestor of one (HOME and `/`
   included). `word_touches` uses it for deleting and moving words in place of anchor equality.
2. `destroys`: `gio trash|remove|rm`, and `find` with a deleting or running action; `relocates`:
   `gio move|mv|rename|copy|cp`. For `find`, only the start paths (the words before the first
   expression) carry the deletion.
3. `folder_options(argv)`: the values of the options above; each is checked as a whole-folder,
   deleting word (folder itself, inside, or an ancestor), and joins the segment's bases.
4. `parse_rule`: a project-layer warning names `project:<line>` and the reason, never the text.
5. Docs (configuration known asks), CHANGELOG Fixed, F-33 and F-34 closed.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | F-34: project warnings without text; tests (story 3) | a | — | — |
| T02 | deletions: ancestors, `find` actions, `gio`; tests (story 1) | a | auth | T01 |
| T03 | folder options as targets and bases; tests (story 2); agy rows (story 4) | a | auth | T02 |
| T04 | docs, CHANGELOG, findings closed | b | — | T03 |

## Trade-offs

- `find -exec` of any command counts, over following the command: the exec'd program is opaque
  to the start-path check, and a read-only `find ~ -exec cat {} +` asking is a rare prompt.
- An ancestor of a protected folder asks only for deleting, moving and folder-option words: a
  read (`ls ~`, `git -C ~ log` excepted below) stays silent. Known ask: `git -C ~ <anything>`
  and `tar -C ~ …`, since HOME is an ancestor of `~/.gemini`.

Residuals named: archive members not on the command line (`tar -xf e.tar` with
`.gemini/config/x` inside it, run from HOME); options of other tools that name a folder
(`7z -o`, `cpio -D`, `rsync --temp-dir`).

## Challenger verdict

Pass 1, 2026-11-15: **SOUND WITH CHANGES**, eight points, folded after T01–T04 (each row a test):

- BLOCKER start paths are not only the words before the first expression (paths after it are
  accepted) → every word of a deleting `find` outside what it runs counts.
- MAJOR what `-exec`/`-execdir`/`-ok`/`-okdir` run was not judged → each body is judged as a
  command of its own (rules and the protected check); `--` no longer hides the start paths; a
  deleting `find` with `-files0-from` asks.
- MAJOR a copy or move into a folder holding a protected folder's parent → asks when a source
  carries the next folder's name or copies a folder's contents (a trailing `/`, a hole); `cp a ~`
  stays silent.
- MAJOR folder options: abbreviated long options, short clusters for every tool, tar's old-style
  first word, `GIT_WORK_TREE`/`GIT_DIR`, `--one-top-level`.
- MAJOR an `=` value of any program (`of=`, `--target-directory=`, `--output=`) is checked as a
  path word.
- MINOR the `;` rows now use `\;`; the known asks are named; `explain`, `show` and `sync` print
  project rules on the owner's own stdout by design.

## Converge

pending
