# Spec — editors and debuggers, newlines, loader variables and dotglob (F-63, F-64, F-65)

size: medium · profile: library · owner: YpNo · date: 2026-11-24 · revision 3 (challenger
folded, the 2.1.331 option diff folded) · base `main` `3e83cc6` (PRs 82–85 merged)

## Goal

Close F-63 (MEDIUM), F-64 (LOW, **raised to HIGH** below), F-65 (MEDIUM) and the dotglob residual
of spec gate-f58 (T05 build note). This is the last gate spec before a release. Each gap lets a
command run code, or reach a protected file, without a decision:

- **F-64, now HIGH.** `shell_items` rewrites newlines before it reads quotes or escapes:
  - `\<nl>` becomes a blank, and a quoted newline becomes ` ; `.
  - An escaped backslash before a newline (`echo a\\<nl>rm -rf /`) is read as a line
    continuation, so the second line is hidden. Bash runs it as two commands. It gets none, so
    `never` rows are bypassed today (the challenger found it; re-measured).
  - An awk comment swallows the rest of the program: `awk '#x<nl>BEGIN{system("x")}'` gets none.
- **F-63.** Editors and debuggers run commands the gate does not read. Debuggers, profilers and
  some launchers also start a program the gate never sees: `valgrind rm -rf /` and
  `fakeroot rm -rf /` get none, where `rm -rf /` is refused.
- **F-65.** A loader variable set in the command (`LD_PRELOAD`, `DYLD_*`, `JAVA_TOOL_OPTIONS`,
  `OPENSSL_CONF`) makes any program load code, with no decision.
- **dotglob.** `shopt -s dotglob` set in the command makes `*` reach `.mcp.json` and
  `~/.claude.json` with no ask.
- **Found while measuring: command variables, `git -c` and `--exec-path`.** This spec opens the
  class as **F-70** (Q5):
  - `git -c core.fsmonitor=x status` runs `x` with no decision, where
    `git config core.fsmonitor x` asks;
  - `git --exec-path=/tmp fetch` runs `/tmp/git-remote-https`;
  - `GIT_SSH_COMMAND=x git fetch` and `LESSOPEN='|x %s' less f` are the same class.

Measured with `plugins/cobot/bin/cobot-rules check "<cmd>"` on `3e83cc6`, with the owner and
project layers empty. The challenger re-ran every row. The dotglob rows ran in a folder holding
`.mcp.json`. `<nl>` is a newline, and `\\` is two backslashes as bash receives them.

