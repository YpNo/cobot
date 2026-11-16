# Spec — a security auditor agent, fanned out by the sweep

size: medium · profile: library · owner: YpNo · date: 2026-11-16 · revision 1 · built on `main`
`a11dd3b`

## Goal

`/cobot:security-sweep` runs today inside the generic `consultant` agent, as a forked skill, at
medium effort (`docs/02-design.md:111` calls this temporary). On a dogfood repository (F-45) it
read about six source files under "scope: the whole tree". It never retried a history scan the
gate refused because one compound command also read a protected file. It left two installed
scanners unrun. It kept an unchecked finding at MEDIUM and mixed two confidence scales.

After this spec:

- **A dedicated `auditor` agent** runs the sweep's procedure, at the session's model and high
  effort. Its prompt makes each step either done or reported as failed with the reason.
- **The sweep fans out from the main thread.** A small tree gets one auditor. A larger one gets
  one auditor per pack present, plus one for history, secrets and dependency scanners, at most
  five in all.
- **A fresh auditor verifies** every CRITICAL, HIGH and MEDIUM finding before the report, against
  its file and, for a third-party action or package, its upstream source at the pinned ref.
- **The report tells the truth:** one confidence scale, and per pack how many files were read
  out of how many.

Unchanged: the packs' rule ids, the report sections, `.agent/accepted-risks.md`, the owner-typed
invocation (`disable-model-invocation: true`), and `/security-review` for diffs. The consultant
and `/cobot:consult` are not changed.

## Owner's answers (2026-11-16, before drafting)

- Model → `inherit`, effort `high`, like the challenger.
- Fan-out → one auditor for a small tree. Above the threshold: one per pack, plus the history and
  scanners unit, at most five.
- Verify → one fresh auditor checks MEDIUM and above. LOW findings and hazards are checked by the
  auditor that found them.
- Design-time trust boundaries in `/cobot:spec` → later, in its own spec. The build records it as
  a finding.

## Principles check

- Proportionality: medium (a new agent, a skill rewritten from a fork to a main-thread router, a
  gate alias, evals).
- Rules before autonomy: the auditor reuses the consultant's read list through an alias. No new
  allow row, and every write still asks.
- Knowledge is a skill: the packs stay the knowledge. The auditor is a container, and each
  specialist is the auditor with one pack (decision 28).
- Proof not promises: an eval with a deleted `.env` in the history proves the history step. Gate
  tests prove the alias gives the same decisions. `check-plugin` proves the agent budget.
- Governance (`docs/01-decisions.md`): decisions 21, 22 and 28 hold. A new decision records the
  auditor, the fan-out and the verify pass: the next free number at build time (29 is taken by the
  unmerged `onboard-environment` spec).
- Architecture: plain layering. The change is a skill, an agent file and one gate function.
- New dependencies: none.
- Delivery: one branch, `feat/security-auditor`, one PR. The tasks below are the commits.

## Stories and acceptance

1. **The auditor agent.**
   - `claude-agents/auditor.md`: `model: inherit`, `effort: high`; tools Read, Grep, Glob, Bash,
     WebFetch and WebSearch.
   - Its prompt holds these rules:
     - work in place, as the consultant does;
     - every procedure step ends `done` or `failed: <reason>`;
     - a call the gate refuses is retried once, split into its parts, never combined with a
       protected path;
     - every step-3 tool on PATH is run, or reported `absent` or `failed: <reason>`;
     - before a finding is kept, it is checked against its file and, for third-party code, against
       the upstream at the pinned ref;
     - confidence is `CONFIRMED` or `PLAUSIBLE` only.
   - `agents/auditor.md` is written by `sync-agents`. Under agy, like the consultant, the auditor
     has no command tools, and its report says that scanners and history did not run.
   - Accept: `check-plugin` passes, with the agent listing at or under 600 tokens (today 523), and
     `sync-agents --check` passes.
