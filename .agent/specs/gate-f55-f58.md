# Spec — what the gate cannot read in a shell command (findings F-55 to F-58)

size: medium-large · profile: library · owner: YpNo · date: 2026-11-23 · revision 3 (two
challenger passes folded) · base `main` `cc525b7` (PR 81 merged)

## Goal

Close the gate findings PR 81's bypass reviews parked (journal 2026-11-22), F-55 first: shell
text the gate reads as plain when bash would not, so it gets no decision on a protected file or
hidden code. F-55 also rests on files Claude Code sources between calls (story 2). Measured with
`cobot-rules check "<cmd>"` on `cc525b7`, owner and project layers empty:

| # | command | today | after |
|---|---|---|---|
| F-55 | `cp x ~/.claude/$X` · `cp x "$HOME/.claude/${X}"` · `tee ~/$X` · `gh repo $V o/r` | none | ask |
| F-55 | `X=cobot.rules; cp x ~/.claude/$X` · `D=~/.claude/cobot.rules; cp x $D` · `cp x ${X:+~/.claude/cobot.rules}` · `HOME=~/.claude; cp x ~/cobot.rules` | none | deny |
| F-55 | `D='e/a ~/.claude.json'; tee $D` · `BASH_ENV=e/x bash -c true` · `ZDOTDIR=e zsh -c true` | none | ask |
| F-55 | `for D in …; do cp x $D; done` · `read D; cp x $D` · `set -- ~/.claude/cobot.rul; cp x ${1}es` · `ls …; cp x ${_}es` · `A=(…); cp x "${A[0]}"` · `${!N}` · `declare -n` | none | ask |
| F-55 | `cp e/s.sh ~/.claude/session-env/<id>/snapshot-bash-1.sh` · `cp x "$CLAUDE_ENV_FILE"` | none | deny |
| F-55 | `tee -a ~/.bashrc` · `cp x ~/.zshenv` · `mv x ~/.profile` · `cp x ~/.curlrc` | none | ask |
| F-56 | `cp e/.claude.json ~/` · `cp -t ~ e/.claude.json` · `mv`, `ln -s`, `install`, `rsync`, `scp`, `docker cp`, `rclone copy` into `~` | none | ask |
| F-56 | `scp h:/x/cobot.rules ~/.claude` · `cd ~/.claude && tar -xf e.tar` · `cd ~/.claude && unzip e.zip` | none | deny |
| F-56 | `curl --output-dir ~ -O https://h/.claude.json` · `curl --output-dir ~ -o .claude.json u` · `wget -P ~ https://h/.claude.json` · `wget -P ~ -i urls.txt` · `tar -xPf e.tar` · `curl -K e/cfg` · `wget -e dir_prefix=~ u` | none | ask |
| F-56 | with `CLAUDE_CONFIG_DIR=/tmp/cc`: `cp e/cobot.rules /tmp/cc/` · `tar -C /tmp/cc -xf e.tar` · `unzip -d /tmp/cc e.zip` · `ln -sfn e /tmp/cc` | none | deny |
| F-57 | `node -p …` · `node --eval=…` · `node --import data:…` · `python3 -ic …` · `python3.12 -c …` · `echo … \| python3` · `python3 -m timeit …` · `python3 -m pip install x` · `tsx -e …` · `php -r …` · `bun -e …` · `deno eval …` · `awk 'BEGIN{system("…")}'` · `sed 's/x/y/e' f` · `vim -c '!…'` | none | ask |
| F-58 | `claude` with `--dangerously-skip-permissions`, `--permission-mode`, `--allowedTools`, `--setting-sources`, `--bare` or `--safe-mode` · `CLAUDE_CODE_SIMPLE=1 claude -p …` · `export CLAUDE_CONFIG_DIR=/tmp/c; claude -p …` · `unset CLAUDE_CONFIG_DIR; claude -p …` · `HOME=/tmp/h claude -p …` | none | ask |
| F-58 | `pnpx x` · `deno x npm:x` · `dx npm:x` · `corepack pnpm x` · `volta run x` · `asdf exec x` · `fnm exec x` · `nvm exec x` · `npm explore x -- …` · `uv tool run x` | none | ask |
| F-58 | `cp /usr/bin/claude /tmp/c` · `cp ~/.local/bin/clau?e /tmp/c` · `dd if=/usr/bin/claude of=/tmp/c` · a link to Claude Code by another name · `tee ~/.cl*.json` (names the existing `~/.claude.json`) | none | ask |

