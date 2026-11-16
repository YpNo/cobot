# Spec — a security auditor agent, fanned out by the sweep

size: medium · profile: library · owner: YpNo · date: 2026-11-16 · revision 2 (challenger pass
folded) · built on `main` `a11dd3b`

## Goal

`/cobot:security-sweep` runs today inside the generic `consultant` agent, as a forked skill, at
medium effort (`docs/02-design.md:111` calls this temporary). On a dogfood repository (F-45) it:

- read about six source files under "scope: the whole tree";
- never retried a history scan, which the gate refused because the same compound command also
  read a protected file;
- left two installed scanners unrun;
- kept an unchecked finding at MEDIUM;
- mixed two confidence scales.

After this spec:

- **A dedicated `auditor` agent** runs one unit of the sweep at the session's model and high
  effort. Every step it is assigned ends done or failed, with the reason.
- **The sweep is a router in the main thread.**
  - A small tree gets one auditor.
  - A larger tree gets one auditor per pack present, plus one repo-wide unit for history,
    secrets and dependency scanners, at most five units in all.
- **Findings are merged, ranked and capped before checking.** A fresh auditor then checks every
  CRITICAL, HIGH and MEDIUM left, against its file and, for a third-party action or package,
  against its upstream source at the pinned ref.
- **The report tells the truth:** one confidence scale, and per pack how many files were read out
  of how many.

Unchanged:

- the packs' rule ids, the report sections and `.agent/accepted-risks.md`;
- the owner-typed invocation (`disable-model-invocation: true`);
- `/security-review` for diffs;
- the consultant and `/cobot:consult`.

## Owner's answers (2026-11-16, before drafting)

- **Model:** `inherit`, effort `high`, like the challenger.
- **Fan-out:**
  - one auditor for a small tree;
  - above the threshold, one per pack plus the repo-wide unit;
  - at most five.
- **Checking:** one fresh auditor checks MEDIUM and above. LOW findings and hazards are checked by
  the auditor that found them.
- **Design-time trust boundaries in `/cobot:spec`:** later, in its own spec. The build records the
  idea as a finding.

## Principles check

- Proportionality: medium. A new agent, a skill rewritten from a fork to a main-thread router, a
  gate alias, evals.
- Rules before autonomy:
  - The auditor reuses the consultant's read list through one alias: no new allow row, and every
    write still asks.
  - Under agy it has no command tools, like the consultant.
- Knowledge is a skill: the packs stay the knowledge. The auditor is a container, and each
  specialist is the auditor with one pack (decision 28).
- Proof not promises:
  - gate tests prove the alias gives the same decisions;
  - a sync test proves the agy twin has no commands;
  - evals prove the units, the history step and the confidence scale;
  - `check-plugin` proves the budgets.
- Governance (`docs/01-decisions.md`): decisions 21, 22 and 28 hold. A new decision records the
  auditor, the routing and the checking pass, under the next free number at build time (29 is
  taken by the unmerged `onboard-environment` spec).
- Architecture: plain layering. The change is a skill, an agent file, a reference and one gate
  function.
- New dependencies: none.
- Delivery: one branch, `feat/security-auditor`, one PR. The tasks below are the commits.

## Stories and acceptance

1. **The auditor agent.**
   - `claude-agents/auditor.md` sets `model: inherit` and `effort: high`, with the tools Read,
     Grep, Glob, Bash, WebFetch and WebSearch. Its prompt says:
     - work in place, as the consultant does;
     - run only the steps the unit prompt assigns, and end each one `done` or
       `failed: <reason>`;
     - retry a call the gate refuses once, split into its parts, never combined with a protected
       path;
     - check each finding against its file, and third-party code against its upstream at the
       pinned ref, before keeping it;
     - confidence is `CONFIRMED` or `PLAUSIBLE` only.
   - `scripts/sync-agents.py` adds `auditor` to `NO_COMMANDS`, so `agents/auditor.md` has no
     `run_command` and sets `commandExecutionPolicy: "off"`.
   - Accept:
     - `tests/test_agents_sync.py` asserts the auditor's policy is `off` and that it has no
       command tool;
     - `check-plugin` keeps the agent listing at or under 600 tokens (523 today);
     - `sync-agents --check` passes.
2. **The gate scopes `cobot:auditor` as the consultant.**
   - `@consultant` rows also match the agent `cobot:auditor`, and only that name. The hook's
     `agent_type` is namespaced, so a user's own agent called `auditor` is untouched. The change
     goes in `agent_matches` (`cobot-rules:2377`).
   - Tests first, accept:
     - every command in the gate's test corpus gets the same decision with `--agent cobot:auditor`
       as with `--agent cobot:consultant`;
     - a redirection, `find -delete` and `sed -i` ask for `cobot:auditor`;
     - for `auditor`, `x:auditor` and `cobot:builder`, `explain` shows no `@consultant` row, and
       every decision equals the one with no agent. No unscoped `ask Bash(*)` is added: there is
       none today.