2. **The gate treats `auditor` as the consultant.** Agent-scoped rows for `@consultant` also match
   `auditor` and `cobot:auditor`, through the function that already maps `cobot:consultant`
   (`cobot-rules`, near line 2378). Accept:
   - for every default command in the gate's test corpus, `cobot-rules check <cmd> --agent
     cobot:auditor` gives the same decision as `--agent cobot:consultant`;
   - a redirection, `find -delete` and `sed -i` still ask for the auditor;
   - an unrelated agent name still gets the `ask Bash(*)` fallback.
3. **The sweep runs in the main thread.** `context: fork` and `agent:` leave `security-sweep`.
   - **Step 1, inventory.** The main thread counts files only (`git ls-files`, then Glob per pack
     signal) and reads no source. The tree is small when it holds `SWEEP_SMALL_FILES = 200` files
     or fewer of kinds a pack covers, or when only one pack is present. A small tree gets one unit.
     A larger tree gets one unit per pack, core included in each, plus a repo-wide unit for
     history, secret scanners and dependency scanners. Units past five are merged, smallest first.
   - **Step 2, fan-out.** One message holds one `Agent` call per unit (`subagent_type:
     cobot:auditor`, `run_in_background: false`), with a prompt naming the repository, the
     unit's paths and packs, and the plugin root.
   - **Step 3, verify.** One fresh auditor receives every CRITICAL, HIGH and MEDIUM finding and
     returns, for each: kept, rescaled (with the new severity), or dropped (with the evidence).
   - **Step 4, report.** One report in the template. Findings are merged and capped at ten. Per
     pack, scope says "read N of M files". Units that never reported are listed under scope as
     `not run`.
   - A host without `run_in_background` (F-35) returns "Async agent launched". The main thread
     then waits for every unit's hand-back before step 3. A missing hand-back is `not run`, never
     clean.
   - Accept: `sweep-every-pack` passes. A new eval case `sweep-fan-out` (one Terraform tree, one
     shell script, more than 200 files) shows two pack units, the repo-wide unit and one verify
     call (`tool_used Agent`, `min: 4`).
4. **The history step proves itself.** The history scan runs as its own command in the repo-wide
   unit, or in the single unit. A new eval case, `sweep-history-secret`, is built by a scaffold
   that commits `.env` and then deletes it. Accept: its report holds a CRITICAL naming `.env`
   (graders: `regex` on the last message, and `tool_used Bash input_match "diff-filter=A"`).
   Eval Bash can read git history, so this case is not blocked by the read-only eval sandbox.
5. **One confidence scale.** The skill's template line becomes `<severity> · <CONFIRMED |
   PLAUSIBLE> · <rule id> · …`, matching step 6. Accept: a `regex` grader in `sweep-every-pack`
   rejects `· (high|medium|low) ·`.
6. **Packs name document languages.** `CORE-INJECT-05` adds LaTeX and other typesetting input
   (`\input`, `\write18`, and the engine's shell-escape switch) next to HTML and JS. Accept: the
   pack line reads it, and markdownlint passes.
7. **Agy parity.** Under agy the sweep fans out through `invoke_subagent`, with one unit per
   subagent and the same verify pass. The brief line in `cobot-session` stays true ("security-sweep
   ... through invoke_subagent"). Accept: `HOME=<tmp> agy plugin validate` passes. The agy tests for
   the session brief keep the line.

## Plan

1. `claude-agents/auditor.md` and its prompt; `sync-agents`; the `check-plugin` budget (shorten
   the consultant's description if needed).
2. The gate alias in `cobot-rules`, with its tests, before the code.
3. Rewrite the `security-sweep` skill: the main-thread router, units, the verify pass, the report
   truth, the confidence scale, and the F-35 wait.
4. `CORE-INJECT-05`, for document languages.
5. Eval cases `sweep-fan-out` and `sweep-history-secret`, and the confidence grader in
   `sweep-every-pack`.
6. Docs: `docs/02-design.md` (the security reviewer, consultant and agents rows), the new decision,
   CHANGELOG. F-45 is closed, and the trust-boundaries idea is recorded as a finding.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `auditor` agent (Claude and agy), the budget, `check-plugin` and `sync-agents --check` | a | — | — |
| T02 | gate alias `auditor` → the consultant scope; tests first (same decisions, writes ask) | b | auth | — |
| T03 | `security-sweep` as a main-thread router: inventory, units, fan-out, verify, report, F-35 wait | a | — | T01 |
| T04 | `CORE-INJECT-05`, document languages | c | — | — |
| T05 | evals `sweep-fan-out`, `sweep-history-secret`, confidence grader; one run each, `--runs 1` | a | — | T02, T03 |
| T06 | docs, decision, CHANGELOG, F-45 closed, trust-boundaries finding | b | — | T03 |

## Trade-offs

- One agent and fan-out, not one agent per tool or domain: the packs already hold the
  specialist knowledge, and the listing budget (600 tokens) holds one more agent, not five.
- A gate alias, not a copy of the 130 `@consultant` rows: one read list to keep. The auditor gains
  no command the consultant lacks.
- A router in the main thread, not a fork: a forked skill's agent cannot start agents. The main
  thread pays for the inventory counts and the merged reports only.
- A size threshold over always fanning out: a small tree audited by five agents costs more and
  finds no more.
- A verify pass for MEDIUM and above, not for every finding: the costly mistakes are the
  high-severity ones, and LOW findings stay self-checked under the same prompt.

## Not in scope

- `/cobot:spec` asking for trust boundaries: a finding at build time, then its own spec.
- The consultant's own effort and `/cobot:consult`.

## Clarify

Asked before drafting. The answers are under *Owner's answers*.

## Challenger verdict

pending

## Converge

pending
