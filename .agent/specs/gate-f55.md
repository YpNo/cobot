# Spec — a shell variable is a hole, and the files sourced between calls are protected (F-55)

size: medium · profile: library · owner: YpNo · date: 2026-11-23 · revision 5: split from
gate-f55-f58 by the owner ("Split, F-55 first"), two challenger passes folded before the split ·
base `main` `cc525b7` (PR 81 merged)

## Goal

Close F-55 (CRITICAL; journal 2026-11-22): the gate reads a plain shell variable as text, so a
path built from one reaches no decision, past the never rows on cobot's owner files. The
challenger found that F-55 also rests on files Claude Code sources between Bash calls. Through
those, an agent can set an "inherited" variable or plant code that runs in a later call, so this
spec protects them too (story 2). F-56, F-57 and F-58 are parked (last section). Measured with
`plugins/cobot/bin/cobot-rules check "<cmd>"` on `cc525b7`, owner and project layers empty:

| command | today | after |
|---|---|---|
| `cp x ~/.claude/$X` · `cp x "$HOME/.claude/${X}"` · `tee ~/$X` · `gh repo $V o/r` | none | ask |
| `X=cobot.rules; cp x ~/.claude/$X` · `D=~/.claude/cobot.rules; cp x $D` · `cp x ${X:+~/.claude/cobot.rules}` · `HOME=~/.claude; cp x ~/cobot.rules` | none | deny |
| `for D in ~/.claude/cobot.rules; do cp x $D; done` · `D=~/.claude/cobot.rules bash -c 'cp x $D'` · `bash -c 'cp x "$1"' _ ~/.claude/cobot.rules` · `sh -c 'cp x $0' ~/.claude/cobot.rules` | none | deny |
| `set -- ~/.claude/cobot.rul; cp x ${1}es` · `ls …; cp x ${_}es` · `A=(…); cp x "${A[0]}"` · `${!N}` · `declare -n` · `f(){ cp x $D; }; D=…; f` · `read D; cp x ~/.claude/$D` | none | ask |
| `D='e/a ~/.claude.json'; tee $D` | none | ask |
| `cp e/s.sh ~/.claude/session-env/<id>/snapshot-bash-1.sh` · `cp x "$CLAUDE_ENV_FILE"` · Write on a session-env file | none | deny |
| `tee -a ~/.bashrc` · `cp x ~/.zshenv` · `mv x ~/.profile` · `cp x ~/.curlrc` · `BASH_ENV=e/x bash -c true` · `ZDOTDIR=e zsh -c true` | none | ask |

Unchanged: `cp x ~/.claude/$(…)`, `HOME=/tmp true; cp x ~/.claude.json` and `bash script.sh` (ask);
`cp x $HOME/.claude/cobot.rules` (deny).

Silent and unchanged (the friction guard, each one a test row): `cp x $DEST` and `cat "$f"` with
`DEST`/`f` never assigned in the command, `D=out; cp a $D`, `for f in *.md; do wc -l "$f"; done`,
`echo $HOME`, `git log $REV` with `REV` unassigned, `cat ~/.bashrc`, `bash -c true`.

## Principles check

- **Proportionality:** medium, one topic: `_cobot_shell.py`, `cobot-rules` and the default layer.
- **Rules before autonomy:** every change adds an ask or a deny; nothing is silenced.
- **Proof, not promises:** each Goal row is a row in a new `tests/test_gate_f55.py`, and the
  differential corpus (`tests/test_gate_differential.py`) gets the variable rows bash can run. A
  bypass-aimed review follows each build task.
- Governance (`docs/01-decisions.md`): decision 18 (attribution) holds; 20 (one spec, one PR, a
  task per commit) holds, the reason for the split; 22 holds, no dependency; 28 (read-only agents)
  holds, the new asks apply to them too; 31 (stamp) holds; 33 (trust boundaries) holds, below; 34
  (session grants) holds: no grant kind covers a new ask or deny (a test row: an active grant on
  the target leaves the verdict unchanged); ADR-0003 holds (the rows protect files, nothing
  writes them); ADR-0007 (both runtimes) holds, story 3; the others are not relevant.
