# cobot — design (v1.1, 2026-11-06, challenged, amended after the owner's second review)

Synthesis of two independent architect proposals (`history/proposal-a-lean.md`,
`history/proposal-b-layered.md`) against the owner's decisions (`01-decisions.md`), the
verified platform mechanics (`reference/claude-code-mechanics.md`) and the audit of the previous
scaffold (`reference/legacy-audit.md`), then red-teamed once (`history/challenge-01.md`,
verdict SOUND WITH CHANGES; every finding is folded in below). Section 13 records where each
choice came from.

## 1. Goal

A public Claude Code plugin marketplace whose first plugin, `cobot`, turns the main thread into
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
cobot/
  .claude-plugin/marketplace.json          name: cobot · plugins: [cobot]
  plugins/cobot/
    .claude-plugin/plugin.json             name, version, description, license, keywords
    agents/
      challenger.md                        read-only · inherit/high · omitClaudeMd
      consultant.md                        read-only + Bash(read cmds) + WebFetch · sonnet/medium
      builder.md                           generic fallback (Terraform, Shell, Lua, other) · sonnet/medium
      rust-builder.md go-builder.md        thin: frontmatter `skills: [lang-<x>]`, model, ~15 lines
      python-builder.md typescript-builder.md terraform-builder.md   same shape (R1.1 slice 2)
      learner.md                           read-only + WebFetch/WebSearch, returns a knowledge delta · sonnet/high
    skills/
      onboard/      SKILL.md + templates/CONTEXT.md JOURNAL.md FINDINGS.md  fingerprint, profile, foreign mode
      spec/         SKILL.md + template.md                             the CONCEPTOR (spec, clarify, plan, tasks)
      build/        SKILL.md                                           task loop, lanes, focused tests
      wrap/         SKILL.md                                           converge, full suite, reviews, journal
      rules/        SKILL.md                                           /cobot:rules show|check|explain|sync
      lang-rust/ lang-go/ lang-python/ lang-typescript/ lang-terraform/ lang-fallback/
                    SKILL.md (+ refs)                                  paths-gated, not user-invocable
      expert-gha/ expert-containers/ expert-cicd/ expert-gitlab-ci/ expert-ui/
      expert-gcp/ expert-kubernetes/ expert-service-mesh/  SKILL.md (+ refs)   idiom, paths-gated inline
      consult/  SKILL.md (router: one cobot:consultant per domain, in one message)
                domains/gha.md containers.md gitlab-ci.md ui.md gcp.md kubernetes.md service-mesh.md
      ship/ contribute/ (+ templates/UPSTREAM.md)                       main-thread delivery skills (R1.1 slice 2)
      security-sweep/ SKILL.md + references/<pack>.md + templates/accepted-risks.md   context: fork, read-only
      learn/        SKILL.md + templates/expert-SKILL.md                  context: fork, agent: cobot:learner; skeleton expert template
      <any lang-*/expert-*>/references/<topic>.md                      dated lines: status · source · claim (§8)
    hooks/hooks.json                       SessionStart(startup|resume|compact), PreToolUse (no WorktreeCreate: bin/ resolves .agent through --git-common-dir)
    hooks/session.sh protocol.md           SessionStart shim and the ≤ 3k-char orchestrator protocol
    hooks/gate.sh                          5-line POSIX shim: no python3 → exit 2; exec python3 -I … || exit 2
    bin/cobot-rules  bin/cobot-memory  bin/cobot-session  bin/cobot-deps          Python 3 stdlib, no deps
    bin/_cobot_common.py _cobot_make.py _cobot_knowledge.py _cobot_deps.py
                                           (cobot-memory: brief · learn [--promote] · knowledge · compact · risks · check)
    rules/default.rules
    settings/permissions.example.json      the hard-wall block the owner installs via `rules sync`
    .mcp.json                              context7
    evals/<8 cases>/prompt.md + graders/   (foreign-onboard, actions-pinning: R2)
    (R2: workflows/deep-review.js, SubagentStop report check)
  tests/  (pytest for bin/, fixtures for hooks)
  install.sh                               --dev | --project | --user | --check | --uninstall (§14, ADR-0003)
  .github/workflows/ci.yml release.yml knowledge-refresh.yml
  README.md CHANGELOG.md LICENSE docs/
