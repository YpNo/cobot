# Spec — the gate judges brace and glob expansion by what bash runs

size: medium · profile: library · owner: YpNo · date: 2026-11-13 · revision 3 (two challenger passes folded) · follow-up of
`gate-substitution.md` Q4, built on `feat/gate-substitution`

## Goal

`judge_bash` in `plugins/cobot/bin/cobot-rules` reads unquoted `{a,b}`, `*`, `?` and `[…]` as
literal text, but bash expands them before it runs the command. All of these are **silent
today** (`cobot-rules check`, owner layer off, 2026-11-13):

| command | bash runs | today | after |
|---|---|---|---|
| `cargo {publish,}` | `cargo publish` | silent | deny |
| `terraform {apply,}` · `{terraform,} apply` | `terraform apply` | silent | deny |
| `git push origin {main,--force}` | `git push origin main --force` | ask | deny |
| `cargo publis?` · `cargo publi[s]h` (a file named `publish`) | `cargo publish` | silent | ask |
| `cat ~/.claude/settings.js?` · `echo x > ~/.claude/settings.js?` | a protected file | silent | ask |
| `git log *` as `@consultant` (a file named `-c` or `--output=x`) | `git log -c …` | silent | ask (Q2) |
| `cargo +(publish)` · `!(zzz) apply` (bash with `extglob` on) | a command word from file names | silent | ask |
| `uv run --with * publish` (files `aa`, `cargo`) | `uv run --with aa cargo publish` | silent | ask |

After this change brace expansion, which depends only on the text, is computed exactly, as bash
does, and the gate judges the words bash will run. Pathname expansion depends on the files present
when the command runs, so each glob becomes a **glob hole**, judged like a split substitution hole:
a structural ask in the command word or verb zone, a viability ask in the tail.

What does not change: the precedence, the gate never emits `allow`, every row of
`DEFAULT_DECISIONS`, substitution holes, and these stay silent: `ls *.py`, `git add src/*`,
`find . -name '*.py'`, `mkdir -p src/{a,b}`, `cp f{,.bak}`, `uv run pytest tests/test_*.py`,
`gh api repos/o/r/pulls?state=all`, and for `@consultant` and `@learner` `ls plugins/*/agents`,
`cat src/{a,b}.rs`, `ls {src,tests}`, `grep -rn x --include=*.py .`.

Out of scope, pre-existing: a variable in the verb position (`cargo $V`, silent today, a
substitution spec non-goal); a relative protected name without `/` (`cat settings.json` from
`~/.claude`); the `@consultant` read list admitting `find . -delete` and `find . -fprint x`
(literal, no glob involved: finding F-21); text inside an unquoted `${…}` operator word, which
agent-scoped allows never see and bash globs (`${x:---kubeconfig=./evil}`, `find ${x:-*}`:
finding F-22).

## Principles check

- Proportionality: medium, one parsing path, no new surface; holds.
- Rules before autonomy: fail closed — an `extglob` group and an over-large brace expansion
  are scanner errors and ask; holds.
- Proof not promises: a row per table line, the differential test gains the brace and glob rows
  and an agent-scoped pass; holds.
- Governance (`docs/01-decisions.md`): 6 holds (asks are added; no default row holds `{`, so
  none is lost to expansion); 20 holds (one PR, stacked on `feat/gate-substitution`); 22 holds;
  28 holds (an unanchored glob can no longer smuggle an option past an agent-scoped read list;
  `${…}` words still can, F-22); 0–5, 7–19, 21, 23–27 not relevant.
- Architecture: plain layering (library profile). Expansion is read in `bin/_cobot_shell.py`,
  judging stays in `cobot-rules`, as in the predecessor spec.
- New dependencies: none (stdlib only in `bin/`).
- Delivery: one branch `feat/gate-expansion` from `feat/gate-substitution`, one PR after it
  merges; tasks below are the commits.

## The model

