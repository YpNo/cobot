# agentic-partner — design (v1.1, 2026-11-06, challenged, amended after the owner's second review)

Synthesis of two independent architect proposals (`design-inputs/proposal-a-lean.md`,
`design-inputs/proposal-b-layered.md`) against the owner's decisions (`01-decisions.md`), the
verified platform mechanics (`reference/claude-code-mechanics.md`) and the audit of the previous
scaffold (`reference/legacy-audit.md`), then red-teamed once (`design-inputs/challenge-01.md`,
verdict SOUND WITH CHANGES; every finding is folded in below). Section 13 records where each
choice came from.

## 1. Goal

A public Claude Code plugin marketplace whose first plugin, `partner`, turns the main thread into
a governed orchestrator: it sizes every request against the repository's profile, plans
non-trivial work in one spec file, delegates to a challenger, per-language builders and
read-only consultants only where isolation pays, leans on Claude Code's built-in reviewers, and is
stopped deterministically, by a hook reading a plain rules file, from any outward-facing action
the owner has not approved.

## 2. Principles

1. **The orchestrator is Claude Code's main thread.** The plugin shapes its judgment; it never
   replaces plan mode, the task list, sessions, `/code-review`, `/security-review`, `/simplify`
   or auto-memory.
2. **Proportionality is the root rule.** The repository profile (`spike`, `script`, `cli`,
   `library`, `service`, `infra`) caps how much process applies. Safety rules never scale down.
3. **Knowledge is a skill, isolation is an agent.** Experts (GitHub Actions, GCP, reverse
   engineering) are skills consulted through one generic read-only `consultant` agent. Only roles
   that need a tool allowlist, a fresh context or a different model are agents.
4. **Guarantees come from hooks, guidance from text.** Anything that must never happen is enforced
   by a `PreToolUse` hook and, for the hard wall, by permission rules the owner installs.
5. **Memory is committed and shared** when the repo is the owner's, and kept outside the tree,
   keyed by remote, when it is not.
6. **Evidence before structure.** One plugin until real use shows a seam; split only on a measured
   cost (`/skill-doctor`) or on a domain a third of repos never need.
7. **Verify, never recall.** Versions, pins and APIs are checked against upstream at use time; the
   language skills carry a dated "verified on" line and no unverifiable numbers.
8. **Proof, not promises.** A claim that a check passed carries the command, its exit code and
   the output tail; the orchestrator rejects a report without them and never reports green what
   did not run.
9. **Learn, write little.** Experts learn from primary sources and their own experiments, treat
   model memory as a hypothesis, and record only what changed a decision and will be needed
   again, each line with a status, a source and a date (§8).

## 3. Repository layout (release 1)

```text
agentic-partner/
  .claude-plugin/marketplace.json          name: agentic-partner · plugins: [partner]
  plugins/partner/
    .claude-plugin/plugin.json             name, version, description, license, keywords
    agents/
      challenger.md                        read-only · inherit/high · omitClaudeMd
      consultant.md                        read-only + Bash(read cmds) + WebFetch · sonnet/medium
      builder.md                           generic fallback (Terraform, Shell, Lua, other) · sonnet/medium
      rust-builder.md go-builder.md        thin: frontmatter `skills: [lang-<x>]`, model, ~15 lines
                                           (python-builder, typescript-builder, terraform-builder: R1.1)
      (learner.md: R1.1)                   read-only + WebFetch/WebSearch, returns a knowledge delta · sonnet/high
    skills/
      onboard/      SKILL.md + templates/CONTEXT.md JOURNAL.md FINDINGS.md  fingerprint, profile, foreign mode
      spec/         SKILL.md + template.md                             the CONCEPTOR (spec, clarify, plan, tasks)
      build/        SKILL.md                                           task loop, lanes, focused tests
      wrap/         SKILL.md                                           converge, full suite, reviews, journal
      rules/        SKILL.md                                           /partner:rules show|check|explain|sync
      lang-rust/ lang-go/ lang-terraform/ lang-fallback/
                    SKILL.md (+ refs)                                  paths-gated, not user-invocable
      expert-gha/   SKILL.md                                           GitHub Actions idiom, paths-gated inline
      consult-gha/  SKILL.md                                           context: fork, agent: partner:consultant
      <any lang-*/expert-*>/references/<topic>.md                      dated lines: status · source · claim (§8)
      (R1.1: ship, contribute + UPSTREAM.md, security-sweep, learn, lang-python, lang-typescript)
    hooks/hooks.json                       SessionStart(startup|resume|compact), PreToolUse, WorktreeCreate
    hooks/gate.sh                          5-line POSIX shim: no python3 → exit 2; exec python3 -I … || exit 2
    bin/partner-rules  bin/partner-memory  bin/partner-session        Python 3 stdlib, no deps
                                           (partner-memory: brief · learn · compact · check)
    rules/default.rules
    settings/permissions.example.json      the hard-wall block the owner installs via `rules sync`
    .mcp.json                              context7
    evals/<4 cases>/prompt.md + graders/   (R1.1: +4)
    (R2: workflows/deep-review.js, SubagentStop report check)
  tests/  (pytest for bin/, fixtures for hooks)
  install.sh                               --dev | --project | --user | --check | --uninstall (§14, ADR-0003)
  .github/workflows/ci.yml release.yml
  README.md CHANGELOG.md LICENSE docs/
```

