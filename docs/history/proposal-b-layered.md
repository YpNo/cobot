# Proposal B — complete and layered (architect agent, 2026-11-06)

GOAL: One public marketplace repo whose plugins make Claude Code's main thread a governed
orchestrator that delegates to a conceptor, a challenger, per-language builders, domain experts
and built-in reviewers, where each repo enables only the plugins its stack needs and every
outward action is gated by a deterministic rules hook.

## Layout (release 1)
```
agentic-partner/
  .claude-plugin/marketplace.json            name=agentic-partner, core defaultEnabled
  plugins/core/                              always enabled; 4 agents
    .claude-plugin/plugin.json
    agents/conceptor.md challenger.md scout.md reviewer.md
    skills/onboard design(+spec-template.md) build wrap ship rules fallback-lang
    hooks/hooks.json                         SessionStart, PreToolUse(Bash|mcp__github__.*), SubagentStop
    bin/partner-session partner-rules partner-memory   (POSIX sh, no jq/yq)
    rules/default.rules
    templates/CONTEXT.md JOURNAL.md SPEC.md UPSTREAM.md
    settings/permissions.deny.json           hard-guarantee block the USER pastes
    .mcp.json                                context7 + github (read-only toolsets)
    evals/{rules-never-push,size-tiny-no-agents,size-medium-conceptor-first,foreign-memory,
           challenger-verdict,builder-routing}/  evals/mocks/
  plugins/lang-rust|lang-go|lang-python|lang-typescript|lang-terraform/
    plugin.json agents/<lang>-builder.md skills/<lang>/SKILL.md (+refs); terraform adds .mcp.json
  plugins/delivery-github/ plugin.json agents/github-expert.md skills/actions-security skills/release
  tests/hooks/*.bats tests/fixtures/{own-repo,foreign-fork}/
  .github/workflows/ci.yml release.yml  CHANGELOG.md README.md docs/
```
Split rationale: agent descriptions are paid in every session, so the unit of split is "what a
repo never needs": one plugin per language (1 agent) and per expert domain (1 agent). A Rust CLI
repo enables core + lang-rust + delivery-github = 6 agents. Terraform's MCP schema loads only
where `*.tf` exists. Protocol injected by SessionStart `additionalContext` ≤ 3 000 chars.

## Role catalogue
| Role | Kind | Tools | Model/effort | Returns | Called by |
|---|---|---|---|---|---|
| orchestrator | main thread | all | user's | decisions; inline edits for tiny and `hard` tasks | user |
| scout | agent | Read Grep Glob Bash | haiku/low | verified fingerprint + commands | /onboard |
| conceptor | agent, memory: project | Read Grep Glob Write Edit (spec only) | opus/high | `specs/<slug>.md` (principles, stories+AC, ≤5 clarify Qs, plan, T001 tasks tagged hard/parallel); converge delta | /design, /wrap |
| challenger | agent | Read Grep Glob | opus/high | SOUND or ranked objections each with a simpler alternative | orchestrator |
| `<lang>-builder` ×5 + fallback-lang | agent, skills: preload | Read Grep Glob Edit Write Bash | sonnet/medium | report: files, tests run + output, open; never commits | /build |
| github-expert | agent | Read Grep Glob Bash (gh read, actionlint, zizmor) | opus/medium | findings (severity, file:line, fix) | /design, /ship, wrap |
| gcp-expert, re-expert (R2) | agent | Read Grep Glob Bash | opus/medium–high | findings / hypotheses + evidence log | orchestrator |
| /code-review /security-review /simplify | built-in | — | — | findings | /wrap |
| reviewer | agent (fallback) | Read Grep Glob | sonnet/medium | ranked findings | when built-ins absent |
| feature | workflow (R2) | per stage | per stage | merged branch + report | user opt-in |
No agent has `Agent` in its tools: depth is exactly one.

## Workflow schema
```
intake -> classify(profile x size) --tiny--> edit inline -> focused test -> journal
                                   --small-> builder -> /code-review -> journal
   |                               --medium> conceptor(spec+clarify) ==> [challenger || experts] -> tasks
   |                                          -> builders (parallel if disjoint) -> converge -> [review fan-out] -> wrap
   +-- large = medium + worktree per builder + Workflow script (R2) + security-sweep + github-expert at /ship
gates: user answers clarify | SOUND or objections folded | tests green per task | converge delta empty | findings triaged
```
Sizes: tiny ≤1 file no behaviour change; small ≤3 files one module; medium new API / multi-module;
large new component / infra / cross-repo. SubagentStop hook blocks a builder report lacking `TESTS:`.