**Brace expansion, exact.** In the scanner's `top` and `sub` modes (never inside double quotes,
a here-document, arithmetic or `${…}`, never after `$`), an unquoted `{` opens a brace
expression when a matching unquoted `}` closes it inside the same word (quotes and
substitutions may sit inside, an unquoted blank or operator may not) and it holds an unquoted
top-level `,` or is a sequence `{x..y[..n]}` (integers, optional sign and zero padding, or single
letters). Anything else is literal, as in bash (`{}`, `{a}`, `{a,b`, `stash@{0}`, `{ cmd; }`).
The scanner records each expression as a *brace hole* with its alternatives (each scanned, so a
`$(…)` or a glob inside is a hole of its own); after `split_segments`, so an alternative never
becomes an operator, each token holding one is replaced by the cartesian product of its
alternatives, left to right, nested braces recursively, alternatives unquoted with `shlex`.
Bash globs the words braces build, not the alternatives: `cargo publi{[,x}s{],y}h` builds
`publi[s]h`, and in `settings.[{j],x}son` a bracket swallows the brace. So a word holding both an
unquoted brace expression and an unquoted `[` or `]` is `Scan.error` ("brackets and braces in one
word"); `*` and `?` are one character and stay holes inside an alternative.
Empty words are dropped (bash keeps a quoted empty word; dropping it only moves later words
forward, which is stricter). Words are counted before any is built: more than
`MAX_BRACE_WORDS` (256) in one command is `Scan.error` ("brace expansion too large"), so
`{a,b}{c,d}…` cannot exhaust memory. Over-expansion where bash does not expand (a prefix
assignment `X={a,b} cmd`, inside `[[ … ]]`, a `case` word) yields extra words only. A
redirection target is expanded too; bash refuses a target of more than one word, and checking
each against the protected files is stricter.

**Glob holes.** In the same modes, each unquoted `*` and `?`, and an unquoted `[` with an unquoted
`]` later in the same path component, from that `[` through the **last** unquoted `]` before the
next `/` (bash's bracket rules make `[]j]` and `[[:alpha:]]` one expression, and a bracket never
holds `/`: `~/.claude[/]settings.json` stays literal; the longest span inside a component is
sound without the rules, and stopping at `/` keeps `~/.[c]laude/settings.jso[n]` two holes),
becomes a hole of kind `glob`: `quoted=False`, no body, its span the
glob text, its sentinel in place of the text, so the literal parts stay visible. Not a glob: the
character after `$` (`$*`, `$?`, `$#`, `$@`), an escaped or quoted one, and the bracket of a word
shaped `NAME[…]=` or `NAME[…]+=` **in the assignment prefix before the command word** (an array
assignment; as an argument it globs: `make PYTES[T]="cargo publish" test` meets a file named
`PYTEST=cargo publish` and becomes a make override). The judge applies this exception, which
knows the prefix; the scanner marks the hole. Bash globs no leading `NAME=` value either
(`X=* cmd`): such holes reuse `holes_only_in_assignments` and `prefix_key` (gate-substitution,
`632b072`), so the segment is judged and expanded as one without a hole. An unquoted `?(`, `*(`, `+(`, `@(` or `!(`
anywhere is `Scan.error` ("extended glob"): with `extglob` on each group globs, `!(zzz) hi` at a
command start included; `! (cmd)` with a blank stays the negated subshell. A brace that builds
`$NAME` (`{$,}x`) is a parameter after expansion, the out-of-scope class of `cargo $V`, not
literal text.
`Hole` gains `kind: "substitution" | "glob"` and every reason names it (`glob 'publis?' decides
what runs`, `glob '*' could match ask Bash(git push*) (default layer)`).

A glob hole stands for **zero or more words of existing file names**, so it is a split hole:
`never_anyway`, `structural_key`, `viable`, `covers` and the trace use it unchanged. The
protected-file check reads a glob hole as a wildcard that never matches `/` (a bash glob never
crosses one): `globs_meet` gains that second star, so `git add src/*` and `cp -r assets/* dist/`
do not meet `*/.claude/settings*.json`, while `~/.claude/settings.js?` does. Shell options the
Bash tool's snapshot or the owner's rc may set without the command showing them are assumed on:
`**` is the star that crosses `/` (`globstar` with `dotglob`: `cat ~/**` reads
`~/.claude/settings.json`), and a token holding a glob hole meets the patterns case-insensitively
(`nocaseglob`: `~/.claude/SETTINGS.JSO?`). A substitution hole keeps the crossing `*`; in a token
holding a split substitution hole, a later unquoted `]` widens that star through the `]` (bash
globs the built word: `cat ~/.claude/settings.$(printf '[j')]son` reads `settings.json`, silent
today). Three places differ from a substitution hole, because a glob's words are file names
the command text constrains:

- **Anchored glob.** A glob hole is *anchored* when its token's literal text before the first hole
  is non-empty and either does not start with `-`, `$` or a sentinel, or holds `=` after a
  leading `-` (`src/*`, `./*.py`, `~/x*`, `repos/o/r/pulls?state=all`, `--include=*.py`).
  Every word it yields starts with that text: never an option name, never a variable's value.
- **Agent-scoped allows (Q2).** An agent-scoped allow counts on a segment whose holes are all
  anchored glob holes, when `covers` accepts it and `executes_foreign` does not refuse the
  segment; a substitution hole or an unanchored glob hole still never counts for it (a file
  named `-c` turns `git log *` into `git log -c`, which `executes_foreign` refuses; a file named
  `-delete` turns `find *` into a delete). The reason says so: `glob '*.py' could expand to an
  option; anchor it: ./*.py`. The main thread and owner allows keep step 4 of the predecessor.
- **API zone.** In a `gh|glab|gt|tea api` segment, the whole segment is the zone because a method
  or body flag anywhere changes what runs; an anchored glob hole cannot be a flag, so it is not
  structural there. In every other whole-segment zone (shells, `OPAQUE`, interpreters, make,
  `WHOLE_WRAPPERS`, opaque segments) any glob hole is structural: it can pick the script, the
  target or the code (`bash scripts/*.sh`, `python3 *.py`).

**Runner expansion through globs.** Three rules, so globs turn runners opaque only where they must:

- `command_parts` accepts glob holes in a runner body (`"lint": "ruff check src/*"`, `bash -c 'ls
  *.py'`, a make recipe) and returns their holes; substitution holes keep the body opaque, as
  today.
- `expand_segments` never expands a runner **resolved by name** (npm, pnpm, yarn and bun scripts,
  make targets, mise tasks) whose own argv holds a glob hole: such runners read options anywhere
  in their argv or paste values into code (`make show X=*` with a file named `X=;echo INJECTED`
  runs `echo INJECTED`; npm reads `--prefix=…` after the script name). The segment stays opaque
  and the glob structural (`npm test -- src/*`, `make test FILES=src/*` ask). A glob inside a
  script body read from disk is unaffected.
- For an **argv runner** (container `exec` and compose `run`/`exec`, `uv run`, `nix … -c`,
  `distrobox … --`, `toolbox run`, `mise exec --`, `npm exec`), `expand_segments` expands a
  segment whose holes are all glob holes only when **every one of them is a word of the inner
  argv** the expander returns, compared token by token, never by searching the joined text. A glob is zero or more words,
  so a hole the runner's parser consumes (an option, an option's value, a container, service or
  box slot) can shift every later word: `uv run --with * publish`, with files `aa` and `cargo`,
  runs `cargo publish` while `expand_uv` reads `*` as `--with`'s value and judges `publish`. Such
  a segment is not expanded; it stays opaque, a whole zone, and any glob in it is structural (the
  rule above, now reached). A hole in the inner command word is structural there. The expanders build their output with `shell.join(tokens)`, which quotes each literal
  piece and leaves issued sentinels bare, and `scan(text, issued)` accepts exactly the sentinels
  in `issued` and keeps their holes (a sentinel in the owner's command is still an error). A
  runner body read from disk (package.json script, Makefile recipe, mise task) is checked for the
  reserved characters before extra arguments are joined on, so a planted sentinel there is an
  error, not an issued hole.
  Hole keys stay unique across a command and its expansions (one counter).

**Soundness target**, amended in the module and in `docs/architecture.md`: *a hole in the
command's words — a substitution or a glob — is never silent where some text in its place, for a
glob some set of file names, would change which program runs or make a rule match the form that
names what runs; brace expansion is computed, not approximated.*

Known asks it costs, written in `docs/configuration.md`: every interpreter (`python`, `python3`,
`node`, `deno`, `ruby`, `perl`, `php`) with any glob, a whole zone (`node --test test/*.js`, as
`node --test test/$(echo x).js` today), and for `python`/`python3` also the promote rows, viable
for every hole after `python3 `; `terragrunt` with any glob; a glob in a code-reader segment; a
runner whose own options or slots hold a glob; a runner resolved by name with any glob in its
argv; `if !(grep -q x f)` (valid without `extglob`, the error); `ls ~/.claude/*` (the protected-file check, as for
`$(…)`); an unanchored glob under an agent scope (Q2); `kubectl get pods x*` under an agent
scope (the agent `never kubectl get *[sS][eE][cC][rR][eE][tT]*` rows are viable); `[[ $x ==
@(a|b) ]]`, valid without `extglob` (the error); a word mixing braces and brackets; `echo
{1..300}` (the cap).

## Stories and acceptance

1. As the owner, a brace expression never hides a ruled command. Accept: `cobot-rules check`
   denies `cargo {publish,}`, `terraform {apply,}`, `{terraform,} apply`, `git push origin
   {main,--force}`, `git {push,} --force`; rows in `tests/test_cobot_rules.py` (`-k brace`).
2. As the owner, a glob in a command word or verb zone asks. Accept: `cargo publis?`,
   `cargo publi[s]h`, `terraform appl*`, `/usr/*/git push`, `*`, `uv run car* publish` ask with a
   `glob '…' decides what runs` reason; `uv run --with * publish`, `docker compose exec * x`
   ask (a glob the runner's parser consumes), as do `make show X=*`, `npm test -- src/*`
   (a runner resolved by name); `cargo +(publish)`, `!(zzz) apply`,
   `cargo publi{[,x}s{],y}h` ask as unparseable (`-k glob`).
3. As the owner, ordinary globs and braces stay silent. Accept: every *after: silent* command in
   *Goal*, plus `echo [WARN]`, `for f in *.md; do wc -l "$f"; done`, `[[ $x == *y* ]]`,
   `git stash show stash@{0}`, `npm test` with a script holding `src/*` (fixture package.json).
4. As the owner, agents keep their read lists. Accept: the `@consultant` and `@learner` silent
   rows of *Goal* stay silent; `ls *.py`, `find *`, `git log *` ask with the anchor reason;
   `ls $(echo x)` still asks; the agent-scope tests pass unchanged (`-k agent`).
5. As the owner, protected files are not reached by a glob. Accept: `cat ~/.claude/settings.js?`,
   `echo x > ~/.claude/settings.js?`, `cp x ~/.claude/{settings.json,y}`, `cat
   ~/.claude/settings.[]j]son`, `cat ~/.claude/settings.j[[:alpha:]]on`, `cat
   ~/.[c]laude/settings.jso[n]`, `cat ~/**`, `cat ~/.claude/SETTINGS.JSO?`, `cat
   ~/.claude/settings.$(printf '[j')]son` ask, while `git add src/*` and `cp -r assets/* dist/`
   stay silent (`-k protected`).
6. As a maintainer, the scanner matches bash. Accept: `tests/test_cobot_shell.py` covers brace
   alternatives, nesting, sequences (letters, padding, step), quoting inside braces, the literal
   cases, the cap, the brace-and-bracket error, glob kinds and the longest bracket span, `$*`,
   the array-assignment exception (prefix only), the `extglob` errors, the issued-sentinel
   pass-through and a planted sentinel in a runner body; `tests/test_gate_differential.py`
   gains the brace and glob rows (files created with `: > publish`, `: > aa`, `: > cargo`, a
   Makefile and `: > 'X=;cargo publish'` inside the fresh directory, so `uv run --with *
   publish`, `make show X=*`, `cargo publis?` and `terraform {apply,}` can fail it; `make` runs
   for real there, its recipe reaching only stubs), stubs for each new head (`cargo`, `uv`, `mkdir`, `cp`), a pass under `bash -O
   extglob` (`: > publish; cargo +(publish)`, `: > echo; !(zzz) apply`), and a pass under
   `agent="consultant"` (`: > ./-c; git log *`, `ls plugins/*/agents`, …). Rows the oracle cannot
   see are unit rows instead, said in the test: `find *` with a `-delete` file (the literal judge
   allows `find -delete` for `@consultant`, F-21), redirection targets of builtins (`echo x >
   …` logs nothing). Skipped where bash is absent.
7. Coverage on `bin/` stays ≥ 85 %.

Proof commands (CONTEXT.md verified table): pytest with `--cov-fail-under=85`, ruff check and
format, shellcheck, markdownlint, `claude plugin validate plugins/cobot --strict` and `.`,
`python3 -I scripts/check-plugin.py`, and `cobot-rules check` on the *Goal* rows.

## Clarify

- Q1 Braces: computed exactly, or a split hole like a glob? → a) exact: denies where a `never`
  row applies, no false ask (`ls {src,tests}` for an agent, `uv run pytest tests/{a,b}.py`), costs
  a word pass and the cap · b) a split hole: one model for both, `cargo {publish,}` asks instead
  of denying, an agent's `ls {src,tests}` asks (unanchored) → recommended: a), brace expansion is
  a pure function of the text and the scanner's rule is "model exactly or ask" →
  **answer:** a) exact (owner, 2026-11-13)