- Architecture: plain layering (`library`): the scanner says what a word holds, the gate judges.
- New dependencies: none (stdlib only).
- Experts: shell → `lang-shell` (read; expansion facts are bash's own, checked by the differential
  corpus); Python → `lang-python`. CONTEXT.md has no `domains:` bullet: an onboard refresh is
  proposed at hand-over.
- Delivery: one branch `security/gate-f55`, one PR; tasks below are the commits.

## Stories and acceptance

Every story's acceptance is `uv run --no-project --python 3.13 --with pytest==9.2.0 --with
pytest-cov==7.1.0 pytest tests/test_gate_f55.py -k <story>` plus its Goal rows through
`cobot-rules check`, each failing on `cc525b7` and passing after its task. Its negative rows are
the hostile commands of its Goal rows; its friction rows must stay silent.

1. **A variable is a hole, not text.** A plain `$NAME` or `${NAME}` is read like a substitution
   wherever the gate reads holes: `*` in a path word for `path_may_match`, and in a verb position
   the gate reads (`gh repo $V`), a hole that "decides what runs".
   - **Operator words** (`-`, `:-`, `+`, `:+`, `=`, `:=`) are alternatives, as brace alternatives
     are: the variable's value or the word, each judged (`${X:+~/.claude/cobot.rules}` denies).
     Every other operator is a full hole.
   - Every name falls in one of three classes, each a different hole:
     - **Put in** (the value is in the command text):
       - one plain `NAME=literal` (also after `export`, `readonly` or `declare`/`declare -x`) at
         the top level of the list, before its use; a `NAME=v cmd` prefix and the right side of
         `&&`/`||` do not count;
       - a `for NAME in w…` loop variable: each word, a glob judged as a glob, so
         `for f in *.md` stays silent;
       - inside a `sh|bash|zsh|dash|ksh -c` body: a name the outer command assigns (a prefix,
         `env NAME=`, `export`), and `$0`…`$9`, `$@` and `$*` from the argv after the body.
       - An unquoted use is split on the default IFS and each field judged, glob characters as
         globs. Any `IFS` assignment makes every unquoted put-in a full hole.
     - **Full hole** (in the text, but not computed): never spared by `reads_like_a_variable` or
       `folder_named`, and pathlike in `word_touches` (its `pathlike` gate, `cobot-rules` ~3599,
       drops a whole-word hole before any rule is read). Full holes are:
       - `${!…}`, a subscript (`${A[0]}`, `${A[@]}`) and `$_`;
       - a positional parameter, or `$@`/`$*`, once the command runs `set` or `shift`, outside a
         `-c` body with known argv;
       - a name with `printf -v`, `let`, `((…))`, `+=`, `${NAME:=…}`/`${NAME=…}`, an array or
         `declare -n|-a|-A`; a second assignment; or one in a branch, subshell or pipeline part;
       - any use inside a function body of a name the command assigns: the order is the order
         the function runs in, not its text.
     - **Run-time data** (the value comes from input when the command runs): read like `$(…)`
       today, spared as a whole word, a hole where glued to path text (`~/.claude/$D`). This
       covers `read`, `mapfile`, `getopts`, `select`, and the builtins' implicit names `REPLY`,
       `MAPFILE`, `OPTARG`, `BASH_REMATCH`, `OLDPWD` and `DIRSTACK` whenever their builtin
       appears. As with `cp x $(cat e/p)` today, the whole-word form is an accepted residual,
       raised as F-59 for the owner (spare or ask: a trade against friction on `while read f`
       loops).
   - `HOME`, `PWD` and `CLAUDE_CONFIG_DIR`: the gate's own values (`home_forms`, `expand_pwd`,
     `config_dir()`) are always judged. An in-command assignment *adds* its value and never
     replaces them, for `~` too: `HOME=~/.claude; cp x ~/cobot.rules` denies, and
     `HOME=/tmp true; cp x ~/.claude.json` still asks.
   - **Inherited:** a name never assigned in the command, and not one of the above, is read like
     `$(…)` today: spared where it stands for a whole unknown path (`cp x $DEST`). Story 2 is what
     makes that sound.
   - Special parameters other than `$_` (`$?`, `$$`, `$#`, `$!`, `$-`) stay text: none of them can
     hold a path the agent chose.
   - Accept: the variable rows of the Goal; the friction rows stay silent.
