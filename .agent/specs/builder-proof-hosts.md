# Spec — a builder's proof is checked wherever its report is delivered (F-35)

size: medium · profile: library · owner: YpNo · date: 2026-11-18 · revision 2 (challenger pass
folded) · built on `main` `9d3bd14` (memory-and-ship merged as PR 74)

## Goal

F-35, from the 2026-11-15 dogfood sessions: in the desktop app every `Agent` call returned "Async
agent launched" (24 and 2 calls). The foreground rule from PR 48 (`run_in_background: false`)
cannot hold there, because the parameter does not exist. The report hook then skips the result
(`status: async_launched`), so **no builder report is checked for a command and an exit code in
that host**, and none of its `Noticed:` items are parked either.

What the Claude Code docs say (hooks and sub-agents references, read 2026-11-18):

- `PostToolUse` on `Agent` fires once, at launch, with `status: "async_launched"` for a
  background call. The docs never say it fires again with the result.
- A subagent that reports through the `SubagentHandback` tool delivers its report as that call's
  `message` input, which "a PreToolUse/PostToolUse hook matched on `SubagentHandback` receives
  as `tool_input.message`". Plain text after it "is NOT delivered".
- `SubagentStop` gives `agent_type`, `agent_id`, `last_assistant_message` and
  `stop_hook_active`, and can block. Under a hand-back, the last message is closing text, not the
  report. `r2.md` dropped `SubagentStop` for that ambiguity.
- `run_in_background` is not documented for `Agent`.
- Not covered: whether these hooks fire for a background agent in the desktop app, whether
  `agent_id` is in a subagent's `PreToolUse` payload, and whether `updatedInput` can rewrite a
  hand-back. Story 1 measures each.

