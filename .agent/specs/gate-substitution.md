# Spec — the gate judges a substitution by what it runs

size: large · profile: library · owner: YpNo · date: 2026-11-13 · revision 3 (two challenger passes folded)

## Goal

Today `judge_bash` in `plugins/cobot/bin/cobot-rules` asks for every command that holds `$(…)`,
a backtick, `<(…)` or `>(…)` (`opaque_all = has_substitution(command)`): a hook `ask` prompts
even in auto mode. In the owner's latex-resume-generator test (2026-11-11 to 13) seven gate
prompts named a substitution: four `"$(cat <<'EOF' … EOF)"` message bodies (`cobot-memory
journal add`, `git commit -m`; the commits still ask through `ask Bash(git commit*)`), one an
escaped backtick inside a double-quoted `grep` pattern, the others read-only (`$(wc -c < f)`).

After this change the gate parses each substitution body as its own command, judges it with
the same rules, and asks only when the substituted text could decide what runs or make a rule
match. The blanket ask also hid bypasses in the same parsing path, all **silent today** (checked
with `cobot-rules check`, owner layer off); the new parser has to close them or it would expose
them:

| command | today | after |
|---|---|---|
| `cat <<EOF > f; git push --force` ⏎ body ⏎ `EOF` (line cut at `<<`) | silent | deny |
| unquoted here-document body holding `$(git push --force)` | silent | deny |
| `cat <<E"O"F` ⏎ `x` ⏎ `EOF` ⏎ `terraform apply` (quote removal in the delimiter) | silent | deny |
| `! git push`, `{ git push; }`, `do git push`, `then git push`, `function f { git push; }` | silent | ask |
| `time -p git push`, `command -p git push`, `exec -a x git push`, `rtk proxy git push --force` | silent | ask / deny |
| `</dev/null terraform apply`, `X=1 >/dev/null git push --force`, `cargo 2>/dev/null publish` | silent | deny |
| `echo x # '` ⏎ `git push --force` ⏎ `# '` (a quote inside a comment) | silent | deny |
| `trap 'git push --force' EXIT` | silent | ask (opaque) |
| `git commit -m "$(cat <<'EOF'` … `Co-Authored-By:` … `EOF` `)"` | ask | deny (Q2) |

What does not change: the precedence (never > counting allow > ask > silence), the gate never
emits `allow`, runner and wrapper expansion, a runner body or `bash -c` string holding `$(…)`
stays opaque, every other row of `DEFAULT_DECISIONS` keeps its verdict.

Out of scope, pre-existing and not loosened here (Q4): brace and glob expansion in a verb
position (`cargo {publish,}`, `cargo publis?` with a file named `publish`), and data-dependent
arithmetic on a variable set outside the command (`[[ $X -eq 0 ]]` with `X` from the
environment).

## Principles check

- Proportionality: the change is large because the parsing path is; it adds no surface; holds.
- Rules before autonomy: **fail closed** — every construct the scanner does not model exactly is
  an error and asks, as today; holds.
- Proof not promises: one test row per bypass, plus a differential test against bash; holds.
- Governance (`docs/01-decisions.md`): 6 holds (asks move, none disappears where a rule could
  match); 18 holds and gets stronger (Q2); 20 holds, see Q3; 22 holds; 0–5, 7–17, 19, 21, 23–28
  not relevant.
- Architecture: plain layering (library profile). New stdlib module `bin/_cobot_shell.py` holds
  the scanner (text → structure, tested alone, like `_cobot_make`); judging stays in
  `cobot-rules`.
- New dependencies: none. `bashlex` (unmaintained, GPL-3.0) and `tree-sitter-bash` (native
  build) rejected: stdlib only in `bin/`.
- Delivery: one branch `feat/gate-substitution`, one PR; tasks below are the commits.

## The model

**Scanner** (`_cobot_shell.scan(command) -> Scan`), one pass, modelled on bash 5.2:

- Quotes: single, double, `$'…'` (backslash escapes inside), backslash outside single quotes.
- Comments: an unquoted `#` at word start (after start, blank, or `;&|()<>`) runs to the end of
  the line and is dropped; never inside `${…}` (brace depth tracked), never after `$` or `{`.
- `$(…)` with nesting; backticks close at the **next unescaped backtick, quotes ignored**
  (bash), and the body, unescaped (`\\`, `` \` ``, `\$`, and `\"` inside double quotes), is
  scanned again; unquoted `<(…)` and `>(…)`.
- Arithmetic: `$((…))` is arithmetic only if the paren depth never falls below 2 before the
  final `))`; otherwise it is `$(` with a body starting `(` (`$((echo A); (git push))`). Inside
  `$((…))`, `((…))` at a command start and `$[…]`, `<<` is a shift, not a here-document, and
  substitutions found inside are judged (`$(( a[$(id)] ))`).
- Here-documents (`<<`, `<<-`, not `<<<`): the delimiter word is read with quote removal, quoted
  if any quote or backslash appears in it (`E"O"F` → `EOF`, quoted); several on one line queue.
  The operator and word go, **the rest of the line stays**, the body lines go. A quoted body is
  data; an unquoted body's substitutions run, so they are judged as *detached* units.
- Redirections (`<`, `>`, `>>`, `>|`, `<>`, `&>`, `&>>`, `N>`, `N>&M`, `<&`, `>&`) no longer
  split a segment: operator and target leave the argv, and the target stays visible to the
  protected-file check. `done < <(find …)` therefore keeps `<(…)` out of a command position.

Each substitution becomes a **hole**: the outer text holds a sentinel (`<n>`,
private-use characters, never NUL, which `Path.resolve` rejects); the hole keeps its span, whether
it is *quoted* (one word) or *split* (zero or more words, globbed), and its scanned body.
`$'…'` makes its token a quoted hole with no body (a computed word: `terraform $'apply'`).

`Scan.error` asks the whole command with `cobot gate: unparseable command (…)` on: an
unbalanced quote; an unclosed substitution, backtick or `${`; the word `case` inside any
substitution body, `<(…)` and `>(…)` included; more than `MAX_SUBSTITUTION_DEPTH` (8) levels; a
sentinel character in the input; a `${…@P}` operator (prompt expansion re-runs `$(…)` held in
a variable's value: `x=$'\x24(git push)'; echo "${x@P}"`, silent today).

**Reserved words and wrapper options** (`strip_wrappers`): drop `!`, `{`, `}`, `do`, `then`,
`else`, `elif`, `if`, `while`, `until` at a segment head, repeatedly; `function NAME` and
`coproc [NAME]` before `{`; `time -p`, `command -p`, `exec -a NAME` / `-c` / `-l`, `rtk proxy`.
A head of `for`, `select` or `case` runs nothing: its words are data, its holes judged by body.
`trap` joins `OPAQUE`.

**Quoted code that bash may still run.** Single-quoted text reaches execution through arithmetic
on a variable (`x='a[$(…)]'; echo $((x))`), `${x@P}`, `PS4` with `set -x`, `printf -v`,
`test -v`, `declare`, `read` and similar. A segment that is an assignment, or whose command is
`printf`, `test`, `[`, `[[`, `((`, `let`, `declare`, `typeset`, `local`, `export`, `readonly`,
`read`, `mapfile`, `readarray`, `set`, `trap`, asks when any of its quoted text holds `$(` or a
backtick. Arguments of other programs (`grep -n "a \`b\` c"`, `git commit -m '…$(x)…'`) stay
data.

**Judging.** Every body (outer, each hole's, each detached one) is a *unit*: split, expanded and
judged with today's rules; an inner unit's verdict carries `via $(…)` and its trace lines end in
`<- $(…)`. The most restrictive verdict of all units wins. A segment with no hole is judged as
today. A segment with a hole, in this order:

1. A `never` rule matching a form with each hole read as one unknown character → **deny**.
2. **Structural hole → ask** (`cobot gate: substitution '…' decides what runs`), whatever any
   allow says, decided from the **command name**, never from `is_opaque` on sentinel text:
   - in the command word (`$(x) arg`, `"$(x)"`, `a$(x)=b cmd`) or a token `strip_wrappers`
     consumed (`timeout $(x) cmd`, `env X=$(x) cmd`: after `env`, `X=…` is an argument and is
     split); the one exception is a hole **after the `=`** of a token matching
     `^[A-Za-z_][A-Za-z0-9_]*=` before the first wrapper, which bash does not split
     (`arr[$(x)]=1` fails the pattern and runs its subscript: structural);
   - in the verb zone of a canonicalised CLI: through the verb for `GLOBAL_OPTIONS` heads
     (`git -C $(x) status`), through group and verb for `CLI_ALIASES` heads, through the first
     verb for `gcloud`, anywhere after `api` for `gh|glab|gt|tea`;
   - anywhere in a segment whose head is in `WRAPPER_PARSERS`, `SHELLS`, `OPAQUE`, `INTERPRETERS`,
     `MAKE_NAMES`, `OPAQUE_SUBCOMMANDS`, or is `mise`, `uv`, `npm`, `pnpm`, `yarn`, `bun`; such a
     segment is not expanded (`bash -c "echo $(x)"` runs the output as code).
3. A `never` rule **viable** → ask, naming the rule.
4. An allow that **covers every value** → silence: an allow that `allow_counts` accepts and that is
   not agent-scoped (today: the owner layer), shaped `<literal>*`, whose literal is a prefix of
   the form's text before its first hole. An agent-scoped allow never
   counts on a segment with a hole (a hole could hold `-c core.pager=…`).
5. An `ask` rule viable → ask, naming it (`cobot gate: substitution '…' could match ask
   Bash(git push*) (default layer)`).
6. Otherwise silence: `cat $(find .claude -type f)`, `git log $(git merge-base main HEAD)`,
   `VIS=$(gh repo view o/r --json visibility -q .visibility)`.

**Viable**, per form: a form without a hole is tested with `fnmatchcase`, as today; a form with
a hole is viable when the rule's literal prefix (up to its first `*`, `?` or `[`) and the form's
literal prefix (up to its first hole) are compatible, one a prefix of the other — a sound
over-approximation of glob intersection. For `gcloud`, whose holes after the first verb are past
the cut, only the cut form is tested, and it holds no hole, so `fnmatchcase` decides: the 63
`gcloud * <verb>*` rows match any text after the verb, and the literal judge's ask on
`gcloud x describe --project delete` is a false positive the hole should not inherit.

**Protected files**: a token holding a hole and a literal `/` or `~` is tested against the
`never` Edit/Write patterns with the hole as `*` (`cat ~/.claude/$(echo settings.json)` asks);
a token that is only a substitution is not resolved, like a variable today (`cat "$F"`).

**Known value (Q2)**: a quoted hole whose body is exactly `cat <<D` ⏎ body ⏎ `D`, with `D`
quoted, or unquoted with no `$`, backtick or backslash in the body, and with no `cat` function
or alias defined in the command, is judged twice: with the body as the word (trailing newlines
removed, `<<-` tabs stripped) and as a plain hole; the stricter verdict wins, so the value can
only turn an ask into a deny.

**Soundness target**, written in the module and in `docs/architecture.md`: *a hole in the
command's words is never silent where some text in its place would change which program runs,
or make a rule match the form that names what runs; a never rule denies only when it matches
whatever the hole holds.* Code reaching execution from a variable's value (arithmetic, `@P`)
is handled by the quoted-code rule and the `@P` error, not by holes.
Known asks it costs: a rule with `*` before a literal anchor (`*x*`) is viable for every hole
(Q1 rewrites the one default row); `terragrunt * apply*` makes every `terragrunt` with a hole ask.

## Stories and acceptance

1. As the owner in auto mode, read-only commands with a substitution run without a prompt.
   Accept: `cobot-rules check` prints `none` for `for f in $(find .claude -type f); do cat "$f";
   done`, `VIS=$(gh repo view o/r --json visibility -q .visibility)`, `git log
   $(git merge-base main HEAD)`, `echo "n=$(wc -c < f)"`, `grep -n "a \`b\` c" f`, `echo
   $((1+2))`, `while read l; do echo "$l"; done < <(find . -name x)`, `gcloud projects describe
   p --project "$(gcloud config get-value project)"`, `cobot-memory journal add "$(cat <<'EOF'`
   … `)"`; parametrised in `tests/test_cobot_rules.py`.
2. As the owner, a substitution never hides what the rules would catch. Accept: one test row
   per case named in *The model* and in the challenger verdict, with verdict and reason.
3. As the owner, the bypasses in *Goal* are closed. Accept: a test row per table line.
4. As the owner, deny paths and agent read lists are unchanged. Accept: `DEFAULT_DECISIONS` and
   the agent-scope tests pass with only the substitution rows updated.
5. As a maintainer, the scanner matches bash. Accept: `tests/test_cobot_shell.py` covers every
   construct and error above. A differential test runs a fixed corpus (story and bypass rows)
   through `env -i PATH=<stubs> bash --norc --noprofile -c` in a fresh `tmp_path`, where `<stubs>`
   holds one logging script for **every** external head in the corpus (so nothing real runs and
   nothing reaches the network; wrapper stubs log their own argv, never exec), and asserts the
   gate is at least as strict on the whole command as the literal judge on every argv logged.
   Its scope is written in the test: it validates the decomposition into external argv only;
   builtin and arithmetic sinks are unit-tested rows. Skipped where bash is absent.
6. Coverage on `bin/` stays ≥ 85 %.

Proof commands (CONTEXT.md verified table): pytest with `--cov-fail-under=85`, ruff check and
format, shellcheck, markdownlint, `claude plugin validate plugins/cobot --strict` and `.`,
`python3 -I scripts/check-plugin.py`, and `cobot-rules check` on the story rows.

## Clarify

- Q1 The default `ask Bash(*cobot-memory learn *--promote*)` starts with `*`, so it is viable for
  every hole and keeps every substitution asking. → a) replace it by `cobot-memory learn
  *--promote*` (paths are basenamed) plus `python3 *cobot-memory learn *--promote*` and `python
  *cobot-memory learn *--promote*` · b) keep it · c) an interpreter-script form in `candidates`
  → recommended: a) → **answer:** a) anchored rows (owner, 2026-11-13)