2. **The files Claude Code sources between calls are protected.**
   - **`never`** Edit, Write and shell access to `~/.claude/session-env/*`, and to its twin under
     a moved config dir: its snapshots are sourced into later Bash calls. Also `never` on the file
     `CLAUDE_ENV_FILE` names, read from the gate's environment when it is set.
   - **`ask`** on the shell start files: `~/.bashrc`, `~/.bash_aliases`, `~/.bash_profile`,
     `~/.bash_login`, `~/.bash_logout`, `~/.profile`, `~/.zshrc`, `~/.zshenv`, `~/.zprofile`,
     `~/.zlogin`, `~/.config/fish/config.fish` and `~/.config/fish/conf.d/*`, with the zsh files'
     twins under `ZDOTDIR` read from the gate's environment, as `config_dir()` reads
     `CLAUDE_CONFIG_DIR`; and on the download
     tools' config, `~/.curlrc` and `~/.wgetrc`, which steer a later plain `curl` or `wget`.
   - **`ask`** on a command that assigns `BASH_ENV`, `ENV` or `ZDOTDIR` (as a prefix, through
     `export`, `declare -x` or `env NAME=`) and runs a shell anywhere in it: that shell sources a
     file the gate never reads.
   - At build, before T02, a dated note records three checks, and the rows land either way, since
     a file the agent can plant code in needs no proof that it runs:
     - that the snapshot is sourced on each call, from a session's `session-env` folder and the
       `--debug` output of one Bash call;
     - that `CLAUDE_CONFIG_DIR`, `CLAUDE_ENV_FILE` and the session id reach the PreToolUse hook's
       environment;
     - that the env file sits under `session-env/`. If `CLAUDE_ENV_FILE` is absent from the hook's
       environment, its row is dropped rather than shipped as a dead check; `session-env/*` is the
       guard.
   - Residual until F-56 lands: start files planted by a copy into `~` (`cp e/.bashrc ~/`,
     `cp -t ~ e/.zshenv`, `tar -xf e.tar -C ~`, `unzip -d ~`, `rsync e/ ~/`).
   - Accept: the session-env, `CLAUDE_ENV_FILE`, start-file, rc-file and shell-variable rows,
     through both the shell and the file tools; `cat ~/.bashrc` stays silent.
3. **Both runtimes (ADR-0007).** Under agy (`run_command`), story 1 reaches the same judgement on
   `~/.gemini/config` paths. Story 2's rows are Claude Code's files: under agy, the start-file and
   rc-file rows apply, and the session-env rows have no twin. Accept: rows in
   `tests/test_gate_agy.py`, a deny there for every story 1 row that denies under Claude Code.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| an agent's shell text naming a protected file through a variable or parameter | variable holes, operator alternatives, full holes, put-in values split as bash splits them | 1 |
| a nested `sh -c` body given names or argv by the outer command | outer assignments and argv put into the inner scan | 1 |
| files sourced into later Bash calls: session snapshots, `CLAUDE_ENV_FILE`, start files, rc files | never and ask rows, through the shell and the file tools | 2 |
| a shell told to source a file by `BASH_ENV`, `ENV` or `ZDOTDIR` | an ask on the assignment with a shell | 2 |
| the same text under Antigravity | the shared judge | 3 |

## Clarify

Answered by the owner with the split, 2026-11-23, relayed by the orchestrator session:

