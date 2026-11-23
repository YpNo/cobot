# Spec — inline code beyond `-c`, `-e` and `-` (F-57)

size: medium · profile: library · owner: YpNo · date: 2026-11-23 · revision 2 (challenger
folded) · base `security/gate-f56-f60` `f433a0a` (PR 83, not merged yet; this branch is cut from
its tip)

## Goal

Close F-57 (HIGH; bypass review of F-53, 2026-11-22): the gate asks on inline code only when an
interpreter in `INTERPRETERS` (`python`, `python3`, `node`, `deno`, `ruby`, `perl`, `php`) has a
word that is exactly `-c`, `-e` or `-`. Every other way to hand an interpreter code that never
passed through a file tool reaches no decision, so an agent can run code the gate never reads,
including code that writes cobot's owner files. Measured with `plugins/cobot/bin/cobot-rules
check "<cmd>"` on `f433a0a`, owner and project layers empty (the challenger re-ran every row):

| # | command | today | after |
|---|---|---|---|
| 1 | `node -p x` · `node --print x` · `node --eval=x` · `node --eval x` · `node -pe x` · `node --import data:text/javascript,x` | none | ask |
| 2 | `python3 -ic x` · `python3 -Ic x` · `python3 -Sc x` · `python3 -cprint(1)` · `ruby -eputs` · `python3.12 -c x` · `python3.13t -c x` · `pypy3 -c x` | none | ask |
| 3 | `echo x \| python3` · `echo x \| node` · `python3 < s.py` · `python3 <<< x` · `python3 <<'X'` (no write) · `echo x \| python3 -i s.py` · `python3 /dev/stdin <<< x` · `node /dev/fd/0` · `echo x \| { python3; }` | none | ask (code on stdin) |
| 4 | `python3 -m timeit x` · `python3 -m code` · `python3 -m pdb s.py` · `python3 -m asyncio` · `python3 -m runpy x` | none | ask (the module runs code from its arguments or a prompt) |
| 5 | `python3 -m pip install x` | none | judged as `pip install x` (asks) |
| 6 | `perl -ne x f` · `perl -pe x f` · `perl -E x` · `perl '-MPOSIX;system(q(x))'` · `ruby -ne x f` · `php -r x` · `php -B x` · `php -R x` | none | ask |
| 7 | `deno eval x` · `deno repl --eval x` · `deno run -` · `deno run https://h/e.ts` · `deno run data:text/javascript,x` · `bun -p x` · `bun run -` · `tsx -e x` · `ts-node -e x` · `ts-node -p x` | none | ask |
| 8 | `python3 /tmp/s.py` · `node ~/x.js` · `perl /dev/shm/s.pl` (a script outside the project, Q1) | none | ask, as `bash /tmp/s.sh` does |
| 9 | `poetry run python -c x` · `pdm run …` · `hatch run …` · `conda run …` · `pipx run …` · `corepack pnpm exec node -e x` · `node --run build` | none | ask (launchers read as the runners already are; `node --run` opaque, as `npm run` is) |
| 10 | `awk 'BEGIN{system("x")}'` · `gawk …` · `mawk …` · `nawk …` · `busybox awk …` · `awk '{print \| "sh"}'` · `awk '{"x" \| getline}'` · `gawk '@load "x"'` · `gawk -l x` · `gawk -e …` · `awk -f /dev/stdin` · `sed 's/x/y/e' f` · `sed 's\|x\|y\|gew' f` · `sed '1e x' f` · `sed '/r/{e x}' f` · `sed -f /dev/stdin f` | none | ask (runs a command, loads code or reads its program from stdin) |
| 11 | `awk '{print > "/home/u/.claude/cobot.rules"}' f` · `sed -n "w $HOME/.claude/cobot.rules" f` | none | deny, as `tee ~/.claude/cobot.rules` (a literal write target; sed and awk do not expand `~`) |
| 12 | `node -e 'require("fs").writeFileSync("x","y")'` · `node -p 'fs.copyFileSync(…)'` | ask | deny, as Python's (Q4: "a script that writes files") |
| 13 | `perl -Mstrict -e 'print 1'` · `perl -MList::Util=sum -le …` · `perl -eprint` | deny (wrongly: the `-i` check reads any word with an `i`) | ask (inline code, no in-place edit) |
| 14 | `perl -c s.pl` | ask | ask (unchanged; a syntax check runs `BEGIN` blocks) |
| 15 | `python3 s.py -c x` | ask | silent (`-c` after the script is the script's argument) |

Unchanged: `python3 -c x`, `node -e x`, `perl -e x`, `ruby -e x`, `bun -e x`, `python3 - <<X`,
`python3 -W ignore -c x`, `python3 -X importtime -c x`, `node --require ./x -e x`, `bash /tmp/s.sh`
(ask); `python3 <<X` that writes a file, and `printf … > /tmp/s.py && python3 /tmp/s.py` (deny);
`uv run python -c x`, `uvx`, `npx -c x`, `pnpm dlx`/`bunx tsx -e x`, `mise exec -- python3 -c x`,
`xargs python3 -c x`, `find -exec python3 -c x`, `python3 <(curl …)` (ask).

Silent and unchanged, the friction guard (each one a test row): `python3 s.py`, `node s.js`,
`python3 scripts/check-plugin.py` (a script in the project), `python3 -m pytest`,
`python3 -m venv .venv`, `python3 -m http.server`, `node --version`, `node -v | cat`,
`echo x | python3 --version`, `node --test`, `node --check s.js`, `deno run s.ts`,
`awk '{print $1}' f`, `awk '/a|b/' f`, `awk '$1==1 || $2==2' f`, `awk '{split($0,a,"|")}' f`,
`awk '{gsub(/\|/,",")}' f`, `awk -F, '{s+=$2} END{print s}' f`, `sed -n '1,5p' f`,
`sed 's/a/b/g' f`, `sed 's/e/E/' f`, `sed -n 'w /dev/stdout' f`, `sed --sandbox 's/x/y/e' f`,
`jq -n x`.

## Principles check

- **Proportionality:** medium, one topic: `plugins/cobot/bin/cobot-rules` (the interpreter
  reading, the launchers and the script-write check), and `tests/test_gate_f57.py`.
- **Rules before autonomy:** every change adds an ask or a deny, except row 15 (a misread) and
  row 13 (a deny that was a bug), both test rows.
- **Proof, not promises:** each Goal row is a test row failing on `f433a0a`; friction rows stay
  silent; a bypass-aimed review follows each build task.
- Governance (`docs/01-decisions.md`): decisions 18 (attribution), 20 (one spec, one PR, a task
  per commit), 22 (no dependency), 28 (read-only agents: the asks apply to them too), 31 (stamp),
  33 (trust boundaries, below) and 34 (session grants: no grant kind covers an inline-code ask; a
  test row holds an active grant) hold. ADR-0007 (both runtimes) holds, story 8.
- Architecture: plain layering (`library`); one table per interpreter family, read by one parser.
- New dependencies: none (stdlib only).
- Experts: shell → `lang-shell`; Python → `lang-python`; Node → `lang-typescript` (its runtime
  flags are read from `node --help`, not from memory).
- Delivery: branch `security/gate-f57`, one PR after PR 83; tasks below are the commits.

## Facts read (2026-11-23)

| tool | source | what it says |
|---|---|---|
| node 26.13.0 | `node --help` (local) | `-e, --eval`, `-p, --print`, `-i, --interactive`, `--import`, `-r, --require`, `--loader`/`--experimental-loader` (preload), `--input-type`, `-C, --conditions` (values), `-c, --check` (syntax only), `--test`, `--run` (a package.json script) |
| Python 3.13.15 | `python3 --help` (local) | `-c cmd` and `-m mod` end the option list; `-` or no file reads stdin; `-i` inspects after; `-W arg`, `-X opt` take values; `PYTHONSTARTUP` on an interactive start |
| Python 3.15.2 docs | docs.python.org timeit, code, runpy | `-m timeit` runs its statement arguments and `-s` setup; `-m code` reads stdin; runpy "is not a sandbox" |
| Perl 5.44.0 | perldoc.perl.org/perlrun | `-e`, `-E` (repeatable), `-n`, `-p`, `-i[ext]`, `-M`/`-m` (attached; separate since 5.39.8), `-x`; no file reads stdin, `-` names it; `PERL5OPT` takes `-[CDIMTUWdmtw]` |
| PHP | php.net CLI options | `-r`, `-B`, `-R`, `-E`, `-F`, `-a`; stdin when no file |
| Deno | docs.deno.com eval (2026-05-20), repl (2026-03-12), run (2026-06-19) | `deno eval` (`-p`), `deno repl --eval`/`--eval-file`, `deno run -` (stdin), `--preload`, `--require` |
| Bun | bun.com/docs/cli/run | `-e, --eval`, `-p, --print`, `bun run -` (stdin), `-r, --preload` (`--require`, `--import` aliases); `preload` in bunfig |
| ts-node | typestrong.org options | `-e, --eval`, `-p, --print`, `-r, --require`, `-i, --interactive` |
| GNU awk | gnu.org gawk manual, I/O functions and redirection | `system()`, `print > file`, `print \| cmd`, `\|&`; all off under `--sandbox` |
| GNU sed 4.9 | `sed --help` and `info sed` (local) | `--sandbox` rejects `e`, `w`, `r`; `-i[SUFFIX]` |
| mawk 1.3.4 | `mawk -W usage` (local) | `-f`, `-F`, `-v`; the program is the first operand |

Not read yet, each a build checkpoint before its task (not an assumption): Ruby's options and
clusters (docs.ruby-lang.org 404; before T01), tsx (TLS failure; before T01), gawk's option list
(`-e/--source`, `-i/--include`, `-l/--load`, `-E`; rate-limited; before T04; the challenger's
finding 9 depends on it), sed's `e` command, `e` flag and special files (rate-limited; before
T04; finding 10), mawk's `-W exec` (before T04).