Unchanged: `cp x ~/.claude/$(…)`, `python3 -c`, `perl -e`, `npx`, `npm exec`, `claude mcp add`,
`HOME=/tmp true; cp x ~/.claude.json` (ask); `cp x $HOME/.claude/cobot.rules`, copies into `~/.claude` (deny).

Silent and unchanged (the friction guard, each one a test row): `cp x $DEST` and `cat "$f"` with
`DEST`/`f` never assigned in the command, `D=out; cp a $D`, `for f in *.md; do wc -l "$f"; done`,
`cp a ~`, `cp report /tmp/` (also with the config dir moved to `/tmp/cc`), `python3 script.py`,
`python3 -m pytest`, `node app.js`, `node --max-old-space-size=4096 build.js`, `node --test`,
`deno test`, `bun test`, `awk '{print $1}' f`, `sed -n 1,10p f`, `claude -p hi`, `claude mcp list`.

## Principles check

- **Proportionality:** medium-large, one topic: `cobot-rules`, `_cobot_shell.py`, the default layer.
- **Rules before autonomy:** every change adds an ask or a deny; nothing is silenced.
- **Proof, not promises:** each Goal row is a row in a new `tests/test_gate_f55_f58.py`, and the
  differential corpus gets the rows bash can run. A bypass-aimed review follows each build task.
- Governance (`docs/01-decisions.md`): decision 18 (attribution) holds; 20 (one spec, one PR, a
  task per commit) holds; 22 (new dependencies) holds, none; 28 (read-only agents) holds, the new
  asks apply to them too; 31 (one commit per verified change, stamp) holds; 33 (trust boundaries)
  holds, below; 34 (session grants) holds: no grant kind covers a new ask (a test row per story:
  an active grant on the target leaves the verdict unchanged); ADR-0003 holds (the new rows protect
  files, nothing writes them); ADR-0007 (both runtimes) holds, story 10; the others are not relevant.
- Architecture: plain layering (`library`); the scanner says what a word holds, the gate judges.
- New dependencies: none (stdlib only).
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
     `((…))`, `+=`, `${NAME:=…}`/`${NAME=…}`, an array, `declare -n|-a|-A`, a second assignment, or
     one in a loop, branch, subshell or pipeline part.
   - **Put in:** a name with exactly one plain `NAME=literal` (also after `export`, `readonly` or
     `declare`/`declare -x`) at the top level of the list, before its use. A `NAME=v cmd` prefix and
     the right side of `&&`/`||` do not count. An unquoted use is split on the default IFS and each
     field judged, glob characters as globs (`D='e/a ~/.claude.json'; tee $D` asks). Any `IFS`
     assignment makes every unquoted put-in a full hole.
   - `HOME`, `PWD` and `CLAUDE_CONFIG_DIR`: the gate's own values (`home_forms`, `expand_pwd`,
     `config_dir()`) are always judged. An in-command assignment *adds* its value and never replaces
     them, for `~` too: `HOME=~/.claude; cp x ~/cobot.rules` denies, and
     `HOME=/tmp true; cp x ~/.claude.json` still asks.
   - **Inherited:** a name never assigned in the command, and not one of the above, is read like
     `$(…)` today: spared where it stands for a whole unknown path (`cp x $DEST`). Story 2 is what
     makes that sound.
   - Accept: every F-55 variable row; the friction rows stay silent.