- Q2 Judge `"$(cat <<'EOF' … EOF)"` also with its text, stricter verdict wins? → a) yes: the
  attribution `never` rows deny heredoc commit and PR bodies instead of asking · b) no →
  recommended: a) → **answer:** a) judge both, stricter wins (owner, 2026-11-13)
- Q3 The pre-existing bypass fixes (first table) → a) this PR, as the first commits · b) a small
  security PR first (decision 20 allows it) → recommended: a), the scanner is the fix for half
  of them and they share tests → **answer:** a) this PR, first commits (owner, 2026-11-13)
- Q4 Brace and glob expansion in a verb position, as computed words → a) a follow-up spec: it
  changes how ordinary globs meet the agents' read lists · b) here → recommended: a) →
  **answer:** a) a follow-up spec; build approved (owner, 2026-11-13)

## Plan

1. T01 `strip_wrappers` reserved words, wrapper options, data segments, `trap` opaque.
2. T02 redirections in `split_segments` (argv without them, targets kept for the protected
   check); the scanner registers a `>(…)` or `<(…)` target as a hole first, so its body is
   judged even when the redirection leaves argv.
3. T03 `_cobot_shell.py` scanner, its tests and the bash differential harness.
4. T04 `judge_bash` on scanned units: the six steps, zones by name, viability, cover, protected
   tokens, known value, errors; substitution rows replaced, bypass rows added.
