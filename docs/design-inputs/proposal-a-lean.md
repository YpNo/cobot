# Proposal A — lean (architect agent, 2026-11-06)

GOAL: One public marketplace repo whose single release-1 plugin makes Claude Code's main thread a
governed orchestrator: it classifies work by profile and size, writes one spec file per
non-trivial change, delegates only where isolation earns its tokens (challenger, parallel
builders, expert consults), and is blocked deterministically from every outward-facing action by
a hook that reads a plain rules file — proven on cartridge-os, headscale, server-automation and a
Terraform module before anything is split or generalised.

## Layout (release 1)
```
agentic-partner/
  .claude-plugin/marketplace.json        plugins: [partner]  (R2 adds partner-gcp, R3 partner-reverse)
  plugins/partner/
    .claude-plugin/plugin.json
    agents/challenger.md builder.md consultant.md          # 3 agents ≈ 1k of the 15k budget
    skills/onboard (+templates CONTEXT.md JOURNAL.md)       # fingerprint, profile, commands, foreign mode
    skills/spec (+template.md)                              # CONCEPTOR: principles-once, spec+clarify+plan+tasks
    skills/build  skills/wrap  skills/ship  skills/contribute
    skills/lang-{rust,go,python,typescript,terraform,fallback}   # paths-gated, not user-invocable
    skills/expert-github-actions (+CONSULT.md)              # inline idiom + forked consult checklist
    skills/security-sweep (+scripts/sweep.sh)               # forked into consultant
    hooks/hooks.json session-start.sh rules-gate.sh
    rules/default.rules   bin/partner-rules  bin/partner-memory
    .mcp.json                                               # context7 only
    evals/<5 cases>/
  tests/hooks/*.bats  .github/workflows/ci.yml release.yml  README CHANGELOG LICENSE docs/
```
Single plugin because agents are the only budget that bites and there are three; language skills
are `paths:`-gated; domain content (GCP, reverse) becomes its own plugin when it exists. Split
further only when `/skill-doctor` shows the listing above ~3k tokens.