## Stories and acceptance

Acceptance for each story: `uv run --no-project --python 3.13 --with pytest==9.2.0 pytest -q
tests/test_gate_f57.py -k <story>`; its rows fail on `f433a0a` and pass after its task; its
friction rows stay silent.

1. **An interpreter's code options are read from a table, in every form (rows 1, 2, 6, 7, 13,
   15).** `INLINE_CODE` maps each family to its code letters, long names (`--eval x`,
   `--eval=x`, a unique prefix where the program accepts one), value-taking options (`-W`, `-X`,
   `-r`, `--require`, `--import`, `--loader`, `--conditions`, `--input-type`), and the
   subcommands that evaluate (`deno eval`, `deno repl --eval`). A code letter takes the rest of
   its cluster as its value (`-cprint(1)`, `-eputs`; perl's `-ie` is `-i` with suffix `e`). The
   parser stops at the script operand, so `python3 s.py -c x` is the script's argument (row 15).
   Floor: after an option the table does not know (a long name, or a letter read on as a
   flag), any later word that is `-c`, `-e`, `-` or one of the family's own code options asks,
   so a missing entry costs friction, never a hole (challenger finding 2; T01 review). Perl
   `-M`/`-m` asks unless its value is a module name with an optional `=a,b` word list (a `use`
   list is an expression run at BEGIN); the in-place check reads clusters, so only a real `-i`
   denies (row 13). Families: `python`, `python3`, `python3.N`, `python3.Nt`, `pypy`,
   `pypy3`; `node`, `nodejs`; `perl`, `perl5.N`; `php`, `php8.N`; `ruby`; `deno`; `bun`; `tsx`;
   `ts-node`. A `deno run` or `bun` operand that is a URL, `data:`, `npm:` or `jsr:` asks.
2. **Code on stdin asks (row 3).** A bare interpreter (no operand and no info flag such as
   `--version`, `-V`, `-h`) asks wherever it runs: a tool never runs one interactively on
   purpose, so this needs no pipe tracking (challenger finding 3). So do `-i`/`--interactive`,
   and an operand under `/dev/` or `/proc/*/fd/`. A heredoc whose Python code writes a file keeps
   its deny.
3. **`python -m` is read as the module (rows 4, 5).** `python -m pip …` is judged as `pip …`;
   `-m timeit`, `code`, `pdb`, `cProfile`, `profile`, `trace`, `asyncio`, `_pyrepl`, `idlelib`,
   `IPython`, `runpy` ask (Q2). Any other module stays as today.
4. **A script outside the project asks (row 8, Q1).** A script operand that is not under the
   project root (`/tmp`, `$TMPDIR`, HOME outside the project, `/dev/shm`) asks, as `bash /tmp/s.sh`
   does: a file the agent did not write with Write or Edit (`curl -so /tmp/s.py`, `cp`,
   `git show … > /tmp/s.py`) must not be a silent second step (challenger finding 1). A script in
   the project stays silent.
5. **Launchers are read as runners (row 9).** `poetry run`, `pdm run`, `hatch run`,
   `conda run` (past its `-n`/`-p` values), `pipx run` and `corepack <pm>` join the wrapper
   parsers, so their inner command is judged; `node --run` is opaque, as `npm run` is.
6. **awk and sed run commands or write files (rows 10, 11; F-55 Q3 b).** Families: `awk`,
   `gawk`, `mawk`, `nawk`, `original-awk`, `busybox awk`. The program (the first operand, or `-e`/
   `--source`) is scanned with token-aware patterns: `system\s*\(`, a `print`/`printf` into
   `|`, a string or command `| getline`, `|&`, a gawk indirect call `@name(`, `@load`; these ask,
   as do gawk's `-l`/`--load`, `-i`/`--include` and a `-f` from `/dev/`. A literal `print >
   "file"`/`>> "file"` is a write target, judged as a redirect is; a target that is not a
   literal (`print > f`) asks. sed's script (`-e`, `-f`, the first operand) is parsed per command
   with its delimiter: the `e` command (after an address or in a block) and the `e` flag (among
   other flags) ask; `w`/`W` and the `w` flag are write targets, `/dev/stdout` and `/dev/stderr`
   exempt; `-f /dev/stdin` asks. `--sandbox` turns them off, so it is silent.
7. **A Node inline script that writes a file is refused (row 12, Q4).** `NODE_WRITES_RE` reads the
   `fs` writers called on `fs.`, `fsp.` or a `require('fs')`/`require('node:fs')`/
   `fs/promises` result (`writeFile*`, `appendFile*`, `copyFile*`, `cp`, `cpSync`, `rename*`,
   `createWriteStream`) in inline and stdin code, as `PYTHON_WRITES_RE` does for Python. Its
   evasions (`process.binding`, `child_process`, `import()`, a computed name) fall back to the
   ask, not to silence.
8. **Both runtimes.** agy rows: one per story, `force_ask` for an ask and `deny` for a deny.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| code on an interpreter's command line, any option form | `INLINE_CODE` per family, today's rule as a floor | 1 |
| code on an interpreter's stdin | a bare interpreter, `-i`, `/dev/` operands ask | 2 |
| a Python module that runs code from its arguments | `-m` read as the module | 3 |
| a script the file tools never saw | outside the project root asks | 4 |
| a launcher that runs an interpreter | the wrapper parsers | 5 |
| awk or sed running a command or writing a file | a per-language scan of the program | 6 |
| a Node inline script writing a file | `NODE_WRITES_RE` | 7 |
| the same under Antigravity | the shared judge | 8 |

## Clarify

For the owner. The stories carry the recommended defaults.

- **Q1** A script file run by an interpreter: ask when it lies outside the project root, stay
  silent inside it? → recommended: **yes** (story 4). The challenger showed that "every script
  passed through Write or Edit" is false: `curl -so /tmp/s.py u` then `python3 /tmp/s.py` is two
  silent steps today, while `bash /tmp/s.sh` asks. A project's own scripts run all day; a script
  in the project that the agent fetched (`curl -o s.py u && python3 s.py` in two commands) stays
  a residual, weaker than `bash s.sh` (which always asks).
- **Q2** `python -m <module>`: ask only on the named modules that run code from their arguments
  or a prompt (story 3), or on every module not on a list? → recommended: **the named list**.
  `-m pytest`, `-m venv`, `-m pip` (read as pip) run all day; an unknown module is a file on
  `sys.path`, the Q1 class.
- **Q3** Which interpreters: story 1's families only, or also `lua -e`, `Rscript -e`,
  `osascript -e`, `jshell`, `erl -eval`, `guile -c`, `julia -e`…? → recommended: **story 1's
  families**; the others are a residual, one table row each when wanted.
- **Q4** A Node inline script that writes a file: refused, as a Python one is, or asked? →
  recommended: **refused** (story 7), the same protocol rule; Perl and Ruby inline writes keep
  the ask.
- **Q5** Code through the environment (`NODE_OPTIONS=--require=…`, `PERL5OPT=-M…`, `RUBYOPT=-r…`,
  `PYTHONSTARTUP`, `PYTHONINSPECT`): ask when the command sets one, or only on a code form? →
  recommended: **ask when the command sets any of them**: each changes what the interpreter runs,
  and none is set in daily commands. An inherited one is F-59's whole-word residual.

## Plan

1. **T01, the table (story 1):** read Ruby's and tsx's options first. `INLINE_CODE`,
   `interpreter_family(name)`, `inline_code(argv)` (clusters, attached values, value options,
   the script operand, the floor), perl `-M`, the cluster-aware perl `-i`, URL operands.
2. **T02, stdin and scripts (stories 2, 4):** a bare interpreter, `-i`, `/dev/` operands; a script
   operand outside the project root (`Path(cwd)` resolved, as `RepositoryConfig` reads it).
3. **T03, `-m` and launchers (stories 3, 5):** `python_module(argv)`; pip re-read; the named
   modules; the new wrapper parsers; `node --run` opaque.
4. **T04, awk and sed (story 6):** read gawk's options, sed's `e` pages and mawk's `-W exec`
   first. `awk_program`, `sed_commands` and their scans; write targets join `reached.paths`.
5. **T05, Node writes and the environment (story 7, Q5):** `NODE_WRITES_RE` in
   `writes_by_script`; the environment variables ask.
6. **T06, both runtimes and docs:** agy rows; CHANGELOG Security; `docs/configuration.md`;
   FINDINGS F-57 closed, F-63 open for vim, emacs and gdb.

Each task is test first, then the code, the focused tests, ruff and the gate dry run, with a
bypass-aimed review folded before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `INLINE_CODE` per family, every option form, the floor, perl `-M`/`-i` | gate | auth | — |
| T02 | a bare interpreter, `-i`, `/dev/` operands; scripts outside the project | gate | auth | T01 |
| T03 | `python -m`; launchers; `node --run` | gate | auth | T01 |
| T04 | awk and sed programs | gate | auth | — |
| T05 | Node inline writes; environment variables | gate | auth | T01 |
| T06 | agy rows, CHANGELOG, configuration.md, FINDINGS | gate | — | T01–T05 |

One lane: T01–T05 all edit the interpreter reading in `cobot-rules`.

## Trade-offs

- A table per interpreter family over "any option of an interpreter asks": `node --version`,
  `python3 -m pytest` and `node --check` stay silent, and a new flag is one entry. The floor
  keeps today's asks for any option the table misses.
- Ask, not deny, for inline code: the owner may approve `python3 -c 'print(1)'`; a deny is kept
  for what the protocol already refuses (a script that writes files).
- Scanning awk and sed programs, token-aware, over asking on every awk: `awk '/a|b/'` and
  `awk '{print $1}'` run all day.
- The project root as the line for scripts: the gate already reads it for the repository
  configuration; a finer line (was this file written by Write?) would need state across calls.

## Residuals (kept out of this spec, and why)

- **A script fetched, copied or linked into the project** (`curl -o s.py u`, then `python3 s.py`,
  in one command or two): Q1; weaker than `bash s.sh`, which always asks.
- **A planted module or path** (`PYTHONPATH=/tmp python3 s.py`, `ruby -r json` with a planted
  `json.rb` on the load path): the Q1 class; Q5's variables are the ones that run code directly.
- **A copy or link of an interpreter under another name** (`ln -s /usr/bin/python3 p; ./p -c x`):
  the gate reads names, not files; F-58 holds the same class for `claude`.
- **Other interpreters** (`lua`, `Rscript`, `osascript`, `jshell`, `erl`, `guile`, `tclsh`,
  `julia -e`): Q3.
- **Editors and debuggers that run commands** (`vim -c '!x'`, `vim -es`, `emacs --batch --eval`,
  `gdb -ex 'shell x'`): F-55's Q3 answer (b) makes them a new finding when F-57 is specced:
  **F-63**, opened with this spec.
- **A Python module planted on `sys.path`** (`python3 -m mymod`): the Q1 class.
- **An inherited `NODE_OPTIONS` or `PERL5OPT`:** the F-59 whole-word residual (accepted).
- **A Node write through `process.binding`, `child_process` or `import()`:** asks (story 7 falls
  back), not refused.
- **Nested Claude Code** (`claude -p …`): F-58, parked after F-57.

## Challenger verdict

2026-11-23, revision 1: **SOUND WITH CHANGES** (1 CRITICAL, 9 MAJOR, 5 MINOR; every quoted
decision re-run on `f433a0a`). Folded into revision 2:

- CRITICAL 1, scripts outside the project: Q1 reversed to ask there (story 4, row 8).
- MAJOR 2, a value option read as the script: value options in the table, today's rule kept as a
  floor; the three asks that work today are Unchanged rows.
- MAJOR 3, stdin: a bare interpreter asks; `-i`, `/dev/` operands (story 2, row 3).
- MAJOR 4, launchers: story 5, row 9; `node --run` opaque.
- MAJOR 5, perl `-M` code and the `-i` misread: story 1, rows 6 and 13.
- MAJOR 6, attached values: story 1, row 2.
- MAJOR 7, remote code: story 1, row 7.
- MAJOR 8, `-m` modules: story 3, row 4.
- MAJOR 9, awk: token-aware patterns, gawk's options, non-literal targets (story 6, row 10, the
  friction rows); gawk's option list is read before T04.
- MAJOR 10, sed: per-command parse, delimiters, flags, addresses, blocks, special files (story 6,
  rows 10 and 11, friction rows).
- MINOR 11, rows wrong today: `perl -c` stays an ask (row 14); `python3 s.py -c x` (row 15).
- MINOR 12, `~` in sed and awk targets: row 11 uses `$HOME` and a literal path.
- MINOR 13, names: `python3.Nt`, `nawk`, `busybox awk`, `original-awk` in; a copied interpreter
  is a residual.
- MINOR 14, `NODE_WRITES_RE`: anchored on `fs.`/`fsp.`/a require; evasions fall back to the ask.
- MINOR 15, unverified facts: each a checkpoint before its task.

## Converge

- 2026-11-23, the owner: **Q1–Q5 as recommended** (scripts outside the project root ask; the
  named `-m` modules ask; story 1's families only; a Node inline write is refused; setting
  `NODE_OPTIONS`, `PERL5OPT`, `RUBYOPT`, `PYTHONSTARTUP` or `PYTHONINSPECT` asks). Build
  T01–T06.
- T01 build: `plugins/cobot/bin/_cobot_inline.py` holds the tables and the walk; the gate calls
  it from `opaque_as_read`, `whole_segment_is_zone` and `writes_by_script`. The walk decides
  stdin as it reads (a bare interpreter, `-`, a `/dev/` or `/proc/` operand), so story 2 lands
  with T01; T02 adds the scripts outside the project. Ruby (ruby.1, master) and tsx's docs were
  read first; tsx is read with node's table (a drop-in, its own `-e`/`-p` not documented, so
  they ask). Bypass review (SOUND WITH CHANGES, 4 MAJOR, 1 MINOR, none a regression), each a
  test row: the floor reads the family's code options; an unknown cluster letter reads on; perl
  `-M` with an expression asks, `-Mlib=lib` stays silent; deno's `--frozen`, `--lock`,
  `--node-modules-dir`, `--vendor` take no second word; schemes without case, `node22`,
  `deno x` and `bun <script>` ask. `perl -c` keeps its ask (BEGIN blocks), a documented friction.
- T02 build: `outside_script` in the gate's segment loop; the root is the hook's working
  directory, a relative script is read from each folder the walk gives, an unknown folder or an
  expansion asks, symlinks are followed, an owner allow lifts it. cobot's own tools stay silent:
  `own_tool_run`, and the plugin folders Claude Code and agy install into (the session brief runs
  `python3 -I <config dir>/plugins/…/bin/cobot-env`; one route row moved from a made-up
  `/home/me` to the real config dir). Bypass review (SOUND WITH CHANGES, 4 MAJOR, 1 MINOR), each a
  test row: after an unknown option every later word is a possible script; `ruby -C`/`-X`,
  `bun --cwd`, `ts-node --cwd`/`--dir` move the base; preload, include and config files
  (`-r ./x`, `--import`, `-I`, `php -c`, `bun --config`, `ts-node -P`, `deno --preload`) are judged
  where they lie; `perl -S` and `ruby -S` without a `/` ask. Accepted (Q1's residual, below): a
  script copied, linked or fetched into the project earlier in the same command
  (`curl -o d.py u && python3 d.py`, `ln -s /tmp l && python3 l/s.py`): the gate resolves paths as
  they are when it checks. Friction: a cd the walk does not end (`pushd sub && popd`, `cd sub &`),
  and a script under HOME outside the project (`python3 ~/.local/x.py`).
- T03 build: `CODE_MODULES` asks on the module's top package (`asyncio.__main__`,
  `idlelib.pyshell` too); `python -m pip` (and `pip.__main__`) expands to `pip` through
  `expand_runner`; `inner_launcher` reads `poetry`, `pdm`, `hatch` (and `hatch env run`, its
  `env:` prefix and `+py=` filters), `conda`, `mamba`, `micromamba` around `run`; `inner_corepack`
  maps the managers and their binaries (`pnpx` is `pnpm dlx`), an unknown first word stays
  opaque; `pipx run`/`runpip`, `pixi run`/`exec`/`x` and `rye run` are opaque. Bypass review (3
  HIGH, 3 MEDIUM, 1 LOW), each a test row. Accepted: `corepack pnpm@<url>` (the command is read,
  its source is not; corepack refuses a URL unless `COREPACK_ENABLE_UNSAFE_CUSTOM_URLS`); pdm and
  hatch scripts named in pyproject.toml are judged as the command word they look like; friction,
  `conda run -nbase` (an attached value) asks.
- T04 build: `read_program` in `_cobot_inline.py` reads awk (gawk, mawk, nawk, original-awk,
  busybox) and sed (gsed, busybox). awk: options letter by letter and long names by unique
  prefix; the program scanned with strings, regexes (a `/` after an operator or a keyword such as
  `print`, bracket expressions kept whole) and comments set aside. sed: options read after
  operands too (GNU getopt), each command parsed after its address. Asks through
  `opaque_as_read`; literal write targets join `reached.paths`, so an owner file denies; `-f`
  program files go through `outside_script`. `is_opaque` takes only this reading for awk, sed and
  the interpreters (its verb-skipping readings dropped `--sandbox`). The gawk options page stayed
  unread (rate-limited): an option outside the tables makes every awk operand a program. Bypass
  review (2 BLOCKER, 6 MAJOR, 1 MINOR), each a test row. Found on the way, older than this branch:
  the command splitter (`shell_items`) turns a newline inside quotes into ` ; ` and a quoted
  `\` and newline into a blank, so the sed reader takes ` ; ` and `\ ` as possible line ends (a
  false ask at worst); the splitter itself is **F-64**. Friction: `awk '{print > ($1 ".txt")}'`
  (a computed target), `awk '{… | "sort"}'` ask.
- T05 build: `NODE_WRITES_RE` joins `PYTHON_WRITES_RE` in `writes_by_script` (`SCRIPT_WRITES_RE`
  per family: node, tsx, ts-node, bun), so a Node inline or stdin script calling an `fs` writer
  is refused; a write the pattern does not name, a destructured or computed name keeps the ask.
  `START_VARIABLES` gains Q5's five. Bypass review (2 MAJOR): an exported name the command
  computes (`export $N=…`, `export NODE_{OPTIONS,X}=…`) now asks for every start variable
  (`COMPUTED_EXPORT_RE`, older than this branch for `BASH_ENV` too); `BUN_OPTIONS`,
  `PYTHONHOME` and `PHP_INI_SCAN_DIR` join the list (each runs code directly). Accepted, the
  planted-module class: `NODE_PATH`, `RUBYLIB`, `PERL5LIB`, `PYTHONPATH`, `PYTHONWARNINGS` (its
  import needs a planted module). Seen, out of scope, **F-65**: loader variables of any program
  (`LD_PRELOAD`, `JAVA_TOOL_OPTIONS`). A string or comment naming an `fs` writer denies, as
  Python's rule does.