| # | command | today | after |
|---|---|---|---|
| 1 | `echo a\\<nl>rm -rf /` · `bash -c 'echo a\\<nl>rm -rf /'` · `echo a\\<nl>git push --force origin main` | none | deny (the second line's `never` row) |
| 2 | `awk '#x<nl>BEGIN{system("x")}'` · `gawk '#x<nl>@load "x"'` | none | ask, as without the comment |
| 3 | `vim -c '!x' f` · `vim +'!x' f` · `vim --cmd x f` · `vim -S s.vim f` · `vim -u x.vim f` · `vi -c x f` · `ex -c x f` · `view -c x f` · `vimdiff -c x a b` · `rvim -c x f` · `vim -Z -c x f` · `busybox vi -c x f` · `printf ':!x\n' \| vim f` | none | ask (Q1) |
| 4 | `vim.basic -c x f` · `vim.tiny -c x f` · `/usr/bin/vim.basic -c x f` · `editor -c x f` · `sensible-editor f` · `vipe` | none | ask (Q1; names installed on this host) |
| 5 | `nvim -c x f` · `nvim --cmd x` · `nvim --headless -c x` · `emacs --batch --eval '(x)'` · `emacs -l x.el` · `emacs --script x.el` · `emacs -x x.el` · `emacsclient --eval '(x)'` · `ed f` · `kak -e x` | none | ask (Q1) |
| 6 | `gdb -ex 'shell x'` · `gdb -batch -ex run ./a` · `gdb -x cmds ./a` · `gdb ./a` · `gdb -p 1` · `lldb -o 'platform shell x'` · `lldb-18 -o x` · `lldb ./a` · `rust-gdb ./a` · `cgdb ./a` · `dlv exec ./a` · `jdb x` | none | ask (Q2) |
| 7 | `valgrind rm -rf /` · `ltrace rm -rf /` · `perf stat rm -rf /` · `perf_6.12 stat rm -rf /` · `perf record -- rm -rf /` · `gdb --args rm -rf /` · `lldb -- rm -rf /` · `rr record rm -rf /` · `catchsegv rm -rf /` · `heaptrack rm -rf /` · `uftrace rm -rf /` · `gdbserver :1 rm -rf /` · `sotruss rm -rf /` · `xtrace rm -rf /` · `memusage rm -rf /` | none | ask (Q2) |
| 8 | `perf report --objdump=/tmp/x` · `perf annotate --objdump=/tmp/x` · `perf --exec-path=/tmp report` | none | ask (the read-only subcommands run a program through these options) |
| 9 | `fakeroot rm -rf /` · `eatmydata rm -rf /` · `nsenter -t 1 rm -rf /` · `setpriv rm -rf /` · `prlimit rm -rf /` · `xvfb-run rm -rf /` · `ssh-agent rm -rf /` | none | ask (Q6) |
| 10 | `LD_PRELOAD=/tmp/x.so ls` · `LD_AUDIT=/tmp/x.so ls` · `DYLD_INSERT_LIBRARIES=/tmp/x.dylib ls` · `export LD_PRELOAD=/tmp/x.so; ls` · `env LD_PRELOAD=/tmp/x.so ls` · `GCONV_PATH=/tmp ls` · `OPENSSL_CONF=/tmp/x.cnf curl https://x` · `PERL5DB='system(1)' perl -d x.pl` | none | ask |
| 11 | `JAVA_TOOL_OPTIONS=-javaagent:x.jar java -version` · `_JAVA_OPTIONS=x java` · `JDK_JAVA_OPTIONS=x java` | none | ask |
| 12 | `LD_LIBRARY_PATH=/tmp ls` · `DYLD_LIBRARY_PATH=/tmp ls` · `PYTHONPATH=/tmp python3 x.py` · `PYTHONUSERBASE=/tmp/u python3 x.py` · `PERL5LIB=/tmp perl x.pl` · `RUBYLIB=/tmp ruby x.rb` · `NODE_PATH=/tmp node x.js` · `cd /tmp && PYTHONPATH=. python3 x.py` | none | ask (a search path outside the project; Q3) |
| 13 | `shopt -s dotglob; cat *` · `shopt -s dotglob; tee *.json` · `shopt -s nullglob dotglob; cp x *.json` · `shopt -s dotglob; cat ~/*` · `shopt -s dot''glob; cat *` · `GLOBIGNORE=x; cat *` · `export GLOBIGNORE=x; cat *` · `bash -O dotglob -c 'cat *'` · `bash -c 'shopt -s dotglob; cat *'` · `o=dotglob; shopt -s $o; cat *` | none | ask, as `cat .mc?.json` asks (Q4) |
| 14 | `git -c core.fsmonitor=x status` · `git -c core.sshCommand=x fetch` · `git --config-env=core.fsmonitor=V status` · `git --config-env core.fsmonitor=V status` · `git --exec-path=/tmp status` · `git --exec-path /tmp status` | none | ask, as `git config <key> x` asks (Q5) |
| 15 | `GIT_SSH_COMMAND=x git fetch` · `GIT_EXEC_PATH=/tmp git status` · `GIT_CONFIG_GLOBAL=/tmp/x git status` · `LESSOPEN='\|x %s' less f` · `EDITOR=x crontab -e` | none | ask (Q5) |
| 16 | `claude --model --managed-settings-in-initialize -p x` · `claude --model --initialize-fields -p x` (2.1.331 reads both from the raw argv, so a value slot does not hide them) | none | ask (story 7) |
| 17 | `claude -p x --managed-settings-in-initialize` · `--trusted-folder /tmp/x` · `--organization-gateway` · `--gateway-json` · `--web` · `--routine r` · `--discard` | ask (an option the gate does not know) | ask, with the class's own reason (Q7) |

Unchanged, and each a test row. These ask or deny today and keep doing so:
- `strace ls` and `strace -o out ls` ask (opaque); `strace -o ~/.claude/settings.json ls` asks;
- `vim -c 'w! ~/.claude/settings.json' f` asks (a protected file);
- `ex -s f <<'EOF'<nl>%s/a/b/<nl>wq<nl>EOF` and `ed -s f <<< '!x'` are refused (a script that
  writes files);
- `bash -c 'echo a<nl>rm -rf /'`, `r\<nl>m -rf /` and `# it's<nl>rm -rf /` are refused;
- `cat {.,}*.json` and `cat .mc?.json` ask;
- `shopt -s dotglob && rm -f *` asks;
- `git -c alias.st='!x' st` asks;
- `git config core.pager cat` asks;
- `PATH=/tmp:$PATH ls` asks (its test asserts the ask, not today's reason);
- `GIT_EDITOR=x git commit` asks;
- `sed 's/a/b/\<nl>e' f` asks;
- `grep -rn 'NODE_OPTIONS=' .` asks (a known cost of F-58 T03, by name).

Silent and unchanged, the friction guard, each a test row:
- `vim --version`, `emacs --version`, `gdb --version`, `vim --help`;
- `perf list`, `perf version`, `perf report`, `perf annotate`;
- `less f`, `man ls`, `more f`, `nano f`;
- `ls *`, `cat *.json`, `shopt -s nullglob; cat *.json`, and `shopt -s dotglob; ls *.md` (no
  protected file matches), each in a folder holding `.mcp.json`;
- `PYTHONPATH=. pytest`, `PYTHONPATH=src python3 -m pytest`, `PYTHONPATH=$PWD/src pytest`,
  `PYTHONPATH=src:$PYTHONPATH pytest`, and `LD_LIBRARY_PATH=./build ./a.out` (Q3);
- `rg 'LD_LIBRARY_PATH=' .`, `grep -n 'PYTHONPATH=' Makefile`, `grep -rn 'GIT_EDITOR=' .`
  (value-read names come from assignment words, not the text);
- `GIT_EDITOR=true git rebase --continue`, `GIT_PAGER=cat git log`, `PAGER=cat man ls`,
  `git --no-pager log`, `git -c color.ui=always log` (Q5);
- `echo "a<nl>b"`, `sed -n 'p<nl>w out' f`, `cat <<'EOF'<nl>rm -rf /<nl>EOF` (a heredoc body is
  data);
- `bash -c "echo a\<nl>rm -rf /"` (bash joins it into `echo arm -rf /`).

Three rows ask today and keep asking: `git commit -m 'a<nl>b'`, `gh pr create --body 'a<nl>b'`
and `python3 -c 'x=1<nl>y'`.

## Principles check

- **Proportionality:** medium, one topic. The work sits in `plugins/cobot/bin/cobot-rules`:
  `OPAQUE`, `shell_items`, `START_VARIABLES`, `glob_names_asked_file` and the git reader. It also
  touches `_cobot_nested.py`, `plugins/cobot/rules/default.rules`,
  `tests/test_gate_f63_f65.py` and the agy rows.
- **Rules before autonomy:** every change adds an ask or a deny, and no row is lifted. Story 3
  makes the splitter pass what bash passes, which can only remove a miss or a false ask.
- **Proof, not promises:** each Goal row is a test row failing on `3e83cc6`. Friction rows stay
  silent, and a bypass-aimed review follows each build task.
- **Governance** (`docs/01-decisions.md`): these decisions hold:
  - 18, attribution;
  - 20, one spec, one PR, a task per commit;
  - 22, no new dependency;
  - 28, read-only agents (the asks apply to them too);
  - 31, the stamp;
  - 33, trust boundaries (below);
  - 34, session grants (no grant kind covers these asks).

  ADR-0007 (both runtimes) holds too: the judge is shared, so agy's `run_command` gets the same
  decisions.
- **Architecture:** plain layering (`library`). Opaque names join the existing table, as a family
  pattern for versioned names. Variables join `START_VARIABLES` and `START_PREFIXES`. `git -c`
  reuses `git_exec_key`, and `--config-env` reuses `git_alias_set`'s parse.
- **New dependencies:** none (stdlib only).
- **Delivery:** branch `security/gate-f63-f65`, one PR; the tasks below are the commits.

## Facts read (2026-11-24)

| tool | source | what it says |
|---|---|---|
| Vim 9.1 | `vim --help` (local) | `-c <command>`, `+<command>`, `--cmd <command>` and `-S <session>` run Ex commands; `-u <vimrc>` sources a file; `-s <scriptin>` reads Normal-mode keys from a file (`-s` alone is silent mode in Ex mode); `-w`/`-W <scriptout>`, `--startuptime <file>`, `--log <file>` and `-i <viminfo>` write files; `-Z` (rvim) is restricted mode, which blocks shell commands but still writes files |
| bash 5.2.37 | run in a scratch folder | `*` skips `.mcp.json`; `{.,}*.json`, `.*` and `@(.m*)` (extglob) reach it; `[.]mcp.json` and `?mcp.json` do not; `GLOBIGNORE=x` (not empty) turns dotglob on; `BASHOPTS` is read-only inside bash; `echo a\\<nl>echo SECOND` prints `a\` then `SECOND` (the challenger) |
| git, man, less | run in a scratch repository, no terminal (the challenger) | `GIT_PAGER='echo X' git log \| cat`, `git -p log` and `MANPAGER='echo X' man ls` never run the pager; `LESSOPEN='\|echo X %s' less f \| cat` runs it; `V=v git --config-env core.abc=V config core.abc` prints `v` (the space form is accepted) |
| this host | `command -v` | `vim.basic`, `vim.tiny`, `editor` and `sensible-editor` are installed; gdb, lldb, emacs, nvim, perf and valgrind are not |
| cobot | `cobot-rules` | `strace` is in `OPAQUE`, so every run asks, and an opaque launcher keeps none of its inner deny (`strace rm -rf /` asks), while `chroot / rm -rf /` keeps it (a wrapper parser). `git_exec_key` holds the keys whose value git runs, and `git_alias_set` parses both `--config-env` forms. `START_VARIABLES` is read by name from the command's text, and `START_PREFIXES` by prefix. The scanner strips comments and here-documents before `shell_items`. |
| Claude Code 2.1.331 | the ci-claude-pin session's diff of the binary's commander specs against 2.1.311 (commit `f5cb6ff`, relayed) | 18 options added. With no value: `--agents-view-if-allowed`, `--discard`, `--gateway-json`, `--hold-repository-while-parked`, `--managed-settings-in-initialize`, `--organization-gateway`, `--web`. With a required value: `--event`, `--initialize-fields`, `--lead-verify-key`, `--list`, `--max-cost`, `--metadata`, `--output`, `--path`, `--review-md`, `--session-began-as-copy`, `--trusted-folder`. One removed: `--registry <url>`. No value shape changed, and no letter was added or removed. `--managed-settings-in-initialize` and `--initialize-fields` are read from the raw argv before commander. `--trusted-folder <absolute>` reads "The current directory, which the host says a person trusted". `--session-began-as-copy` and `--lead-verify-key` are forwarded to a session. `--max-cost` may only be a prefix of `--max-cost-usd`. `--routine` is in both binaries and is forwarded, but is missing from the gate's table (an older gap) |
| cobot | `cobot-rules` `glob_names_asked_file` | returns early on a last segment that does not start with `.` ("without dotglob, bash reaches a dotfile only through a leading literal dot") |

Not read yet. Each is a build checkpoint before its task, not an assumption:

1. **The readers' line assumptions.** After story 3, each reader that sees a quoted word gets
   real newlines. The readers are:
   - the sed and awk readers, and the inline readers (`_cobot_inline`);
   - the setter scan and the `never` rows' fnmatch (the challenger checked that fnmatch crosses
     newlines and that `LINE` meets operator tokens only).

   The checkpoint is a grep for `\n`, `[^\n]` and ` ; ` in each, with a test row per reader.
   Before T01.
2. **The option lists** of gdb, lldb, emacs, nvim, valgrind, perf, rr, ltrace, dlv, fakeroot,
   nsenter, setpriv, prlimit and xvfb-run, from each tool's manual. None is installed here. They
   give the launch forms, perf's program options and, under Q2's or Q6's alternative, the option
   tables. Before T02.
3. **zsh's names for dotglob**: `setopt globdots`, `GLOB_DOTS`, `-o globdots`, from zsh's manual
   (zsh is not installed here). `zsh -c` already asks as opaque, and `*(D)` as unparseable. Before
   T05.
4. **Whether Antigravity's `run_command` gives the command a terminal** (Q5's sub-question). Read
   agy's docs, or run a probe in the owner's terminal: `test -t 1 && echo tty`. Before T04.
5. **The meaning of the 2.1.331 options whose class Q7 leaves unread**: `--event`, `--list`,
   `--metadata`, `--output`, `--path`, `--review-md`, `--lead-verify-key`,
   `--session-began-as-copy`, `--agents-view-if-allowed`, `--hold-repository-while-parked`. Read
   them from the 2.1.331 binary's option descriptions and Claude Code's CLI reference. An option
   that stays unclear stays out of the table, so it keeps asking (F-58 Q1). Before T06. The diff
   itself is read (Facts read).

## Stories and acceptance

Acceptance for each story: `uv run --no-project --python 3.13 --with pytest==9.2.0 pytest -q
tests/test_gate_f63_f65.py -k <story>`. Its rows fail on `3e83cc6` and pass after its task, and
its friction rows stay silent.

1. **Editors that run commands ask (rows 3–5; Q1).**
   - These join `OPAQUE`:
     - the vi family: `vim`, `vi`, `ex`, `view`, `vimdiff`, `rvim`, `rview`, `gvim`, `evim`,
       `vimx`, `nvim`, `nvi`;
     - the emacs family: `emacs`, `emacsclient`, `emacs-nox`;
     - `ed`, `red` and `kak`;
     - Debian's alternatives `editor`, `sensible-editor` and `vipe`, which may be any editor.
   - A versioned or suffixed name counts as its family: `vim.basic`, `vim.tiny`, `emacs-29.4`,
     and any path whose basename matches. This is read by a family pattern
     (`^(?:vim?|nvim|gvim|emacs|gdb|lldb|perf)(?:[._-][\w.]+)?$`), not by listing names.
   - `busybox vi` and `busybox ed` are read as `vi` and `ed` (busybox is already a wrapper).
   - `--version`, `--help` or `-h` stays silent only as the sole argument.
   - `nano`, `micro`, `joe`, `mg` and `hx` are interactive only, and none runs a command from
     argv (checkpoint 2 confirms). They stay silent.
2. **Debuggers and profilers ask (rows 6–8; Q2).**
   - These join `OPAQUE`, as `strace` is, with the family pattern of story 1:
     - debuggers: `gdb`, `gdb-multiarch`, `rust-gdb`, `cgdb`, `gdbserver`, `lldb`, `rust-lldb`,
       `lldb-server`, `dlv`, `jdb`;
     - tracers and profilers: `ltrace`, `valgrind`, `rr`, `catchsegv`, `heaptrack`, `uftrace`,
       `bpftrace`;
     - glibc's own tracers: `sotruss`, `xtrace`, `memusage`.
   - Each runs a program it is given, or commands from its options or a file.
   - `perf` is opaque except for a short list:
     - `list`, `version`, `--version` and `help` stay silent;
     - so do `report`, `annotate` and `diff`, but only with no global option before them and no
       option naming `objdump`, `addr2line` or `exec-path` (row 8).
   - The sole-argument rule of story 1 applies.
3. **The splitter reads newlines as bash does (rows 1, 2; F-64).** In `shell_items`, newlines
   are read in the same pass that tracks quotes and escapes, not by a `replace` before it:
   - an unquoted newline is a separator;
   - a newline inside single or double quotes stays in its word, as bash passes it;
   - a backslash-newline is a line continuation only after an odd run of backslashes:
     - outside quotes, the continuation is removed, joining the two words (today it becomes a
       blank);
     - in double quotes, it is removed;
     - in single quotes, both characters stay;
   - `\\<nl>` is an escaped backslash, then a separator.

   A `bash -c` string goes through the same splitter. Each reader in checkpoint 1 then reads the
   real program. The sed reader's ` ; ` line-end guess can stay, since it costs only a false ask.
4. **Loader and runtime-option variables ask (rows 10–12; Q3).**
   - These join `START_VARIABLES` and ask by name:
     - `LD_PRELOAD`, `LD_AUDIT`, `DYLD_INSERT_LIBRARIES`, `GCONV_PATH`;
     - `OPENSSL_CONF`, which loads an engine into any TLS program;
     - `JAVA_TOOL_OPTIONS`, `_JAVA_OPTIONS`, `JDK_JAVA_OPTIONS`, which every JVM reads;
     - `DOTNET_STARTUP_HOOKS`;
     - `LUA_INIT` (code, or `@file`), `PERL5DB` (code);
     - `ERL_AFLAGS`, `ERL_FLAGS`, `ERL_ZFLAGS` (`-eval`).
   - `LD_`, `DYLD_`, `CORECLR_PROFILER` and `COR_PROFILER` join `START_PREFIXES`, minus the
     search paths below. The text scan then never sees a search path's name.
   - The search paths follow Q3. They are `LD_LIBRARY_PATH`, `DYLD_LIBRARY_PATH`,
     `DYLD_FALLBACK_LIBRARY_PATH`, `DYLD_FRAMEWORK_PATH`, `DYLD_FALLBACK_FRAMEWORK_PATH`,
     `PYTHONPATH`, `PYTHONUSERBASE`, `PERL5LIB`, `PERLLIB`, `RUBYLIB`, `NODE_PATH`, `LUA_PATH`,
     `LUA_CPATH`, `CLASSPATH`, `GEM_PATH` and `GEM_HOME`.
     - They are read from the assignment words of the parsed segments (`NAME=v cmd`,
       `export NAME=v`, `env NAME=v`), never from the text. So `rg 'LD_LIBRARY_PATH=' .` stays
       silent.
     - Under Q3's default, one asks when an entry of its value (split on `:`) lies outside the
       project, from the folder the walk tracks for the segment. An empty entry or `.` is that
       folder.
     - `$PWD`, `${PWD}` and `$(pwd)` are read as the tracked folder. The variable's own name
       (`$PYTHONPATH`) is the inherited value, the F-59 class. Any other expansion, `~` or a
       glob asks.
   - The setter forms of F-57 T05 and F-58 T03 apply to the by-name variables: `export`, `env`,
     `declare`, a computed name and a quoted separator.
5. **A command that turns dotglob on reaches dotfiles (row 13; Q4).**
   - The scan reads the unquoted words of each segment, the strings of `bash -c` included, so
     `dot''glob` is `dotglob`. The command turns dotglob on when a segment is one of these:
     - `shopt` with `-s` naming `dotglob`, or naming any word that is not a plain known option
       (an expansion);
     - a shell with `-O` and the same reading;
     - zsh's `setopt` with `globdots` or `glob_dots`, in any case, or `-o globdots`
       (checkpoint 3).
   - `GLOBIGNORE` set non-empty also turns it on. That is read with `sets_start_variable`, so
     `read`, `printf -v`, a nameref and `+=` count.
   - Then `glob_names_asked_file` skips its leading-dot return for every glob in the command. A
     glob that matches a protected file on disk asks, as F-58's Q6 made `.mc?.json` ask.
   - The `never` rows already read globs dotglob-safe, so they do not change.
6. **Command variables, `git -c` and `--exec-path` (rows 14, 15; Q5; F-70).**
   - `git -c <key>=<value>` and both forms of `git --config-env` are read with `git_exec_key`,
     so an exec key asks, as `git config <key> <value>` does. `--config-env` is parsed as
     `git_alias_set` parses it.
   - `git --exec-path=<dir>` and `--exec-path <dir>` ask. Bare `git --exec-path`, which only
     prints the path, stays silent.
   - These ask by name:
     - `GIT_SSH_COMMAND`, `GIT_SSH`, `GIT_PROXY_COMMAND`, `GIT_EXEC_PATH`, `GIT_ASKPASS`,
       `SSH_ASKPASS`, `GIT_EXTERNAL_DIFF`, `GIT_TEMPLATE_DIR`;
     - `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG`, `GIT_CONFIG_PARAMETERS`, and
       `GIT_CONFIG_COUNT` with its `GIT_CONFIG_KEY_<n>` and `GIT_CONFIG_VALUE_<n>`;
     - `LESSOPEN` and `LESSCLOSE`, which run without a terminal.
   - `GIT_EDITOR`, `GIT_SEQUENCE_EDITOR`, `EDITOR` and `VISUAL` ask unless the value is safe:
     empty, `true`, `:` or `cat`. They are read from assignment words, as story 4's search paths
     are.
   - Pagers depend on Q5's sub-question (checkpoint 4):
     - with no terminal under either runtime (the default), they are left out, since a pager
       never runs there: `GIT_PAGER`, `PAGER`, `MANPAGER`, `MANOPT`, `man -P`, and the
       `core.pager` and `pager.*` keys under `git -c`;
     - if agy's `run_command` has a terminal, they join the editor list, with `less` and `more`
       carrying options only added to the safe values.
7. **The nested-`claude` table follows the CI pin, 2.1.331 (rows 16, 17; Q7).**
   - `--managed-settings-in-initialize` and `--initialize-fields` join `RAW_SCANNED` and
     `FOREIGN`. A value slot does not hide them (row 16), as F-58 T02 found for `--bare`.
   - Under Q7's default, these get a class:
     - `--managed-settings-in-initialize`, `--initialize-fields` and `--trusted-folder` are
       foreign (settings, or a folder trusted without the person);
     - `--organization-gateway` and `--gateway-json` route the traffic, the F-66 class, with its
       reason;
     - `--web` and `--routine` move the session elsewhere (F-58 Q3);
     - `--discard` asks, the F-69 class (it may drop work).
   - `--max-cost` is known and silent, with a required value, as `--max-cost-usd` is.
   - The other ten stay out of the table until checkpoint 5 reads them, so they keep asking as
     unknown (F-58 Q1).
   - `--registry` stays in the table with its 2.1.311 shape, for older installs.
8. **The other launchers (row 9; Q6).**
   - Under the default, `fakeroot`, `eatmydata`, `nsenter`, `setpriv`, `prlimit`, `xvfb-run` and
     `ssh-agent` join `OPAQUE`.
   - Under Q6's alternative, they and Q2's launchers become `PREFIX_COMMANDS`, so the inner
     command is judged.
9. **Both runtimes.** agy rows: one per story, `deny` for a deny and `force_ask` for an ask.
   Also `docs/configuration.md` and its Antigravity part, and the CHANGELOG Security entry. In
   FINDINGS, F-63, F-64, F-65 and F-70 are closed or set to accepted.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| a command line hidden behind a newline the splitter misreads | the splitter | 3 |
| an editor running commands or writing files from argv or stdin | opaque names, the family pattern | 1 |
| a debugger, profiler or launcher running a program or commands | opaque names, `perf`'s subcommands | 2, 8 |
| a library or runtime option loaded into any program | start variables and prefixes | 4 |
| a module search path outside the project | the value reading (Q3) | 4 |
| a glob reaching a protected dotfile under dotglob | the dotglob scan | 5 |
| a command git or an editor runs from a variable, `-c` or `--exec-path` | `git_exec_key`, start variables | 6 |
| a nested Claude Code option added since 2.1.311, or read from the raw argv | the option tables, `RAW_SCANNED` | 7 |
| the same under Antigravity | the shared judge | 9 |

## Clarify

These are for the owner. The stories carry the recommended defaults. Each question can also be
answered with **accept the risk**: the shape stays as it is today, it is recorded as an
accepted residual in this spec and in FINDINGS, and its rows are dropped. Story 3 (F-64, now
HIGH) has no question: it is a misreading of bash, and its fix is to read as bash does.

- **Q1: editors.** Should every run of a vi-family editor, emacs or ed ask, or only the options
  that run commands?
  - Recommended: **every run asks**, except `--version` or `--help` as the sole argument.
    - Vim alone has seven command or file options.
    - Other forms reach commands too: Normal-mode keys on a stdin that is not a terminal,
      `-s scriptin`, a modeline, the project's `.exrc` or `.nvim.lua`, and emacs's
      `.dir-locals.el`.
    - An agent edits through Edit and Write, so an editor in Bash is rare. The friction is
      `nvim --headless` test runs (the lang-fallback skill names them), which ask as
      `python3 -c` does.
  - Other options: an option table per editor (a plain `vim f` stays silent); accept the risk.
- **Q2: debuggers and profilers.** Should every run ask, as `strace` does?
  - Recommended: **every run asks**. The exceptions are `--version` or `--help` as the sole
    argument and perf's read-only subcommands of story 2.
    - Each runs a program it is given (`gdb --args`, `valgrind <cmd>`), or commands from `-ex`,
      `-o`, `-x`, `-s`, or a project's `.gdbinit` or `.lldbinit`.
    - The cost is an ask on each run of a debugging session. An inner deny becomes an ask, as
      with `strace rm -rf /`.
  - Other options:
    - read the launch forms as prefix commands, so the inner command is judged and an inner
      deny stays a deny, as `chroot` does, and ask only on the command options (an option table
      per tool, checkpoint 2);
    - accept the risk.
- **Q3: search paths.** Should `LD_LIBRARY_PATH`, `PYTHONPATH`, `NODE_PATH` and story 4's other
  search paths ask always, or only when an entry lies outside the project?
  - Recommended: **outside the project, or computed**, as story 4 reads it.
    - Each names where a program finds its libraries or modules, ahead of the system's, so a
      planted `json.py` in `/tmp` shadows the standard one.
    - Inside the project, the agent could already run the code directly (`python3 x.py` is
      silent), so the variable adds nothing. That is F-57 story 4's line: a script outside the
      project asks, one inside does not.
    - It keeps `PYTHONPATH=. pytest`, `PYTHONPATH=$PWD/src pytest` and
      `LD_LIBRARY_PATH=./build ./a.out` silent.
  - Other options: ask always, by name as `NODE_OPTIONS` does; accept the risk.
- **Q4: dotglob.** In a command that turns dotglob on, should a glob ask when it matches a
  protected file on disk, or always?
  - Recommended: **when it matches on disk, for any verb**, as F-58's Q6 decided for globs with
    a leading dot. In a repository holding `.mcp.json`, `shopt -s dotglob; ls *` asks, and
    `shopt -s dotglob; ls *.md` stays silent.
  - Accepting the risk is defensible here. A whole-folder read or copy already reaches
    `.mcp.json` with no ask (`grep -r token .`, `cp -r /tmp/x/. .`, `rsync -a /tmp/x/ ./`,
    `tar xzf /tmp/x.tgz`), so story 5 guards one narrow path. Those forms are a residual
    whatever the answer.
  - Other option: every glob in such a command asks.
- **Q5: command variables, `git -c` and `--exec-path` (F-70, found while measuring).** Should
  story 6 be in this spec?
  - Recommended: **yes, as written**.
    - `git -c core.fsmonitor=x status` runs any command with no decision, while the
      `git config` row beside it already asks.
    - The safe values keep `GIT_EDITOR=true git rebase --continue` silent.
  - **Sub-question: pagers.** Under Claude Code's Bash, no pager runs (measured with no
    terminal). Should the pager variables be left out?
    - Recommended: **left out, unless checkpoint 4 finds a terminal under agy.**
    - Other option: include them in both runtimes.
  - Other options:
    - `git -c`, `--exec-path` and the git variables only, with the editor variables and
      `LESSOPEN` left in F-70;
    - all of story 6 left in F-70 for a later spec;
    - accept the risk.
- **Q6: other launchers that hide a deny today.** `fakeroot`, `eatmydata`, `nsenter`, `setpriv`,
  `prlimit`, `xvfb-run` and `ssh-agent` run the command after them, and `<launcher> rm -rf /`
  gets none (row 9). Should they be in this spec?
  - Recommended: **yes, as opaque names**, the same reading as Q2.
  - Other options: as prefix commands keeping the inner deny (Q2's alternative); a finding for
    later; accept the risk.
- **Q7: the 2.1.331 options.** All 18 ask today as unknown, except in a value slot (row 16).
  Should the clear ones get a class (story 7)?
  - Recommended: **as story 7 reads them.**
    - `--managed-settings-in-initialize`, `--initialize-fields` and `--trusted-folder` ask as
      `--managed-settings` does. Each brings in settings, or trust the person did not give.
    - `--organization-gateway` and `--gateway-json` ask as `ANTHROPIC_BASE_URL` does.
    - `--web` and `--routine` ask as `--cloud` does.
    - `--discard` asks.
    - `--max-cost` is silent.
    - The ten unread options keep the unknown-option ask until checkpoint 5.
  - The asks are the same as today's, so the gain is row 16 and a reason that says what the
    option does.
  - Other options:
    - only the raw-scanned pair (row 16), with the rest left unknown;
    - make `--trusted-folder` silent if checkpoint 5 shows only the host sets it;
    - accept the risk on row 16.

## Plan

1. **T01, the splitter (story 3).** Run checkpoint 1 first. Then read newlines in
   `shell_items`'s quote pass, with a test row per reader. It goes first: it is the HIGH, and the
   later rows quote multi-line text.
2. **T02, editors, debuggers and launchers (stories 1, 2, 8).** Run checkpoint 2 first. Then the
   `OPAQUE` names, the family pattern, `perf`'s subcommands and options, and the
   sole-argument exemption.
3. **T03, loader variables (story 4).** The names and prefixes, then the search-path reading
   from assignment words under Q3.
4. **T04, command variables, `git -c` and `--exec-path` (story 6).** Run checkpoint 4 first. Then
   the git reader, the variables and the safe values.
5. **T05, dotglob (story 5).** Run checkpoint 3 first. Then the dotglob scan on unquoted words,
   and the flag through to `glob_names_asked_file`.
6. **T06, the nested-`claude` diff (story 7).** Run checkpoint 5 first. Then the raw-scanned
   pair, the class of each option under Q7, `--max-cost` and `--routine`. The CI pin's commit
   (`f5cb6ff`, branch `chore/ci-claude-code-2.1.331`) lands separately: this task edits the
   gate's table, not CI.
7. **T07, both runtimes and docs (story 9).** The agy rows, `docs/configuration.md`, the CHANGELOG
   Security entry and the FINDINGS rows.

Each task is test first, then the code, the focused tests, ruff and the gate dry run, with a
bypass-aimed review folded before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | newlines in `shell_items`, as bash reads them | gate | auth | — |
| T02 | editors, debuggers, profilers and launchers opaque | gate | auth | — |
| T03 | loader variables, search paths | gate | auth | — |
| T04 | command variables, `git -c`, `--exec-path` | gate | auth | — |
| T05 | dotglob | gate | auth | — |
| T06 | nested-`claude` option diff | gate | auth | checkpoint 5 |
| T07 | agy rows, docs, CHANGELOG, FINDINGS | gate | — | T01–T06 |

## Trade-offs

- **Opaque names, not option tables**, for editors, debuggers and launchers (Q1, Q2, Q6). The
  list and the family pattern stay correct as the tools add options. The cost is an ask on a
  plain `vim f` or `gdb ./a`, and an inner deny that becomes an ask.
- **Search paths read by value from assignment words (Q3)**, unlike the name-only start
  variables read from the text. This keeps `PYTHONPATH=.` and a `grep` for the name silent, at
  the cost of one more reader.
- **dotglob read once for the whole command**, not tracked segment by segment. A `shopt -s
  dotglob` anywhere in the command turns the shortcut off for every glob in it, even the ones
  before the `shopt`. That is a false ask at worst.

## Residuals (kept out of this spec, and why)

- **An inherited variable**: `LD_PRELOAD` or `GLOBIGNORE` already in the gate's environment, or
  `$PYTHONPATH` in a value. This is the F-59 and F-68 class.
- **Build-tool variables:** `GOFLAGS=-toolexec=x`, `RUSTC_WRAPPER`, `CC`,
  `CARGO_TARGET_<triple>_RUNNER`, `MAVEN_OPTS`, `GRADLE_OPTS` and `JAVA_HOME` before
  `./gradlew`. The builds they change already run repository code (`build.rs`, `go generate`, a
  Gradle script), which the gate does not judge either.
- **Another repository's config:** `git -C /tmp/evil status`, `git --git-dir=…`, `GIT_DIR=…`
  and `cd /tmp/evil && git status` run that repository's `core.fsmonitor`. Writing that config
  first is a script write, which is refused, so story 6 leaves it out.
- **Whole-folder reads and copies reaching `.mcp.json`** (`grep -r`, `cp -r x/. .`, `rsync`,
  `tar x`): see Q4.
- **A pager's own commands** (`less +'!x' f`). When its output is not a terminal, `less` copies
  its input as `cat` does.
- **The inner deny of an opaque launcher**: see Trade-offs, and Q2's and Q6's alternative.
- **The name scan's false asks on data** (`grep 'LD_PRELOAD=' .`, `echo 'BASH_ENV=x'`). This is
  F-58 T03's known cost, now with more names. The value-read names of stories 4 and 6 avoid it.
- **Interpreters outside `_cobot_inline`'s families** (`lua -e`, `Rscript -e`, `julia -e`,
  `osascript -e`): F-57's residual, unchanged.

## Challenger verdict

2026-11-24, revision 1: **SOUND WITH CHANGES** (1 BLOCKER, 6 MAJOR, 5 MINOR). Every Goal,
Unchanged and friction row was re-run on `3e83cc6` and held. Folded into revision 2:

- **BLOCKER 1, `echo a\\<nl>rm -rf /` gets none today.** `shell_items` replaces `\<nl>` before
  reading escapes, so an escaped backslash hides the next line from the `never` rows. Re-measured,
  with `git push --force` too. F-64 is raised to HIGH. Row 1 is added, and story 3 now reads
  newlines in the quote pass, with the odd-run rule.
- **MAJOR 2:** `git --config-env core.fsmonitor=V` (the space form) and `git --exec-path=<dir>`
  are now in row 14 and story 6.
- **MAJOR 3:** `perf report --objdump=/tmp/x` runs a program, so perf's exemption is narrowed
  (row 8).
- **MAJOR 4:** `vim.basic`, `vim.tiny`, `editor`, `sensible-editor`, `lldb-18`, `perf_6.12`,
  `sotruss`, `xtrace` and `memusage` are now in rows 4, 6 and 7, read by a family pattern.
- **MAJOR 5:** Q3's value reading now reads `$PWD` and `$(pwd)` as the tracked folder and a
  self-reference as inherited, and resolves from the tracked folder. Friction rows
  `PYTHONPATH=$PWD/src pytest` and `PYTHONPATH=src:$PYTHONPATH pytest` are added, with the ask
  row `cd /tmp && PYTHONPATH=. python3 x.py`. Q3's reasoning is reworded.
- **MAJOR 6:** with no terminal, no pager runs under Claude Code (the challenger measured it). The
  pagers are now Q5's sub-question, and checkpoint 4 asks whether agy has a terminal. `LESSOPEN`
  runs regardless and stays.
- **MAJOR 7:** the value-read names come from assignment words, not the text, so
  `rg 'LD_LIBRARY_PATH=' .` stays silent (friction rows).
- **MINOR 8–12:**
  - `dot''glob` is caught: story 5 scans unquoted words, and reads `GLOBIGNORE` with
    `sets_start_variable`. Q4 states the whole-folder residual and that accepting the risk is
    defensible.
  - `--version` and `--help` are exempt as the sole argument only.
  - `OPENSSL_CONF`, `PERL5DB` and `PYTHONUSERBASE` are added. `MAVEN_OPTS` and `GRADLE_OPTS`
    move to the build-tool residual, beside `JAVA_HOME`.
  - `GIT_DIR` is dropped, and another repository's config is a residual.
  - `fakeroot`, `eatmydata`, `nsenter`, `setpriv`, `prlimit`, `xvfb-run` and `ssh-agent` hide a
    deny today: row 9, story 8, Q6. An inner deny is Q2's and Q6's alternative.
- `PATH=/tmp:$PATH ls` asks for an odd reason, so its test asserts the ask only.

## Converge

- 2026-11-24, the 2.1.331 option diff, relayed from the ci-claude-pin session (commit `f5cb6ff`),
  is folded as story 7 and Q7. Re-measured: `claude --model --managed-settings-in-initialize -p x`
  and `--initialize-fields` give none (row 16). `--trusted-folder` in a value slot also gives
  none, but commander reads it as the value there, so it is not raw-scanned.
- 2026-11-24, the owner (relayed verbatim): "All as recommended".
  - Q1: every editor run asks.
  - Q2: every debugger or profiler run asks.
  - Q3: a search path asks when an entry is outside the project or computed.
  - Q4: under dotglob, a glob asks when it matches a protected file on disk.
  - Q5: story 6 goes in as written. The pagers stay out unless checkpoint 4 finds a terminal
    under agy.
  - Q6: the launchers become opaque names.
  - Q7: the 2.1.331 options are classed as story 7 reads them.

  Build T01–T07.
- T01 build.
  - `bash_escapes` replaces the two `replace` calls at the top of `shell_items`. It reads
    newlines in the pass that tracks quotes and escapes, keeps a quoted newline in its word, and
    joins a backslash-newline only when the backslash is not escaped.
  - Checkpoint 1: the awk reader ends a comment at `\n`, so row 2 asks now. The sed reader's
    ` ; ` line end stays as a guess. The inline readers match across newlines.
  - Bypass review: SOUND WITH CHANGES (no regression against `3e83cc6`; 2 MAJOR, 1 MINOR), each
    a test row:
    - a Makefile recipe line ending in `\\` joined the next line (`_cobot_make.join_continuations`,
      the same blind replace). Only an odd run continues a line now.
    - In double quotes, `\$` and `` \` `` are `$` and `` ` `` to bash, but shlex kept the
      backslash, so `bash -c "echo \$'it\\'s'; git push --force …"` reached its reader as one
      quoted word, and so did an unbalanced quote in backticks. The pass now drops that
      backslash. Such a body holds an ANSI-C quote or a substitution, so it is opaque and asks.
      It was silent before.
