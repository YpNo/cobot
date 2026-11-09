# Architecture

For agents and architects. The README is for people; the full design and its reasons are in
[02-design.md](02-design.md), the decisions in [01-decisions.md](01-decisions.md) and
[adr/](adr/). This page is the map.

## Layers

| Layer | What | Where |
|---|---|---|
| Protocol | ≤ 3k-char orchestrator rules injected at session start | `plugins/cobot/protocol.md` |
| Gate | `PreToolUse` hook on Bash, Edit, Write, NotebookEdit and MCP tools; three rule layers; never widens; blocks on failure | `hooks/gate.sh` → `bin/cobot-rules`, `rules/default.rules` |
| Memory | `.agent/CONTEXT.md`, `JOURNAL.md`, `FINDINGS.md`, `specs/`, `knowledge/`; trusted repositories only; foreign mode keeps memory outside the tree | `bin/cobot-memory`, `bin/cobot-session` |
| Learning | dated knowledge lines with a status and a source; staleness in the brief (versions 30 days, idiom 90); deltas applied by `cobot-memory learn`, promoted into this repository by `learn --promote`; a weekly refresh PR | `bin/_cobot_knowledge.py`, `agents/learner.md`, `skills/learn`, `.github/workflows/knowledge-refresh.yml` |
| Currency | how far the lockfiles are behind and whether advisories exist, through the ecosystems' own tools, cached per repository; one line in the brief | `bin/cobot-deps` |
| Report check | `PostToolUse` hook on Agent: a builder report without a command and an exit code goes back | `hooks/report.sh` → `bin/cobot-rules report` |

## Roster

| Kind | Members | Where |
|---|---|---|
| Agents | `challenger` (red team), `consultant` (read-only experts), `learner` (read-only research), `builder`, `rust-builder`, `go-builder`, `python-builder`, `typescript-builder`, `terraform-builder` | `plugins/cobot/agents/` |
| Workflow skills | `/cobot:onboard`, `/cobot:spec`, `/cobot:build`, `/cobot:wrap`, `/cobot:rules`, `/cobot:learn`, `/cobot:ship`, `/cobot:contribute`, `/cobot:security-sweep` | `plugins/cobot/skills/` |
| Consults (forked, read-only audits) | `consult-gha`, `consult-gitlab-ci`, `consult-containers`, `consult-gcp`, `consult-kubernetes`, `consult-service-mesh`, `consult-ui` | `plugins/cobot/skills/` |
| Knowledge skills (path-gated) | `lang-rust`, `lang-go`, `lang-python`, `lang-typescript`, `lang-terraform`, `lang-fallback`, `expert-gha`, `expert-cicd`, `expert-gitlab-ci`, `expert-ui`, `expert-containers`, `expert-gcp`, `expert-kubernetes`, `expert-service-mesh` | `plugins/cobot/skills/` |

Knowledge is a skill, isolation is an agent. Only the orchestrator writes memory, through
`cobot-memory`. Builders never commit. See ADR-0001 to ADR-0003; experts as skill pairs in
ADR-0005 and ADR-0006.

## Flow

Intake names the size (tiny, small, medium, large) and the profile caps it. Tiny and small work
is done in the main thread with a focused check. Medium and large work goes through
`/cobot:spec` (≤ 5 clarify questions, challenger and consults in parallel), `/cobot:build` (one
builder per task, up to three worktree lanes, proof lines checked), then `/cobot:wrap` (full
checks, reviews, journal with a verified stamp). One spec is one branch and one pull request.

## Memory commands

The orchestrator calls these; they also work by hand from a checkout:

```bash
plugins/cobot/bin/cobot-memory check
```

```bash
plugins/cobot/bin/cobot-memory findings add "ci.yml" "checkout is on a floating tag"
```

```bash
plugins/cobot/bin/cobot-memory knowledge --stale
```

```bash
plugins/cobot/bin/cobot-memory learn --promote --dry-run '{"topic": "go", "entries": []}'
```

```bash
plugins/cobot/bin/cobot-deps check --fresh
```

`cobot-usage [--since DATE] [--session PREFIX] [--json]` reads this repository's local Claude Code
transcripts (and its worktrees') and reports requests and tokens per session, model and agent
type plus Skill and Agent call counts, never message text. Claude Code's `/usage` shows the live
session; this is the history a routing decision needs (design §10).

## Security model

The gate is argv and pattern matching: it stops honest and careless attempts, not determined
obfuscation. Interpreters running code, task runners, remote execution and command substitution
are opaque and ask. `mise` tasks, `make` targets (read from the Makefile), a shell's `-c` string
and container or sandbox entry wrappers (`distrobox enter`, `toolbox run`, `docker exec`,
`nix develop -c`, …) are looked through and the command behind them is judged.

MCP tools are judged by name: a read (`list`, `get`, `describe`, `search`, `read` first, and no
write word joined to it as in `get_or_create`) and the desktop app's own UI tools are silent;
every other MCP tool asks, a browser server's clicks and navigation included, since it acts with
the owner's sign-ins. An owner or project `ask` outranks a read; `never` outranks everything.

Hooks run as the user. An untrusted repository's `.agent/` is never injected into the session;
that protection is advisory for the model's own reads.
