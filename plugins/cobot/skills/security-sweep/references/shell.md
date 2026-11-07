# Shell rule pack

Loads for `.sh`, `.bash` and `.zsh` files and applies `core.md` to shell scripts. Rule ids are `SH-<CAT>-<nn>`.
Shell scripts are consistently under-audited and consistently run with high privilege: treat an installer,
entrypoint or CI script as production code.

## Quoting & word splitting

- **SH-QUOTE-01** Unquoted `$VAR` / `$(cmd)` where the value can contain whitespace or glob characters. Word
  splitting turns one argument into many: `rm -rf $DIR` with `DIR="/ tmp"` is the canonical disaster.
- **SH-QUOTE-02** Unquoted `$@` (use `"$@"`); `$*` where `"$@"` is meant.
- **SH-QUOTE-03** Glob expansion of a filename into a command position: a file named `-rf` or
  `--checkpoint-action=exec=...` becomes an option. Use `./*` or `--` before operands.
- **SH-QUOTE-04** `[ $x = y ]` with an empty or multi-word `$x`: syntax error or wrong branch. Use `[[ ]]`, or quote.

## Injection & execution

- **SH-EXEC-01** `eval` with any interpolated value.
- **SH-EXEC-02** Input interpolated into a command run by another interpreter: `ssh host "cmd $VAR"`,
  `docker exec sh -c "$VAR"`, `awk "/$VAR/"`, `sed "s/$VAR/.../"`, `find -exec sh -c "... $VAR"`. Local quoting
  does not protect the remote parse.
- **SH-EXEC-03** `curl ... | sh` / `wget -O- | bash`: remote code execution by design, no integrity check. If
  unavoidable, require a pinned checksum or signature verification.
- **SH-EXEC-04** `source`/`.` of a file whose path or content is not controlled.
- **SH-EXEC-05** `$IFS` or `$PATH` not set explicitly in a privileged script, or a command invoked by bare name
  where `PATH` could be hostile.
- **SH-EXEC-06** Command substitution landing in an arithmetic context: `$(( $VAR ))` executes code in bash.

## Secrets

- **SH-SEC-01** Secret passed as a command-line argument: visible in `ps`, `/proc` and audit logs to every user on
  the box. Use env, stdin or a file.
- **SH-SEC-02** Secret echoed, or `set -x` / `bash -x` active while a secret is in scope (`-x` prints every expansion).
- **SH-SEC-03** Secret written to a file with a default umask, or into `/tmp` without `mktemp`. Key material needs
  `umask 077` or an explicit `chmod 600`.
- **SH-SEC-04** Secret in a heredoc that lands in a log, or in shell history via an interactive-style invocation.
- **SH-SEC-05** `curl -u user:pass` or a token in a URL.

## Files & privilege

- **SH-FILE-01** Predictable temp file (`/tmp/$$`, `/tmp/myapp.tmp`): symlink attack. Use `mktemp -d` and clean up
  with a `trap`.
- **SH-FILE-02** `rm -rf "$DIR"` where `$DIR` can be empty or `/`. Guard with `[ -n "$DIR" ]` and a prefix
  assertion; `rm -rf "$DIR"/*` with unset `DIR` is `rm -rf /*`.
- **SH-FILE-03** `chmod 777` / `chmod -R 777`, or a world-writable directory.
- **SH-FILE-04** `sudo` in a script with no explanation of the least privilege needed; root required for operations
  that do not need it.
- **SH-FILE-05** `cd $DIR` without checking success, then destructive operations in a possibly wrong directory.
  Use `cd x || exit`.
- **SH-FILE-06** `tar`/`unzip` extracting an archive from a remote source without path validation.

## Robustness

- **SH-HAZ-01** No `set -euo pipefail` (or a documented decision not to). Without `-e` a failed step continues;
  without `-o pipefail` a mid-pipe failure is invisible; without `-u` a typo'd variable expands to empty, which
  is how `rm -rf $EMPTY/` happens.
- **SH-HAZ-02** Exit status of a critical command unchecked.
- **SH-HAZ-03** `trap` absent where temp files, locks or background processes need cleanup on signal or error.
- **SH-HAZ-04** No lock (`flock`) on a script that must not run concurrently.
- **SH-HAZ-05** Bash-only syntax (`[[`, arrays, `${x,,}`) under a `#!/bin/sh` shebang: breaks under dash.
- **SH-HAZ-06** Shebang absent, or `#!/bin/bash` where `#!/usr/bin/env bash` is needed for portability (notably
  macOS's system bash versus a Homebrew bash).
- **SH-HAZ-07** Parsing `ls` output, or `for f in $(ls)`: breaks on any filename with a space. Use globs or
  `find -print0 | xargs -0`.
- **SH-HAZ-08** Reading lines with `for line in $(cat f)` instead of `while IFS= read -r line`.

## Verification commands (read-only)

```bash
shellcheck -S style <script>          # if installed; this pack largely encodes it
grep -rn "eval\|curl.*| *sh\|rm -rf\|chmod 777" --include='*.sh' .
grep -rLn "set -euo pipefail" --include='*.sh' .   # scripts missing strict mode
```

If `shellcheck` is installed, run it and fold its findings in, but still apply `SH-SEC-*` and `SH-FILE-*`, which
shellcheck does not cover.