2. **The files Claude Code sources between calls are protected (F-55, challenger).**
   - `never` Edit, Write and shell access to `~/.claude/session-env/*`, and to its twin under a
     moved config dir. Its snapshots are sourced into later Bash calls, so a planted line there
     would set an "inherited" variable or run code ungated.
   - `never` on the file `CLAUDE_ENV_FILE` names, read from the gate's environment when set.
   - `ask` on the shell start files: `~/.bashrc`, `~/.bash_aliases`, `~/.bash_profile`,
     `~/.bash_login`, `~/.profile`, `~/.zshrc`, `~/.zshenv`, `~/.zprofile`, `~/.zlogin`,
     `~/.config/fish/config.fish`, `~/.config/fish/conf.d/*` (decision per Q4). Also `ask` on the
     download tools' own config, `~/.curlrc` and `~/.wgetrc`, which steer a later plain `curl` or `wget`.
   - The build confirms that `CLAUDE_CONFIG_DIR`, `CLAUDE_ENV_FILE` and the session id reach the
     PreToolUse hook's environment, and that the env file sits under `session-env/`.
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
   - Landings the gate cannot place ask: `tar -P|--absolute-names`, `cpio -i` without
     `--no-absolute-filenames`, `unzip -:`, `curl -K|--config`, `wget -e|--execute`, and a command
     that assigns `WGETRC` or `CURL_HOME`.
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
     command assigns `NODE_OPTIONS`, `PERL5OPT`, `RUBYOPT`, `PYTHONSTARTUP`, or (with a shell)
     `BASH_ENV`, `ENV` or `ZDOTDIR`.
   - Not opaque: a lone info flag (`--version`). `python -m M args` is read as the command
     `M args`, so rows and opaque checks apply (`python3 -m pip install x` asks as `pip install`
     does; `-m pipx run` and `-m uv tool run` are launchers). The modules that run text are opaque:
     `timeit`, `code`, `pdb`, `trace`, `cProfile`, `profile`, `runpy`.
   - `tsx` and `ts-node` join the tables, with their `-e`/`-p` code flags.
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
     `export`, `declare -x`, `env NAME=`), or unsets one (`unset`, `export -n`, `env -u`), and runs
     `claude` anywhere asks. The help text names those
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
     input. A glob word is expanded under `GlobBudget` first (`cp ~/.local/bin/clau?e /tmp/c`). As
     one of those operands, so does a hole whose body runs `which`, `command -v`, `type -p`,
     `realpath` or `readlink` on `claude`. Friction rows: `which claude`, `claude --version`,
     `ls -la $(which claude)`.
   - Accept, with a stub `claude` on a test `PATH`: `<link> mcp add x`,
     `cp <stub> /tmp/c` and `dd if=<stub> of=/tmp/c` ask.
   - Residual, named here and in FINDINGS: a copy made by a command that never names the file,
     such as a download of the release, and later run by another name.
9. **Ask rows meet a glob that names their file now (F-58).** For an ask row with a literal
   pattern (`~/.claude.json`, `~/.claude.json.backup*`, `.mcp.json`), a glob word is expanded
   against the filesystem under `GlobBudget` (as `glob_links` does): a match asks, and so does a
   budget overrun. A glob that only *could* name the file stays silent, as today. Accept, with a
   fixture `~/.claude.json` under a temporary HOME: `tee ~/.cl*.json` asks, the same command
   without the file stays silent, and `cat .m*.json` asks with `.mcp.json` present. Friction:
   `cat **/*.json` stays silent and within budget, since `*` skips dot files as bash does.
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

For the owner at review; the stories carry the recommended defaults, as challenged.

- Q1 Where is a variable a hole? → a) the scanner emits a `variable` hole, and the gate's `$`-text
  sites move to it · b) the gate reads `$NAME` text as a hole, and the scanner is untouched →
  recommended: a), one representation, as the scanner's soundness target says → **answer:** pending
- Q2 Put in a single literal assignment (split and globbed as bash does), or treat every assigned
  name as a full hole (every `D=…; cp a $D` asks)? → recommended: put in, since agents write that
  shape often → **answer:** pending
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

Both passes on 2026-11-23. Every shape behind every objection was reproduced on `cc525b7`, and
every objection is folded.

- Revision 1: **UNSOUND** (2 BLOCKER, 6 MAJOR, 2 MINOR). Story 1: the hole was too narrow, and an
  in-command `HOME`. Story 2: planted "inherited" variables. Stories 3 and 4: copiers, extraction,
  parents as targets. Story 5: `-m timeit…`, V8 flags. Story 7: mode variables, `uv tool run`.
  Story 8: `dd`/`cat` copies.
- Revision 2: **UNSOUND** (1 BLOCKER, 6 MAJOR, 2 MINOR). Story 1: a put-in value is split and
  globbed (BLOCKER); `HOME`/`PWD` overrides add a value, never replace it; `${D:=w}`. Story 2:
  `BASH_ENV`/`ENV`/`ZDOTDIR`, `.bash_aliases`, fish `conf.d`, curl and wget rc files. Story 3:
  absolute members, `curl -K`, `wget -e`. Story 5: `-m M` read as `M`, `tsx`, `ts-node`. Story 7:
  unsets. Story 8: glob words, `which` friction. Story 9: dot-file friction.
- Revision 3 is not challenged again; the bypass-aimed review per build task is the next check.

## Converge

pending: the owner answers Q1 to Q4, then starts the build with `/cobot:build gate-f55-f58`.
