---
name: lang-shell
description: >-
  Senior shell: POSIX sh against bash 5.x, strict mode and where set -e is ignored, quoting, traps
  and temp files, getopts, idempotent automation, shellcheck, shfmt and bats-core with pinned
  installs, injection and secret hygiene. Use on *.sh, *.bash, *.zsh, installers, entrypoints and
  cron scripts, in builder when the brief names it.
paths:
  - "**/*.sh"
  - "**/*.bash"
  - "**/*.zsh"
user-invocable: false
---

# lang-shell

Promoted from `lang-fallback` on 2026-11-10 (decision 24, server-automation onboarded).
CONTEXT.md and the governance file override it. Versions, dates and sources:
`references/versions.md`; re-verify a line the brief flags stale.

## sh or bash

POSIX `sh` for anything run by `/bin/sh` on unknown hosts (Debian's is dash, Alpine and OpenWrt
use BusyBox ash), container entrypoints and installers. `bash` when you need arrays, `[[ ]]`,
`mapfile`, process substitution or `local -`; then say so: `#!/usr/bin/env bash`.

- [verified 2026-11-10 · src: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html] POSIX.1-2024 brings `set -o pipefail`, `$'...'` and `;&` to sh, but dash 0.5.12 lacks `$'...'` and `read -d`: on real hosts treat them as bash.
- [verified 2026-11-10 · src: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html] `local` is not POSIX (dash and BusyBox have it); `mktemp` is not POSIX either, yet present everywhere in practice.
- [verified 2026-11-10 · src: https://cgit.git.savannah.gnu.org/cgit/bash.git/plain/NEWS?h=bash-5.3] bash 5.3 features (`${ cmd; }`, `GLOBSORT`, `source -p`) only where every target runs 5.3; LTS servers may still run 5.2.
- [verified 2026-11-10 · src: https://cgit.git.savannah.gnu.org/cgit/bash.git/plain/NEWS?h=bash-5.3] bash 5.2+: `&` in `${v/p/r}` means the match; quote the replacement or write `\&`.
- zsh is for zsh configuration only; [verified 2026-11-10 · src: https://github.com/koalaman/shellcheck/wiki/SC1071] shellcheck does not parse it: format with `shfmt -ln zsh`, check syntax with `zsh -n` (reported).

## Strict mode and its limits

- `set -eu` in sh; `set -euo pipefail` in bash.
- [verified 2026-11-10 · src: https://www.gnu.org/software/bash/manual/bash.html] `set -e` is ignored in `if` and `while` tests, every `&&` and `||` element but the last, a pipeline but its last command, after `!`, and for whole functions called from those contexts even if they set `-e` themselves: check critical commands explicitly.
- [verified 2026-11-10 · src: https://www.gnu.org/software/bash/manual/bash.html] bash clears `-e` inside `$(...)` unless `shopt -s inherit_errexit`; assign a substitution on its own line, never in `local x=$(…)`, which masks its status (SC2155).

## Idiom

- Quote every expansion: `"$var"`, `"$@"`, `"$(cmd)"`; `--` before variable operands
  (`rm -- "$f"`); `rm -rf "${dir:?}/"` so an empty variable fails loudly.
- Never change global `IFS`; scope it: `while IFS= read -r line; do …; done < file`.
- `printf '%s\n'` over `echo` for data; `command -v` over `which`; `$(...)` over backticks;
  `cd "$dir" || exit`.
- [verified 2026-11-10 · src: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/xargs.html] `find … -print0 | xargs -0 -r` is POSIX now; `mapfile -t arr < <(cmd)` and `mapfile -d ''` are bash only.
- A quoted here-doc delimiter (`<<'EOF'`) disables expansion: use it for templates and remote
  files.
- `trap cleanup EXIT` plus `INT TERM` (names without `SIG`); traps reset in subshells; `mktemp`
  or `mktemp -d` with the trap, never fixed paths in `/tmp`; `umask 077` before writing secrets.
- `getopts` for short options; long options through a `case` loop. Exit 0 ok, 1 failure, 2 usage,
  126 and 127 as the shell defines them; log to stderr with `printf '%s\n' "$*" >&2`.
- [verified 2026-11-10 · src: https://www.gnu.org/software/bash/manual/bash.html] `exec >>"$log" 2>&1` redirects a whole script; `BASH_XTRACEFD` sends `set -x` traces to their own descriptor.
- Idempotent automation: check before acting, `mkdir -p`, write to a temp file then `mv`,
  `install -m`; when Ansible owns the state, let it.

## Tools and tests

- `shellcheck -x -S style <files>` (`-s sh|bash` when there is no shebang).
  [verified 2026-11-10 · src: https://github.com/koalaman/shellcheck/wiki/Directive] Directives: `# shellcheck source=path`, `shell=`, `disable=SCxxxx # reason`; `external-sources=true` only in `.shellcheckrc`.
- [verified 2026-11-10 · src: https://raw.githubusercontent.com/mvdan/sh/v3.14.1/cmd/shfmt/shfmt.1.scd] `shfmt -d .` when `.editorconfig` sets the style (any parser or printer flag turns it off), else `shfmt -d -i 2 -ci <files>`.
- [verified 2026-11-10 · src: https://raw.githubusercontent.com/bats-core/bats-core/master/docs/source/writing-tests.md] bats-core: `test/*.bats` with `load test_helper`; `setup` and `teardown` per test, `setup_file` per file, `setup_suite` in `setup_suite.bash`; `run -N`, `run !`, `BATS_TEST_TMPDIR`, `bats_require_minimum_version`; `assert_stderr` needs `run --separate-stderr`.
- Test name: `@test "parse_args_missingFile_exits2"`; run `bats test/`.
- Install tools by pinned version and check the release asset's sha256 (`references/versions.md`
  holds today's digests); never `curl | sh` from a moving branch. A tool missing on the machine is
  reported as missing, not installed as a side effect.

## Security

- Never `eval` or `sh -c` with interpolated data: pass data as arguments,
  `sh -c '… "$1"' _ "$value"`; validate a value before using it in a path.
- [verified 2026-11-10 · src: https://cgit.git.savannah.gnu.org/cgit/bash.git/plain/NEWS?h=bash-5.3] Scripts run as root or by cron set `PATH=/usr/sbin:/usr/bin:/sbin:/bin` explicitly; an empty `PATH` means the current directory in bash 5.3.
- Secrets never in argv (visible in `ps`) or under `set -x`: read them from stdin, a descriptor
  or a 0600 file; turn tracing off around them.
- `sudo` only on the commands that need it, `sudo -n` in automation, never `sudo bash` on a
  downloaded script.

## Do not

- Do not use bash features under a `#!/bin/sh` shebang, or zsh syntax anywhere shellcheck runs.
- Do not disable a shellcheck rule without a reason in the directive.
- Do not install shellcheck, shfmt or bats as a side effect of a task.
