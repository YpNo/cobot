# Spec — outward and account commands, every ask named, shell writes (findings F-36, F-40, F-44)

size: medium-large · profile: library · owner: YpNo · date: 2026-11-17 · revision 3 (two
challenger passes folded) · T02–T06 built on `main` `b972f61` (T01 merged as PR 71)

## Goal

Close the three gate findings from the 2026-11-15 dogfood sessions (curriculo, ha-manager), in
both runtimes. The challenger found that the parsing beneath them also lets existing rows be
bypassed; that is fixed first (story 0). Measured 2026-11-16/17 with `cobot-rules check` and an
empty owner and project layer:

| # | command | today | after |
|---|---|---|---|
| 0 | `gh release -R o/r create v1` (a never row) · `gh pr -R o/r create` · `glab mr -R x merge 1` | none | as without `-R` |
| 0 | `gh pr new` · `gh issue new` · `gh secret remove X` · `gh ext install x/y` · `gh cs delete` | none | as the canonical verb |
| 0 | `fd -x sh -c 'git push'` · `fd -X sed -i …` · `parallel …` · `watch git push` | none | the inner command judged |
| F-36 | `gh auth setup-git` · `gh secret set X` · `gh variable set X` · `gh repo edit --visibility public` · `gh repo create x` · `gh workflow run ci.yml` · `gh run rerun 1` · `gh extension install x/y` | none | ask |
| F-36 | `rustup update` · `rustup default stable` · `rustup toolchain install 1.99` · `gcloud config set project x` · `npm login` · `npm config set x y` · `npm set x y` | none | ask |
| F-36 | `git config --global user.name x` · `git config -f ~/.gitconfig user.email x` · `git config core.hooksPath .h` · `git config core.hooksPath .h --local` · `GIT_CONFIG=~/.gitconfig git config user.email x` | none | ask |
| F-36 | `git config --global --get user.name` · `git config --list` · `git config user.name` · `rustup toolchain list` | none | none |
| F-36 | `gh auth token` · `gh auth status --json hosts --show-token` · `gcloud auth print-access-token --account a` · `gcloud secrets versions access latest --secret s` · `git credential fill` | none | ask |
| F-36 | `gh release delete v1` · `gh secret delete X` · `gh label delete x` · `gh cache delete x` | none | deny |
| F-36 | `glab ci delete 1` · `tea releases delete v1` | ask | deny |
| F-40 | `git rebase main && git push origin x && git commit -m y` | ask, reason names `git rebase*` only | ask, reason names all three |
| F-44 | `cat > a.md <<'EOF'` · `cat >> src/lib.rs <<'EOF'` · `printf x > a.txt` · `echo x >> .agent/JOURNAL.md` · `tee a.txt <<< x` · `echo x \| dd of=f` · `patch -p1 <<'EOF'` · `jq -rn x > f` | none | deny |
| F-44 | `{ echo a; } > f` · `printf x \| { cat > f; }` · `ssh h <<'EOF' > out` | none | ask |
| F-44 | `sed -i s/a/b/ f.txt` · `sed -i.bak …` · `awk -i inplace 1 f` · `ruby -pi -e … f` | none | deny |

Already asking or denied and unchanged:
- `gh pr create|merge|comment|review`, `gh issue create|comment`, `gh api` with a write method or
  a body flag, `git push`, the install routes of decision 29;
- `gh repo delete`, `gh api -X DELETE` and `gh release create`, without `-R` (never);
- `python3 -c` and `perl -i` writes (PR 61);
- the attribution trailer (decision 18).

Silent and unchanged:
- `gh auth status`, `gh secret list`;
- `git config --get`, `git -c k=v <cmd>` (the gate already judges `-c`);
- command output to a file (`cargo metadata > m.json`, also beside `echo done` in either order);
- `cat a b > c`, `cp`, `mv`;
- `git commit -m "$(cat <<'EOF' … EOF)"` (a here-document read by a substitution, no file written).

## Principles check

- **Proportionality:** medium-large. Two modules: `cobot-rules`, and `_cobot_shell.py` for the
  per-pipeline ownership of writes (challenger 1). Plus the default layer and the tests. Holds,
  as one topic: what the gate cannot see or name today.
- **Rules before autonomy:** every change adds an ask or a deny, or makes an existing row reachable;
  nothing is silenced. Holds.
