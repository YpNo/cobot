# Shell — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale lang-shell`). Moved from `lang-fallback` on
2026-11-10, then extended.

## Tools

| Tool | Current | Released | Last commit |
|---|---|---|---|
| shellcheck | 0.11.0 | 2025-08-04 | 2026-11-05 |
| shfmt (mvdan/sh) | 3.14.1 | 2026-09-06 | — |
| bats-core | 1.14.0 | 2026-07-21 | — |
| bats-assert | 2.2.4 | 2025-10-14 | — |
| bats-support | 0.3.0 | 2022-03-04 | — |

- [verified 2026-11-06 · src: https://github.com/koalaman/shellcheck/releases] shellcheck 0.11.0 is the latest release; master is active (commit 2026-11-05).
- [verified 2026-11-06 · src: https://github.com/koalaman/shellcheck/wiki/SC1071] shellcheck supports sh, bash, dash and ksh only; no zsh.
- [verified 2026-11-06 · src: https://github.com/mvdan/sh/releases] shfmt 3.14.1; parses POSIX sh, bash, zsh and mksh; building from source needs Go 1.26+.
- [verified 2026-11-06 · src: https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd] shfmt applies `.editorconfig` only when no parser or printer flag is given.
- [verified 2026-11-06 · src: https://github.com/bats-core/bats-core/releases] bats-core 1.14.0.
- [verified 2026-11-06 · src: https://github.com/bats-core/bats-assert/releases] bats-assert 2.2.4; bats-support 0.3.0 is old but still the dependency bats-assert expects.
- [verified 2026-11-06 · src: https://www.shellcheck.net/wiki/SC3040] `set -o pipefail` entered POSIX in POSIX.1-2024; older `/bin/sh` implementations reject it.

## Shells and standards

- [verified 2026-11-10 · src: https://ftp.gnu.org/gnu/bash/bash-5.3-patches/] bash 5.3 (2025-07-30), patch level 5.3.20 (2026-09-14).
- [verified 2026-11-10 · src: https://cgit.git.savannah.gnu.org/cgit/bash.git/plain/NEWS?h=bash-5.3] bash 5.3 adds `${ cmd; }` and `${| cmd; }` (no fork), `GLOBSORT`, `source -p PATH`, `array_expand_once`, `BASH_MONOSECONDS`, `BASH_TRAPSIG`; an empty `PATH` now means the current directory.
- [verified 2026-11-10 · src: https://cgit.git.savannah.gnu.org/cgit/bash.git/plain/NEWS?h=bash-5.3] bash 5.2 turned on `patsub_replacement` (`&` in `${v/p/r}` is the match) and `globskipdots`.
- [verified 2026-11-10 · src: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html] POSIX.1-2024 adds `set -o pipefail`, `$'...'`, `case` fallthrough `;&`, and `{location}>` (implementation-defined); `local` is still not POSIX.
- [verified 2026-11-10 · src: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/read.html] POSIX.1-2024 adds `read -d`, `find -print0`, `xargs -0 -r`; `realpath`, `readlink`, `timeout` joined the utility index; `mktemp` is still not POSIX.
- [verified 2026-11-10 · src: https://manpages.debian.org/testing/dash/dash.1.en.html] dash 0.5.12 documents `local` and `pipefail`, not `$'...'`, `read -d` or `[[`.
- [verified 2026-11-10 · src: https://github.com/koalaman/shellcheck/releases/tag/v0.11.0] shellcheck 0.11.0 adds SC2331 and SC2332 and SC3062, turns SC2002 off by default and drops SC3013 (POSIX 2024 covers it).
- [verified 2026-11-10 · src: https://raw.githubusercontent.com/mvdan/sh/v3.14.1/cmd/shfmt/shfmt.1.scd] shfmt 3.14.1: any parser or printer flag (`-ln`, `-p`, `-s`, `-i`, `-ci` …) turns `.editorconfig` off; `-d` and `-l` keep it; keys `shell_variant`, `switch_case_indent`, `binary_next_line`, `space_redirects`, `function_next_line`.
- [verified 2026-11-10 · src: https://github.com/bats-core/bats-core/releases/tag/v1.14.0] bats 1.14.0 breaking: `run` honours `set -e` inside functions; no tests found is an error (`--allow-empty-suite`); adds `--errexit`.
- [verified 2026-11-10 · src: https://api.github.com/repos/koalaman/shellcheck/releases/tags/v0.11.0] shellcheck v0.11.0 linux x86_64 tar.xz `sha256:8c3be12b05d5c177a04c29e3c78ce89ac86f1595681cab149b65b97c4e227198`; shfmt v3.14.1 linux amd64 `sha256:76e77641faa025814b77f153b29796b8e6fa2fca03e0c76a691608b86c7ea7bf` (the release asset digests; neither project publishes a checksum file).