## Role catalogue
| Role | Kind | Tools | Model/effort | Returns | Called by |
|---|---|---|---|---|---|
| Orchestrator | main thread | all, under rules-gate | user's | decisions, final work | user |
| Conceptor | skill `/partner:spec`, main thread | Read Grep Glob Write(.agent/specs/*) AskUser | inherit/high | `.agent/specs/<slug>.md`: ≤5 clarify answers, plan, trade-offs, T001.. tasks | orchestrator (medium/large) |
| Challenger | agent, read-only | Read Grep Glob | inherit/high | SOUND or ranked objections each with a simpler alternative | spec, ship |
| Builder | agent, worktree when parallel | Read Edit Write Bash Grep Glob Skill (no Agent) | sonnet/medium; inherit for no_std, unsafe, Terraform state | diff summary + focused-test evidence + open questions | build (large path) |
| Language senior dev | skill `lang-*`, paths-gated, inline | knowledge | — | idiom, toolchain versions, pitfalls | auto-activation |
| Consultant | agent, read-only generic | Read Grep Glob Bash(read-only) WebFetch | sonnet/medium | findings: severity, file:line, fix, confidence | expert skills via `context: fork`, onboard |
| Expert GH Actions / release / supply chain | skill, dual entry | via consultant | sonnet/medium | findings | ship, wrap |
| Security sweep | skill `context: fork` → consultant | via consultant + scripts | sonnet/high | triaged findings vs baseline | wrap (service/library/infra), user |
| Reviewers | built-ins /code-review /security-review /simplify | — | — | findings | wrap; never re-implemented |

## Workflow schema
```
intake ─► classify(profile × size) ─┬ tiny   ─► edit ─► lint ─► done
                                    ├ small  ─► plan inline ─► build inline ─► /code-review ─► journal
                                    ├ medium ─► /spec(+clarify) ─► challenger ─gate─► tasks ─► build inline
                                    │           ─► wrap{/code-review ∥ /security-review ∥ consults} ─► converge ─► journal
                                    └ large  ─► /spec ─► challenger ─gate─► lanes ─► builders ∥ (worktrees, ≤3)
                                                ─► integrate + focused tests ─► wrap fan-out ─► converge ─► journal ─► (/ship, /contribute on request)
```
Profile caps size: spike/script never exceed small; infra never skips plan review.

## Rules engine
`<never|ask|allow> <Tool(pattern)>` per line, fnmatch over the full command, `#` comments.
Precedence: plugin default < `~/.claude/partner.rules` < `.agent/partner.rules`; most restrictive
wins; `never` cannot be relaxed. Hook (PreToolUse on Bash|Edit|Write|mcp__.*) splits compound
commands and judges every segment; `bash -c`, `sh -c`, `eval`, `xargs`, backticks → `ask`. Emits
deny or ask, never allow. `allow` lines only feed `partner-rules sync`, which writes settings for
the human. Fails closed. `partner-rules show|check|sync`.
Defaults: never — force push, terraform/tofu apply|destroy, cargo|npm|uv publish, gh release
create, git tag -a v*, editing settings.json (no self-widening). ask — git push, gh pr
create|comment|review, gh issue create|comment, ansible-playbook, kubectl apply|delete, gcloud
create|delete|update, rm -rf, git reset --hard, git clean, git rebase, mcp write tools.

## Memory
`.agent/CONTEXT.md` (profile, stack, environment, verified commands, constraints, ≤20-line Shape
replacing ARCHITECTURE.md) and `.agent/JOURNAL.md` (append-only, newest at the BOTTOM; hook reads
the tail). Specs in `.agent/specs/<slug>.md`. Session start injects CONTEXT head + last two
entries (≤10k chars). `partner-memory compact` when JOURNAL > 400 lines.
Foreign mode: `/partner:onboard --foreign` creates `~/.local/share/agentic-partner/repos/<host>/
<org>/<repo>/`, symlinks `.agent` to it, appends `.agent` to `.git/info/exclude`.

## Model routing
orchestrate/spec/plan/challenge: inherit, high · build standard: sonnet/medium · build risky
(no_std/unsafe Rust, Terraform state, auth): inherit/high · consult/sweep/fingerprint:
sonnet/medium (sweep high) · compaction/converge checklist: haiku/low. Spec tasks carry a `risk:`
mark that raises the builder model.

## Parallelism
Agent tool only. (1) large-path builder lanes, worktrees, max 3; (2) wrap review fan-out, read-only;
(3) foreign-repo onboarding of a large codebase. Workflow scripts deferred (user opt-in per run,
so not a mechanism the orchestrator can rely on).

## MCP
R1: context7 only (library-doc rot was the audit's biggest source of stale facts). GitHub MCP
rejected (gh covers it at zero context cost and rules match `Bash(gh …)`). Terraform MCP ships
with partner-gcp (R2). Home Assistant MCP with partner-reverse (R3).

## Quality
Evals: tiny-no-ceremony, medium-spec-then-challenge, profile-caps-size, never-apply,
foreign-onboard, + ablation on medium. Hook tests: bats fixtures (push, force push in any flag
order, compound commands, bash -c opacity, gh pr create, terraform plan vs apply, mcp write,
project tightening a user rule, malformed input, < 50 ms). CI: validate --strict, shellcheck +
shfmt, bats, zizmor; evals on main + dispatch. release.yml: tag → plugin.json / marketplace /
CHANGELOG agree → GitHub release (human-triggered).

## Release plan
R1: the layout above; dogfood on cartridge-os, server-automation, headscale (foreign), one
Terraform module; exit when five evals green and `~/.agents` removed from workstation-starter.
R2: partner-gcp (GCP skill, Terraform MCP, gcd-universe on provider 8.x), hardened GH Actions
consult, compaction tuned, Workflow script only if evals show inconsistent fan-out.
R3: partner-reverse (host-before-device, capture/replay, HA MCP), partner-delivery-extra (GitLab
CI, ArgoCD, Crossplane, OPA), GDC/S3NS expert.

## Trade-offs / rejected / risks
One builder + language skills: idiom reaches the builder only through the brief or the Skill
tool (mitigated by a templated brief). Hook never emits allow. Foreign symlink invisible to a
fresh clone. Rejected: three plugins and ~15 agents from day one (structure before evidence).
Risks to check first: rules-gate against compound/quoted commands; hooks.json matcher on mcp__*
names and `ask` honoured from a plugin hook; `paths:` activation inside a subagent; agent budget
after R2.
