# Spec — outward and account commands, every ask named, shell writes (findings F-36, F-40, F-44)

size: medium-large · profile: library · owner: YpNo · date: 2026-11-17 · revision 2 (challenger
pass folded) · built on `main` `7cb4fa5` (docs tidy merged as PR 70)

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
| F-44 | `cat > a.md <<'EOF'` · `cat >> src/lib.rs <<'EOF'` · `printf x > a.txt` · `echo x >> .agent/JOURNAL.md` · `tee a.txt <<< x` · `{ echo a; } > f` · `echo x \| dd of=f` · `patch -p1 <<'EOF'` | none | deny |
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
- command output to a file (`cargo metadata > m.json`, also inside `cargo metadata > m.json && echo done`);
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
- **Delivery:** one branch `security/gate-f36-f40-f44`, one PR; the tasks below are the commits.
  T01 is a live bypass fix that could ship alone (see Converge).

## Stories and acceptance

0. **Existing rows reach their commands.**
   - For `gh`, `glab`, `gt` and `tea`, a reading drops `-R`, `--repo[=]` and `--hostname`
     wherever they stand after the group word.
   - `CLI_ALIASES` gains a `gh` entry, taken from the ALIASES sections of `gh <group> --help`
     (gh 2.103): `new` for `create` and `remove` for `delete` per group, `ext`/`extensions` for
     `extension`, `cs` for `codespace`, and the rest the help names.
   - `fd -x/-X/--exec/--exec-batch`, `parallel` and `watch` are unwrapped like `find -exec`.
   - Accept: the story-0 rows match the same row as their plain forms; one test per CLI and runner.
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
6. **Shell writes are refused.** Text the agent writes into a file through the shell is denied
   with `WRITING_SCRIPT`'s reason (use Edit or Write), wherever the file is.
   - **Exempt** after the path is normalised: exactly `/dev/null`, `/dev/stdout`, `/dev/stderr`,
     `/dev/tty` and `/dev/fd/N`. Nothing else under `/dev`, `/proc` or `/sys` (`/dev/tcp/…` sends
     the text out).
   - **A literal source:** a here-document, a here-string, or an `echo`/`printf` stage.
   - **Denied:** a pipeline whose non-interpreter stage is fed by a literal source and that writes a
     file, through:
     - a redirection owned by the pipeline, an enclosing group, subshell or loop, or an earlier
       `exec` redirection;
     - `tee`'s file operands, `dd of=`, or `sponge`.

     `-` counts as no file operand.
   - **Also denied:**
     - `patch`, `git apply`, `ed` and `ex` fed by a here-document;
     - in-place editors: `sed`/`gsed` `-i`/`--in-place` (suffix and combined flags), `awk`/`gawk`
       `-i inplace`/`--include=inplace`, and `ruby -i`.
   - Accept: the F-44 rows deny; the "silent and unchanged" rows stay silent, the compound with
     `&& echo done` included.
   - `bash -c 'cat > f <<EOF …'`, `distrobox enter b -- sed -i …` and `fd -X sed -i …` deny.
7. **Both runtimes.** Under agy, `run_command` reaches the same judgement.
   - Accept: one agy test per story through `judge_plan`.
   - `scripts/sync-agents.py --check` and `check-plugin` pass.

## Clarify

Asked 2026-11-16 in one call; the owner took every recommended default.

- **Q1** Literal shell writes and in-place editors: a) deny, any file except `/dev` · b) deny in
  the project only · c) ask. **Answer:** a). The fold narrows "except `/dev`" to five exact paths
  (challenger 7): stricter, in the answer's direction.
- **Q2** Forge-CLI deletions: a) never, like `gh api -X DELETE` · b) ask. **Answer:** a).
  `glab ci delete` and the `tea` deletions move from ask to never.
- **Q3** Which git config calls ask: a) global/system writes plus local exec keys · b) global
  writes only · c) every global call. **Answer:** a).
- **Q4** Commands that print a credential: a) ask · b) never · c) leave silent. **Answer:** a).

## Plan

1. **Readings, aliases, runners (story 0).**
   - `readings()` gains the `-R`/`--repo`/`--hostname` drop for `API_CLIS` after the group word.
   - `CLI_ALIASES["gh"]` comes from gh 2.103's help, dated in a comment.
   - `fd` exec options, `parallel` and `watch` join the unwrapped runners.
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
5. **git config canonical form:** `canonical_git_config` beside `canonical_gh_api`.
   - It uses a full option table. These take a value: `-f`/`--file`, `--blob`, `--comment`,
     `--default`, `--type`, `--value`, `--url`.
   - It scans the scope over all of argv, and an assignment prefix `GIT_CONFIG*` or `GIT_DIR`
     means `--file`.
   - It reads both syntaxes:
     - the old one: `--get*`, `--list`, `-l` and a single key are reads; `--unset*`, `--add`,
       `--replace-all`, `--edit`, `-e`, `--rename-section`, `--remove-section` and key plus value
       are writes;
     - the new one (git 2.46+): `get`, `list`, `set`, `unset`, `edit`, `rename-section`,
       `remove-section`.
   - It emits `git config <scope> <read|write> <key> <value>`, with `--local` when no scope is
     given.
   - Exec keys, matched case-insensitively:
     - by suffix family: `.cmd`, `.command`, `.program`, `.helper`, `.driver`, `.textconv`, `.path`,
       `.editor`, `.pager`;
     - named keys: `core.hooksPath`, `core.fsmonitor`, `core.sshCommand`, `core.gitProxy`,
       `core.alternateRefsCommand`, `core.worktree`, `core.askPass`, `pager.*`,
       `remote.*.uploadpack|receivepack`, `protocol.*.allow`, `url.*.insteadOf`, `sendemail.*`,
       `interactive.diffFilter`, `submodule.*.update`, `filter.*.*`, `include.path`,
       `includeIf.*.path`;
     - `alias.*` whose value starts with `!` or `-`.
   - Docs: an owner allow line must name the canonical form (`git config --global write …`).