- **Proof, not promises:** each Goal row becomes a test, in both runtimes. A bypass-aimed review
  follows the build, as for every gate spec.
- **Governance** (`docs/01-decisions.md`):
  - decision 18 (attribution) holds, unchanged;
  - decision 22 (new dependencies) holds: none;
  - decision 28 (read-only agents): the read list is unchanged, and the new rows ask for those
    agents too;
  - decision 29 (install routes ask): extended to `rustup`, holds;
  - decisions 20 and 21 hold;
  - the others are not relevant.
- **Architecture:** plain layering, as for gate-f33-f34:
  - in `cobot-rules`: readings, aliases, canonical forms, one check beside `writes_by_script`;
  - in the scanner: ownership data;
  - rows in `default.rules`.
- **New dependencies:** none.
- **Delivery:** T01 shipped alone (PR 71, a live bypass fix). T02–T06 are the commits of one
  branch `security/gate-asks-and-writes`, one PR.

## Stories and acceptance

0. **Existing rows reach their commands.** Built as T01 (PR 71; details in its body, the
   CHANGELOG and `docs/configuration.md`): cobra readings of options before a gh/glab group or
   verb, gh's built-in aliases (gh 2.103), a literal `;` kept a word, `fd -x` bodies and clusters,
   more opaque runners, `busybox` unwrapped, gh user aliases and extensions ask. `gt` and `tea`
   option placement is unchecked; `watch git status` asks, like any `xargs`.
1. **Outward and account commands ask.** A command that changes the forge account, a
   repository's settings, CI state or the machine's global tool configuration asks.
   - Accept: every F-36 "ask" row.
   - Each row carries a `# note` without `)`: the rule regex is greedy, so a `)` in a note joins
     the pattern. A test asserts no default row's note holds one.
   - `rustup` rows are per verb, so `list` stays silent.
2. **Forge deletions are refused.** Deletion through a forge CLI joins `gh repo delete` and
   `gh api -X DELETE` in the never tier, for `gh`, `glab`, `gt` and `tea` alike.
   - Accept: the F-36 "deny" rows, in both their plain and `-R` forms.
   - `cobot-rules sync` renders them in `permissions.deny`.
3. **git config asks only for writes that outlive the session:**
   - a `--global`, `--system`, `--file`/`-f` write, or one with `GIT_CONFIG`,
     `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` or `GIT_DIR` as an assignment prefix;
   - a local or `--worktree` write of a key that runs code later.

   Accept: the git config rows; `git -C x config --global user.email y` asks;
   `git config --comment c core.hooksPath .h` asks; `git config --global --get-all x` and
   `git config get --global x` stay silent; `git config alias.x '!sh'` and
   `git config alias.x '-c core.fsmonitor=y status'` ask; `git config alias.x status` stays
   silent.
4. **Credentials do not reach the transcript silently.** A command that prints a known credential
   asks: the printers listed in Plan step 4, in any argument order, with bundled short flags
   split.
   - Accept: the F-36 credential rows.
   - An owner `allow` line silences one form (tested).
   - The claim is the named printers, not every way a secret can be printed.
5. **Every ask is named.** When several segments ask, the reason names each distinct ask (a rule
   with its `via`, or a ruleless note cut to 40 characters), up to three, then `+N more`.
   - The ask set before the segment loop (a protected-file access) is in the list.
   - One ask keeps today's exact reason, and a deny shows only the deny.
   - For an agent-scoped call, the agent-scoped ask comes first, so `consult-fan-out`'s
     `read-list-only` grader still sees `ask Bash(*) @consultant`.
   - Accept: the F-40 row; a four-ask compound with a `git push` ends `+1 more` and keeps the
     stamp; `cat ~/.claude/settings.json; git push` names both.
   - The budget is `REASON_LIMIT` minus the ` · stamp: …` suffix that `gate()` and `gate_agy()`
     add.