- Q1 Where is a variable a hole? → **answer: a)**, the scanner emits a `variable` hole, and the
  gate's `$`-text sites move to it.
- Q2 Put in a single literal assignment, or treat every assigned name as a full hole? →
  **answer:** put in, split and globbed as bash does.
- Q4 Shell start files: ask or never? → **answer: a)**, ask; session snapshots and
  `CLAUDE_ENV_FILE` are never.
- Q3 (vim, emacs, gdb) belongs to F-57: **answer: b)**, awk and sed only when F-57 is specced. It is
  recorded under Parked.

## Plan

1. **T01, variable holes.**
   - Scanner: `_cobot_shell.dollar()` and `parameter()` emit a `variable` hole with the name for a
     plain parameter, and for the six operator words a hole whose alternatives are the value and
     the word.
   - The gate sites that read `$` as text move to the hole: `cobot-rules:726`, `:1784`, `:2143`,
     `:2715` (`PWD_NAMES`), `:3546`, `:3787` (`HOME_WORDS`) and `:4507`. `SECRET_EXPANSION_RE`
     (`:4401`) reads the raw command and stays.
   - A new `assignments(scan)` gives each name its literal fields, `FULL` or `RUNTIME`, and passes
     the outer names and argv into a `-c` body's scan. `path_glob` puts the fields in or widens the
     hole. `reads_like_a_variable` and `folder_named` spare inherited and run-time names only.
     `word_touches` treats a full hole as pathlike.
   - The differential corpus gets the variable rows.
2. **T02, sourced files:** the rows in `default.rules` (notes without `)`), the `CLAUDE_ENV_FILE`
   check beside `config_dir()`, and the shell-variable ask in `judge_bash`.
3. **T03, both runtimes and docs:**
   - the agy rows;
   - the CHANGELOG Security entry;
   - FINDINGS: F-55 closed, F-56 to F-58 pointed at this spec's Parked section;
   - the gate section of the design doc, where it says variables are text.

Each task is test first (its rows fail on `cc525b7`), then the code, then the focused tests, ruff
and the gate dry run. Each one gets a bypass-aimed review before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | variable holes, operator alternatives, assignments, the `$`-text sites, differential rows (`_cobot_shell.py`, `cobot-rules`, tests) | gate | auth | — |
| T02 | session-env and `CLAUDE_ENV_FILE` never rows, start-file and rc-file ask rows, the `BASH_ENV`/`ENV`/`ZDOTDIR` ask | gate | auth | T01 |
| T03 | agy rows, CHANGELOG, FINDINGS, design doc | gate | — | T01, T02 |

The tasks run in order, in one lane: T01 and T02 both edit `cobot-rules`.

## Trade-offs

- A variable hole in the scanner (Q1), over a second text form: more sites change in T01, but
  every later check sees one representation.
- Inherited variables are spared as `$(…)` is today, over asking on every unassigned variable.
  Story 2 closes the routes by which the agent could plant one.
- Start files ask rather than deny (Q4): the owner edits them through an agent at times.

## Parked, later specs

Decided one at a time after this spec merges; any of them may become an accepted risk. Each is
still an open FINDINGS row. The shapes below were measured on `cc525b7` (each one gets `none`), and
the folds are the revision 1 to 3 challenger answers, kept for the spec that takes each finding up.

- **F-56 (HIGH), copies into a folder and a moved config dir.**
  - Shapes: `cp e/.claude.json ~/`, `cp -t ~ e/.claude.json`, `mv`/`ln -s`/`install`/`rsync` into `~`,
    `scp h:/x/cobot.rules ~/.claude`, `docker cp`, `rclone copy`, `cd ~/.claude && tar -xf e.tar`,
    `curl --output-dir ~ -O|-o`, `wget -P ~` (also `-i`), `tar -xPf`, `cpio -i`, `curl -K`,
    `wget -e`. With `CLAUDE_CONFIG_DIR` outside HOME: `cp`, `tar -C`, `unzip -d` and `ln -sfn` into
    it.
  - Fold: `<target>/<basename>` landing words through `word_touches`; extraction into the tracked
    cwd; unplaceable landings ask; the moved dir is an anchor, its parents count only as move or
    remove sources.
  - Until it lands, `cp e/.bashrc ~/` slips past story 2's ask rows, as `cp e/.claude.json ~/`
    does today.