6. **Shell writes.** `_cobot_shell.py` records, per pipeline:
   - the writes it owns: its own redirections, plus those of the group, subshell or loop around it,
     plus earlier `exec` redirections;
   - its here-documents and here-strings (here-strings are not recorded today), and its stages.

   `writes_by_shell(segment, unit, holes)` reads these, beside `writes_by_script`: same deny, same
   reason, one call site.
7. **Tests that change, named up front** (challenger 13):
   - `test_judgeBash_ruleBackedAskAfterOpaque_reportsTheRule` gains the list.
   - The protected-file cases written as `cat >`, `printf >` or `echo >` (lines 54, 55, 58, 59, 60,
     3647, 3789, 3822 on `7cb4fa5`) are rewritten with `cp` or command output, so they keep testing
     the protected-file check. The write forms gain their own deny tests.
8. **Docs:** `docs/configuration.md` (what asks, what is refused, what stays silent and why,
   canonical forms for allow lines), CHANGELOG, findings (below).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | story 0: `-R`/`--repo` readings, gh aliases, fd/parallel/watch unwrapped; tests for existing rows (live bypass) | a | auth | — |
| T02 | F-40: every ask named, budget minus stamp, agent-scoped first; tests incl. agy (stories 5, 7) | a | auth | T01 |
| T03 | git config canonical form, option table, env prefixes, exec families; tests (story 3) | a | auth | T02 |
| T04 | rows: outward and account, credential printers, gcloud verbs, deletions in never; note lint; parity and sync tests (stories 1, 2, 4) | a | auth | T03 |
| T05 | scanner ownership per pipeline; shell writes and in-place editors denied; protected-file tests rewritten (story 6) | a | auth | T04 |
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
- **Ownership in the scanner over a whole-command test:** a whole-command test either denies
  `cargo metadata > m.json && echo done` or misses `{ echo a; } > f`. Per-pipeline data is the
  only reading that gets both right.
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

**2026-11-16: UNSOUND** (2 BLOCKER, 8 MAJOR, 7 MINOR). The challenger said that, with its folds,
F-36 and F-40 would be SOUND WITH CHANGES. Revision 2 folds every point below. The reworked
story 6 (scanner ownership) has not been challenged again: second pass not run.

| # | level | point | fold |
|---|---|---|---|
| 1 | BLOCKER | writes and here-docs are whole-command data; here-strings are not recorded | Plan 6, story 6 |
| 2 | BLOCKER | `-R`/`--repo` after the group word bypasses every gh/glab row, never rows included (verified live) | story 0, T01 |
| 3 | MAJOR | gh built-in aliases (`pr new`, `secret remove`, `ext`, `cs`) are not rewritten (verified live) | story 0 |
| 4 | MAJOR | gcloud verb sets lack `set`, `print-access-token` and others; rows with no star never match | Plan 3 |
| 5 | MAJOR | git config grammar: value options, `-f`, scope anywhere, `GIT_CONFIG` env | Plan 5, story 3 |
| 6 | MAJOR | exec keys incomplete; an alias starting with `-` sets config | Plan 5 families |
| 7 | MAJOR | the `/dev`, `/proc`, `/sys` prefix exemption is escapable (`/proc/self/root`, `/dev/tcp`) | story 6, five exact paths |
| 8 | MAJOR | closed lists of sources and writers; patch, git apply and ed as a fallback | story 6, generalised |
| 9 | MAJOR | fd, parallel and watch not unwrapped (verified live) | story 0 |
| 10 | MAJOR | credential rows depend on argument order; printers missing | Plan 4, story 4 bounded |
| 11 | MINOR | the stamp suffix eats the F-40 budget | story 5 |
| 12 | MINOR | `via`, long notes, and the protected-file ask outside the list | story 5 |
| 13 | MINOR | existing tests change unannounced | Plan 7 |
| 14 | MINOR | `rustup … list` would ask | Plan 3, per verb |
| 15 | MINOR | `npm set`, pnpm, yarn, pip3; tea deletions | Plan 3, Q2 |
| 16 | MINOR | the consult-fan-out grader would stop seeing the agent-scoped ask | story 5 |
| 17 | MINOR | the greedy rule regex takes a `)` in a note into the pattern | story 1, note lint |

Checked clear by the challenger: `sync` renders the never rows; precedence holds; the read-only
agents' allows cover none of the new rows; `bash -c`, `distrobox`, `find -exec`, `timeout` and
`nice` unwrap; the commit-message substitution stays silent; agy reaches `judge_bash`.

## Converge

pending