- Q2 An unanchored glob (`ls *.py`, `grep -n x *`, `find *`) under `@consultant` or `@learner` →
  a) ask with the anchor reason, and the two agent prompts say "anchor a glob: `./*.py`" · b)
  count when the payload's `cwd` holds no entry whose name starts with `-` and no segment
  changes directory (a race with a concurrent writer stays) · c) count, as today (a hostile
  repository's `-delete` file reaches `find *`) → recommended: a), deterministic and the prompts
  make it rare → **answer:** a) ask with the anchor reason and the prompt line (owner,
  2026-11-13)

## Plan

1. T01 scanner: brace holes with exact expansion and the cap, glob holes, `extglob` errors,
   `Hole.kind`, `shell.join`, `scan(text, issued)`, one key counter.
2. T02 judging: brace words after `split_segments`, kind-aware reasons, anchored globs for
   agent-scoped allows (Q2), the API-zone exception, the prefix-only array exception, protected
   glob tokens and targets with the slash-bound star in `globs_meet`.
3. T03 expansion: `command_parts` with glob holes, name-resolved runners never expanded over a
   glob in their argv (`npm run te*`, `make t*` included), argv runners only when every glob hole is an inner argv word, expanders on `shell.join`,
   runner bodies checked for reserved characters.
4. T04 differential rows and the agent pass. T05 agent prompts (Q2 a). T06 docs and CHANGELOG.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `_cobot_shell.py`: brace holes, exact expansion helper, `MAX_BRACE_WORDS`, brace-and-bracket error, glob holes (longest bracket span), `extglob` error, `kind`, `join`, `issued`; rows → pytest `tests/test_cobot_shell.py` | shell | auth | — |
| T02 | `cobot-rules`: brace words in `split_segments` callers, reasons by kind, anchored rule in `judge_holed`, API-zone exception in `structural_key`, prefix-only array exception, slash-bound star (and `**` crossing, case-insensitive) in `globs_meet` for protected tokens, the `]` after a substitution; rows → pytest `-k "brace or glob or protected or agent"` | gate | auth | T01 |
| T03 | `cobot-rules`: `command_parts`, `expand_segments` (name-resolved runners not over a glob; argv runners when every glob hole is an inner argv word), expanders on `shell.join`, reserved characters in runner bodies; rows → pytest `-k "runner or launcher or make or mise"` | gate | auth | T02 |
| T04 | `tests/test_gate_differential.py`: brace and glob rows, file setup, new stubs, `-O extglob` pass, agent pass, scope note for unit-only rows → pytest on that file | tests | — | T03 |
| T05 | `agents/consultant.md`, `agents/learner.md`: one line on anchoring globs (Q2 a) → `python3 -I scripts/check-plugin.py` | agents | — | T02 |
| T06 | `docs/architecture.md` (soundness target), `docs/configuration.md` (known asks, anchoring), `docs/02-design.md` §6, CHANGELOG Unreleased; full verified commands | docs | — | T04, T05 |

