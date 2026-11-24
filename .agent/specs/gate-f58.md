# Spec — nested Claude Code, plugin removal, launchers and copies (F-58)

size: medium · profile: library · owner: YpNo · date: 2026-11-24 · revision 2 (challenger
folded) · base `main` `de4a125` (PRs 83 and 84 merged)

## Goal

Close F-58 (MEDIUM; bypass review of F-53, 2026-11-22): Bash can switch the gate off for Claude
Code, start a session the gate does not govern, or reach Claude Code's own rows by a route they
do not name.

- `claude plugin disable cobot` and `claude plugin uninstall cobot` get no decision. agy's twins
  are refused (`never Bash(agy *plugin* disable*cobot*)`).
- A nested session started with `--bare`, `--safe-mode`, `--setting-sources`, `--restricted` or
  `CLAUDE_CODE_SIMPLE=1` loads no plugin hook. The gate is off inside it, and its agent can write
  cobot's owner files.
- A launcher (`volta run`, `pnpx`) or an unread option of a subcommand (`claude agents
  --dangerously-skip-permissions`) gets past the rows. So does a glob that names
  `~/.claude.json` where the written-out word asks.

Measured with `plugins/cobot/bin/cobot-rules check "<cmd>"` on `de4a125`, with Claude Code
2.1.311 and the owner and project layers empty. The challenger re-ran every row:

| # | command | today | after |
|---|---|---|---|
| 1 | `claude plugin disable cobot` · `claude plugins disable cobot@cobot` · `claude plugin uninstall cobot` · `claude plugin remove cobot` | none | deny (agy's rule) |
| 2 | `claude plugin i x` · `claude plugin update x` · `claude plugin init x` · `claude plugin eval --trust-plugin x` | none | ask (as `claude plugin install` asks) |
| 3 | `claude -p x --bare` · `claude --bare -p x` · `claude -r --bare` · `claude -p x --safe-mode` · `claude -p x --setting-sources project` · `claude --restricted -p x` | none | ask (the gate's hooks do not load) |
| 4 | `claude -p x --managed-settings {}` · `--permission-prompt-tool x` · `--sdk-url wss://h` · `--dangerously-load-development-channels server:x` · `--plugin-url https://h/p.zip` | none | ask (settings, a permission answerer, a transport or plugin code from outside) |
| 5 | `claude -p x --dangerously-skip-permissions` · `--allow-dangerously-skip-permissions` · `--permission-mode bypassPermissions` · `--permission-mode=auto` · `--add-dir ~/.claude` | none | ask (Q2) |
| 6 | `claude --cloud x` · `claude --remote-control` · `claude --environment e` · `claude --teleport` · `claude --desktop` · `claude ultrareview` | none | ask (Q3: the session or the branch runs elsewhere) |
| 7 | `claude agents --dangerously-skip-permissions` · `claude agents --permission-mode bypassPermissions` · `claude agents --setting-sources project` | none | ask (a subcommand's own options, read from its own table) |
| 8 | `claude -p x --flag-not-in-the-binary` | none | ask (Q1) |
| 9 | `bash -c "claude --bare"` · `env claude --bare` · `claude-code --bare` · `mise exec -- claude --bare` · `npm exec -- claude --bare` · `pnpm exec claude --bare` · `yarn exec claude --bare` | none | ask (the reader runs on every unwrapped form) |
| 10 | `CLAUDE_CODE_SIMPLE=1 claude -p x` · `CLAUDE_CODE_SAFE_MODE=1 …` · `CLAUDE_CONFIG_DIR=/tmp/c …` · `CLAUDE_CODE_PLUGIN_DIRS=/tmp/p …` · `CLAUDE_CODE_MANAGED_SETTINGS_PATH=/tmp/s.json …` · `CLAUDE_CODE_SHELL_PREFIX=/tmp/w …` · `CLAUDE_ENV_FILE=… claude` | none | ask (Q8) |
| 11 | `volta run claude mcp add x` · `asdf exec claude mcp add x` · `fnm exec -- claude --bare` · `npm explore x -- claude --bare` · `nvm exec claude --bare` | none | the inner command's decision |
| 12 | `pnpx @anthropic-ai/claude-code mcp add x` · `dx npm:@anthropic-ai/claude-code -p x` · `uv tool run x` | none | ask (a package's binary, as `npx`, `uvx` and `deno x` ask) |
| 13 | `…/node_modules/@anthropic-ai/claude-code/cli.js mcp add x` (run by path) | none | read as `claude` (a name row; Q4) |
| 14 | `tee ~/.claude.js?n` · `cp x ~/.claude.j*` · `rm ~/.claude.j*` · `tee .mc?.json` · `tee ~/.claude.json.b*` | none | ask, as the written-out word asks (Q6) |
| 15 | `claude install latest` · `claude update` · `claude upgrade` · `claude purge` · `claude import codex --yes` · `claude auto-mode reset` | none | ask (Q7) |

Unchanged, and each a test row. These ask today: `claude -p x --settings s.json`,
`--mcp-config m.json`, `--plugin-dir p`, `--plugin-dir-no-mcp p`, `claude mcp add x`,
`claude plugin install x`, `/usr/local/bin/claude --settings s`, `command claude mcp add x`,
`mise exec -- claude mcp add x`, `node …@anthropic-ai/claude-code…`, `npx …`, `bunx …`,
`bun x …`, `yarn dlx …`, `pnpm dlx …`, `deno x …`, `HOME=/tmp claude -p x`, `clau?e --bare`,
`$c --bare`, `agy …`, `tee ~/.claude/cobot.r*`, `cp x ~/.claude.json` and `cat ~/.bashrc`.

Silent and unchanged, the friction guard, each a test row:
- `claude`, `claude -p x`, `claude -c`, `claude --resume`, `claude -r abc`, `claude --version`;
- `claude -p x -- --bare` (after `--`, the word is the prompt's);
- `claude -p x --model sonnet --output-format json`, `claude -p x --max-turns 3` (a hidden option
  the repository's spikes use), `claude -p x --max-budget-usd 1`;
- `claude -p x --permission-mode plan`, `--permission-mode acceptEdits`,
  `--allowedTools "Bash(git push:*)"`, `--allowedTools Read`;
- `claude --bg x`, `claude -w x`, `claude mcp list`, `claude doctor`, `claude plugin list`;
- `ls ~`, `cp x ~/.config/y`.

## Principles check

- **Proportionality:** medium, one topic. The work sits in `plugins/cobot/bin/cobot-rules`: a
  reader of `claude`'s argv, launcher parsers and glob matching on the protected file words.
  Also `plugins/cobot/rules/default.rules` and `tests/test_gate_f58.py`.
- **Rules before autonomy:** every change adds an ask or a deny, and no row is lifted. The
  plugin-removal deny follows the agy precedent (`default.rules`, "disabling, removing or
  relinking cobot drops the gate").
- **Proof, not promises:** each Goal row is a test row failing on `de4a125`; friction rows stay
  silent; a bypass-aimed review follows each build task.
- **Governance** (`docs/01-decisions.md`): these decisions hold:
  - 18, attribution;
  - 20, one spec, one PR, a task per commit;
  - 22, no new dependency;
  - 28, read-only agents (the asks apply to them too);
  - 31, the stamp;
  - 33, trust boundaries (below);
  - 34, session grants (no grant kind covers these asks).

  ADR-0007 (both runtimes) holds too: the gate judges `claude …` under agy's `run_command` as
  under Claude Code, and `agy …` already asks.
- **Architecture:** plain layering (`library`). Option tables per command and subcommand, read
  like `_cobot_inline`'s interpreter tables.
- **New dependencies:** none (stdlib only).
- **Delivery:** branch `security/gate-f58`, one PR; the tasks below are the commits.

## Facts read (2026-11-24)

| tool | source | what it says |
|---|---|---|
| Claude Code 2.1.311 | `claude --help` (local) | `--bare` skips hooks from settings and plugins and sets `CLAUDE_CODE_SIMPLE=1`. `--safe-mode` disables plugins, hooks and MCP servers (`CLAUDE_CODE_SAFE_MODE`). `--restricted` drops the code-running tools unless `--tools` names them, and ignores user, project and local settings. `--setting-sources` picks which settings load. `--plugin-url` fetches a plugin for the session. `--cloud`, `--environment`, `--remote-control` and `--teleport` run or reach a session elsewhere. `--permission-mode` choices: acceptEdits, auto, bypassPermissions, manual, dontAsk, plan. |
| Claude Code 2.1.311 | `claude <opt> auth status` (the challenger) | hidden options are accepted: `--managed-settings`, `--system-prompt-file`, `--append-system-prompt-file`, `--permission-prompt-tool`, `--sdk-url`, `--dangerously-load-development-channels`, `--channels`, `--forward-home-settings`, `--resume-session-at`, `--plugin-dir-no-mcp`, `--max-turns`; an unknown option fails ("unknown option") |
| Claude Code 2.1.311 | `claude agents --help` | the sessions it dispatches take `--dangerously-skip-permissions`, `--permission-mode`, `--setting-sources`, `--restricted`, `--mcp-config`, `--plugin-dir` |
| cobot | `docs/reference/claude-code-mechanics.md` | a nested `claude -p` loads the installed plugin, so the gate governs it; in `-p` a hook's ask refuses the call; spike B: the gate's ask held over `--allowedTools` |
| cobot | `default.rules` | `never Bash(agy *plugin* disable*cobot*)`, `uninstall`, `link`; `ask Bash(agy *)` ("a nested agy session runs outside this gate"); the `claude *--settings*`, `--mcp-config`, `--plugin-dir`, `mcp *add*`, `plugin install` rows |
| agy 1.5.9 | `agy --help` (local) | `--dangerously-skip-permissions`, `--settings`, `--remote-agent`, `--sandbox` (already asked by `agy *`) |

Not read yet. Each is a build checkpoint before its task, not an assumption:

1. **The option table's source.** Read the binary's own option list (`grep -ao '"--[a-z-]*'` on
   the `claude` binary, each candidate confirmed through `claude <opt> auth status`), for 2.1.311
   and for 2.1.322, the CI pin. Record each option's value shape: none, required, optional
   `[value]` or variadic. Note the aliases (`--allowed-tools`, `--disallowed-tools`,
   `--background`) and each subcommand's own options (`agents`, `mcp add`, whose words after
   `--` belong to the server). Before T01.
2. **Whether a plugin hook's deny and ask still hold** in a nested `claude -p` with
   `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` or `auto`. This is a
   spike in the owner's terminal, because a sandboxed `claude -p` cannot sign in. Q2's default
   does not depend on the answer; the docs line does. Before T01.
3. **Whether `--restricted` alone loads cobot.** Cobot is enabled through `enabledPlugins` in user
   settings, which `--restricted` ignores (inferred, not run). Also which project files its file
   tools may still edit: `.agent/cobot.rules`, `.agents/hooks.json`. It is in the same spike,
   and row 3 asks either way. Before T01.
4. **What the `CLAUDE_CODE_*` variables do.** Their names come from the binary
   (`CLAUDE_CODE_PLUGIN_DIRS`, `CLAUDE_CODE_MANAGED_SETTINGS_PATH`, `CLAUDE_CODE_SHELL_PREFIX`,
   `CLAUDE_CODE_SHELL`, `CLAUDE_CODE_PLUGIN_CACHE_DIR`,
   `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS`); their meaning is inferred from the
   names. Read Claude Code's settings and environment docs. Before T02.
5. **The option syntax of `volta run`, `asdf exec`, `fnm exec`, `nvm exec` and `npm explore`**,
   from each tool's own docs. Before T03.

## Stories and acceptance

Acceptance for each story: `uv run --no-project --python 3.13 --with pytest==9.2.0 pytest -q
tests/test_gate_f58.py -k <story>`. Its rows fail on `de4a125` and pass after its task, and its
friction rows stay silent.

1. **Cobot's plugin cannot be disabled or removed through Claude Code (rows 1, 2).**
   - `never` rows for `claude *plugin* disable*cobot*`, `uninstall*cobot*` and `remove*cobot*`
     mirror agy's.
   - `ask` rows cover the install alias `i`, `update`, `init` and `eval --trust-plugin`.
   - No question: this follows the agy precedent.
2. **A nested session's options are read from tables (rows 3–9).**
   - `CLAUDE_OPTIONS` holds the top level's options. Each subcommand that starts or dispatches
     a session (`agents`) has its own table. The tables come from checkpoint 1, and each option
     has a value shape: none, required (takes the next word even when it starts with a dash),
     optional (`-r`, `--cloud`, `-d`, `--remote-control`, `--teleport`, `-w`, `--from-pr`,
     `--prompt-suggestions` take the next word only when it is not an option) or variadic
     (`--allowedTools`). `--name=value`, options after the prompt, and the aliases are read.
     `--` ends the options.
   - These ask:
     - the options that switch the gate's hooks off: `--bare`, `--safe-mode`,
       `--setting-sources` and `--restricted`;
     - the ones that bring in settings, a permission answerer, a transport or plugin code:
       `--managed-settings`, `--permission-prompt-tool`, `--sdk-url`,
       `--dangerously-load-development-channels` and `--plugin-url`;
     - Q2's widening options, Q3's moving options and `ultrareview`;
     - an option a table lacks (Q1).
   - The reader runs wherever the `claude *` rows match: on `claude`, on a path whose basename
     is `claude`, on `claude-code`, and on every unwrapped form (`bash -c`, `env`, `mise exec`,
     `npm exec`, `pnpm exec`, `yarn exec`, the launchers of story 4).
3. **The variables that change what Claude Code loads ask (row 10; Q8).** `CLAUDE_CODE_SIMPLE`,
   `CLAUDE_CODE_SAFE_MODE`, `CLAUDE_CONFIG_DIR`, `CLAUDE_ENV_FILE` and every `CLAUDE_CODE_*` name
   join the start variables, so setting one in the command asks. That includes a computed
   exported name (F-57 T05).
4. **Launchers are read (rows 11, 12).**
   - `volta run`, `asdf exec`, `fnm exec`, `nvm exec` and `npm explore <pkg> --` join the
     wrapper parsers, so their inner command is judged. An option a parser lacks leaves the
     command opaque, so it asks.
   - `pnpx`, `dx` and `uv tool run` are opaque, as `npx`, `deno x` and `uvx` are.
5. **The npm package's entry, run by path, is read as `claude` (row 13; Q4).** A command word
   matching `*/@anthropic-ai/claude-code/cli.js` (or `cli.mjs`) is read as `claude`.
   Identifying copies of the binary by file is Q4's alternative, not the default.
6. **A glob that names a protected file now asks as the word does (row 14; Q6).**
   - A glob word is matched against the files protected by name (`~/.claude.json`, its backups,
     `.mcp.json` and the `CLAUDE_CONFIG_DIR` twins) on disk at check time, bounded as the glob
     deadline is.
   - A glob that matches one asks with that file's reason.
   - Globs inside a protected folder keep today's ask.
7. **The subcommands that change Claude Code itself ask (row 15; Q7).** These are `install`,
   `update`, `upgrade`, `purge`, `import` and `auto-mode reset`. `doctor`, `mcp list`,
   `plugin list` and `auth status` stay silent.
8. **Both runtimes.** agy rows: one per story, `deny` for a deny and `force_ask` for an ask.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| cobot's plugin removed or disabled | `never` rows | 1 |
| a nested Claude Code session without the gate | the option tables, the start variables | 2, 3 |
| settings, a permission answerer or plugin code from outside the session | the named options | 2 |
| a nested session with more permissions than the owner gave | Q2's options | 2 |
| the session or the branch moved to the cloud or a remote | Q3's options | 2 |
| a launcher in front of `claude` | the wrapper parsers, opaque launchers | 4 |
| Claude Code's npm entry under its path | the name row | 5 |
| a glob naming a protected file | a match on disk | 6 |
| Claude Code replaced or its state edited | Q7's subcommands | 7 |
| the same under Antigravity | the shared judge | 8 |

## Clarify

These are for the owner. The stories carry the recommended defaults. Each question can also be
answered with **accept the risk**: the shape stays as it is today, it is recorded as an
accepted residual in this spec and in FINDINGS, and its rows are dropped.

- **Q1: an option the table does not know.** Should it ask, or should only the named options
  ask?
  - Recommended: **ask**. Claude Code adds options often, some of them hidden, and a new one
    may switch hooks off.
  - The table comes from the binary's own option list (checkpoint 1), not from `--help`. Hidden
    daily options such as `--max-turns` are therefore known and stay silent.
  - The cost is an ask after a release that adds an option, until the table catches up.
  - Other options: ask on the named options only; accept the risk.
- **Q2: permission-widening options.** These are `--dangerously-skip-permissions`,
  `--allow-dangerously-skip-permissions`, `--permission-mode bypassPermissions`, `auto` and
  `dontAsk`, and `--add-dir` naming a protected folder. Should they ask?
  - Recommended: **ask**. The nested agent would act without the permission prompts the owner
    answers, and whether the gate's own ask still holds under bypass is unverified
    (checkpoint 2).
  - `--allowedTools` and `--tools` stay silent: spike B showed the gate's ask holds over them.
  - Other options: ask on the two `dangerously` options and `bypassPermissions` only; accept the
    risk.
- **Q3: moving the session or the branch elsewhere.** These are `--cloud`, `--environment`,
  `--remote-control`, `--teleport`, `--desktop` and `claude ultrareview`. Should they ask?
  - Recommended: **ask**. Each runs or reaches a session outside this machine's gate, and
    `--cloud` and `ultrareview` send the branch away.
  - Other options: stay silent; accept the risk.
- **Q4: copies of the binary.** This covers `cp /usr/bin/claude c && ./c --bare`, `ln -s`, `cat
  >`, `dd if=`, `install` and `rsync`.
  - Recommended: **accept the risk**. The easiest forms escape any file check
    (`cp "$(command -v claude)" c`, `cp /proc/self/exe c`), a native install has no `cli.js`
    to compare, and the gate reads names, not files, as F-57's copied-interpreter residual
    already does.
  - Story 5 keeps the one name row that costs nothing.
  - Other option: identify the binary by file (`os.path.samefile` against
    `shutil.which("claude")`) on copy sources and command words. That is a stat per word, and
    the forms above stay residual.
- **Q5: an inherited `CLAUDE_CODE_SIMPLE` or `CLAUDE_CONFIG_DIR`.** Story 3 asks only when the
  command sets one. Should a nested `claude` also ask when the variable is already in the gate's
  own environment?
  - Recommended: **no, accept the risk**. The owner's shell set it, not the agent. It is the
    F-59 class.
- **Q6: globs on protected files.** Should a glob ask when it matches a protected file on disk,
  when it could match one by pattern, or not at all?
  - Recommended: **when it matches now, for any verb.** `tee .mc?.json` asks in a repository
    with a `.mcp.json`. `~/.claude.json` exists on every Claude Code machine, so `ls ~/.claude*`,
    `ls ~/.c*`, `ls -d ~/.*` and `du -sh ~/.*` always ask, as `ls ~/.claude.json` does today.
  - Other options: match on disk for writing, moving and removing verbs only (reads keep
    today's silence); could match by pattern; accept the risk.
- **Q7: the subcommands that change Claude Code itself.** These are `install`, `update` and
  `upgrade` (each replaces the binary that every later session and hook runs under), `purge`
  (edits `~/.claude.json`), `import` (writes configuration) and `auto-mode reset`. Should they
  ask?
  - Recommended: **ask, all six**.
  - Other options: ask on `purge` and `import` only (state and configuration), leaving the
    binary's own updates silent; accept the risk.
- **Q8: which environment variables.** Story 3 names five and the `CLAUDE_CODE_*` prefix.
  - Recommended: **the five and the prefix**. A prefix keeps up with new names (the binary holds
    dozens); none is set in daily commands.
  - Other options: the five named only; accept the risk.

## Plan

1. **T01, plugin rows (story 1).** The `never` and `ask` rows in `default.rules`, with test
   rows.
2. **T02, the option tables (story 2).** Run checkpoints 1–3 first. Then build `CLAUDE_OPTIONS`
   and the subcommand tables, and `claude_reading(argv)`. Wire it into `opaque_as_read`, or a
   judged ask with its own reason, on every unwrapped form. The existing `claude *…*` rows stay.
3. **T03, the variables (story 3).** Run checkpoint 4 first. Then `START_VARIABLES` and the
   `CLAUDE_CODE_` prefix.
4. **T04, the launchers and the name row (stories 4, 5).** Run checkpoint 5 first. Then the
   wrapper parsers, the opaque entries and the `cli.js` name row.
5. **T05, globs (story 6).** Match glob words against the protected file names, bounded.
6. **T06, subcommands and both runtimes (stories 7, 8).** Rows in `default.rules`, agy rows,
   the CHANGELOG Security entry, `docs/configuration.md`, and FINDINGS F-58 closed or set to
   accepted.

Each task is test first, then the code, the focused tests, ruff and the gate dry run, with a
bypass-aimed review folded before its commit.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | plugin disable, uninstall and install rows | gate | auth | — |
| T02 | `claude` option tables, per subcommand, on every unwrapped form | gate | auth | — |
| T03 | start variables | gate | auth | — |
| T04 | launchers, the `cli.js` name row | gate | auth | T02 |
| T05 | globs on protected files | gate | auth | — |
| T06 | subcommand rows, agy rows, docs, FINDINGS | gate | — | T01–T05 |

## Trade-offs

- **Option tables, not "every nested `claude` asks"** as `agy *` does. With the tables,
  `claude -p x` (which the gate still governs) and `claude --version` stay silent. The tables
  have to follow Claude Code releases, and Q1's default makes a lagging table ask rather than
  stay silent.
- **Deny for removing the plugin, ask for the rest.** Removing cobot drops the gate for every
  later session, as agy's rows already say. A nested `--bare` run may be wanted on purpose (a
  clean benchmark).
- **A glob matched on disk, not by pattern.** This keeps `cat .*.json` silent in a repository
  without a `.mcp.json`. The answer can change between the check and the run, and that window
  is the accepted cost.

## Residuals (kept out of this spec, and why)

- **An inherited start variable:** Q5, the F-59 class.
- **A copy of the binary** under any name (Q4's default): the gate reads names, not files.
- **A link made earlier in the same command** (`ln -s /usr/bin/claude c && ./c --bare`): paths
  are resolved as they are at check time, as in F-57's Q1 residual.
- **Claude Code reached through its SDK** (`node -e 'require("@anthropic-ai/claude-agent-sdk")…'`,
  `python3 -c 'import claude_agent_sdk'`): this is inline code, which already asks (F-57). A
  script in the project that calls the SDK is F-57's Q1 class.
- **A plugin edited in its cache** (`~/.claude/plugins/cache/…`): this is under the config dir,
  whose protection is gate-f56-f60's.
- **Editors and debuggers that run commands:** F-63.

## Challenger verdict

2026-11-24, revision 1: **SOUND WITH CHANGES** (1 BLOCKER, 7 MAJOR, 6 MINOR). Every Goal row was
re-run on `de4a125` and held. One friction row was wrong (`cat ~/.bashrc` asks: it is a
protected file), so it moved to Unchanged. Folded into revision 2:

- **BLOCKER 1,** `claude plugin disable` and `uninstall cobot` get none, while agy's twins are
  refused. Now story 1, rows 1 and 2.
- **MAJOR 2,** hidden options (`--managed-settings`, `--permission-prompt-tool`, `--sdk-url`,
  `--dangerously-load-development-channels`): row 4. The table comes from the binary
  (checkpoint 1).
- **MAJOR 3,** subcommands with their own options (`claude agents --dangerously-skip-…`): row 7,
  a table per subcommand.
- **MAJOR 4,** value shapes: none, required, optional and variadic, plus the aliases and `--`
  (story 2). The friction rows `claude -r abc` and `claude -p x -- --bare` are added, and the ask
  row `claude -r --bare`.
- **MAJOR 5,** `--restricted` alone: row 3, checkpoint 3.
- **MAJOR 6,** the `CLAUDE_CODE_*` variables: row 10, Q8, checkpoint 4.
- **MAJOR 7,** unwrapped forms (`bash -c`, `env`, `mise exec`, `npm`/`pnpm`/`yarn exec`): row 9.
- **MAJOR 8,** identity by file is costly and misses the easiest forms. Q4 now recommends
  accepting the risk, and story 5 keeps the `cli.js` name row.
- **MINOR 9–14:**
  - Q7 now covers `update`, `upgrade`, `import` and `auto-mode reset`.
  - Q3 covers `ultrareview` and `--desktop`.
  - Q1's table comes from the binary, so `--max-turns` is known.
  - Q2 is narrowed: `--allowedTools` stays silent, per spike B.
  - Q6 states its friction, with a writing-verbs-only option.
  - `install` and `rsync` copies are now in Q4, not the residuals.

## Converge

- 2026-11-24, the owner (relayed verbatim): "All as recommended". Q1 ask on an option the table
  lacks; Q2 ask on the widening options; Q3 ask on the moving options; Q4 accept the risk
  (copies of the binary); Q5 accept the risk (an inherited variable); Q6 ask when a glob matches
  a protected file on disk, for any verb; Q7 ask on all six subcommands; Q8 the five named
  variables and the `CLAUDE_CODE_*` prefix. Build T01–T06; Q4 and Q5 go to FINDINGS as accepted
  residuals.
- T01 build: `never` rows for disabling (by name, `--all`, `-a`), uninstalling or removing cobot
  and removing its marketplace; `ask` rows for the `i` alias, `update`, `init`/`new`,
  `eval --trust-plugin`, `prune`/`autoremove`/`--prune`, `configure --values-stdin`, any
  `disable`, a marketplace removed or refreshed, and `tag --push`. Bypass review (SOUND WITH
  CHANGES, no deny-level bypass; 1 MAJOR, 3 MINOR), each a test row: `tag --push` and `--prune`
  ask; the name is matched in any case (`[Cc][Oo][Bb][Oo][Tt]`, Claude Code's id matching
  unverified); the verb is pinned right after `plugin` or `plugins`, so a prompt's words and
  `--plugin-dir` no longer hit a deny.