5. T05 default rule rows (Q1). T06 docs and CHANGELOG.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `strip_wrappers`: reserved words, `function`/`coproc`, `time -p`, `command -p`, `exec -a`, `rtk proxy`, `for/select/case` data; `trap` in `OPAQUE`; rows → pytest `-k "reserved or wrapper"` | gate | auth | — |
| T02 | `split_segments`: redirections leave argv, targets kept for `protected_file_touched`; rows → pytest `-k redirect` | gate | auth | T01 |
| T03 | `bin/_cobot_shell.py` scan, Hole, Scan, errors; `tests/test_cobot_shell.py` + differential harness → pytest on that file | shell | auth | — |
| T04 | `judge_bash` on units with the six steps; rows for every bypass → pytest `tests/test_cobot_rules.py` | gate | auth | T02, T03 |
| T05 | `default.rules` promote rows (Q1); tests → pytest `-k promote` | gate | auth | T04 |
| T06 | `docs/architecture.md`, `docs/configuration.md` (anchor rules on the command word), `docs/02-design.md` §6, CHANGELOG Unreleased; full verified commands | docs | — | T05 |

## Trade-offs

- A hand-written scanner over a parser library: stdlib rule; the price is the explicit model and
  error list above, held to bash by the differential test.
- Zones per canonicaliser and per command name, not derived: each reads fixed positions; a
  comment at `candidates` says a new canonicaliser must add its zone.