## Rules engine
One rule per line, `<decision> <permission-rule>` in Claude's matcher syntax: `never Bash(git push *)`,
`ask Bash(git commit *)`, `allow Bash(cargo test *)`, `never mcp__github__create_pull_request`.
Layers: plugin default < `~/.claude/partner/rules` < `<memory-dir>/rules`. `never` is monotonic;
ask/allow most-specific layer first. Malformed file fails closed to `ask`.
Enforcement: PreToolUse (Bash | mcp__github__.*) runs `bin/partner-rules decide` on every segment
of the command (split on `; && || |`), returns permissionDecision deny/ask/allow; exit 2 fallback.
Hard guarantee: `/partner:rules install` prints a `permissions.deny` block for the user to paste;
`/partner:rules explain "<cmd>"` shows the winning rule.
Defaults: never — git push, gh pr create|merge|comment|review, gh issue comment, gh release,
gh api write verbs, terraform|tofu apply|destroy, kubectl apply|delete, gcloud create|delete,
cargo|npm|uv publish, git tag, mcp__github create/update/merge. ask — git commit, git rebase,
git checkout --, rm -r, terraform plan, docker run. allow — CONTEXT.md verified commands,
git status|diff|log|add, gh pr view|checks|diff.

## Memory
Load order: CONTEXT.md (profile, verified commands, constraints, 10-line Shape; ARCHITECTURE.md
only for library/service/infra), JOURNAL.md (newest on top; SessionStart injects top 2 entries),
`specs/<slug>.md` (moved to `specs/done/` after converge), UPSTREAM.md (foreign repos), optional
project rules layer. Pruning: /wrap folds entries beyond 20 into one History paragraph; warn when
CONTEXT.md > 150 lines.
Foreign mode: `bin/partner-memory resolve` → in-repo `.agent/` when it exists or every remote
owner is in `~/.claude/partner/identities`; otherwise `${XDG_DATA_HOME}/agentic-partner/memory/
<host>/<owner>/<repo>/`, keyed by remote. Foreign mode writes nothing into the repo; plugins
enabled with `--scope local`.

## Model routing
orchestrator: user's model (also builds `hard` tasks inline) · conceptor, challenger: opus/high ·
experts: opus/medium · builders: sonnet/medium (tasks tagged hard stay in main thread) · scout,
fallback reviewer: haiku/sonnet · evals: pinned id in CI only; release.yml fails on raw ids in frontmatter.

## Parallelism
Agent tool, several calls per message, `background: true` for read-only roles; `isolation:
worktree` only on large; shipped `workflows/feature.js` (R2) when the user opts in. Never parallel:
tiny, small, anything writing the same files.

## MCP
core: context7 (current docs), github read-only (repos, issues, pull_requests). lang-terraform:
HashiCorp terraform MCP. Outward writes via gh/git CLI only (hook matches command strings); MCP
write tools are `never`. R2 evaluates a Google Cloud MCP.

## Quality
Evals (runs 3, threshold 1.0, pinned model, ablation on the medium case): rules-never-push,
size-tiny-no-agents, size-medium-conceptor-first, foreign-memory, challenger-verdict,
builder-routing, actions-pinning. Hook tests: bats for partner-rules and partner-memory;
shellcheck, shfmt. CI: validate --strict, hooks, docs lints (SKILL.md < 500 lines, description
budget), zizmor on own workflows; evals nightly / on label. release.yml on tag: per-plugin
version bump check, changelog entry, GitHub release.

## Release plan
R1: core, five thin language plugins, delivery-github, tests + CI. R2: /contribute + UPSTREAM.md,
cloud-gcp (+ gcd-universe), reverse, security-sweep (context: fork), workflows/feature.js,
SubagentStop check. R3: cloud-gdc, delivery-gitlab, delivery-gitops, policy-opa, Ansible, expert memory.

## Trade-offs / rejected / do not do / risk
Nine plugins = nine enablement entries and versions. Rules hook is string matching (stops honest
and careless attempts, not determined obfuscation); the pasted deny block is the wall. Rejected: one
monolithic plugin with a single builder (pays every description and MCP schema everywhere).
Do not: plugin CLAUDE.md, second review agent, coverage numbers, writing into foreign repos, relying
on hook `if`, routing outward actions through MCP. Risk: unverified — plugin agent names in the
Agent tool, PreToolUse firing for subagent Bash, settings.local.json git-ignored. Day-one spike:
install core locally, spawn rust-builder, make it `git push` in a scratch repo, watch the deny.