| host | how the report is delivered | checked today | after |
|---|---|---|---|
| CLI, foreground call | the `Agent` result (the hand-back's text) | `PostToolUse` on `Agent` | the same, sharing state |
| desktop app (async, hand-back) | `SubagentHandback` `message` | no | `PreToolUse` on `SubagentHandback` |
| async without a hand-back | the subagent's last reply | no | `SubagentStop`, only if story 1 finds such a host |

## Owner's answers (2026-11-18, before drafting)

- **Where:** every place a report is delivered, checked once.
- **On failure:** send it back (block). After one refusal of the same builder, the report goes
  through, marked unproven.
- **The skill rule:** keep `run_in_background: false` where the host offers it, and add "wait for
  every hand-back"; `check-plugin` enforces both.

## Principles check

- **Proportionality:** medium. One module (`cobot-rules`), `hooks.json`, six skill texts,
  `check-plugin`, tests, and a probe.
- **Rules before autonomy:** the check only refuses an unproven report, and it fails open: when
  it cannot record a refusal, it allows and marks the report unproven, so a builder is never stuck.
- **Proof, not promises:** unit tests for each path. The probe is the only live proof, since
  `builder-routing` runs under `claude plugin eval` (CLI, no Bash) and covers none of the new
  paths.
- **Governance:** decision 18 is untouched. A new decision, 32, records where a report is checked.
- **New dependencies:** none.
- **Delivery:** one branch `feat/builder-proof-hosts`, one PR; the tasks below are the commits.

## Stories and acceptance

1. **A probe measures the hook points in the desktop app** (challenger 1: the marketplace is
   registered from the main checkout, so installing from the branch would run main's hooks).
   - cobot prints a probe for the owner to add to a test project's `.claude/settings.local.json`
     (the gate refuses those files to the agent):
     - hooks for `PreToolUse` on `^SubagentHandback$` and for `SubagentStop`, each running a
       script of about ten lines from the session's scratch folder;
     - the script appends its raw stdin to a log, and denies a builder's first hand-back.
   - In a desktop session in that project, one `cobot:builder` call is asked for a report without
     an exit code.
   - The log must show:
     - whether each hook fired, and with which fields (`agent_type` plugin-scoped, `agent_id`,
       `session_id`, `tool_use_id`);
     - whether the deny reached the background builder and it handed back again;
     - whether `SubagentStop` fires, also for a foreground call;
     - whether `updatedInput` rewrites a hand-back's message.
   - Accept: a journal entry quoting the log. A hook point that does not fire, or a field that is
     missing, is dropped from the design, and the spec says so. The owner removes the probe.
2. **The hand-back is checked (`PreToolUse` on `SubagentHandback`).**
   - `hooks.json` gains a `PreToolUse` entry matching `^SubagentHandback$`. It runs
     `cobot-rules handback` through the report shim, where every failure allows.
   - For a builder (`BUILDER_TYPE_RE` on `agent_type`), `judge_report` checks the message with
     `check_report`:
     - a failing first report is denied with `REPORT_BLOCK_REASON`;
     - a passing one is allowed and its `Noticed:` items parked;
     - a non-builder hand-back is allowed untouched, and a malformed payload allows.
   - Accept: those four cases, as tests.
3. **The paths share one state, so a report is judged once** (challenger 2).
   - The state lives in `data_dir().parent / "reports" / <session>.json`: UUID-shaped session ids
     only, a week kept, written through a temporary file and a rename.
   - It records refusals by `agent_id`, and the sha256 of each report text a path let through.
   - `PostToolUse` on `Agent` (a foreground call) allows a text whose hash is already known: the
     hand-back path judged it.
   - Accept: a hand-back allowed on its second try is not blocked again by `PostToolUse`.
4. **One refusal, then through, marked, and never stuck** (challengers 3 and 5).
   - The second failing report from the same `agent_id` is allowed.
   - It is marked so the orchestrator sees it at once: `updatedInput` prefixes the message with
     `UNPROVEN: `, if story 1 shows that works; otherwise the report hook adds the line as
     `additionalContext` on the parent's side.
   - It is also parked in `.agent/noticed.md` when the memory is trusted.
   - When no refusal can be recorded (no `agent_id`, a bad session id, an unwritable folder), the
     first failing report is allowed and marked the same way. A builder is never denied twice.
   - Build step 3 refuses to tick a task whose report is `UNPROVEN`: it re-runs the task or asks
     the owner.
   - Accept: the second failure is allowed and marked; a missing `agent_id` allows the first and
     marks it; the build skill's text names the rule (text test).
5. **`SubagentStop`, only if needed** (challenger 4).
   - Built only if story 1 finds a host where an async run without a hand-back delivers its last
     reply.
   - If built, it decides from the shared state by `agent_id`, never by reading the transcript or
     `stop_hook_active`: a builder whose refused hand-back was never let through is blocked with
     "hand back your report".
   - Accept: written from story 1's findings, or dropped with the reason in Converge.
6. **The skills say what every host can do** (challenger 6).
   - The six skills that call `Agent` (build, consult, ship, security-sweep, wrap, spec) carry two
     exact strings: "`run_in_background: false` where the host offers it" and "wait for every
     hand-back". security-sweep's "every unit's hand-back" is reworded to match.
   - `check-plugin`'s `FOREGROUND` rule requires both strings in a skill that calls `Agent`.
   - Accept: `check-plugin` fails on a skill with one string without the other (tested), and
     passes on the six. A text check cannot catch a negation; that limit is accepted.
7. **Docs and the finding.**
   - Decision 32.
   - `docs/02-design.md`: the report-check row.
   - `docs/configuration.md`: the hooks and the reports state.
   - CHANGELOG.
   - F-35 closed, or re-scoped if the probe drops a hook point.

## Plan

1. **Probe** (story 1): the probe script and the settings snippet, printed for the owner.
2. **`cobot-rules`:**
   - `judge_report(text, agent_type, agent_id, cwd)`, shared by `report()` and `handback()`: the
     check, the shared state, parking and marking;
   - the state helpers, beside `with_offer`'s and under the same folder rules;
   - `main` routes `handback` (and `subagent-stop` if story 5 is built).
3. **`hooks.json`:** the new entry. `report.sh` takes the mode as its argument, keeping its rule
   that every failure allows.
4. **Skills and `check-plugin`** (story 6).
5. **Docs** (story 7).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | probe: script and settings snippet; the owner runs one desktop session; findings journaled (story 1) | a | — | — |
| T02 | `handback` path, shared state, refusal and marking, `PostToolUse` sharing it; tests (stories 2–4) | a | auth | T01 |
| T03 | `SubagentStop`, only if T01 found it needed (story 5) | a | auth | T02 |
| T04 | the six skills, build step 3, `check-plugin` (story 6) | b | — | — |
| T05 | docs, decision 32, CHANGELOG, F-35 (story 7) | a | — | T02–T04 |

## Trade-offs

- **The hand-back as the main path:** it is where this host delivers the report, and a check in
  any other place reads closing text.
- **One refusal, then through, marked:** a builder that cannot prove its work should neither loop
  nor strand the session. The mark reaches the orchestrator in the report itself, and the build
  will not tick the task.
- **A probe before the build:** the docs leave the background case open. A hook that never fires
  would be a check that looks present but is not.

## Not in scope

- Agy: not probed. Its `invoke_subagent` call may have a hook point, but agy gives no agent
  identity, so builder reports there stay "requested, not enforced", as the brief says.
- Consultant and auditor reports: they report findings, not commands.

## Clarify

Asked 2026-11-18 in one call; the owner took every recommended option (above).

## Challenger verdict

**Pass 1, 2026-11-18: SOUND WITH CHANGES** (1 BLOCKER, 4 MAJOR, 3 MINOR), all folded in revision
2. Checked by hand: the marketplace source is the main checkout (`claude plugin marketplace list`);
`r2.md` dropped `SubagentStop` for the hand-back ambiguity; `noticed add` parks nothing in an
untrusted memory.

| # | level | point | fold |
|---|---|---|---|
| 1 | BLOCKER | the spike would run main's hooks; no event logged before T02; the log lacks ids | story 1, a probe in settings.local, raw payloads |
| 2 | MAJOR | the CLI judges one report twice under two keys, a re-spawn loop | story 3, shared state by hash |
| 3 | MAJOR | an unrecorded refusal denies forever | story 4, fail open, marked |
| 4 | MAJOR | `SubagentStop` misjudges a refused hand-back, `stop_hook_active` skips the mark | story 5, conditional, state by id |
| 5 | MAJOR | "unproven" reaches wrap only, nothing in untrusted memory | story 4, `UNPROVEN:` in the report, build step 3 |
| 6 | MINOR | the phrases are loose; security-sweep's wording differs | story 6, exact strings |
| 7 | MINOR | agy "no hook point" overstates | Not in scope |
| 8 | MINOR | T02 too big; no eval covers the paths | tasks split, the probe named as the only live proof |

Checked clear: the anchored matchers; the shim allows on every failure; `agent_type` is
plugin-scoped in a subagent's `PreToolUse` (r1 spike E); transcript size and timeout; the
`check-plugin` rule reaches exactly the six skills.

## Converge

**T01, the probe, 2026-11-18** (desktop app, one `cobot:builder` call in a test folder; the
owner ran it, the log quoted in the journal):

- `PreToolUse` on `SubagentHandback` fires for a background builder. It carries `agent_type`
  `cobot:builder` (plugin-scoped), `agent_id`, a UUID `session_id`, and the report in
  `tool_input.message`.
- A deny reaches the background builder: it handed back again two seconds later.
- `updatedInput` rewrites the hand-back: the orchestrator received the `UNPROVEN-PROBE:` prefix
  word for word.
- `PostToolUse` on `Agent` fires once, at launch (`async_launched`). Its `agentId` equals the
  hand-back's `agent_id`, and it never fires with the result.
- `SubagentStop` fires for the builder with its identity but no `last_assistant_message`, so it
  cannot check a report here. Internal agents fire it with an empty `agent_type`.

Design consequences:

- Story 4 marks with `updatedInput`.
- Story 3 keys refusals and allowed reports by `agent_id` on every path. `PostToolUse` takes it
  from `tool_response.agentId` when present, and falls back to the text hash.
- Story 5 (`SubagentStop`) and task T03 are dropped: no host seen needs them.