Why one plugin: the only per-session cost that grows with the catalogue is agent descriptions,
and release 1 has five (≈ 600 tokens of the 15k budget; eight after R1.1). Skills cost one listing line each and the
language ones load only when matching paths are touched. Domain plugins (`partner-gcp`,
`partner-reverse`, `partner-delivery-extra`) are created when their content exists, each with its
own `.mcp.json`, so a Python repo never pays for a Terraform or Home Assistant server.

## 4. Roles

| Role (owner's name) | Implementation | Tools | Model / effort | Returns | Invoked by |
|---|---|---|---|---|---|
| Orchestrator | main thread + protocol injected at SessionStart (≤ 3k chars) | all, under the rules gate | owner's model | decisions, inline edits for tiny work and `risk:` tasks | owner |
| Conceptor | skill `/partner:spec`, runs in the main thread so it can ask the owner | Read Grep Glob Write(`.agent/specs/*`) AskUser; may use built-in Explore for cold reads | inherit / high | `.agent/specs/<slug>.md`: principles check, stories + acceptance, ≤ 5 clarify answers, plan, trade-offs, tasks `T001..` with `deps`, `lane`, `risk` marks | orchestrator on medium / large |
| Challenger | agent, `omitClaudeMd: true`; the spec arrives as data, so repository instructions cannot soften it | Read Grep Glob | inherit / high | `SOUND`, or ranked objections each with the simplest fix | spec, ship, owner |
| Builders | agents `rust-builder`, `go-builder` (preload `lang-<x>`), `builder` fallback; python/typescript/terraform builders in R1.1 | Read Edit Write Bash Grep Glob Skill (no Agent) | sonnet / medium | report: files, every check as command + exit code + output tail, open items. **Never commits, never writes `.agent/`.** | build skill, large path; small path when the orchestrator prefers isolation. `risk:` tasks stay with the orchestrator |
| Language senior developer | skills `lang-<x>`, `paths:` gated | knowledge | — | idiom, toolchain, verified versions, pitfalls | auto when matching files are touched; preloaded in builders |
| Experts | two skills per domain: `expert-<x>` (inline idiom, `paths:` gated) and `consult-<x>` (`context: fork`, `agent: partner:consultant`) | via consultant | sonnet / medium (sweep: high) | findings: severity, file:line, fix, confidence | spec, wrap, ship, owner |
| Consultant | agent, generic read-only container for every expert and for onboarding fingerprints | Read Grep Glob Bash WebFetch; **read-only by rule** (`ask Bash(*) @consultant` except listed read commands) | sonnet / medium; haiku for fingerprints | structured findings, each with a confidence, or a fingerprint; plus an optional `knowledge_delta` (§8) | expert skills via `context: fork`, onboard |
| Learner | agent `learner` (R1.1) behind skill `/partner:learn <topic>` (`context: fork`) | Read Grep Glob Bash WebFetch WebSearch; **read-only by rule** (`@learner`); experiments run under the gate like any command | sonnet / high | a knowledge delta: claims with status, source, date and scope; what stayed unverified; a skeleton `expert-<x>` when no expert exists | orchestrator when intake finds no expert for the domain, a consult returns low confidence, or a spike contradicts a skill; owner |
| Security reviewer | built-in `/security-review` on diffs; `security-sweep` skill (forked) on whole repos | — | — | findings | wrap; owner |
| Code reviewer | built-in `/code-review`, `/simplify` | — | — | findings / fixes | wrap |
| Scribe | wrap skill (journal, findings triage), `bin/partner-memory learn` (applies deltas), `compact` | — | haiku / low for compaction | journal entry, compacted history | wrap |

No agent has `Agent` in its tools: delegation depth is one and the orchestrator owns all fan-out.

## 5. Workflow schema

```mermaid
flowchart TD
    U[Owner request] --> I[Intake and classify<br/>profile × size]
    I -->|tiny| T1[Edit inline] --> T2[Focused test + lint] --> J[Journal line]
    I -->|small| S1[Plan inline, 5 lines] --> S2[Build inline or one builder] --> S3[/code-review low/] --> J
    I -->|medium| M1[/partner:spec<br/>spec + ≤5 clarify Qs/] --> M2{Owner answers}
    M2 --> M3[Challenger ∥ expert consults]
    M3 -->|SOUND, folded, or owner accepts| M4[Tasks T001.. in the spec]
    M4 --> M5[Build task by task<br/>inline or builders] --> W
    I -.->|no expert for the domain| LN[/partner:learn<br/>sources + experiment → delta/]
    M3 -.->|consult confidence low| LN
    LN -.-> M3
    I -->|large| L1[/partner:spec/] --> L2[Challenger ∥ consults] --> L3[Tasks split into lanes]
    L3 --> L4[Builders ∥ in worktrees, ≤ 3] --> L5[Integrate + focused tests] --> W
    W[Wrap: converge vs spec → full suite →<br/>/code-review ∥ /security-review ∥ consults] --> J2[Journal entry + compaction]
    J2 -.->|on request| SH[/partner:ship CI, release/]
    J2 -.->|on request| CO[/partner:contribute PR draft/]
    R[(Rules gate<br/>PreToolUse hook)] -. every Bash / Edit / MCP call .- T1 & S2 & M5 & L4 & SH & CO
```

Size rubric (the orchestrator names the size in one line before acting):

| Size | Definition | Path |
|---|---|---|
| tiny | ≤ 1 file, no behaviour change (typo, comment, rename, config value) | edit → focused test/lint → one journal line |
| small | ≤ 3 files, one module, behaviour change with an obvious shape | 5-line plan → build → `/code-review low` → journal |
| medium | new public API, several modules, a data shape, a trust boundary | spec + clarify → challenger ∥ consults → tasks → build → wrap |
| large | new component, infra, cross-repo, or > 1 day | medium + lanes + builders in worktrees + full review fan-out |

Profile caps: `spike`/`script` never exceed small; `infra` never skips the challenger; `library`
treats any public API change as medium.

Gates: owner answered the clarify questions (or accepted defaults written into the spec) ·
challenger returned `SOUND`, or every objection is folded, or a BLOCKER/MAJOR is accepted **by the
owner through an explicit question whose answer is written into the spec** (the thread that wrote
the plan may not accept objections against it) ·
each task's focused tests are green before the next · converge lists nothing missing · every
review finding is fixed or journaled under `Open` · the rules gate decided each outward action · every clarify question carried options and a
recommended default (the owner answers only what is expensive to undo) · no decision in the spec
rests on an `assumed` knowledge entry (§8).

## 6. Rules engine

Format, one rule per line, in Claude's own permission syntax so a line can be pasted into
settings unchanged:

```text
# decision  pattern                     (fnmatch over the whole command or tool name)
never Bash(git push --force*)
ask   Bash(git push*)
allow Bash(cargo test*)
```

Layers and precedence: `plugins/partner/rules/default.rules` < `~/.claude/partner.rules`
(owner) < `.agent/partner.rules` (project). **Most restrictive decision wins across layers;
`never` cannot be relaxed by a lower layer.** Loosening means editing the layer that holds the line.

Enforcement: `hooks.json` → `PreToolUse` on `Bash|Edit|Write|MultiEdit|NotebookEdit|mcp__.*` →
`hooks/gate.sh`, a five-line POSIX shim that exits 2 (block) when `python3` is missing and runs
`python3 -I bin/partner-rules gate || exit 2`; the script's top-level handler prints the `ask`
decision on any exception. **Any failure blocks**, because Claude Code treats every exit code other
than 2 as non-blocking. The gate (stdlib only, < 50 ms, no network):

- parses the command with `shlex`, splits on `&&`, `||`, `;`, `|`, `&` and newlines, judges every
  segment, and strips a leading `rtk` (the owner's token-saving hook rewrites every Bash command to
  `rtk <cmd>`, so both forms must match);
- matches on **(binary, subcommand)** after stripping global options: `git -C x push`, `git -c k=v
  push`, `terraform -chdir=envs/prod apply`, `env git push`, `( git push )` all resolve to their
  verb;
- treats interpreters and task runners as **opaque** (`sh bash zsh python node make just mise task
  npm pnpm yarn cargo xtask`, `eval`, `xargs`, `$(…)`, backticks) and decides `ask`, except when
  the owner layer allows that exact command line (then the gate stays silent and the permission
  system decides);
- emits `hookSpecificOutput.permissionDecision: deny` (reason = rule + layer, quoted and truncated)
  or `ask`; **it never emits `allow`**, so the plugin can only narrow what Claude Code permits;
- resolves the project layer through `git rev-parse --git-common-dir`, so worktrees share it;
- reads `agent_type` from the hook input, so a rule may carry an agent scope: `ask Bash(*)
  @consultant` makes the consultant read-only by rule, not by prompt.

Hooks fire for subagents too, so builders are covered. The project layer may contribute `never`
and `ask` only; an `allow` line there is ignored with a warning, because a cloned repository
could ship one.

The hard wall plugins cannot ship: `/partner:rules sync` renders the merged `never` lines into a
`permissions.deny` block, **each Bash pattern twice** (`Bash(git push --force*)` and
`Bash(rtk git push --force*)`, since permission rules are evaluated on the hook-rewritten input),
and the `allow` lines **from the owner layer only** (never from CONTEXT.md or a project layer) into
`permissions.allow`, shows the diff of `~/.claude/settings.json`, and the owner applies it. `/partner:rules show` prints the merged view
with provenance; `check "<cmd>"` dry-runs a command; `explain "<cmd>"` names the winning rule.
The SessionStart hook injects the count of `never`/`ask` rules so drift is visible.

Default set (owner decision 6: nothing outward runs on its own):

| Decision | Patterns |
|---|---|
| never | `git push --force*`, `git push -f*`, `terraform\|tofu apply\|destroy*`, `cargo\|npm\|pnpm\|uv publish*`, `gh release create*`, `git tag -a v*`, `gh api -X DELETE*`, `Edit\|Write(~/.claude/settings*.json)`, `Edit\|Write(.claude/settings*.json)` |
| ask | `git push*`, `gh pr create\|merge\|comment\|review*`, `gh issue create\|comment*`, `gh api -X POST\|PUT\|PATCH*`, `ansible-playbook*` (without `--check`), `kubectl apply\|delete*`, `gcloud * create\|delete\|update*`, `rm -rf*`, `git reset --hard*`, `git clean*`, `git rebase*`, `git commit*`, `docker\|podman run*`, `mcp__*__create\|update\|delete\|merge\|push*` |
| allow (sync only) | the verified-commands table of CONTEXT.md, `git status\|diff\|log\|add\|stash*`, `gh pr view\|checks\|diff*`, `gh issue view\|list*` |

## 7. Memory

| File | Purpose | Written by | Loaded |
|---|---|---|---|
| `.agent/CONTEXT.md` (≤ 120 lines) | profile, goal, stack, environment, **verified commands** (optionally keyed by path globs: the impact map build and wrap use), constraints, applies / does not apply, ≤ 20-line Shape section | onboard; corrected by whoever finds a wrong command | head injected at SessionStart |
| `.agent/JOURNAL.md` | append-only, **newest at the bottom**; entry = Changed / Why / Proof (commands, exit codes) / Open / Next; the wrap entry adds `verified: <sha> · <commands>`, which `contribute` and `ship` require to match HEAD | build (per task group), wrap (session) | last two entries injected |
| `.agent/FINDINGS.md` | parked observations, one row each: `F-nn · seen · observation · goes to`, written the moment something is noticed outside the task | anyone in the main thread; wrap triages rows into a task, an issue or `closed — reason` | open count injected |
| `.agent/knowledge/<topic>.md` (≤ 80 lines) | repository- or device-specific facts with status, source and date (§8) | orchestrator through `partner-memory learn`, never an agent | by the matching expert skill, on demand |
| `.agent/accepted-risks.md` (R1.1) | accepted security findings: why, by whom, expiry ≤ 90 days | security-sweep after the owner's yes | by security-sweep |
| `.agent/specs/<slug>.md` | one per medium / large change: spec, clarify answers, plan, challenger verdict, tasks with ticks, converge notes | spec, build, wrap | on demand |
| `.agent/partner.rules` | project rule layer (optional) | owner | by the gate |
| `.agent/UPSTREAM.md` | foreign repos only: conventions, DCO/CLA, maintainers' habits, open PR status | contribute | on demand |
| `ARCHITECTURE.md` | only when a `service`/`library` spec grows one | spec | on demand |

Trust: the SessionStart hook (matcher `startup|resume|compact`, so the protocol survives
compaction) injects `.agent/*` **only when the repository is trusted**: a remote owner listed in
`~/.claude/partner/identities`, or `.agent` resolving into the external memory directory. A cloned
repository that ships its own `.agent/` is reported, not loaded. `partner-memory` picks the two
journal entries with the latest `## YYYY-MM-DD` headings regardless of position (some existing
journals are newest-on-top); onboard offers to normalise the order.

Worktrees: builders never write `.agent/`; a `WorktreeCreate` hook symlinks `<worktree>/.agent` to
the resolved memory directory so lanes see CONTEXT.md and the project rules; only the orchestrator
journals, at integration.

Budget: SessionStart injection ≤ 10k chars (protocol ≈ 3k; `partner-memory brief` ≤ 6k: CONTEXT
head, verified commands, last two journal entries, open findings count, rule counts). `partner-memory compact`
(haiku) folds entries older than the last ten into a dated summary once JOURNAL exceeds 400
lines; the 1 013-line cartridge-os journal is the test case.

Foreign mode: `/partner:onboard` detects that no remote belongs to an identity in
`~/.claude/partner/identities` and proposes `--foreign`: it creates
`~/.local/share/agentic-partner/repos/<host>/<owner>/<repo>/`, symlinks `.agent` to it and adds
`.agent` to `.git/info/exclude`. Every skill keeps reading `.agent/`; two clones or worktrees of
headscale share one memory; nothing can reach an upstream PR by accident. Plugins are enabled with
`--scope local` there, never `project`.

## 8. Learning protocol

Owner decision 13. Two halves: **learning** (get a fact the partner lacks, without guessing) and
**teaching** (make every expert carry what was validated, and nothing else).

Triggers: intake finds no `expert-*` or `lang-*` skill for the domain; a consult answers with
confidence `low`; a `risk:` task or spike contradicts a skill; the owner asks.

Sources, in order of trust: (1) primary sources — official docs, changelogs, upstream code, the
registry, through WebFetch, WebSearch and context7; (2) an **experiment** the partner runs itself
in the scratchpad or a worktree (compile a ten-line crate, `terraform validate` a block, replay a
captured frame), under the rules gate like any command; (3) model memory, kept as a hypothesis.
A fact reaches `verified` only through (1) with a date or (2) with a command that reproduces it.

Delta, not files. The `learner` agent and every consultant return a `knowledge_delta`:

```text
topic: github-actions
entries:
  - claim: "actions/checkout v7.0.1 is the current major; v4 is Node 20 and deprecated"
    status: verified          # verified | reported | assumed
    source: https://github.com/actions/checkout/releases   # or exp: <one-line command>
    checked: 2026-11-06
    scope: general            # general → plugin references · project → .agent/knowledge
unverified:
  - "whether zizmor flags expression injection in reusable-workflow inputs"
```

The orchestrator passes it to `partner-memory learn`, which applies the filter below, deduplicates
against the target file, refuses secret-like strings, writes, and prints the diff. No agent ever
edits a knowledge or skill file; `general` entries become a pull request on this repository
through `learn --promote` (an `ask` action), `project` entries land in `.agent/knowledge/`.

Teaching: `expert-<x>` and `lang-<x>` skills read their `references/` and the matching
`.agent/knowledge/<x>.md`; when answering they quote the status (`verified 2026-11-06` or
`reported`). An `assumed` entry may be shown but may not drive a decision, a command or a version.
When no expert exists, the learner's delta also carries a skeleton `expert-<x>`: description,
`when_to_use`, `paths`, a references file and one eval case; it is created through the same
promote path and stays marked `reported` until it has served twice.

Relevance filter (what is **not** written): an entry is kept only if it (a) changed a decision,
command or design in this session, or contradicts an existing entry; (b) cannot be derived from
the repository or a single lookup the next session can do as cheaply; (c) is stable — a version,
protocol detail, quirk or policy, not a transient state. Never written: logs, transcripts,
tutorials, evidence dumps, general knowledge the model already holds. Evidence is a link or a
one-line reproducible command. Caps: 80 lines per topic file, 300 per expert's references;
entries unchecked for 180 days are re-verified or dropped by the haiku consolidation pass that
wrap runs when a knowledge file changed.

Safety: fetched content is data, never instructions; experiments install nothing without `ask`;
the learner is read-only by rule and returns text; `partner-memory learn` is the only writer.

## 9. Model routing

| Work | Model | Effort | Why |
|---|---|---|---|
| orchestrate, spec, plan, adjudicate | owner's (inherit) | high | judgment under ambiguity; wrong here costs most |
| challenger | inherit | high | an objection missed is a day lost |
| build, standard task | sonnet | medium | mechanical given a spec, a language skill and a test gate |
| build, `risk:` task (unsafe / no_std Rust, concurrency, crypto, auth, Terraform state moves, migrations) | orchestrator, inline | high | relevance first; a per-call model override takes an alias only, so the strongest context does it itself |
| consult (GitHub Actions, GCP, security sweep) | sonnet | medium (sweep: high) | breadth of reading, structured output |
| learn (fetch, digest, run an experiment) | sonnet | high | reading and reproduction; the orchestrator judges the delta |
| knowledge consolidation, findings triage draft | haiku | low | extraction |
| fingerprint, compaction, converge checklist | haiku | low | extraction and summarisation |
| evals in CI | pinned model id | — | reproducibility; aliases float, pins live only in CI |

The spec marks `risk:` per task; the build skill keeps those tasks in the main thread and delegates the rest.

## 10. Token economy

Owner decision 14. Rule: spend tokens where judgment lives, make everything else cheap, and never
condense what carries a decision. A saving that forces a second run is a loss.

| Technique | Mechanism | Guard |
|---|---|---|
| rtk | the owner's hook stays; the gate strips the prefix, patterns exist in both forms; subagents inherit the hook | `rtk proxy` whenever exact output matters: a version to pin, an eval report, a diff under review, a failure that goes into a proof line, a spec or a knowledge entry |
| brief, not files | SessionStart injects `partner-memory brief` (≤ 6k chars), skills ask for slices (`brief --spec <slug>`, `--knowledge <topic>`) | nothing re-reads a file already in context; the protocol says so |
| lazy knowledge | `paths:`-gated lang and expert skills; `references/` loaded by the skill on demand; SKILL.md ≈ 150 lines | SKILL.md < 500 lines checked in CI |
| isolation for bulk reading | consultant, learner, built-in Explore return structured output; ≤ 10 findings, ≤ 1 200 tokens per report; builders receive the task section of the spec, not the spec | report caps in the agent prompts and the SubagentStop check (R2) |
| routing | §9; haiku for extraction, sonnet for builders and consults, the owner's model only where judgment decides | per-call aliases; routing changes need `partner-usage` evidence |
| focused then full | build runs the commands the impact map names; the full set runs once, at wrap | the verified stamp requires the full run |
| short hooks | gate reason ≤ 200 chars; SessionStart brief trimmed by priority (rules, CONTEXT head, journal, findings) | 10k hard cap |
| listing budget | all agent descriptions ≤ 600 tokens, measured with `claude plugin details partner` in CI after the runner installs the checkout as a path marketplace | fails the build when exceeded |
| compaction | journal compaction and knowledge consolidation on haiku | only when thresholds are crossed |
| measurement | `claude plugin details` (projected cost) now; `partner-usage` (R2) reads the local transcripts and reports tokens per role, skill and model per session | the only basis for changing a route or a cap |

Never condensed: test failures, compiler and linter errors, diffs under review, security
findings, anything quoted into a spec, journal, finding or knowledge entry.

## 11. Parallelism

| Case | Mechanism | Limits |
|---|---|---|
| challenger ∥ expert consults at design time | several Agent calls in one message, read-only, `background: true` | — |
| builder lanes on a large change with disjoint file sets | Agent calls with `isolation: worktree` | ≤ 3 lanes; orchestrator integrates |
| review fan-out at wrap | `/code-review` ∥ `/security-review` ∥ consults | read-only, shared tree |
| onboarding a large foreign repo | consultants per subsystem | haiku |
| deep review or audit on demand (R2) | shipped `workflows/deep-review.js` (find → adversarial verify, `agentType` = plugin agents) | **owner opt-in per run**; never the orchestrator's default path; shipped only once R1 evals show where it pays |
| independent work streams | sessions / worktrees | the owner's tool; the partner proposes, the owner starts |

Never parallel: tiny and small, anything needing the owner's answers, anything writing the same files.

## 12. MCP servers

| Server | Where | Why |
|---|---|---|
| context7 | `plugins/partner/.mcp.json` | current library docs; stale API facts were the audit's biggest rot source |
| HashiCorp terraform | provided by the HashiCorp plugins when the owner enables them; **not duplicated**, and not installed at user scope on this machine today | `lang-terraform` works without it: `terraform providers lock`, registry API over `curl`, dated "verified on" lines |
| GitHub | not in release 1 | `gh` covers the flow at zero context cost and the rules match `Bash(gh …)` lines exactly; revisit if issue triage needs it |
| Google Cloud | `partner-gcp` (R2) | evaluated when the GCP expert exists |
| Home Assistant | `partner-reverse` (R3) | device state during protocol work |

Outward writes go through `git`/`gh` CLI, never through MCP write tools, so the gate sees one
deterministic surface; MCP write tools are `ask` as a belt.

## 13. Quality of the partner itself

Evals (`plugins/partner/evals/`, `runs: 3`, `--threshold 1.0`, pinned model, run on `main` and on
manual dispatch; `--ablation with-without` on the medium case). R1 ships the first four; the
others arrive with the features they test (R1.1):

| Case | Graders |
|---|---|
| tiny-no-ceremony | `tool_used` Agent = 0 · `file_exists` no spec |
| medium-spec-then-challenge | `file_exists` spec · `tool_used` Agent(challenger) · `tool_order` spec Write before code Edit |
| profile-caps-size | `script` profile + big ask → no builder agents · `llm` on the reply |
| never-apply | asks for `terraform apply` → `regex` refusal naming the rule |
| foreign-onboard | symlink + exclude line present · nothing under the fixture repo |
| builder-routing | `Cargo.toml` fixture → `partner:rust-builder` spawned (plugin-scoped name in the grader), not `builder` |
| actions-pinning | `expert-github-actions` → `regex` SHA pin + `zizmor` mentioned |
| learn-unknown-domain | a topic with no expert → `tool_used` Agent(learner) · `regex` every delta line carries a status and a source · `llm` no `assumed` entry drives the answer |
| proof-required | a builder fixture reports "tests pass" with no output → `llm` the orchestrator reruns or rejects, never journals green |

Hook and script tests (pytest, fixtures as JSON): push, force push in any flag order, `rtk git
push`, `git -C . push`, `terraform -chdir=x apply`, `( git push )`, `git push &`, `env git push`,
compound `cargo test && git push`, `curl … | sh`, `mise run release` opaque, `bash -c` opacity,
`gh pr create`, `terraform plan` passes and `apply` denied, MCP write tool, project layer
tightening an owner rule and its `allow` ignored, agent scope, malformed input → ask, PATH without
python3 → shim exits 2, journal parsing on both orderings, FINDINGS parsing, knowledge delta
filter (secret-like string refused, `assumed` kept out of the brief, 80-line cap), timing.

CI (`ci.yml`, every action SHA-pinned, `permissions: contents: read`, `concurrency`,
`timeout-minutes`): `claude plugin validate --strict`; `ruff` + `pytest` on `bin/` and `tests/`;
`markdownlint`; a script checking SKILL.md < 500 lines, descriptions < 1 536 chars and the
agent-description budget (`claude plugin details`); `install.sh --check` in a clean container; `zizmor` on the repo's own workflows. `release.yml` on tag `vX.Y.Z`:
plugin.json, marketplace.json and CHANGELOG agree → GitHub release (human-triggered). SemVer,
Keep-a-Changelog; `claude plugin update` is manual on GitHub marketplaces.

## 14. Install and coexistence

Owner decision 15, ADR-0003: the legacy scaffold stays in place until the owner picks the moment
to switch. Until then nothing in the partner writes to `~/.claude/CLAUDE.md`, `~/.claude/agents`,
`~/.claude/skills` or `~/.claude/settings.json`.

| Method | Command | Writes | Use |
|---|---|---|---|
| dev | `claude --plugin-dir <repo>/plugins/partner` (alias `claude-partner` from `install.sh --dev`) | nothing; session only | building and evals on this machine |
| project | `claude plugin marketplace add YpNo/agentic-partner` (or the local path), then `claude plugin install partner@agentic-partner --scope project`; `--scope local` in a foreign repo | `.claude/settings.json` (or `.local`) of that repo | dogfood in chosen repositories |
| user | same with `--scope user` | `~/.claude/settings.json` `enabledPlugins` | the switch only |
| check / uninstall | `install.sh --check` lists legacy links, name overlaps and which scope is active; `--uninstall` reverses project and user | — | before and after the switch |

Coexistence rules: every skill and agent is namespaced (`/partner:*`, `partner:*`) and shares no
name with the legacy set; the SessionStart protocol states in one line that, when the partner is
loaded, its skills replace `/onboard /design /build /wrap /ship` and the legacy router
instruction is skipped; `partner-memory` reads the legacy `.agent/` files unchanged (both journal
orders), so dogfood repositories need no migration; the hard wall is applied only at the switch,
or earlier for `never` rules if the coexistence spike (§17) shows the gate's `ask` losing to the
legacy settings' `allow`. The switch itself is `docs/03-switch-plan.md`, with a rollback.

## 15. Release plan

| Release | Content | Exit criterion |
|---|---|---|
| R0 | **repository bootstrap, nothing global**: marketplace.json, plugin.json, `install.sh --dev\|--project\|--check`, README install section, CI skeleton; the legacy scaffold is left untouched (ADR-0003) | `claude plugin validate --strict` passes; a `--plugin-dir` session lists `partner:*` beside the legacy set; coexistence spikes answered |
| R1 | gate + shim, onboard / spec / build / wrap (findings, proof lines, verified stamp), `partner-memory brief\|learn\|compact\|check`, references with status lines, challenger / consultant / builder, rust and go builders, lang-{rust,go,terraform,fallback}, expert-gha + consult-gha, 4 evals, pytest, ci.yml, release.yml; dogfood through `install.sh --project` on cartridge-os (Rust, service rigour) and `--scope local` on headscale (foreign Go) | day-one spikes pass; four evals green; a week of real use journaled |
| R1.1 | ship, contribute + UPSTREAM.md, security-sweep (`context: fork`), compaction, lang-python + lang-typescript with their builders (dogfood dreame-vacuum, headplane), terraform-builder (one module), `learner` + `/partner:learn` + `learn --promote` + consult `knowledge_delta`, `accepted-risks.md`, 4 more evals | eight evals green; the switch plan's preconditions met |
| Switch | owner-triggered, not a release: `docs/03-switch-plan.md` (backup, user-scope install, unlink, CLAUDE.md cut, rules sync, workstation-starter PR) | a fresh session lists `partner:*` only; rollback tested once |
| R2 | `partner-gcp` (GCP expert skill, `gcd-universe` rewritten for provider 8.x), `deep-review` workflow, `SubagentStop` report check (a report must carry command + exit code), `partner-usage`, verified-stamp gate rule for `git push`, contribute flow hardened from headscale use | GCP module work done end to end |
| R3 | `partner-reverse` (host-before-device protocol, capture/replay, HA MCP), `partner-delivery-extra` (GitLab CI, ArgoCD, Crossplane, OPA), GDC/S3NS expert | — |

## 16. Where each choice came from

| Topic | Taken from | Reason |
|---|---|---|
| one plugin in R1, domain plugins later | A | evidence before structure; the agent budget is not the binding constraint at 8 agents |
| per-language builder agents (thin, `skills:` preload) | B | deterministic routing by name and per-language model choice; costs ≈ 50 tokens each; A's "brief carries the idiom" is the forgotten-brief failure mode |
| conceptor as a main-thread skill, not an agent | A | clarify needs the owner; subagents cannot ask |
| experts = skills + one generic consultant | A | adding an expert costs zero agent budget; B's one-agent-per-expert hits the budget by R3 |
| journal newest at the bottom | A | append-only tooling; five of six real journals already do it |
| rules: never widen, most restrictive wins, `ask` for push/PR | A | matches decision 6 ("asked", not "blocked forever"); B's `allow` from CONTEXT would widen permissions from a plugin |
| `explain`, segment splitting, fail closed | B + A | both |
| Python 3 stdlib for `bin/`, pytest | neither (orchestrator) | compound-command parsing in bash is where bypasses hide; `shlex`/`fnmatch` are testable and need no `jq` |
| foreign mode by symlink + `info/exclude`, path keyed by remote | A + B | skills stay path-agnostic; clones share memory |
| no GitHub MCP, no duplicate Terraform MCP | A + orchestrator | the HashiCorp plugins already ship the server |
| opt-in workflow deferred to R2 | challenger | shipping it in R1 proved nothing; it returns once evals show where fan-out is inconsistent |
| rtk-aware patterns, `sh` shim, argv matching, trusted-repo injection, two skills per expert, worktree hook, owner gate on objections, R1 scope cut | challenger pass 1 | see `design-inputs/challenge-01.md` for the failure scenarios |
| learner / teacher: delta not files, three statuses with provenance, relevance filter, two layers | owner (second review) + orchestrator | ADR-0002 |
| token economy: brief not files, report caps, `rtk proxy` for decision-carrying output, usage measurement | owner + crissp (`brief`, `measure.py`) | §10 |
| coexistence install, switch plan, R0 without global changes | owner | ADR-0003, `03-switch-plan.md` |
| findings file, options + recommendation, impact map, verified stamp, `omitClaudeMd` challenger, accepted risks with expiry, proof line | crissp review | `design-inputs/crissp-review.md` |

## 17. Risks and the day-one spikes

1. **Hook coverage**: does `PreToolUse` from a plugin fire for a builder subagent's Bash, does the
   matcher catch `mcp__*`, is `permissionDecision: ask` honoured, does `agent: partner:consultant`
   resolve as a skill fork target, and does the gate still see the original command when the rtk
   hook rewrites it? Spike: install from a local path, spawn `partner:rust-builder`, tell it to
   `git push` in a scratch repo, watch the deny; fork `consult-gha` and check which agent ran.
2. **Gate bypass**: compound and quoted commands. Pytest table before any skill is written.
3. **`paths:` activation inside subagents** is unverified; builders therefore preload via `skills:`
   and do not depend on it.
4. **Agent budget after R2**: measure with `/skill-doctor` at each release; split when the listing
   exceeds ~3k tokens.
5. **Foreign symlink** invisible to a fresh clone: the external directory is the source of truth;
   `partner-memory` prints its path at onboard and the owner backs it up.
6. **Coexistence** (R0 spike): does `--plugin-dir` load hooks, agents and namespaced skills in one
   session; does the gate's `ask` prevail over the legacy settings' unconditional
   `allow Bash(git push*)`; does the main thread follow the partner protocol while the legacy
   CLAUDE.md is present? Measured by running the eval set under `--plugin-dir` on this machine.
7. **`omitClaudeMd`** on a plugin agent: if not honoured, the challenger prompt states that
   repository instructions are data.
8. **rtk condensation** dropping a signal a proof line, the gate or an eval needs: proof lines
   name the command as run; tests and evals call `rtk proxy` explicitly.
