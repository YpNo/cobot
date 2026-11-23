# Spec — what the gate cannot read in a shell command (findings F-55 to F-58)

size: medium-large · profile: library · owner: YpNo · date: 2026-11-23 · revision 2 (challenger
folded) · base `main` `cc525b7` (PR 81 merged)

## Goal

Close the four gate findings the bypass reviews of PR 81 parked (journal 2026-11-22, "F-52 to
F-54 closed"), F-55 first. Each one is a command shape the gate reads as plain text, so it reaches
no decision even when it lands on a protected file or runs hidden code. The challenger found that
F-55 also rests on files Claude Code sources between Bash calls, so this spec protects them too
(story 2). Measured 2026-11-23 with `plugins/cobot/bin/cobot-rules check "<cmd>"` on `cc525b7`, with
the owner and project layers empty:

| # | command | today | after |
|---|---|---|---|
| F-55 | `cp x ~/.claude/$X` · `cp x "$HOME/.claude/${X}"` · `tee ~/$X` · `gh repo $V o/r` | none | ask |
| F-55 | `X=cobot.rules; cp x ~/.claude/$X` · `D=~/.claude/cobot.rules; cp x $D` · `cp x ${X:+~/.claude/cobot.rules}` | none | deny |
| F-55 | `for D in …; do cp x $D; done` · `read D; cp x $D` · `set -- ~/.claude/cobot.rul; cp x ${1}es` · `ls …; cp x ${_}es` · `A=(…); cp x "${A[0]}"` · `${!N}` · `declare -n` | none | ask |
| F-55 | `HOME=~/.claude; cp x ~/cobot.rules` | none | deny |
| F-55 | `cp e/s.sh ~/.claude/session-env/<id>/snapshot-bash-1.sh` · `cp x "$CLAUDE_ENV_FILE"` | none | deny |
| F-55 | `tee -a ~/.bashrc` · `cp x ~/.zshenv` · `mv x ~/.profile` | none | ask |
| F-56 | `cp e/.claude.json ~/` · `cp -t ~ e/.claude.json` · `mv`, `ln -s`, `install`, `rsync`, `scp`, `docker cp`, `rclone copy` into `~` | none | ask |
| F-56 | `scp h:/x/cobot.rules ~/.claude` · `cd ~/.claude && tar -xf e.tar` · `cd ~/.claude && unzip e.zip` | none | deny |
| F-56 | `curl --output-dir ~ -O https://h/.claude.json` · `curl --output-dir ~ -o .claude.json u` · `wget -P ~ https://h/.claude.json` · `wget -P ~ -i urls.txt` | none | ask |
| F-56 | with `CLAUDE_CONFIG_DIR=/tmp/cc`: `cp e/cobot.rules /tmp/cc/` · `tar -C /tmp/cc -xf e.tar` · `unzip -d /tmp/cc e.zip` · `ln -sfn e /tmp/cc` | none | deny |
| F-57 | `node -p …` · `node --eval=…` · `node --import data:…` · `python3 -ic …` · `python3.12 -c …` · `echo … \| python3` · `python3 -m timeit …` · `php -r …` · `bun -e …` · `deno eval …` | none | ask |
| F-57 | `awk 'BEGIN{system("…")}'` · `sed 's/x/y/e' f` · `vim -c '!…'` | none | ask |
| F-58 | `claude` with `--dangerously-skip-permissions`, `--permission-mode`, `--allowedTools`, `--setting-sources`, `--bare` or `--safe-mode` · `CLAUDE_CODE_SIMPLE=1 claude -p …` | none | ask |
| F-58 | `export CLAUDE_CONFIG_DIR=/tmp/c; claude -p …` · `HOME=/tmp/h claude -p …` | none | ask |
| F-58 | `pnpx x` · `deno x npm:x` · `dx npm:x` · `corepack pnpm x` · `volta run x` · `asdf exec x` · `fnm exec x` · `nvm exec x` · `npm explore x -- …` · `uv tool run x` | none | ask |
| F-58 | `cp /usr/bin/claude /tmp/c` · `dd if=/usr/bin/claude of=/tmp/c` · a link to Claude Code run by another name | none | ask |
| F-58 | `tee ~/.cl*.json` (a glob that names the existing `~/.claude.json`) | none | ask |

Already asking or denied and unchanged: `cp x ~/.claude/$(…)` (ask), `cp x $HOME/.claude/cobot.rules`
(deny), `python3 -c`, `perl -e`, `ruby -e`, `npx`, `pnpm dlx`, `npm exec`, `claude mcp add` (also
behind a `CLAUDE_CONFIG_DIR=` prefix), `rtk git push --force` (deny), copies into `~/.claude`
(deny), `cp a ~/.gemini/` (ask).

Silent and unchanged (the friction guard, each one a test row): `cp x $DEST` and `cat "$f"` with
`DEST`/`f` never assigned in the command, `D=out; cp a $D`, `for f in *.md; do wc -l "$f"; done`,
`cp a ~`, `cp report /tmp/` (also with the config dir moved to `/tmp/cc`), `python3 script.py`,
`python3 -m pytest`, `node app.js`, `node --max-old-space-size=4096 build.js`, `node --test`,
`deno test`, `bun test`, `awk '{print $1}' f`, `sed -n 1,10p f`, `claude -p hi`, `claude mcp list`.

## Principles check

- **Proportionality:** medium-large: two modules (`cobot-rules`, `_cobot_shell.py`), the default
  layer and the tests. One topic: shell text the gate reads as literal when bash would not.
- **Rules before autonomy:** every change adds an ask or a deny, or makes an existing row
  reachable; nothing is silenced. The friction list above is a regression guard, not a relaxation.
- **Proof, not promises:** every Goal row is a test row in a new `tests/test_gate_f55_f58.py`; the
  differential corpus (`tests/test_gate_differential.py`) gets the F-55 and F-57 rows bash can
  run; a bypass-aimed review follows the challenger and every build task.
- Governance (`docs/01-decisions.md`): decision 18 (attribution) holds; 20 (one spec, one PR, a
  task per commit) holds; 22 (new dependencies) holds, none; 28 (read-only agents) holds, the new
  asks apply to them too; 31 (one commit per verified change, stamp) holds; 33 (trust boundaries)
  holds, below; 34 (session grants) holds: no grant kind covers a new ask (a test row per story:
  an active grant on the target leaves the verdict unchanged); ADR-0003 holds (the new rows protect
  files, nothing writes them); ADR-0007 (both runtimes) holds, story 10; the others are not relevant.
- Architecture: plain layering (profile `library`): the scanner says what a word holds, the gate
  judges. No new module.
- New dependencies: none (stdlib `os`, `re`, `shutil`, `fnmatch`, `glob`).
- Experts: shell → `lang-shell` (read; the expansion facts are bash's own, checked by the
  differential corpus); Python → `lang-python`. CONTEXT.md has no `domains:` bullet: an onboard
  refresh is proposed at hand-over.
- Delivery: one branch `security/gate-f55-f58`, one PR; tasks below are the commits.

## Stories and acceptance

Every story's acceptance is `uv run --no-project --python 3.13 --with pytest==9.2.0 --with
pytest-cov==7.1.0 pytest tests/test_gate_f55_f58.py -k <story>` plus its Goal rows through
`cobot-rules check`, each failing on `cc525b7` and passing after its task. Each story's negative
rows are the hostile commands of its Goal rows; its friction rows must stay silent.

1. **A variable is a hole, not text (F-55).** A plain `$NAME` or `${NAME}` is read like a
   substitution wherever the gate reads holes: `*` in a path word for `path_may_match`, and in a
   verb position the gate reads (`gh repo $V`), a hole that "decides what runs".
   - **Operator words** (`-`, `:-`, `+`, `:+`, `=`, `:=`) are alternatives, as brace alternatives
     are: the variable's value or the word, each judged (`${X:+~/.claude/cobot.rules}` denies). Every
     other operator is a full hole.
   - **Full holes** are never spared by `reads_like_a_variable` or `folder_named`. They are:
     `${!…}`, a subscript (`${A[0]}`, `${A[@]}`), `$_`, a positional parameter or `$@`/`$*` once the
     command runs `set`, `shift` or a function; and any name with an assignment that is not one
     plain literal assignment: `for NAME in`, `read`, `mapfile`, `printf -v`, `getopts`, `let`,
     `((…))`, `+=`, an array, `declare -n|-a|-A`, a second assignment, or one in a loop, branch or
     subshell.
   - **Put in:** a name with exactly one plain `NAME=literal` (also after `export`, `readonly` or
     `declare`/`declare -x`) at the top level of the list, before its use. An in-command assignment
     to `HOME`, `PWD` or `CLAUDE_CONFIG_DIR` overrides the gate's own value, for `~` too
     (`HOME=~/.claude; cp x ~/cobot.rules` denies). With none, the gate's values are put in: `HOME`
     (`home_forms`), `PWD` (`expand_pwd`), `CLAUDE_CONFIG_DIR` (`config_dir()`).
   - **Inherited:** a name never assigned in the command, and not one of the above, is read like
     `$(…)` today: spared where it stands for a whole unknown path (`cp x $DEST`). Story 2 is what
     makes that sound.
   - Accept: every F-55 variable row; the friction rows stay silent.
2. **The files Claude Code sources between calls are protected (F-55, challenger).**
   - `never` Edit, Write and shell access to `~/.claude/session-env/*`, and to its twin under a
     moved config dir. Its snapshots are sourced into later Bash calls, so a planted line there
     would set an "inherited" variable or run code ungated.
   - `never` on the file `CLAUDE_ENV_FILE` names, read from the gate's environment when set.
   - `ask` on the shell start files: `~/.bashrc`, `~/.bash_profile`, `~/.bash_login`, `~/.profile`,
     `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, `~/.zlogin`, `~/.config/fish/config.fish`
     (decision per Q4).
   - Before T02 the build checks, with a dated note, that the snapshot is sourced on each call: it
     reads a session's `session-env` folder and the `--debug` output of one Bash call. The rows
     land either way, since a file the agent can plant code in needs no proof that it runs.
   - Accept: the session-env, `CLAUDE_ENV_FILE` and start-file rows, through both the shell and
     the file tools.
3. **Landing paths of a copy, move, link or download (F-56).** Each source also lands at
   `<target>/<basename(source)>`, since the target may be a folder and the gate cannot know. That
   word goes through `word_touches` like any path word, so a literal file row (`~/.claude.json`)
   and a folder row meet it the same way, and a source with a hole lands at `<target>/*`.
   - The copiers: `cp`, `mv`, `ln` (also `-t`), `install` (also `-t` and `-D`), `rsync` (a trailing
     `/` copies contents: `<target>/*`), `gio copy|move`, `scp` (a remote source counts by its
     basename), `docker|podman|kubectl cp`, and `rclone copy|copyto|move|moveto|sync`.
   - Downloads: `curl --output-dir D` with `-O`, `--remote-name(-all)` or `-o NAME` lands at
     `D/<url basename>` or `D/NAME`, and at `D/*` with `-J`. `wget -P|--directory-prefix D` lands
     at `D/<url basename>`, and at `D/*` with `-i`, `--content-disposition`, `--trust-server-names`
     or `-r`.
   - Extraction with no `-C`/`-d` (`tar -x`, `bsdtar`, `unzip`, `cpio -i`, `7z x`) lands at
     `<cwd>/*`, the cwd as tracked, and an unknown cwd asks.
   - Accept: every F-56 copy, download and extraction row.
4. **A moved config dir keeps its folder protection (F-56).** `protected_anchors` adds the moved
   config dir (`CLAUDE_CONFIG_DIR` outside HOME) as an anchor. Its parents, except `/`, count only
   where a parent is *moved or removed* (`mv /tmp x`, `rm -r /tmp`), never as a copy *target*, so
   `cp report /tmp/` stays silent. HOME stays out of the anchors. Accept, with `CLAUDE_CONFIG_DIR`
   set in the test's environment to a temporary folder outside HOME: the four moved-dir rows deny,
   `mv <parent> x` and `rm -r <parent>` ask or deny, and the friction rows stay silent.
5. **An interpreter is opaque unless it names a script and no code flag (F-57).**
   `INLINE_CODE_FLAGS` gives way to one table per interpreter: its flags with a value, its flags
   without one, its code flags and its info flags.
   - The interpreters: pythons by basename (`python`, `python3`, `python3.N`, `pypy3`),
     `node`/`nodejs`, `deno`, `bun`, `ruby`, `perl`, `php`, `lua`/`luajit`, `Rscript`, `osascript`
     and `tclsh`.
   - Opaque when: a code flag appears, also inside a short cluster (`-ic`, `-pe`, `-lane`); an
     option is unknown (the script operand could be its value); no script operand follows the
     options (stdin, a REPL), or the operand is `-`; a preload names inline code
     (`node --import|--require|--loader data:…`, `perl -M` with anything past a module name); or the
     command assigns `NODE_OPTIONS`, `PERL5OPT`, `RUBYOPT` or `PYTHONSTARTUP`.
   - Not opaque: a lone info flag (`--version`), and `python -m <module>`, where the module counts
     as the script, except the modules that run text: `timeit`, `code`, `pdb`, `trace`, `cProfile`,
     `profile` and `runpy`.
   - node's known flags include the V8 options of `node --v8-options`, so
     `--max-old-space-size=4096` stays silent. A `--experimental-*` flag counts only when it is
     named in `node --help`.
   - `deno`: `run <file>`, `test`, `fmt`, `lint`, `check`, `info`, `doc` and `bench` are read.
     Opaque: `eval`, `repl`, `task`, a bare `deno`, and `run` with `-` or an
     `npm:`/`jsr:`/`http(s):`/`data:` specifier (`x` and `dx` are story 7).
   - `pwsh`, `powershell`, `nu`, `xonsh`, `elvish`, `tcsh`, `csh`, `mksh`, `ash` and `yash` join
     `SHELLS`, and `busybox <applet>` is read as the applet.
   - Accept: every F-57 interpreter row, `node -p "require('child_process').execSync('git push
     --force')"` among them.
6. **Text programs that run commands are opaque (F-57).**
   - `awk`, `gawk`, `mawk`, `nawk`, `busybox awk`: opaque when the program holds `system`, `|`,
     `getline` or `@load`, when it uses `-l`, `-E` or `-f`, or when the program is a hole.
   - `sed`/`gsed`: opaque when a script holds an `e` command or an `s///e` flag, or comes from `-f`.
   - `vim`, `nvim`, `vi`, `view`, `ex`, `evim`: opaque with `-c`, `--cmd`, `+cmd`, `-S`, `-s` or
     `-u`. `emacs`: with `--eval`, `-l`/`--load`, `--batch` or `-x`. `gdb`: with `-ex` or `-x` (Q3).
   - The checks are lexical and err toward ask: `/a|b/` in awk asks.
   - Accept: the F-57 text-program rows, `awk 'BEGIN{"id"|getline}'` and `sed '1e id' f` among them.
7. **Nested Claude Code and launchers (F-58).**
   - **Flag rows** in `default.rules` ask on a nested `claude` with a flag that lifts or drops the
     owner's governance. The list comes from `claude --help` of 2.1.311, read 2026-11-23, and is
     checked again at build against the CI pin (2.1.322): `--dangerously-skip-permissions`,
     `--allow-dangerously-skip-permissions`, `--permission-mode`, `--allowedTools`,
     `--allowed-tools`, `--tools`, `--setting-sources`, `--bare`, `--safe-mode`,
     `--permission-prompt-tool`, `--plugin-url`, `--add-dir`, `--agents`, `--cloud`, `--environment`,
     `--remote-control` and `--teleport`.
   - **Variable check:** a command that sets `CLAUDE_CONFIG_DIR`, `HOME`, `CLAUDE_CODE_SIMPLE` (what
     `--bare` sets) or `CLAUDE_CODE_SAFE_MODE` (what `--safe-mode` sets) in any form (a prefix,
     `export`, `declare -x`, `env NAME=`) and runs `claude` anywhere asks. The help text names those
     variables, and the build confirms that each one alone switches the mode.
   - **Launchers** are opaque: `pnpx`, `deno x`, `dx`, `corepack`, `volta run`, `asdf exec`,
     `fnm exec`, `nvm exec|run`, `npm explore`, `npm|pnpm|yarn|bun create`, `npm init <pkg>`,
     `pipx run`, `uv tool run`, `proto run` and `pkgx`.
   - Accept: the F-58 rows, `claude --bare -p x` and `export CLAUDE_CONFIG_DIR=/tmp/c; claude mcp
     list` among them.
8. **Claude Code under another name (F-58).**
   - A program word whose file is the Claude Code executable is read as `claude` before the rows
     match. The test is `os.path.samefile` against `shutil.which("claude")` and its `realpath`,
     which catches a symlink and a hard link.
   - Any other word naming that file asks: a copy, link or install source, `dd if=` or a `cat`
     input. So does a hole whose body runs `which`, `command -v`, `type -p`, `realpath` or
     `readlink` on `claude`.
   - Accept, with a stub `claude` on a test `PATH`: `<link> mcp add x`,
     `cp <stub> /tmp/c` and `dd if=<stub> of=/tmp/c` ask.
   - Residual, named here and in FINDINGS: a copy made by a command that never names the file,
     such as a download of the release, and later run by another name.
9. **Ask rows meet a glob that names their file now (F-58).** For an ask row with a literal
   pattern (`~/.claude.json`, `~/.claude.json.backup*`, `.mcp.json`), a glob word is expanded
   against the filesystem under `GlobBudget` (as `glob_links` does): a match asks, and so does a
   budget overrun. A glob that only *could* name the file stays silent, as today. Accept, with a
   fixture `~/.claude.json` under a temporary HOME: `tee ~/.cl*.json` asks, the same command
   without the file stays silent, and `cat .m*.json` asks with `.mcp.json` present.
10. **Both runtimes (ADR-0007).** Under agy (`run_command`), stories 1 to 6 and 9 reach the same
    judgement on `~/.gemini/config` paths. Accept: rows in `tests/test_gate_agy.py`, which give a
    deny there for every row that denies under Claude Code.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| an agent's shell text naming a protected file through a variable or parameter | variable holes, operator alternatives, full holes, put-in assignments | 1 |
| files sourced into later Bash calls (session snapshots, `CLAUDE_ENV_FILE`, shell start files) | never and ask rows, shell and file tools | 2 |
| a copy, move, link, download or extraction that lands in a protected folder or on a protected file | landing paths through `word_touches` | 3 |
| the moved config dir outside HOME | an anchor, parents as sources only | 4 |
| code run by an interpreter or a text program from command-line text or stdin | interpreter tables and lexical checks: opaque, so ask | 5, 6 |
| a nested Claude Code session with lifted permissions, another config, or a renamed binary | flag rows, the variable check, file identity | 7, 8 |
| a glob naming Claude Code's state file | real expansion under a budget | 9 |
| the same text under Antigravity | the shared judge | 10 |

## Clarify

Asked of the owner at review: the defaults below are written into the stories, and the challenger
attacked them as written.

- Q1 Where is a variable a hole? → a) in the scanner: `_cobot_shell` emits a `variable` hole
  for `$NAME`/`${NAME}`, so every sentinel-aware check sees it, and the gate sites that read `$` as
  text move to the hole · b) in the gate only: path words and the verb positions read `$NAME` text
  as a hole, and the scanner is untouched → recommended: a), because the scanner's soundness target
  already names a hole "where some text in its place would change which program runs", and one
  representation means no later check forgets the text form → **answer:** pending
- Q2 Put in a single literal assignment, or treat every assigned name as a full hole? → a) put in
  (`D=~/.claude/cobot.rules; cp x $D` denies, `D=out; cp a $D` stays silent) · b) full hole (every
  `D=…; cp a $D` asks) → recommended: a), because agents write that shape often and the rule is
  narrow → **answer:** pending
- Q3 Story 6 reaches `vim`, `emacs`, `gdb`: in scope, or a later finding? → a) in scope, the same
  class as F-57 · b) awk and sed only → recommended: a), a few table rows → **answer:** pending
- Q4 Shell start files (`~/.bashrc` and the rest, story 2): ask or never? → a) ask: the owner edits
  them through an agent at times · b) never, like `settings.json` → recommended: a); the session
  snapshots and `CLAUDE_ENV_FILE` are never either way → **answer:** pending

## Plan

1. **T01, variable holes (F-55).** Per Q1 a): `_cobot_shell.dollar()` and `parameter()` emit a
   `variable` hole with the name for a plain parameter, and for the six operator words a hole whose
   alternatives are the value and the word. The gate sites that read `$` as text move to the hole:
   `cobot-rules:726`, `:1784`, `:2143`, `:2715` (`PWD_NAMES`), `:3546`, `:3787` (`HOME_WORDS`) and
   `:4507`. `SECRET_EXPANSION_RE` (`:4401`) reads the raw command and stays. A new
   `assignments(scan)` gives each name a literal value or `FULL`, overriding `HOME`, `PWD` and
   `CLAUDE_CONFIG_DIR`. `path_glob` puts the value in or widens the hole. `reads_like_a_variable` and
   `folder_named` spare an inherited name only. The differential corpus gets the F-55 rows.
2. **T02 to T10** follow the stories in order. Where each change sits is in the task table. T05's
   flag sets come from each tool's `--help`, `--v8-options` or man page, read at build and dated in
   a comment, and `own_tool_run` keeps `python3 -I <plugin>/bin/<tool>` silent (a test row).

Each task is test first (its rows fail on `cc525b7`), then the code, then the focused tests, ruff
and the gate dry run. Each one gets a bypass-aimed review before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | variable holes, operator alternatives, assignments, the text sites, differential rows | gate | auth | — |
| T02 | session-env, `CLAUDE_ENV_FILE`, start files: `default.rules` rows, the `CLAUDE_ENV_FILE` check, after story 2's snapshot check | gate | auth | T01 |
| T03 | landing paths: `landing_words(segment)` beside `merge_parts`, checked in `protected_file_touched` | gate | auth | T01 |
| T04 | moved config dir anchor from `config_dir()` in `protected_anchors`, parents as sources only | gate | auth | T03 |
| T05 | `INTERPRETER_FLAGS` replaces `INLINE_CODE_FLAGS`/`INTERPRETERS`, `interpreter_opaque` in `opaque_as_read`, more shells, busybox | gate | auth | T01 |
| T06 | `text_program_opaque`: awk, sed, vim, emacs, gdb | gate | auth | T05 |
| T07 | nested claude rows (notes without `)`), the mode-variable check in `judge_bash`, launchers in `OPAQUE`/`OPAQUE_SUBCOMMANDS` | gate | auth | T01 |
| T08 | file identity in `program_folded`/`strip_wrappers`, and any word naming the binary | gate | auth | T07 |
| T09 | ask-row globs in `word_touches`, under the command's `GlobBudget` | gate | auth | T03 |
| T10 | agy rows, CHANGELOG Security, FINDINGS F-55 to F-58 closed (story 8's residual a new row), design doc | gate | — | T01–T09 |

One lane: every task edits `cobot-rules`, so the tasks run in this order.

## Trade-offs

- A variable hole in the scanner (Q1 a), over a second text form: more sites change in T01, but
  every later check sees one representation.
- Inherited variables are spared, as `$(…)` is today (`cp x $DEST` stays silent), over asking on
  every unassigned variable. Story 2 closes the routes by which the agent could plant one.
- An allowlist of interpreter flags (unknown asks) over a denylist of code flags: interpreters
  gain flags each release, and a denylist fails open.
- Lexical awk and sed checks that err toward ask, over a parser for each language.
- File identity by `samefile` plus any word naming the file, over hashing a 294 MB binary.
- `* mcp add*` rows on any program stay parked (every glob would could-match); story 8 instead.

## Challenger verdict

2026-11-23, revision 1: **UNSOUND** (2 BLOCKER, 6 MAJOR, 2 MINOR). Every objection was folded into
revision 2. I reproduced the shapes behind them on `cc525b7`: each got `none`.

- BLOCKERs: the variable hole was too narrow (operator words, positionals, `$_`, arrays, namerefs,
  `${!…}`), folded into story 1; the agent can set "inherited" variables through the session
  snapshots, `CLAUDE_ENV_FILE` and the start files, folded into story 2 and Q4.
- MAJORs: moved-dir parents as copy targets (story 4); `scp`, `docker cp`, `rclone`, extraction
  into the tracked cwd, `wget -i` (story 3); `CLAUDE_CODE_SIMPLE`, `CLAUDE_CODE_SAFE_MODE`,
  `--environment` (story 7); an in-command `HOME` (story 1); `python -m timeit|code|pdb|…`
  (story 5); `dd if=` and `cat` copies of the binary (story 8).
- MINORs: `uv tool run` (story 7); V8 flags would ask (story 5).

Not re-run on revision 2. A second pass is optional before the build; the bypass-aimed review per
task is not.

## Converge

pending: the owner answers Q1 to Q4, then starts the build with `/cobot:build gate-f55-f58`.
