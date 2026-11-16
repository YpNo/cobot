# Spec — outward and account commands, every ask named, shell writes (findings F-36, F-40, F-44)

size: medium · profile: library · owner: YpNo · date: 2026-11-16 · built on `main` `4288978`
(onboard-environment merged as PR 69)

## Goal

Close the three gate findings from the 2026-11-15 dogfood sessions (curriculo, ha-manager), in
both runtimes. Measured 2026-11-16 on `4288978` with `cobot-rules check`, an empty owner and
project layer:

| # | command | today | after |
|---|---|---|---|
| F-36 | `gh auth setup-git` · `gh secret set X` · `gh variable set X` · `gh repo edit --visibility public` · `gh repo create x` · `gh workflow run ci.yml` · `gh run rerun 1` · `gh extension install x/y` | none | ask |
| F-36 | `rustup update` · `rustup default stable` · `rustup toolchain install 1.99` · `gcloud config set project x` · `npm login` · `npm config set x y` | none | ask |
| F-36 | `git config --global user.name x` · `git config --system x y` · `git config core.hooksPath .h` | none | ask |
| F-36 | `git config --global --get user.name` · `git config --list` · `git config user.name` | none | none |
| F-36 | `gh auth token` · `gcloud auth print-access-token` · `git credential fill` | none | ask |
| F-36 | `gh release delete v1` · `gh secret delete X` · `gh label delete x` · `gh cache delete x` | none | deny |
| F-36 | `glab ci delete 1` | ask | deny |
| F-40 | `git rebase main && git push origin x && git commit -m y` | ask, reason names `git rebase*` only | ask, reason names all three |
| F-44 | `cat > a.md <<'EOF'` · `cat >> src/lib.rs <<'EOF'` · `printf x > a.txt` · `echo x >> .agent/JOURNAL.md` · `tee a.txt <<< x` | none | deny |
| F-44 | `sed -i s/a/b/ f.txt` · `sed -i.bak …` · `awk -i inplace 1 f` · `ruby -pi -e … f` | none | deny |

Already asking or denied and unchanged:
- `gh pr create|merge|comment|review`, `gh issue create|comment`, `gh api` with a write method or
  a body flag, `git push`, the install routes of decision 29;
- `gh repo delete`, `gh api -X DELETE` and `gh release create` (never);
- `python3 -c` and `perl -i` writes (PR 61);
- the attribution trailer (decision 18).

Silent and unchanged:
- `gh auth status`, `gh secret list`;
- `git config --get`, `git -c k=v <cmd>` (the gate already judges `-c`);
- command output redirected to a file (`cargo metadata > m.json`), `cat a b > c`, `cp`, `mv`;
- `git commit -m "$(cat <<'EOF' … EOF)"` (a here-document read by a substitution, no file written).

## Principles check

- **Proportionality:** medium. One module (`cobot-rules`), the default layer and their tests.
  Holds.
- **Rules before autonomy:** every change adds an ask or a deny; nothing is silenced. Holds.
- **Proof, not promises:** each row of the Goal table becomes a test, in both runtimes. A
  bypass-aimed review follows the build, as for the earlier gate specs.
- **Governance** (`docs/01-decisions.md`):
  - decision 18 (attribution) holds, unchanged;
  - decision 22 (new dependencies) holds: none;
  - decision 28 (read-only agents): their read list is unchanged, and the new rows ask for them
    too;
  - decision 29 (install routes ask): extended to `rustup`, holds;
  - decisions 20 and 21 hold;
  - the others are not relevant.
- **Architecture:** plain layering inside `cobot-rules` (a canonical form, a check beside
  `writes_by_script`, rows in `default.rules`), as for gate-f33-f34.
- **New dependencies:** none.
- **Delivery:** one branch `security/gate-f36-f40-f44`, one PR; the tasks below are the commits.

## Stories and acceptance