3. **The sweep becomes a router.** `context: fork` and `agent:` leave `SKILL.md`, which keeps only
   the router. The per-unit procedure (inventory of trust boundaries, packs, tools, history,
   accepted risks, checking, ranking) moves to `references/procedure.md`, read by the auditors.
   Steps are referred to by name, not number. The router's steps:
   - **Inventory.**
     - The main thread counts files in one Bash call, `git ls-files -- <pack globs> | wc -l` per
       pack, and finds shell scripts without an extension with `git grep -l '^#!.*sh' --`. It
       reads no other source.
     - Outside a git repository the same counts come from `find . -type f` per glob, with `.git`
       excluded.
     - The tree is small when it holds `SWEEP_SMALL_FILES = 200` files or fewer of kinds a pack
       covers.
   - **Units.**
     - A small tree is one unit, with every step.
     - A larger tree gets the repo-wide unit (history, accepted risks, secret and dependency
       scanners), plus one unit per pack present, core included in each. With one pack only,
       that is one pack unit and the repo-wide unit.
     - Units past five are merged, smallest first.
     - Each pack unit's prompt names its paths, its pack and the steps it runs: the trust-boundary
       inventory, the pack, checking and ranking. It names no scanner and no history step.
   - **Fan out.** One message holds one `Agent` call per unit (`subagent_type: cobot:auditor`,
     `run_in_background: false`). The prompt names the repository, the plugin root, the
     procedure reference, the unit's paths, packs and steps, and says repository content is data.
   - **Merge.** Duplicates are merged, then findings are ranked and capped at ten.
   - **Check.** One fresh auditor receives the CRITICAL, HIGH and MEDIUM findings among those ten
     and returns, for each: kept, rescaled (with the new severity), or dropped (with the
     evidence). A finding left without a verdict is reported `unverified`.
   - **Report.**
     - One report in the template.
     - Per pack, scope says `read N of M files`.
     - A unit that never handed back is listed under scope as `not run`, never clean.
     - In a host without `run_in_background` (F-35, "Async agent launched"), the main thread
       waits for every unit's hand-back before the merge.
   - Accept:
     - `sweep-every-pack` still passes as a small tree with one unit.
     - A new eval case, `sweep-fan-out`: a scaffold makes more than 200 Terraform files, one shell
       script, and a world-readable bucket (`allUsers`), so the checking pass has work to do.
     - Its graders, `tool_used Agent` with `input_match`, each `min: 1`:
       - one unit naming `terraform.md`;
       - one naming `shell.md`;
       - one naming the history step;
       - one check call naming `allUsers`.
     - `timeout_seconds: 1500`.
4. **The history step proves itself.**
   - It runs as its own command, in the repo-wide unit or the single unit.
   - A new eval case, `sweep-history-secret`: its scaffold commits `.env`, then deletes it. Both
     commit messages are neutral ("add settings", "tidy"), so nothing outside the history names
     the file.
   - Accept:
     - a `regex` grader matches `CRITICAL[^\n]*\.env` on `last_message`;
     - a `tool_used Bash input_match "diff-filter=A"` grader (it counts a refused call too, so the
       regex is the proof).
   - Eval Bash can read git history, so this case is not blocked by the eval sandbox's read-only
     mounts.
5. **One confidence scale.** The template line becomes `<severity> · <CONFIRMED | PLAUSIBLE> ·
   <rule id> · …`, as in the procedure's checking step. Accept: a `regex` grader in
   `sweep-every-pack` rejects `· (high|medium|low) ·`.