- Viability by literal prefixes, not glob intersection: sound, simpler, equal on today's rows.
- Ask on `case` inside a substitution instead of parsing patterns: rare; a wrong close is a
  bypass.

## Challenger verdict

2026-11-13, revision 1: **UNSOUND**. Folded into revision 2:

- BLOCKER single-quoted `$(…)` run by builtins and arithmetic → *Quoted code that bash may still
  run*.
- BLOCKER scanner divergences (comments, backticks ignoring quotes, `$((` depth, `case` in
  `<(…)`, heredoc delimiter quote removal, `<<` as a shift) → *Scanner* and the differential
  test.
- BLOCKER zones decided on sentinel text, `env X=$(…)` → zones by command name, the assignment
  exception only before the first wrapper.
- MAJOR step order cancelled owner allows → never-viable, cover, then ask-viable.
- MAJOR known value spoofable → judged twice, stricter wins, bare `cat <<D` only.
- MAJOR missed bypasses (redirections, `$'…'`, wrapper options, `function`, `coproc`, `trap`) →
  first table, T01, T02; brace and glob → Q4.
- MAJOR every `gcloud` with a hole asks → viability on the cut form; `terragrunt` written down.
- MINOR NUL sentinel → private-use sentinel; protected-file soundness → path-token test; Q2 gain
  → corrected in *Goal*; DP → literal-prefix viability.

Revision 2, second pass: **SOUND WITH CHANGES**, no BLOCKER. Folded into revision 3:

- MAJOR literal-prefix viability made the gcloud cut form ask on every hole → a form without a
  hole is matched with `fnmatchcase`; the claim of equality with glob intersection is dropped.
- MAJOR the differential test was blind to builtin sinks and ran real binaries → stub for every
  corpus head, empty `PATH`, `env -i`, fresh directory; its scope is stated and builtin sinks
  stay unit rows.
- MINOR assignment exception keys on the hole's position after `=` (`arr[$(x)]=1` structural);
  `${…@P}` is an error and the soundness sentence covers the command's words only; step 4
  follows `allow_counts`; T02 registers `<(…)`/`>(…)` targets before dropping redirections.

## Converge

pending
