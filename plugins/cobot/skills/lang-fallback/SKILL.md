---
name: lang-fallback
description: >-
  Procedure for a stack with no dedicated lang-* skill, plus verified tooling for shell and Lua.
  Loads when the session reads or edits **/*.sh, **/*.bash, **/*.zsh, **/*.lua, **/Makefile or
  **/justfile, and whenever a builder works in a language no other lang-* skill covers. Use it
  to establish the repository's own idiom in ten minutes (lint and format config, test runner,
  CI, most-edited files), record the verified commands in .agent/CONTEXT.md, and decide when to
  tell the owner a dedicated skill is worth writing through /cobot:learn. Shell section: POSIX
  sh versus bash, strict mode, shellcheck, shfmt, bats-core, quoting, pinned installs. Lua
  section: Lua 5.4/5.5 versus LuaJIT, luacheck, StyLua, busted, real Lua hosts (Neovim, OpenWrt
  LuCI, NodeMCU, Domoticz dzVents).
paths:
  - "**/*.sh"
  - "**/*.bash"
  - "**/*.zsh"
  - "**/*.lua"
  - "**/Makefile"
  - "**/justfile"
user-invocable: false
---

# lang-fallback

The repository is the authority, not this file and not model memory. Versions and sources:
`references/versions.md`.

## Establish the idiom (ten minutes, read-only)

1. **Configs that already decided things** (2 min): `.editorconfig`, linter and formatter configs
   (`.shellcheckrc`, `.luacheckrc`, `stylua.toml`/`.stylua.toml`, `.pre-commit-config.yaml`,
   `.tool-versions`, `mise.toml`, `.devcontainer/`). They are not up for debate.
2. **Entry points** (2 min): `Makefile`/`justfile` targets, `scripts/`, the README's dev section.
   Prefer the repository's target (`make test`) over the raw tool; it carries the flags.
3. **CI** (2 min): `.github/workflows/*.yml` jobs give the exact lint, test and build commands and
   tool versions the owner trusts. Local commands should match them.
4. **Hot files** (2 min): `git log --since=6.months --name-only --format= | sort | uniq -c | sort -rn | head -3`.
   Read those three: naming, error style, logging, test layout. Match them, including what you
   would do differently.
5. **Prove** (2 min): run each candidate command once; keep only those that exit as expected.
   A command that needs a missing tool is recorded as `missing: <tool>`, not guessed around.

## Record in `.agent/CONTEXT.md`

Under the verified-commands heading, one line per command, with the proof:
`- test: make test  [verified 2026-11-06 · exp: exit 0, 42 tests]`.
Keys: `format`, `lint`, `test-focused`, `test-all`, `build`, `typecheck` (omit what does not
exist; never invent a key). Facts about the repository that took more than one lookup (an
interpreter quirk, a vendored runtime version) go through `cobot-memory learn` into
`.agent/knowledge/<topic>.md`, never by hand.

## When a dedicated skill is worth it

Tell the owner, once, at wrap, when **two** of these hold: the language is the repo's main stack
or appears in two or more of the owner's repos; this session needed a fact you had to look up
twice or got wrong; the toolchain has version-sensitive behaviour (syntax levels, runtime
embeddings). The path is `/cobot:learn <language>` (R1.1): the learner returns a knowledge delta
and a skeleton `lang-<x>`, which stays `reported` until it has served twice. Below that bar, the
knowledge file in `.agent/knowledge/` is enough.

## Shell

**sh or bash.** POSIX `sh` for anything run by `/bin/sh` on unknown hosts (Debian's is dash,
Alpine and OpenWrt use BusyBox ash), container entrypoints and installers. `bash` when you need
arrays, `[[ ]]`, `pipefail`, `mapfile` or process substitution; then say so: `#!/usr/bin/env bash`.
zsh only for zsh config; shellcheck does not parse zsh.

- Strict mode: `set -eu` in sh; `set -euo pipefail` in bash. `-e` is skipped inside `if`, `&&`,
  `||` and functions called from them; check critical commands explicitly. `pipefail` is POSIX
  only since the 2024 edition: do not rely on it in `sh`.
- Quote every expansion: `"$var"`, `"$@"`, `"$(cmd)"`. Unquoted means split and glob.
- Never change global `IFS`; scope it: `while IFS= read -r line; do ...; done < file`.
- `mktemp` plus `trap 'rm -rf "$tmp"' EXIT`; never fixed paths in `/tmp`.
- `printf '%s\n'` over `echo` for data; `command -v` over `which`; `$(...)` over backticks.
- `cd "$dir" || exit` (SC2164); `rm -rf "${dir:?}/"` so an empty variable fails loudly.
- Arguments through arrays (bash) or `"$@"`, never through `eval` or a string rebuilt from input.
- Never `curl | sh` from a moving branch: download a pinned version, verify its checksum or
  signature, then run it.

Commands: `shellcheck -x -S style <files>` (`-s sh|bash` when there is no shebang);
`shfmt -d .` when `.editorconfig` sets the style (any printer flag disables it), else
`shfmt -d -i 2 -ci <files>`;
tests in `test/*.bats` with bats-core plus `bats-support` and `bats-assert`, run by `bats test/`.
Test name: `@test "parse_args_missingFile_exits2"`.

## Lua

**Dialect first.** The host decides, not you: Neovim exposes the Lua 5.1 API and is built with
LuaJIT; NodeMCU is 5.1.4 or 5.3 by build, without `io`/`os`/`debug`; OpenWrt LuCI and Domoticz dzVents embed their own;
standalone code targets 5.4 unless the owner chose 5.5. Lua 5.5 adds syntax (`global`
declarations) that luacheck and StyLua do not list yet: hold back on 5.5-only features while the
tooling lags. LuaJIT has no tagged releases: pin a commit or take the distribution's build.

- `local` everything; globals only through the host's API table (`vim`, `nodemcu` modules).
- Indices start at 1; `#t` is undefined on tables with holes; track `n` yourself.
- Errors: `return nil, err` for expected failures, `error()` for bugs; `pcall` at the boundary.
- Modules return a table; no side effects at `require` time.

Commands: `luacheck .` with `std` set in `.luacheckrc` (`luajit`, `lua54`; Neovim adds
`globals = { "vim" }`); `stylua --check .` (configure `syntax` in `stylua.toml` to the host dialect);
`busted` with specs in `spec/*_spec.lua`, `it("parse_emptyInput_returnsNil", ...)`.
Neovim plugins test in a headless Neovim (`nvim --headless`), since `vim.*` exists nowhere else.

## Do not

- Import an idiom from another project or from memory when the repository shows a different one.
- Record a command in CONTEXT.md that you did not run.
- Install a tool to make a check pass; report `missing: <tool>` and let the owner decide.
- Pipe a remote script into a shell, or pin a tool by `latest`.