6. **Shell writes are refused, or ask when uncertain.** Text the agent writes into a file through
   the shell is denied with `WRITING_SCRIPT`'s reason (use Edit or Write), wherever the file is. A
   write the gate cannot trace for certain asks, so an owner `allow` line can lift it. The claim is
   the named sources, stages and writers, as story 4 bounds its printers.
   - **Exempt** after normalisation: exactly `/dev/null`, `/dev/stdout`, `/dev/stderr`, `/dev/tty`,
     `/dev/fd/1` and `/dev/fd/2`. Nothing else under `/dev`, `/proc` or `/sys`.
   - **A literal source:** a here-document, a here-string, a process substitution holding one, or an
     `echo`, `printf`, `jq -n` or `awk 'BEGIN{…}'` stage, matched by basename (`/bin/echo`).
   - **Deny**, within one list item (split on top-level `;`, `&&`, `||`, `&`, newline): a pipeline
     holding a literal source and no interpreter stage, whose later stages are all pass-through
     (`cat tee dd sponge tr sed base64 xxd head tail sort uniq cut envsubst`), writing a
     non-exempt file:
     - on fd 1 or `&>`, by its own redirection;
     - or through `tee`'s file operands (`-` is none), `dd of=`, `sponge`, `sort -o`, or
       `cp`/`install` from `/dev/stdin` or `-`.
   - **Ask**, in a command holding a literal source:
     - a stage that is not pass-through before such a write (`ssh h <<EOF > out`);
     - a write owned by an enclosing group, subshell or loop, or by an `exec` in scope;
     - a literal source feeding a nested group, subshell or runner body that writes, or a function
       defined in the command whose body writes.
   - **Also denied:** `patch`, `git apply`, `ed` and `ex` fed by any literal source; in-place
     editors: `sed`/`gsed` `-i`/`--in-place` (suffix and combined flags), `awk`/`gawk`
     `-i inplace`/`--include=inplace`, `ruby -i`, and `yq -i`.
   - **Not claimed:** sed's `w` command, `split`/`csplit`, a source the gate does not name.
   - Accept: the F-44 rows deny or ask as the Goal table says; the "silent and unchanged" rows stay
     silent. `bash -c 'cat > f <<EOF …'`, `distrobox enter b -- sed -i …`, `fd -X sed -i …`,
     `cp /dev/stdin f <<<x` and `printf x | git apply` deny. An owner allow line lifts an ask
     (tested).
7. **Both runtimes.** Under agy, `run_command` reaches the same judgement.
   - Accept: one agy test per story through `judge_plan`.
   - `scripts/sync-agents.py --check` and `check-plugin` pass.

## Clarify

Asked 2026-11-16 in one call; the owner took every recommended default.

- **Q1** Literal shell writes and in-place editors: a) deny, any file except `/dev` · b) deny in
  the project only · c) ask. **Answer:** a). The fold narrows "except `/dev`" to exact paths
  (challenger 7). Pass 2 makes the uncertain cases ask; the plain ones still deny (owner yes,
  2026-11-17).
- **Q2** Forge-CLI deletions: a) never, like `gh api -X DELETE` · b) ask. **Answer:** a).
  `glab ci delete` and the `tea` deletions move from ask to never.
- **Q3** Which git config calls ask: a) global/system writes plus local exec keys · b) global
  writes only · c) every global call. **Answer:** a).
- **Q4** Commands that print a credential: a) ask · b) never · c) leave silent. **Answer:** a).

## Plan

1. **Readings, aliases, runners (story 0):** built, T01.
2. **F-40.** `judge_bash` collects every asking verdict, including the initial protected-file one,
   with its `via`. `Verdict.reason()` composes the first reason, then `; also asks: …` and
   `+N more`, inside a budget the caller passes: `REASON_LIMIT` minus the stamp suffix. When the
   call is agent-scoped, the agent-scoped ask comes first. `judge_plan` composes the same way.
3. **Rows** in `default.rules`, notes without `)`.

   | area | asks |
   |---|---|
   | auth and config | `gh auth login\|logout\|refresh\|setup-git\|switch`; `gh config set`; `gh alias set\|import`; `gh extension install\|upgrade` |
   | repository settings | `gh repo create\|edit\|rename\|archive\|unarchive\|sync`; `gh secret set`; `gh variable set`; `gh label create\|edit\|clone` |
   | CI | `gh workflow run\|enable\|disable`; `gh run rerun\|cancel` |
   | issues and PRs | `gh issue edit\|close\|reopen\|transfer\|pin\|lock`; `gh pr edit\|close\|reopen\|ready` |
   | releases, gists, keys | `gh release edit\|upload`; `gh gist create\|edit`; `gh codespace create`; `gh ssh-key add`; `gh gpg-key add` |
   | other tools | `glab auth login`; `rustup` `update`, `default`, `toolchain install\|uninstall\|link`, `target add\|remove`, `component add\|remove`, `override set\|unset`, `self update\|uninstall`, `set`; `gcloud config set\|unset`, `gcloud auth activate-service-account`; `npm login\|logout\|adduser\|set\|config set\|config delete\|token create`; `pnpm config set`; `yarn config set`; `pip`/`pip3`/`python3 -m pip` `config set\|unset`; `docker logout` |

   - **Never block:** `gh release|secret|variable|label|cache|run|gist|ssh-key|gpg-key|issue
     delete` and `gh repo deploy-key delete`, with the `glab`, `gt` and `tea` deletions.
   - **gcloud:** `set`, `unset`, `activate`, `print-access-token`, `print-identity-token` and
     `config-helper` join the verb sets, so the cut canonical form matches. Each is tested with a
     trailing flag.