1. **Outward and account commands ask.** As the owner, a command that changes my forge account,
   a repository's settings, CI state or my machine's global tool configuration asks.
   - Accept: every F-36 "ask" row of the Goal table asks, through `cobot-rules check`.
   - Each row carries a `# note` naming the reach (e.g. "changes the repository's settings for
     everyone").
   - The `gh` verbs and their `glab` and `gt` equivalents are listed in Plan step 2; a verb a CLI
     lacks is skipped.
2. **Forge deletions are refused.** Deletion through a forge CLI joins `gh repo delete` and
   `gh api -X DELETE` in the never tier: GitHub, GitLab and Gitea cannot undo them. The owner runs
   them in their own terminal.
   - Accept: the F-36 "deny" rows deny.
   - `cobot-rules sync` renders them in `permissions.deny`.
3. **git config.** Only writes that outlive the session ask:
   - a `--global`, `--system` or `--file` write;
   - a local write of a key that runs code later.

   Accept:
   - the git config rows of the Goal table;
   - `git -C x config --global user.email y` asks;
   - `git config --global --get-all x` and `git config get --global x` stay silent;
   - `git config alias.x '!sh'` asks and `git config alias.x status` stays silent.
4. **Credentials never reach the transcript silently.** A command that prints a credential
   asks.
   - Accept: the F-36 credential rows ask.
   - An owner `allow` line silences one form (tested).
5. **Every ask is named.** When several segments of one command ask, the reason names each
   distinct ask (rule or ruleless), up to three, then `+N more`. One ask keeps today's exact
   reason. A deny shows only the deny.
   - Accept: the F-40 row; a four-ask compound ends `+1 more`.
   - The count survives `REASON_LIMIT` (200): the first reason's note is shortened first.
   - The single-ask tests and the `consult-fan-out` grader text are unchanged.
6. **Shell writes are refused.** Text the agent writes into a file through the shell is denied
   with `WRITING_SCRIPT`'s reason (use Edit or Write), wherever the file is, except `/dev/*`,
   `/proc/*` and `/sys/*`. Literal text means:
   - `cat` reading a here-document or here-string with no file operand;
   - `echo` or `printf`;
   - `tee` fed by a here-document, a here-string or an `echo`/`printf` stage of its pipeline;

   reaching a file through a redirection or `tee`'s file operands. In-place editors are denied
   too: `sed`/`gsed` `-i` or `--in-place` (attached suffix and combined flags included),
   `awk`/`gawk` `-i inplace` or `--include=inplace`, and `ruby -i`.
   - Accept: the F-44 rows deny; the "silent and unchanged" rows stay silent.
   - `bash -c 'cat > f <<EOF …'` and `distrobox enter b -- sed -i …` deny: the unwrapped inner
     command is judged.
7. **Both runtimes.** Under agy, `run_command` reaches the same judgement.
   - Accept: one agy test per story through `judge_plan`.
   - `scripts/sync-agents.py --check` and `check-plugin` pass.

## Clarify

Asked 2026-11-16 in one call; the owner took every recommended default.

- **Q1** Literal-content shell writes and in-place editors:
  - a) deny, any file except `/dev`;
  - b) deny in the project only;
  - c) ask.

  **Answer:** a). Command output redirected to a file is unchanged.
- **Q2** Forge-CLI deletions:
  - a) never, like `gh api -X DELETE`;
  - b) ask.

  **Answer:** a). `glab ci delete` moves from ask to never.
- **Q3** Which git config calls ask:
  - a) global/system writes plus local exec keys;
  - b) global writes only;
  - c) every global call.

  **Answer:** a).
- **Q4** Commands that print a credential:
  - a) ask;
  - b) never;
  - c) leave silent.

  **Answer:** a).

## Plan

1. **F-40 first**, as it changes no decision. `judge_bash` keeps every segment verdict that asks
   (a distinct rule, or a ruleless note). `Verdict.reason()` composes the first reason plus
   `; also asks: <rule shown> …` and `+N more`. A deny wins unchanged. The same composition serves
   `judge_plan`.
2. **Outward and account rows** in `default.rules`, with notes, in a block after the existing
   forge rows. Parity with `glab` and `gt`, which today are ahead of `gh` (`glab ci run` asks,
   `gh workflow run` does not).

   | area | asks |
   |---|---|
   | auth and config | `gh auth login\|logout\|refresh\|setup-git\|switch`; `gh config set`; `gh alias set\|import`; `gh extension install\|upgrade` (installs code) |
   | repository settings | `gh repo create\|edit\|rename\|archive\|unarchive\|sync`; `gh secret set`; `gh variable set`; `gh label create\|edit\|clone` |
   | CI | `gh workflow run\|enable\|disable`; `gh run rerun\|cancel` |
   | issues and PRs | `gh issue edit\|close\|reopen\|transfer\|pin\|lock`; `gh pr edit\|close\|reopen\|ready` |
   | releases, gists, keys | `gh release edit\|upload`; `gh gist create\|edit`; `gh codespace create`; `gh ssh-key add`; `gh gpg-key add` |
   | other tools | `glab auth login`; `rustup update\|default\|toolchain\|target\|component\|override\|self\|set`; `gcloud config set`; `npm login\|logout\|adduser\|config set\|config delete`; `pip config set\|unset`; `docker logout` |

   The never block gets the deletions: `gh release|secret|variable|label|cache|run|gist|ssh-key|gpg-key|issue delete`, `gh repo deploy-key delete`, and the `glab`/`gt` forms. `gcloud` rows follow the canonical form cut after the verb (no trailing star).