- **F-57 (HIGH), inline code.**
  - Shapes: `node -p|--print|--eval=|--import data:`, `python3 -ic|-Ic`, `python3.12 -c`,
    `echo … | python3`, `python3 -m timeit|code|pdb`, `python3 -m pip install`, `php -r`, `bun -e`,
    `deno eval`, `tsx -e`, `ts-node -e`, `awk 'BEGIN{system(…)}'`, `sed s/x/y/e`.
  - Fold: per-interpreter flag tables (unknown flags ask, V8 options known); `python -m M` read as
    `M`; awk and sed only (Q3 b).
  - vim, emacs and gdb become a new finding when F-57 is specced.
- **F-58 (MEDIUM), nested Claude Code.**
  - Shapes:
    - flags read from `claude --help` 2.1.311 on 2026-11-23: `--dangerously-skip-permissions`,
      `--permission-mode`, `--allowedTools`, `--setting-sources`, `--bare`, `--safe-mode`,
      `--plugin-url`, `--add-dir`, `--agents`, `--cloud`, `--environment`, `--remote-control`;
    - `CLAUDE_CODE_SIMPLE`/`CLAUDE_CODE_SAFE_MODE`/`CLAUDE_CONFIG_DIR`/`HOME` set or unset with
      `claude`;
    - launchers: `pnpx`, `deno x`, `dx`, `corepack`, `volta run`, `asdf exec`, `fnm exec`,
      `nvm exec`, `npm explore`, `uv tool run`;
    - copies of the binary: `cp`, `dd if=`, `cat`, a glob such as `clau?e`, a link;
    - `tee ~/.cl*.json`.
  - Fold: flag rows, the variable check, launchers opaque, file identity by `samefile` with glob
    words expanded, ask rows meeting a glob that names their file now.
  - Residual: a copy made without naming the file.

## Challenger verdict

- Before the split (gate-f55-f58), 2026-11-23:
  - revision 1 **UNSOUND** (2 BLOCKER, 6 MAJOR, 2 MINOR);
  - revision 2 **UNSOUND** (1 BLOCKER, 6 MAJOR, 2 MINOR).
  - Every shape was reproduced on `cc525b7`, and every point was folded. The F-55 points are now in
    stories 1 and 2; the rest are under Parked.
- Revision 4, the split: **UNSOUND** (1 BLOCKER, 4 MAJOR, 3 MINOR), 2026-11-23. Every shape was
  reproduced on `cc525b7`. Folded into revision 5:
  - BLOCKER: a nested `sh -c` turned outer assignments and argv into "inherited" names. They are
    now put into the inner scan (story 1).
  - MAJOR: `word_touches` dropped whole-word holes before any rule was read, so a full hole is now
    pathlike (story 1).
  - MAJOR: the `for` and `wc` friction rows contradicted each other. The `for` list is now put in.
  - MAJOR: implicit names such as `REPLY` were missing. They now form the run-time-data class, and
    the whole-word residual is raised as F-59.
  - MAJOR: `ZDOTDIR` twins (story 2).
  - MINOR: function-body order; `CLAUDE_ENV_FILE` dropped if absent; the F-56 residuals listed.
  - Moved for the owner: `read D; cp x $D` is no longer a Goal ask row. It is the F-59 residual,
    consistent with `cp x $(cat e/p)`.
- Revision 5 is not challenged again: the bypass-aimed review per build task comes next.

## Converge

pending: the owner decides F-59 (spare or ask) and gives the go for `/cobot:build gate-f55`.