4. **Credential printers** (ask, note "prints a credential into the transcript"):
   - `gh auth token`; `gh auth status` with `--show-token` or `-t` anywhere, bundled short flags
     split;
   - `glab auth status` likewise, and `glab config get token`;
   - `gcloud auth print-access-token|print-identity-token`, also under `application-default`;
   - `gcloud secrets versions access`, `git credential fill`, `git credential-<helper> get`,
     `docker-credential-* get`;
   - `kubectl config view --raw`, and `kubectl get secret(s)` with `-o yaml|json|jsonpath|go-template`;
   - `npm token list`.
5. **git config canonical form (built, T03):** `canonical_git_config` emits `git config <scope>
   [<path>] <read|write> [exec] <key> <value>` from both syntaxes, in any order, with git's unique
   abbreviations and short clusters read; an unknown option fails closed (`exec`). Scope comes
   from argv, a `GIT_CONFIG*`, `GIT_DIR` or `GIT_COMMON_DIR` prefix, or `--git-dir`; `export`,
   `local -x`, `set -a` of those variables ask. Exec families as `docs/configuration.md` lists
   them; an alias is `exec` unless it is one read-only verb. An owner allow names that form.
6. **Shell writes.**
   - `_cobot_shell.py` tags each redirection, here-document and here-string (recorded now) with its
     list index and its stack of enclosing `{`, `(` and loop or `if`/`case` openers. That needs the
     reserved words `{ } do done fi esac`, not a full compound-command model.
   - `exec` scope is textual: it ends at a closing `)` or at a substitution, and runs through `}`,
     `done` and `fi` (`{ exec >f; }; echo x` keeps it, `( exec >f ); echo x` does not).
   - One split for both sides: the scanner exports its list items as offsets into `outer`, and
     `cobot-rules` reads stages only within one item.
   - `command_parts` returns each `Part`'s inner `Scan`, and runner entries use it as their unit,
     so a here-document in a `bash -c` body reaches `writes_by_script` and the new check.
   - `writes_by_shell(segment, unit, holes)` sits beside `writes_by_script`, one call site. Its deny
     overrides as today; its ask is judged like a default-layer ask row, so an owner allow lifts it.
7. **Tests that change** (challenger 13, pass 2 point 8):
   - `test_judgeBash_ruleBackedAskAfterOpaque_reportsTheRule` gains the list.
   - Protected-file cases written as `cat >`, `printf >` or `echo >` are rewritten with `cp` or
     command output, so they keep testing that check; the write forms get their own tests.
   - T05 starts by running the suite against a stub deny and records the list here. Pass 2 counted
     26 lines on `b972f61` in the two test files.
8. **Docs:** `docs/configuration.md` (what asks, what is refused, what stays silent and why,
   canonical forms for allow lines), CHANGELOG, findings (below).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | story 0: `-R`/`--repo` readings, gh aliases, fd/parallel/watch unwrapped; tests for existing rows (live bypass) | a | auth | — |
| T02 | F-40: every ask named, budget minus stamp, agent-scoped first; tests incl. agy (stories 5, 7) | a | auth | T01 |
| T03 | git config canonical form, option table, env prefixes, exec families; tests (story 3) | a | auth | T02 |
| T04 | rows: outward and account, credential printers, gcloud verbs, deletions in never; note lint; parity and sync tests (stories 1, 2, 4) | a | auth | T03 |
| T05 | scanner list indexes, openers, `exec` scope, inner scans for runners; shell writes deny or ask; in-place editors denied; changed tests listed then rewritten (story 6) | a | auth | T04 |
| T06 | agy parity sweep, docs/configuration.md, CHANGELOG, findings F-36 and F-40 closed, F-44's gate part closed and its rest re-filed (story 7) | b | — | T05 |