## Trade-offs

- Exact braces over a brace hole (Q1): more code in the scanner, but exact verdicts and no false
  ask; the cap is the price of computing.
- Globs as holes over reading the directory: the gate runs before the command, which can create
  the file it globs (`: > publish; cargo publis?`); a hole is right whatever the files are.
- Anchoring by the literal prefix over per-command option tables: one rule for every read-list
  head; the cost is an ask on `ls *.py` under an agent (Q2).
- `extglob` as an error over parsing its groups: rare in commands, and a wrong close is a bypass.
- Viability unchanged (literal prefixes): a glob's file names may hold blanks, and forms join
  words with blanks, so a tighter test would be unsound against the differential oracle. The
  protected-file check can bind its star at `/` because it tests one token, a path.
- Errors over modelling for brace-and-bracket words and `extglob`: both rare, both places where
  a near-miss model is a bypass.

## Challenger verdict

2026-11-13, revision 1: **SOUND WITH CHANGES** (one BLOCKER; every scenario run under bash
5.2.37). Folded into revision 2: runner expansion read a glob as one word, `uv run --with *
publish` silent (BLOCKER) → glob holes must reach the inner argv; bash globs the words braces
build (`cargo publi{[,x}s{],y}h`) → brace-and-bracket error; the first `]` closed a bracket
(`settings.[]j]son`) → longest span; `!(` globs at a command start under `extglob` → error
everywhere; the protected `*` crossed `/` (`git add src/*` would ask) → slash-bound star;
`${…}` words reach agent allows (pre-existing) → claim on 28 corrected, F-22; MINOR: `NAME[…]=`
exception prefix only, unit rows and a `-O extglob` pass where the oracle is blind, known asks
completed, reserved characters checked in runner bodies.

Revision 2, second pass: **SOUND WITH CHANGES** (two BLOCKERs from the folds). Folded into
revision 3: runners resolved by name read options anywhere or paste values into code (`make
show X=*` with a file `X=;echo INJECTED`) → never expanded over a glob in their argv, argv
runners compared token by token; the longest bracket span swallowed a `/`
(`~/.[c]laude/settings.jso[n]`) → a span ends before `/`; `globstar` and `nocaseglob` may be on
unseen → `**` crosses `/`, case-insensitive protected match; a substitution's `[` meeting a
literal `]` (pre-existing) → the `]` widens the star; MINOR: a brace building `$NAME` is out of
scope like `cargo $V`, `if !(grep …)` is a known ask.

## Converge

pending