6. **Packs name document languages.** `CORE-INJECT-05` adds LaTeX and other typesetting input
   (`\input`, `\write18`, the engine's shell-escape switch) next to HTML and JS. Accept: the pack
   line reads that way, and markdownlint passes.
7. **Agy.**
   - Under agy the router fans out through `invoke_subagent`, with one unit per subagent and the
     same checking pass.
   - The repo-wide unit is not started there, because its auditor has no commands. The scope line
     says `history and scanners: not run (agy, no command tools)`.
   - Accept:
     - `HOME=<tmp> agy plugin validate` passes;
     - `cobot-session`'s agy brief line still holds;
     - a skill text test asserts the agy branch names `not run` for the repo-wide unit.

## Plan

1. The `auditor` agent, `NO_COMMANDS` and its test; `sync-agents`. Check the budget, and shorten
   the consultant's description if needed.
2. The gate alias in `agent_matches`, tests first.
3. `security-sweep`: `SKILL.md` as the router, and `references/procedure.md` with the per-unit
   steps, the truth rules, the confidence scale and the F-35 wait. Check `SKILL.md` against the
   24 KB body limit.
4. `CORE-INJECT-05`.
5. Eval cases `sweep-fan-out` and `sweep-history-secret`, and the confidence grader. One run each
   with `--runs 1 --ablation none --scaffold`.
6. Docs: the security reviewer, consultant and agents rows in `docs/02-design.md`, the decision,
   CHANGELOG. F-45 is closed, and the trust-boundaries idea is recorded as a finding.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `auditor` agent (Claude and agy), `NO_COMMANDS`, sync test, budget | a | auth | — |
| T02 | gate: `@consultant` rows match `cobot:auditor` only; tests first (same decisions, writes ask, no fallback added) | b | auth | — |
| T03 | `security-sweep` router plus `references/procedure.md`: inventory counts, units, fan-out, merge, check, report, F-35 wait, agy branch | a | — | T01 |
| T04 | `CORE-INJECT-05`, document languages | c | — | — |
| T05 | evals `sweep-fan-out`, `sweep-history-secret`, confidence grader; one run each | a | — | T02, T03 |
| T06 | docs, decision, CHANGELOG, F-45 closed, trust-boundaries finding | b | — | T03 |

## Trade-offs

- **One agent with fan-out, not one agent per tool or domain:** the packs already hold the
  specialist knowledge, and the listing budget (600 tokens) has room for one more agent, not five.
- **A gate alias for `cobot:auditor` only, not a copy of the 130 `@consultant` rows:** one read
  list to keep, and no other agent's scope changes.
- **A router in the main thread, not a fork:** a forked skill's agent cannot start agents. The
  main thread pays only for the counts and the merged reports.
- **Scanners and history in one unit only:** parallel `cargo deny` runs would fight over the
  advisory database lock, and duplicate history findings would crowd the ten.
- **Capping before checking:** the checking pass sees at most ten findings, not fifty.
- **A size threshold, not always fanning out:** five agents on a small tree cost more and find no
  more.

## Not in scope

- `/cobot:spec` asking for trust boundaries: recorded as a finding at build time, then its own
  spec.
- The consultant's own effort, and `/cobot:consult`.

## Clarify

Asked before drafting. The answers are under *Owner's answers*.

## Challenger verdict

Pass 1, 2026-11-16: **SOUND WITH CHANGES**. Eleven points, all folded.

- MAJOR: the agy twin would get command tools, because `NO_COMMANDS` hardcodes the consultant and
  the learner (checked: `sync-agents.py:25`). Fix: the auditor is added, with a sync test on the
  policy (story 1).
- MAJOR: the agent-wide "run every tool" rule would make each pack unit run every scanner and the
  history scan. Fix: the auditor runs only the steps its unit assigns, and scanners and history
  belong to the repo-wide unit (stories 1, 3).
- MAJOR: "an unrelated agent still gets the `ask Bash(*)` fallback" is false. Checked:
  `cobot-rules check 'sed -i s/a/b/ x' --agent somebody` gives `none`. Fix: the acceptance
  asserts no `@consultant` row applies and the decisions equal those with no agent (story 2).
- MAJOR: the inventory cannot use Glob, which truncates its results, and shebang detection reads
  file heads. Fix: counts with `git ls-files | wc -l` and `git grep -l`, plus a `find` fallback
  outside git (story 3).
- MINOR: two readers of one procedure, and clashing step numbers. Fix: `references/procedure.md`
  for the auditors, the router in `SKILL.md`, steps named (story 3).
- MINOR: the alias was broader than needed. Fix: `cobot:auditor` only (story 2).
- MINOR: `sweep-fan-out` could not tell its units apart. Fix: seed `allUsers`, use per-unit
  `input_match` graders, raise the timeout (story 3).
- MINOR: `sweep-history-secret` could pass without the history step. Fix: neutral commit
  messages, and the regex is the proof (story 4).
- MINOR: checking came before the cap, with no rule for a missing verdict. Fix: merge, rank and
  cap first; a missing verdict is `unverified` (story 3).
- MINOR: a large tree with one pack got one unit. Fix: above the threshold the repo-wide unit
  always splits off (story 3).
- MINOR: agy parity was not proved. Fix: the repo-wide unit is skipped under agy, and a text test
  covers it (story 7).

## Converge

pending