Every code task touches `cobot-rules`, so one lane: sequential commits. **F-44's rest** is not the
gate's; T06 re-files it as one finding for the memory and ship spec:
- commit approvals with no owner allow line offered;
- builder Noticed items never parked;
- `cobot-deps`' Actions hint with no workflows (`_cobot_deps.py:522`);
- ship's global, unpinned installs.

## Trade-offs

- **Deny literal writes everywhere, not only in the tree (Q1):** one rule, no path judgement to
  bypass. Command output to a file stays silent: it is a tool run, which Write cannot replace.
  Where the gate cannot tell the two apart, it asks rather than denies, so no tool run is walled.
- **List indexes and openers over a whole-command test:** a whole-command test either denies
  `cargo metadata > m.json && echo done` or misses `{ echo a; } > f`. Indexes and an opener
  stack get both right without modelling every compound command.
- **Never for deletions (Q2):** rendered into `permissions.deny`, a hard wall in every layer.
- **A canonical form for git config (Q3):** globs cannot tell a read from a write, and git's
  grammar has value-taking options anywhere.
- **Credentials ask (Q4), for named printers:** the claim is bounded on purpose. A new printer is
  one row.
- **F-40 keeps the first reason verbatim:** graders, tests and the owner's habit read it.
- **Story 0 inside this spec, not a separate one:** it is the same "rows that cannot see their
  command" topic, and every new row depends on it. T01 is first, so it can ship alone if the owner
  wants the live bypass closed sooner.

## Challenger verdict

**Pass 1, 2026-11-16: UNSOUND** (2 BLOCKER, 8 MAJOR, 7 MINOR), all folded in revision 2:
write data (Plan 6); `-R`, gh aliases, fd/parallel/watch (story 0, verified live); gcloud verbs,
`rustup list`, npm/pnpm/yarn/pip3, tea deletions (Plan 3); git config grammar, exec keys (Plan 5);
`/dev` prefixes, closed sources (story 6); credential argument order (Plan 4); the F-40 budget,
`via`, protected-file ask, consult grader (story 5); test changes (Plan 7); `)` in notes (story 1).
Checked clear: `sync` renders never rows, precedence, read-only allows, runners, agy's path.

**Pass 2 on story 6, 2026-11-17: UNSOUND, SOUND WITH CHANGES once folded** (5 MAJOR, 3 MINOR).
Each verified point was reproduced on `b972f61`. Revision 3 folds all eight (owner yes):

| # | level | point | fold |
|---|---|---|---|
| 1 | MAJOR | "fed by" never checks that the text reaches the file: `ssh h <<EOF > out` denied, no allow lifts it | pass-through stages, else ask |
| 2 | MAJOR | here-docs in runner bodies dropped: `bash -c` acceptance cannot pass (verified) | Plan 6, inner `Scan` |
| 3 | MAJOR | the scanner has no positions or openers; `exec` scope is not "earlier" (verified) | Plan 6, indexes, openers, one split |
| 4 | MAJOR | literal text into nested groups, process substitution, functions, runners: silent | story 6 asks |
| 5 | MAJOR | sources and writers still closed (`jq -n`, `cp /dev/stdin`, `yq -i`, `git apply` from printf; verified) | story 6, named and bounded |
| 6 | MINOR | `/dev/fd/N` reaches a descriptor the command opened | `/dev/fd/1` and `/2` only |
| 7 | MINOR | `echo x > f` is not a stage "fed by" a source | "holding a literal source" |
| 8 | MINOR | Plan 7's test list is stale and short | Plan 7, listed at T05 start |

Checked clear: `find -exec`/`fd -X` arrive as segments; `timeout`/`env` stripped; `xargs`/`parallel`
ask; a target with a hole fails closed; no cobot skill runs a pattern story 6 refuses.

## Converge

T01 built 2026-11-17 (ab9bb3a, 97b18ef), merged as PR 71. Revision 3 folds pass 2 on story 6. T02
built 2026-11-17 (9465eb9, review folded); T03 built (cb34eda, bypass review's six gaps folded);
T04–T06 pending on `security/gate-asks-and-writes`.