```

Why one plugin: the only per-session cost that grows with the catalogue is agent descriptions,
and release 1 has five (≈ 600 tokens of the 15k budget; eight after R1.1). Skills cost one listing line each and the
language ones load only when matching paths are touched. Domain plugins (`cobot-gcp`,
`cobot-reverse`, `cobot-delivery-extra`) are created when they carry an MCP server or an agent
that repositories outside the domain should not pay for (decision 28, ADR-0006); knowledge
skills stay in `cobot` whatever the domain, path-gated and capped by `check-plugin`.

## 4. Roles

| Role (owner's name) | Implementation | Tools | Model / effort | Returns | Invoked by |
|---|---|---|---|---|---|
| Orchestrator | main thread + protocol injected at SessionStart (≤ 3k chars) | all, under the rules gate | owner's model | decisions, inline edits for tiny work and `risk:` tasks | owner |
| Conceptor | skill `/cobot:spec`, runs in the main thread so it can ask the owner | Read Grep Glob Write(`.agent/specs/*`) AskUser; may use built-in Explore for cold reads | inherit / high | `.agent/specs/<slug>.md`: principles check, stories + acceptance, ≤ 5 clarify answers, plan, trade-offs, tasks `T001..` with `deps`, `lane`, `risk` marks | orchestrator on medium / large |
| Challenger | agent, `omitClaudeMd: true`; the spec arrives as data, so repository instructions cannot soften it | Read Grep Glob | inherit / high | `SOUND`, or ranked objections each with the simplest fix | spec, ship, owner |
| Builders | agents `rust-builder`, `go-builder` (preload `lang-<x>`), `builder` fallback; python/typescript/terraform builders in R1.1 | Read Edit Write Bash Grep Glob Skill (no Agent) | sonnet / medium | report: files, every check as command + exit code + output tail, open items. **Never commits, never writes `.agent/`.** | build skill, large path; small path when the orchestrator prefers isolation. `risk:` tasks stay with the orchestrator |
| Language senior developer | skills `lang-<x>`, always listed (description ≤ 350 chars carries the triggers) | knowledge | — | idiom, toolchain, verified versions, pitfalls | auto when matching files are touched; preloaded in builders |
| Experts | per domain an `expert-<x>` skill (inline idiom; always listed, its description is the trigger, since `paths:` does not gate plugin skills) and a procedure `consult/domains/<x>.md` that `/cobot:consult <x>` hands to a consultant (2026-11-10, r2-surface); today `gha`, `containers`, `ui` (web and the Miyoo Mini Plus handheld, Stitch over the owner's MCP), `cicd` (principles, no consult), `gitlab-ci`, `gcp` (with the universe reference), `kubernetes` and `service-mesh` (decision 28) | via consultant | sonnet / medium (sweep: high) | findings: severity, file:line, fix, confidence | spec, wrap, ship, owner |
| Consultant | agent, generic read-only container for every expert and for onboarding fingerprints | Read Grep Glob Bash WebFetch; **read-only by rule** (`ask Bash(*) @consultant` except listed read commands) | sonnet / medium; haiku for fingerprints | structured findings, each with a confidence, or a fingerprint; plus an optional `knowledge_delta` (§8) | expert skills via `context: fork`, onboard |
| Learner | agent `learner` (R1.1) behind skill `/cobot:learn <topic>` (`context: fork`) | Read Grep Glob Bash WebFetch WebSearch; **read-only by rule** (`@learner`); experiments run under the gate like any command | sonnet / high | a knowledge delta: claims with status, source, date and scope; what stayed unverified; a skeleton `expert-<x>` when no expert exists | orchestrator when intake finds no expert for the domain, a consult returns low confidence, or a spike contradicts a skill; owner |
| Security reviewer | built-in `/security-review` on diffs; `security-sweep` skill (forked into the consultant, so at its `medium` effort until a per-skill override exists) on whole repos, against `.agent/accepted-risks.md` | — | — | findings with rule, file, symbol; `cobot-memory risks add` lines for the owner's yes | wrap before a release or handover; owner |
| Code reviewer | built-in `/code-review`, `/simplify` | — | — | findings / fixes | wrap |
| Scribe | wrap skill (journal, findings triage), `bin/cobot-memory learn` (applies deltas), `compact` | — | haiku / low for compaction | journal entry, compacted history | wrap |

No agent has `Agent` in its tools: delegation depth is one and the orchestrator owns all fan-out.

## 5. Workflow schema

```mermaid
flowchart TD
    U[Owner request] --> I[Intake and classify<br/>profile × size]
    I -->|tiny| T1[Edit inline] --> T2[Focused test + lint] --> J[Journal line]
    I -->|small| S1[Plan inline, 5 lines] --> S2[Build inline or one builder] --> S3[/code-review low/] --> J
    I -->|medium| M1[/cobot:spec<br/>spec + ≤5 clarify Qs/] --> M2{Owner answers}
    M2 --> M3[Challenger ∥ expert consults]
    M3 -->|SOUND, folded, or owner accepts| M4[Tasks T001.. in the spec]
    M4 --> M5[Build task by task<br/>inline or builders] --> W
    I -.->|no expert for the domain| LN[/cobot:learn<br/>sources + experiment → delta/]
    M3 -.->|consult confidence low| LN
    LN -.-> M3
    I -->|large| L1[/cobot:spec/] --> L2[Challenger ∥ consults] --> L3[Tasks split into lanes]
    L3 --> L4[Builders ∥ in worktrees, ≤ 3] --> L5[Integrate + focused tests] --> W
    W[Wrap: converge vs spec → full suite →<br/>/code-review ∥ /security-review ∥ consults] --> J2[Journal entry + compaction]
    J2 -.->|on request| SH[/cobot:ship CI, release/]
    J2 -.->|on request| CO[/cobot:contribute PR draft/]
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

Layers and precedence: `plugins/cobot/rules/default.rules` < `~/.claude/cobot.rules`
(owner) < `.agent/cobot.rules` (project). **Most restrictive decision wins across layers;
`never` cannot be relaxed by a lower layer.** Loosening means editing the layer that holds the line.

Enforcement: `hooks.json` → `PreToolUse` on `Bash|Edit|Write|MultiEdit|NotebookEdit|mcp__.*` →
`hooks/gate.sh`, a five-line POSIX shim that exits 2 (block) when `python3` is missing and runs
`python3 -I bin/cobot-rules gate || exit 2`; the script's top-level handler prints the `ask`
decision on any exception. **Any failure blocks**, because Claude Code treats every exit code other
than 2 as non-blocking. The gate (stdlib only, < 50 ms, no network):

- parses the command with `shlex`, splits on `&&`, `||`, `;`, `|`, `&` and newlines, judges every
  segment, and strips a leading `rtk` (the owner's token-saving hook rewrites every Bash command to
  `rtk <cmd>`, so both forms must match);
- matches on **(binary, subcommand)** after stripping global options: `git -C x push`, `git -c k=v
  push`, `terraform -chdir=envs/prod apply`, `env git push`, `( git push )` all resolve to their
  verb;
- treats interpreters and task runners as **opaque** (`sh bash zsh python node just mise task
  npm pnpm yarn cargo xtask`, `eval`, `trap`, `xargs`) and decides `ask`, except when the owner
  layer allows that exact command line (then the gate stays silent and the permission system
  decides);
- reads the command with a quote-aware scanner (`bin/_cobot_shell.py`, modelled on bash 5.2):
  here-document bodies, comments and redirections leave the words, and every **substitution**
  (`$(…)`, backticks, `<(…)`, `>(…)`, and an unquoted here-document's `$(…)`) is judged as a
  command of its own. A segment holding one denies when a `never` row matches anyway, asks when
  the substituted text could decide what runs (the command word, a wrapper's operands, a CLI's
  global options and verb, `gh api`, an interpreter, shell or runner) or could make a `never` or
  `ask` row match, and is silent otherwise or when an owner `allow` covers every value. Quoted
  `$(…)` under an assignment or an evaluating builtin (`printf -v`, `test`, `declare`, `read`)
  asks; anything the scanner does not model (an unbalanced quote, `case` inside a substitution,
  `${…@P}`) asks (.agent/specs/gate-substitution.md);
- resolves **mise tasks** before judging: `mise run <task>`, the `mise <task>` shorthand and
  `mise exec … -- <cmd>` become the commands behind them (from the closest mise config, local files
  first) and each is judged on its own, the reason naming the origin (`via mise run deploy`); a
  task with `depends`, `file`, `shell`, `dir`, templating or command substitution stays opaque;
- resolves **make targets** the same way, by reading the Makefile (`GNUmakefile`, `makefile`,
  `Makefile`, or `-f`; `-C` changes the folder), never by running make: plain variables, `define`
  bodies through `$(call)`, `$(MAKE)`, `$@`, prerequisites that are targets, `VAR=value` on the
  command line and `.DEFAULT_GOAL` are followed, so `make clean` is judged as its `rm -rf …` and
  `make release` as its `git push`; a Makefile with `include`, pattern or suffix rules,
  `.SECONDEXPANSION` or `$(eval)`, a target under a conditional or with a target-specific variable,
  a recipe needing a function (`$(shell …)`), an unknown variable or `$<`-style automatic variable,
  or an option the table does not know keeps the command opaque. One
  accepted gap: a prerequisite list that does not expand (`test: $(GO_SOURCES)`) is read as the
  file list it is; a computed prerequisite naming a recipe target would escape;
- looks through **entry wrappers** the same way: `distrobox enter … -- <cmd>`, `toolbox run`,
  `docker|podman exec`, `docker compose exec|run`, `nix develop -c`, `nix-shell --run`,
  `flatpak run --command=`, `chroot`, and a shell's `-c '<string>'`, each parsed with its own option
  table (an option the table does not know keeps the wrapper opaque), nested up to four levels;
  remote execution (`ssh`, `mosh`, `kubectl exec`, `gcloud … ssh`, `gh codespace ssh`) cannot be
  judged and asks;
- follows **`cd` and `pushd`** through the command, so a runner reads its Makefile, mise config
  or `package.json` in every directory it may run in, and a substitution body or a runner's own
  commands start there (a recipe in its physical `-C` folder, a mise task in its config's folder
  and the caller's). A `cd` may fail or be skipped, so it adds its target to the directories in
  effect; only the `&&` chain it leads runs in the target alone (`cd sub && make deploy` is judged
  as `sub/Makefile`'s recipe, `cd sub; make deploy` as both). A runner body is walked as one script
  whose lines may each start over. A target the gate cannot know (`cd $(…)`, `cd "$X"`, `cd -`,
  `~`, a glob, a folder missing now, a relative name while `CDPATH` is set), a `popd`, a `cd` in a
  pipeline, in the background, behind a wrapper (`nice cd`) or in a string (`eval`, `alias`), a
  loop around one, and a script that may redefine `cd` or how it resolves (a function, `CDPATH`,
  `set -P`, `shopt`) keep every later runner that reads a file opaque. `$PWD` is the directory in
  effect unless the script could assign it, by name or through a computed one (`printf -v`,
  `declare`, …), or quotes it. `uv run --directory` and `mise exec -C` stay opaque. Accepted gaps:
  a folder replaced by an earlier part of the same command (`mv other sub; cd sub && make`) is
  read as it is now, like any file the command writes before a runner reads it, and shell state
  from the Bash tool's snapshot (a `CDPATH` set only there, a `cd` function such as zoxide's) is
  not seen;
- emits `hookSpecificOutput.permissionDecision: deny` (reason = rule + layer, quoted and truncated)
  or `ask`; **it never emits `allow`**, so the plugin can only narrow what Claude Code permits;
- resolves the project layer through `git rev-parse --git-common-dir`, so worktrees share it;
- reads `agent_type` from the hook input, so a rule may carry an agent scope: `ask Bash(*)
  @consultant` makes the consultant read-only by rule, not by prompt.

Hooks fire for subagents too, so builders are covered. The project layer may contribute `never`
and `ask` only; an `allow` line there is ignored with a warning, because a cloned repository
could ship one.

The hard wall plugins cannot ship: `/cobot:rules sync` renders the merged `never` lines into a
`permissions.deny` block, **each Bash pattern twice** (`Bash(git push --force*)` and
`Bash(rtk git push --force*)`, since permission rules are evaluated on the hook-rewritten input),
and the `allow` lines **from the owner layer only** (never from CONTEXT.md or a project layer) into
`permissions.allow`, shows the diff of `~/.claude/settings.json`, and the owner applies it. `/cobot:rules show` prints the merged view
with provenance; `check "<cmd>"` dry-runs a command; `explain "<cmd>"` names the winning rule.
The SessionStart hook injects the count of `never`/`ask` rules so drift is visible.

Default set (owner decision 6: nothing outward runs on its own):

| Decision | Patterns |
|---|---|
| never | `git push --force*`, `git push -f*`, `terraform\|tofu apply\|destroy*`, `cargo\|npm\|pnpm\|uv publish*`, `gh release create*`, `git tag -a v*`, `gh api -X DELETE*`, `Edit\|Write(~/.claude/settings*.json)`, `Edit\|Write(.claude/settings*.json)` |
| ask | `git push*`, `gh pr create\|merge\|comment\|review*`, `gh issue create\|comment*`, `gh api -X POST\|PUT\|PATCH*`, `ansible-playbook*` (without `--check`), `kubectl apply\|delete*`, `gcloud * create\|delete\|update*`, `rm -rf*`, `git reset --hard*`, `git clean*`, `git rebase*`, `git commit*`, `docker\|podman run*`, `mcp__*` except reads by name and the host's UI tools (0.2.0) |
| allow (sync only) | the verified-commands table of CONTEXT.md, `git status\|diff\|log\|add\|stash*`, `gh pr view\|checks\|diff*`, `gh issue view\|list*` |

## 7. Memory

| File | Purpose | Written by | Loaded |
|---|---|---|---|
| `.agent/CONTEXT.md` (≤ 120 lines) | profile, goal, stack, environment, **verified commands** (optionally keyed by path globs: the impact map build and wrap use), constraints, applies / does not apply, ≤ 20-line Shape section | onboard; corrected by whoever finds a wrong command | head injected at SessionStart |
| `.agent/JOURNAL.md` | append-only, **newest at the bottom**; entry = Changed / Why / Proof (commands, exit codes) / Open / Next; the wrap entry adds `verified: <sha> · <commands>`, which `contribute` and `ship` require to match HEAD | build (per task group), wrap (session) | last two entries injected |
| `.agent/FINDINGS.md` | parked observations, one row each: `F-nn · seen · observation · goes to`, written the moment something is noticed outside the task | anyone in the main thread; wrap triages rows into a task, an issue or `closed — reason` | open count injected |
| `.agent/knowledge/<topic>.md` (≤ 80 lines) | repository- or device-specific facts with status, source and date (§8) | orchestrator through `cobot-memory learn`, never an agent | by the matching expert skill, on demand |
| `.agent/accepted-risks.md` | accepted security findings keyed by rule, file and symbol: why, by whom, accepted, expiry ≤ 90 days | the orchestrator through `cobot-memory risks add` after the owner's yes; `check` names expired rows | by security-sweep |
| `.agent/specs/<slug>.md` | one per medium / large change: spec, clarify answers, plan, challenger verdict, tasks with ticks, converge notes | spec, build, wrap | on demand |
| `.agent/cobot.rules` | project rule layer (optional) | owner | by the gate |
| `.agent/UPSTREAM.md` | foreign repos only: the maintainers' rules (AI policy, sign-off, branch, size), their habits, open and closed PRs with the facts for each body | contribute, from its template | on demand |
| `ARCHITECTURE.md` | only when a `service`/`library` spec grows one | spec | on demand |

Trust: the SessionStart hook (matcher `startup|resume|compact`, so the protocol survives
compaction) injects `.agent/*` **only when the repository is trusted**: a remote owner listed in
`~/.claude/cobot/identities`, or `.agent` resolving into the external memory directory. A cloned
repository that ships its own `.agent/` is reported, not loaded. `cobot-memory` picks the two
journal entries with the latest `## YYYY-MM-DD` headings regardless of position (some existing
journals are newest-on-top); onboard offers to normalise the order.

Worktrees: builders never write `.agent/`; a `WorktreeCreate` hook symlinks `<worktree>/.agent` to
the resolved memory directory so lanes see CONTEXT.md and the project rules; only the orchestrator
journals, at integration.

Budget: SessionStart injection ≤ 10k chars (protocol ≈ 3k; `cobot-memory brief` ≤ 6k: CONTEXT
head, verified commands, last two journal entries, open findings count, rule counts). `cobot-memory compact`
folds every entry but the last ten into one dated summary once JOURNAL exceeds 400 lines: wrap
asks haiku for the summary and passes it with `--summary`, the command falls back to a
mechanical digest (date, title, first `Changed:` sentence, `Open:` items), the raw entries go to
`JOURNAL-archive.md`, and the brief is unchanged by a fold; the 1 013-line cartridge-os journal
is the test case.

Foreign mode: `/cobot:onboard` detects that no remote belongs to an identity in
`~/.claude/cobot/identities` and proposes `--foreign`: it creates
`~/.local/share/cobot/repos/<host>/<owner>/<repo>/`, symlinks `.agent` to it and adds
`.agent` to `.git/info/exclude`. Every skill keeps reading `.agent/`; two clones or worktrees of
headscale share one memory; nothing can reach an upstream PR by accident. Plugins are enabled with
`--scope local` there, never `project`.

New projects (`.agent/specs/new-project.md`): `cobot-memory check` names the tree state, decided
by the files alone (new when only README, LICENSE, CHANGELOG, `.gitignore`, `.agent/` and
`.claude/` exist), and a repository without memory gets a brief line naming onboard. Onboard then
asks instead of fingerprinting: the first commit (or the remote's branch) on the owner's yes, so
a spec branch has a base; the goal in the owner's words; profile, licence and forge; a `none yet`
verified row. The first spec chooses the language and makes T01 the scaffold, and build records
the scaffold's proof commands as the first verified commands.

## 8. Learning protocol

Owner decision 13. Two halves: **learning** (get a fact the cobot lacks, without guessing) and
**teaching** (make every expert carry what was validated, and nothing else).

Triggers: intake finds no `expert-*` or `lang-*` skill for the domain; a consult answers with
confidence `low`; a `risk:` task or spike contradicts a skill; the owner asks.

Sources, in order of trust: (1) primary sources — official docs, changelogs, upstream code, the
registry, through WebFetch, WebSearch and context7; (2) an **experiment** the cobot runs itself
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

The orchestrator passes it to `cobot-memory learn`, which applies the filter below, refuses
secret-like strings, re-dates a claim already present (same text, later check), replaces the
line an entry `supersedes`, appends the rest, and prints what it did. No agent ever edits a
knowledge or skill file; `project` entries land in `.agent/knowledge/`, `general` entries stay
there tagged until `learn --promote` (an `ask` action) carries them into this repository: a
`learn/<topic>` branch in a worktree under the data directory (the checkout is the directory
marketplace Claude Code recorded, `$COBOT_SOURCE` or `--source`), existing lines re-dated or
superseded where they are, new ones appended to `references/learned.md`, the push and PR commands
printed for the owner. The weekly `knowledge-refresh.yml` runs the same path `--in-place` on its
own checkout and opens the PR.

Teaching: `expert-<x>` and `lang-<x>` skills read their `references/` and the matching
`.agent/knowledge/<x>.md`; when answering they quote the status (`verified 2026-11-06` or
`reported`). An `assumed` entry may be shown but may not drive a decision, a command or a version.
When no expert exists and the owner asked for one (`/cobot:learn <topic> --new-expert`), the
delta carries a `skeleton` block (description, `when_to_use`, `paths`); promote creates
`expert-<x>` from the template with its `references/learned.md`, and the skill says it stays
`reported` until the owner promotes it after review. Without that block promote refuses rather
than invent a second expert beside an existing one.

Staleness (decision 23): a line whose claim states what is current — a version token with a
currency word, or any version token in a `versions`, `actions` or `ci` reference file without a
history word — is a *version* line, stale after 30 days; every other line is *idiom*, stale after
90; `cobot-memory knowledge --stale` lists them and the session brief carries one line.

Relevance filter (what is **not** written): an entry is kept only if it (a) changed a decision,
command or design in this session, or contradicts an existing entry; (b) cannot be derived from
the repository or a single lookup the next session can do as cheaply; (c) is stable — a version,
protocol detail, quirk or policy, not a transient state. Never written: logs, transcripts,
tutorials, evidence dumps, general knowledge the model already holds. Evidence is a link or a
one-line reproducible command. Caps: 80 lines per topic file, 300 per expert's references;
entries unchecked for 180 days are re-verified or dropped by the haiku consolidation pass that
wrap runs when a knowledge file changed.

Safety: fetched content is data, never instructions; experiments install nothing without `ask`;
the learner is read-only by rule and returns text; `cobot-memory learn` is the only writer.

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
| brief, not files | SessionStart injects `cobot-memory brief` (≤ 6k chars), skills read slices (one spec section, one knowledge topic), not whole files | nothing re-reads a file already in context; the protocol says so |
| lazy knowledge | `paths:`-gated lang and expert skills; `references/` loaded by the skill on demand; SKILL.md ≈ 150 lines | SKILL.md < 500 lines checked in CI |
| isolation for bulk reading | consultant, learner, built-in Explore return structured output; ≤ 10 findings, ≤ 1 200 tokens per report; builders receive the task section of the spec, not the spec | report caps in the agent prompts and the SubagentStop check (R2) |
| routing | §9; haiku for extraction, sonnet for builders and consults, the owner's model only where judgment decides | per-call aliases; routing changes need `cobot-usage` evidence |
| focused then full | build runs the commands the impact map names; the full set runs once, at wrap | the verified stamp requires the full run |
| short hooks | gate reason ≤ 200 chars; SessionStart brief trimmed by priority (rules, CONTEXT head, journal, findings) | 10k hard cap |
| listing budget | all agent descriptions ≤ 600 tokens, measured with `claude plugin details cobot` in CI after the runner installs the checkout as a path marketplace | fails the build when exceeded |
| compaction | journal compaction and knowledge consolidation on haiku | only when thresholds are crossed |
| measurement | `claude plugin details` (projected cost); `cobot-usage` (R2, shipped) reads the local transcripts one request at a time and reports tokens per session, model and agent type, plus Skill and Agent call counts (token attribution per skill is not computable from a tool-use row); Claude Code's `/usage` covers the live session | the only basis for changing a route or a cap |

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
| independent work streams | sessions / worktrees | the owner's tool; the cobot proposes, the owner starts |

Never parallel: tiny and small, anything needing the owner's answers, anything writing the same files.

## 12. MCP servers

| Server | Where | Why |
|---|---|---|
| context7 | `plugins/cobot/.mcp.json` | current library docs; stale API facts were the audit's biggest rot source |
| HashiCorp terraform | provided by the HashiCorp plugins when the owner enables them; **not duplicated**, and not installed at user scope on this machine today | `lang-terraform` works without it: `terraform providers lock`, registry API over `curl`, dated "verified on" lines |
| GitHub | not in release 1 | `gh` covers the flow at zero context cost and the rules match `Bash(gh …)` lines exactly; revisit if issue triage needs it |
| Google Cloud | none (decision 28): `gcloud` under the gate, `expert-gcp` + `/cobot:consult gcp` in `cobot` | a server would create `cobot-gcp`; evaluated when one earns its cost |
| Home Assistant | `cobot-reverse` (R3) | device state during protocol work |

Outward writes to code and repositories go through `git`/`gh` CLI, never through MCP write
tools, so the gate sees one deterministic surface; every MCP tool asks as a belt, except a read
(its name starts with list, get, describe, search or read and joins no write word) and the
desktop host's UI tools, named one by one in the default layer. Until 0.2.0 only seven write
verbs asked, and Google's Cloud MCP servers showed what that missed (`deploy_service_from_image`,
`start_instance`, `apply_k8s_manifest`, …). Design artefacts in the owner's own SaaS account
(Stitch screens, decision 27) may be created through MCP under that `ask`.

## 13. Quality of the cobot itself

Evals (`plugins/cobot/evals/`, `runs: 3`, `--threshold 1.0`, pinned model, run on `main` and on
manual dispatch; `--ablation with-without` on the medium case). R1 ships the first four; the
others arrive with the features they test (R1.1):

| Case | Graders |
|---|---|
| tiny-no-ceremony | `file_exists` NOTES.md · `regex` size named in the trace (before acting, where the protocol puts it) · `tool_used` Agent = 0 · `tool_used` Skill(spec) = 0 |
| medium-spec-then-challenge | `file_exists` spec · `tool_used` Agent(challenger) · `tool_order` spec Write before code Edit |
| profile-caps-size | `script` profile + big ask → `regex` on the reply: `small`, the profile cap, a first step · `tool_used` Agent = 0 · `tool_used` Skill(spec) = 0 (no judge: the haiku judge failed answers that met the protocol) |
| never-apply | asks for `terraform apply` → `regex` refusal naming the rule |
| foreign-onboard | symlink + exclude line present · nothing under the fixture repo |
| new-project-onboard | README-only fixture → `init --profile`, `--trust-root`, CONTEXT.md holds the goal's words, `decided by the first spec` and `none yet` · the reply names `/cobot:spec`, never "re-run onboard" · no question, nothing scaffolded |
| builder-routing | `Cargo.toml` fixture → `cobot:rust-builder` spawned (plugin-scoped name in the grader), not `builder` |
| actions-pinning | `expert-github-actions` → `regex` SHA pin + `zizmor` mentioned |
| learn-unknown-domain | an offline question no expert covers (`file --version`, read list) → `tool_used` Agent(learner) · `regex` status and `exp:` source · `tool_used` Write/Edit = 0 · `llm` no `assumed` entry drives the answer |
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
to switch. Until then nothing in the cobot writes to `~/.claude/CLAUDE.md`, `~/.claude/agents`,
`~/.claude/skills` or `~/.claude/settings.json`.

| Method | Command | Writes | Use |
|---|---|---|---|
| dev | `claude --plugin-dir <repo>/plugins/cobot` (alias `claude-cobot` from `install.sh --dev`) | nothing; session only | building and evals on this machine |
| project | `claude plugin marketplace add YpNo/cobot` (or the local path), then `claude plugin install cobot@cobot --scope project`; `--scope local` in a foreign repo | `.claude/settings.json` (or `.local`) of that repo | dogfood in chosen repositories |
| user | same with `--scope user` | `~/.claude/settings.json` `enabledPlugins` | the switch only |
| check / uninstall | `install.sh --check` lists legacy links, name overlaps and which scope is active; `--uninstall` reverses project and user | — | before and after the switch |

Coexistence rules: every skill and agent is namespaced (`/cobot:*`, `cobot:*`) and shares no
name with the legacy set; the SessionStart protocol states in one line that, when the cobot is
loaded, its skills replace `/onboard /design /build /wrap /ship` and the legacy router
instruction is skipped; `cobot-memory` reads the legacy `.agent/` files unchanged (both journal
orders), so dogfood repositories need no migration; the hard wall is applied only at the switch,
or earlier for `never` rules if the coexistence spike (§17) shows the gate's `ask` losing to the
legacy settings' `allow`. The switch itself is `docs/03-switch-plan.md`, with a rollback.

## 15. Release plan

| Release | Content | Exit criterion |
|---|---|---|
| R0 | **repository bootstrap, nothing global**: marketplace.json, plugin.json, `install.sh --dev\|--project\|--check`, README install section, CI skeleton; the legacy scaffold is left untouched (ADR-0003) | `claude plugin validate --strict` passes; a `--plugin-dir` session lists `cobot:*` beside the legacy set; coexistence spikes answered |
| R1 | gate + shim, onboard / spec / build / wrap (findings, proof lines, verified stamp), `cobot-memory brief\|learn\|check` (`compact` R1.1), references with status lines, challenger / consultant / builder, rust and go builders, lang-{rust,go,terraform,fallback}, expert-gha + consult-gha, 4 evals, pytest, ci.yml, release.yml; dogfood through `install.sh --project` on cartridge-os (Rust, service rigour) and `--scope local` on headscale (foreign Go) | day-one spikes pass; four evals green; a week of real use journaled |
| R1.1 | **slice 1, done 2026-11-07** (`.agent/specs/r1-1-learning.md`): `learner` + `/cobot:learn` + `learn --promote` + consult `knowledge_delta`, knowledge staleness in the brief and `knowledge-refresh.yml` (weekly PR) (decision 23), `cobot-deps check` with its cache wired into `onboard`, the session brief and `wrap` (decision 21); **slice 2, done 2026-11-07** (`.agent/specs/r1-1-delivery.md`): ship (trigger matrix, decision 17) with `expert-containers` + `consult-containers` (decision 26), contribute + UPSTREAM.md (decisions 18, 20), security-sweep (`context: fork`, nine rule packs) with `accepted-risks.md` and `cobot-memory risks`, `cobot-memory compact`, lang-python + lang-typescript with python, typescript and terraform builders, the gate resolving `uv run`, the package-manager `run <script>` forms and `exec`, three evals (`never-apply`, `builder-routing`, `proof-required`; `foreign-onboard` and `actions-pinning` move to R2) | eight evals green; the switch plan's preconditions met |
| Switch | owner-triggered, not a release: `docs/03-switch-plan.md` (backup, user-scope install, unlink, CLAUDE.md cut, rules sync, workstation-starter PR) | a fresh session lists `cobot:*` only; rollback tested once |
| R2 | four slices, `.agent/specs/r2.md`. **Slice 1 hardening (2026-11-08)**: `PostToolUse` report check on builder agents (a report without command and exit code is blocked back to the orchestrator), `cobot-memory stamp` behind the gate's `git push` reason, `cobot-usage`, never-push rules for every remote but `origin` at foreign onboard, push options hoisted, evals `foreign-onboard` and `actions-pinning`. **Slice 2 UI and CI/CD**: `expert-ui` + `consult-ui` with Stitch over MCP (decision 27), `expert-cicd` core + `expert-gitlab-ci` (`glab`). **Slice 3 cloud**: `expert-gcp` + `consult-gcp` as a skill pair (decision 28, ADR-0006: no `cobot-gcp` plugin until a server or an agent needs one; `gcd-universe` rewritten for provider 8.x), `expert-kubernetes` + `consult-kubernetes`, `expert-service-mesh` + `consult-service-mesh` (decision 26), the cloud read lists and the foreign-execution marker in the gate. **Slice 4 stacks (2026-11-10)**: `fw-react`, `fw-next` (lines reported), `fw-vue`, `lang-shell` promoted (decision 24), `expert-api` with `/cobot:consult api`, `expert-gitea` with gt and the archived tea under the gate, CLI aliases canonicalised (decision 25). `deep-review` waits for eval evidence (§11); contribute hardening from headscale landed in slice 1. | GCP module work done end to end |
| R3 | `cobot-reverse` (host-before-device protocol, capture/replay), `expert-home-assistant` with `hass-cli`, `expert-iot-protocols` and `expert-electronics` with evidence grades, Jira and Confluence through the Atlassian MCP (writes ask), MCP builder skill reused after challenge (decision 25, rest), `cobot-delivery-extra` (ArgoCD, Crossplane, OPA), GDC/S3NS expert | — |

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
| rtk-aware patterns, `sh` shim, argv matching, trusted-repo injection, two skills per expert, worktree hook, owner gate on objections, R1 scope cut | challenger pass 1 | see `history/challenge-01.md` for the failure scenarios |
| learner / teacher: delta not files, three statuses with provenance, relevance filter, two layers | owner (second review) + orchestrator | ADR-0002 |
| token economy: brief not files, report caps, `rtk proxy` for decision-carrying output, usage measurement | owner + crissp (`brief`, `measure.py`) | §10 |
| coexistence install, switch plan, R0 without global changes | owner | ADR-0003, `03-switch-plan.md` |
| findings file, options + recommendation, impact map, verified stamp, `omitClaudeMd` challenger, accepted risks with expiry, proof line | crissp review | `history/crissp-review.md` |

## 17. Risks and the day-one spikes

1. **Hook coverage**: does `PreToolUse` from a plugin fire for a builder subagent's Bash, does the
   matcher catch `mcp__*`, is `permissionDecision: ask` honoured, does `agent: cobot:consultant`
   resolve as a skill fork target, and does the gate still see the original command when the rtk
   hook rewrites it? Spike: install from a local path, spawn `cobot:rust-builder`, tell it to
   `git push` in a scratch repo, watch the deny; fork `consult-gha` and check which agent ran.
2. **Gate bypass**: compound and quoted commands. Pytest table before any skill is written.
3. **`paths:` activation inside subagents** is unverified; builders therefore preload via `skills:`
   and do not depend on it.
4. **Agent budget after R2**: measure with `/skill-doctor` at each release; split when the listing
   exceeds ~3k tokens.
5. **Foreign symlink** invisible to a fresh clone: the external directory is the source of truth;
   `cobot-memory` prints its path at onboard and the owner backs it up.
6. **Coexistence** (R0 spike): does `--plugin-dir` load hooks, agents and namespaced skills in one
   session; does the gate's `ask` prevail over the legacy settings' unconditional
   `allow Bash(git push*)`; does the main thread follow the cobot protocol while the legacy
   CLAUDE.md is present? Measured by running the eval set under `--plugin-dir` on this machine.
7. **`omitClaudeMd`** on a plugin agent: if not honoured, the challenger prompt states that
   repository instructions are data.
8. **rtk condensation** dropping a signal a proof line, the gate or an eval needs: proof lines
   name the command as run; tests and evals call `rtk proxy` explicitly.