3. **git config canonical form:** `canonical_git_config` beside `canonical_gh_api`. It reads the
   scope (`--global`, `--system`, `--file`, `--local`, `--worktree`) and the operation, in both
   syntaxes:
   - the old one: `--get*`, `--list`, `-l` and a single key are reads; `--unset*`, `--add`,
     `--replace-all`, `--edit`, `-e`, `--rename-section`, `--remove-section` and key plus value
     are writes;
   - the new one (git 2.46+): `get`, `list`, `set`, `unset`, `edit`, `rename-section`,
     `remove-section`.

   It emits `git config <scope> <read|write> <key> …`. Rows ask on `git config --global write*`,
   `--system write*`, `--file write*`, and on local writes of the exec keys:
   - `core.hooksPath`, `core.fsmonitor`, `core.sshCommand`, `core.editor`, `core.pager`,
     `core.askPass`, `sequence.editor`, `gpg.program`, `gpg.*.program`;
   - `credential.helper`, `credential.*.helper`, `diff.external`, `diff.*.textconv`,
     `diff.*.command`, `filter.*.clean|smudge|process`, `merge.*.driver`;
   - `include.path`, `includeIf.*.path`, and `alias.*` whose value starts with `!`.

   Key names are matched case-insensitively, as git reads them.
4. **Credential rows** (ask, note "prints a credential into the transcript"):
   - `gh auth token`, `gh auth status --show-token|-t`, `glab auth status --show-token|-t`;
   - `gcloud auth print-access-token`, `print-identity-token`,
     `application-default print-access-token`;
   - `git credential fill`, `kubectl config view --raw`, `docker-credential-* get`.
5. **Shell writes:** `writes_by_shell(segment, unit, holes)` beside `writes_by_script`.
   - It uses `unit.writes` (the redirection targets the scanner already records) and the
     segment's here-documents and here-strings; `tee` file operands come from argv.
   - The pipeline context for `tee` comes from the unit's stages.
   - Same deny, same reason; one check runs both.
6. **Docs:** `docs/configuration.md` (the reach of the gate: what asks, what is refused, what stays
   silent and why), CHANGELOG, findings (below).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | F-40: every ask named in the reason, the count kept under the limit; tests incl. agy (stories 5, 7) | a | auth | — |
| T02 | git config canonical form, global/system/file writes and exec keys; tests (story 3) | a | auth | T01 |
| T03 | outward and account rows, credential rows, deletions in never; parity tests per row, sync renders the denies (stories 1, 2, 4) | a | auth | T02 |
| T04 | shell writes: literal text and in-place editors denied, unwrapped forms included; tests (story 6) | a | auth | T03 |
| T05 | agy parity sweep for T02–T04, docs/configuration.md, CHANGELOG, findings F-36 and F-40 closed, F-44's gate part closed and its rest re-filed (story 7) | b | — | T04 |

Every code task touches `cobot-rules`, so one lane: sequential commits. **F-44's rest** is not the
gate's; T05 re-files it as one finding for the memory and ship spec:
- four commit approvals with no owner allow line offered;
- builder Noticed items never parked;
- `cobot-deps`' Actions hint with no workflows (`_cobot_deps.py:522`);
- ship's global, unpinned installs, which now ask (decision 29) but are still unpinned.

## Trade-offs

- **Deny literal writes everywhere, not only in the tree (Q1):** one rule, no path judgement to
  bypass with `..` or a symlink. The cost is a scratch file the agent must write with Write. A
  command's own output to a file stays silent: it is a build or a tool run, which Write cannot
  replace.
- **Never for deletions (Q2):** the rows render into `permissions.deny`, a hard wall in every
  layer. An owner who deletes often runs the command in their own shell. Ask would have let a
  prompt-weary owner approve an unrecoverable step.
- **A canonical form for git config, not glob rows (Q3):** globs cannot tell
  `git config --global user.name` (a read) from `git config --global user.name x` (a write). The
  canonical form already exists for `gh api` and `gcloud`; the same pattern keeps rows readable.
- **Credentials ask, not never (Q4):** the owner sometimes needs a token for a one-off `curl`; an
  owner allow line keeps that cheap.
- **F-40 keeps the first reason verbatim:** graders, tests and the owner's habit read it. The list
  is appended, not substituted.

## Challenger verdict

pending

## Converge

pending
