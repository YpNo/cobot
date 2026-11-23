# Architecture

For agents and architects. The README is for people; the full design and its reasons are in
[02-design.md](02-design.md), the decisions in [01-decisions.md](01-decisions.md) and
[adr/](adr/). This page is the map.

## Layers

| Layer | What | Where |
|---|---|---|
| Protocol | ≤ 3.4k-char orchestrator rules injected at session start | `plugins/cobot/protocol.md` |
| Gate | `PreToolUse` hook on Bash, Edit, Write, NotebookEdit and MCP tools; three rule layers; never widens, but for a command a session grant covers under Claude Code (ADR-0008); an error while judging asks, a gate that cannot run or exits non-zero blocks (exit 2 in the shim) | `hooks/gate.sh` → `bin/cobot-rules`, `rules/default.rules` |
| Memory | `.agent/CONTEXT.md`, `JOURNAL.md`, `FINDINGS.md`, `specs/`, `knowledge/`; trusted repositories only; foreign mode keeps memory outside the tree; the tree state (new, existing, inside another repository, not a repository) picks onboard's path; `cobot-memory init` writes the memory even when the config folder is read-only, then prints `trust not recorded:` with the command for the owner's terminal and exits 1 | `bin/cobot-memory` |
| Session brief | at most 10 000 characters: the protocol, rule counts, the memory brief (at most 6 000; when capped, Verified commands, Constraints and then Environment get room first, each only when it fits, and dropped sections are named; past three specs, their count and the three newest by `date:`), then the machine, knowledge and dependency lines | `hooks/session.sh` → `bin/cobot-session`, `bin/cobot-memory brief` |
| Learning | dated knowledge lines with a status and a source; staleness in the brief (versions 30 days, idiom 90); deltas applied by `cobot-memory learn`, promoted into this repository by `learn --promote`; a weekly refresh PR | `bin/_cobot_knowledge.py`, `claude-agents/learner.md`, `skills/learn`, `.github/workflows/knowledge-refresh.yml` |
| Currency | how far the lockfiles are behind and whether advisories exist, through the ecosystems' own tools, cached per repository; one line in the brief | `bin/cobot-deps` |
| Environment | the machine by presence (engines, runtime managers, isolation, container, OS and package manager, helpers), executing nothing: a hit on a PATH entry the repository controls is reported as not trusted and never run, a mise or asdf shim as a shim (not trusted in foreign mode); the owner's install route and declined helpers per host in `~/.claude/cobot/machine.md`; one line in the brief; the `runs:` header (decision 29) | `bin/cobot-env`, `bin/_cobot_env.py`, `skills/onboard/references/workstation.md` |
| Report check | a builder report without a command and an exit code goes back once, then through marked `UNPROVEN:` (decision 32); an investigator's report is judged by its own probe check (a verdict with a command and an exit code, or `Checks: none` with `inconclusive` and `Needs:`) and parks nothing (decision 35): `PostToolUse` on Agent where the call waits for its result (the CLI), `PreToolUse` on `SubagentHandback` where it runs in the background (the desktop app); one state per session, so a report is judged once; every failure allows | `hooks/report.sh` → `bin/cobot-rules report` and `handback` |
| Session grants | one kind of write on one named project or context for a Claude Code session, main thread only (decision 34, ADR-0008): `cobot-rules grant` is a request the gate asks about, `PostToolUse` on Bash records it only after the owner approved that ask, the gate allows a covered command, `SessionEnd` removes the file; never under agy, never for Terraform | `hooks/grant.sh` → `bin/cobot-rules posttool`, `sessionend`, `grant`; `<config dir>/cobot/grants/` |
| Antigravity adapter | the same policy under agy (ADR-0007): a root `hooks.json` sends every tool call to the gate, which translates agy's call and answers `allow` (no opinion), `force_ask` or `deny`, a deny on every failure; SessionStart prints the brief as one `injectSteps` system message with an agy section; no report check (no agy hook sees a subagent's report) | `hooks.json`, `hooks/gate-agy.sh`, `hooks/session-agy.sh` → `bin/cobot-rules gate --runtime agy`, `bin/cobot-session start --runtime agy`, `bin/_cobot_agy.py` |

## Roster

| Kind | Members | Where |
|---|---|---|
| Agents | `challenger` (red team), `consultant` (read-only experts), `learner` (read-only research), `auditor` (read-only sweep unit), `investigator` (read-only debug probe, decision 35), `builder`, `rust-builder`, `go-builder`, `python-builder`, `typescript-builder`, `terraform-builder` | `plugins/cobot/claude-agents/`, listed by file in `.claude-plugin/plugin.json` |
| Agy agents | the same eleven, written by `scripts/sync-agents.py` from `claude-agents/` (agy tool names, tiers, `mainAgent: false`; consultant, learner, auditor and investigator without a command tool) | `plugins/cobot/agents/`, read by agy through `.antigravity-plugin/plugin.json` |
| Workflow skills | `/cobot:onboard`, `/cobot:spec`, `/cobot:build`, `/cobot:wrap`, `/cobot:debug`, `/cobot:rules`, `/cobot:learn`, `/cobot:ship`, `/cobot:contribute`, `/cobot:security-sweep`; onboard, rules and security-sweep are typed by the owner (`disable-model-invocation`) | `plugins/cobot/skills/` |
| Consult router | `/cobot:consult [domain]` spawns one `consultant` per domain in one message (parallel); procedures for `gha`, `gitlab-ci`, `containers`, `gcp`, `kubernetes`, `service-mesh`, `ui`, `api`, `homeassistant` | `plugins/cobot/skills/consult/`, `domains/` |
| Knowledge skills (always listed: `paths:` does not gate plugin skills, so each description carries its triggers, ≤ 350 chars) | `lang-rust`, `lang-go`, `lang-python`, `lang-typescript`, `lang-terraform`, `lang-shell`, `lang-fallback`, `fw-react`, `fw-next`, `fw-vue`, `expert-api`, `expert-gitea`, `expert-gha`, `expert-cicd`, `expert-gitlab-ci`, `expert-ui`, `expert-containers`, `expert-gcp`, `expert-kubernetes`, `expert-service-mesh`, `expert-homeassistant` | `plugins/cobot/skills/` |

Knowledge is a skill, isolation is an agent. Only the orchestrator writes memory, through
`cobot-memory`. Builders never commit. See ADR-0001 to ADR-0003; experts as skill pairs in
ADR-0005 and ADR-0006.

## Flow

Intake names the size (tiny, small, medium, large) and the profile caps it. Tiny and small work
is done in the main thread with a focused check. Medium and large work goes through
`/cobot:spec` (≤ 4 clarify questions, challenger and consults in parallel), `/cobot:build` (one
builder per task, up to three worktree lanes, proof lines checked), then `/cobot:wrap` (full
checks, reviews, journal with a verified stamp). One spec is one branch and one pull request.
An unknown cause goes to `/cobot:debug` first: the lead frames and reproduces it, one read-only
investigator per hypothesis probes it (at most three rounds), and the remedy is printed for the
owner, never run; a code fix comes back to intake. The record lives in `.agent/debug/`.

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
plugins/cobot/bin/cobot-memory debug list --open
```

```bash
plugins/cobot/bin/cobot-memory learn --promote --dry-run '{"topic": "go", "entries": []}'
```

```bash
plugins/cobot/bin/cobot-deps check --fresh
```

```bash
plugins/cobot/bin/cobot-env detect cargo uv
```

`cobot-usage [--since DATE] [--session PREFIX] [--json]` reads this repository's local Claude Code
transcripts (and its worktrees') and reports requests and tokens per session, model and agent
type plus Skill and Agent call counts, never message text. Claude Code's `/usage` shows the live
session; this is the history a routing decision needs (design §10).

## Security model

The gate is argv and pattern matching: it stops honest and careless attempts, not determined
obfuscation. Interpreters running code, task runners and remote execution are opaque and ask.
`mise` tasks, `make` targets (read from the Makefile), a shell's `-c` string and container or
sandbox entry wrappers (`distrobox enter`, `toolbox run`, `docker exec`, `nix develop -c`, …)
are looked through and the command behind them is judged.

A command substitution is judged by what it runs: a quote-aware scanner (`bin/_cobot_shell.py`)
gives each `$(…)`, backtick and process substitution body to the same rules, and the
substitution itself asks only where its text could decide which program runs or make a `never`
or `ask` row match; anything outside the scanner's model asks. A substitution that is a whole
argument is not resolved for the protected-file check, like a variable, and a variable's value
reaching arithmetic is not followed (`read x < f; echo $((x))`). The soundness target, in the
scanner's module: a hole in the command's words (a substitution, a glob, a `${…}` with an
operator word) is never silent where some text in its place, for a glob some set of file names,
would change which program runs or make a rule match the form that names what runs.

Home Assistant's secrets are judged in code, not by rows (decision 36): a reader row such as
`cat *secrets.yaml*` would be viable for every globbed or substituted read. `bin/_cobot_secrets.py`
refuses a read-only agent's command that would print `secrets.yaml` or a `.storage/` file: named,
through a redirect, by a recursive `grep`, any `rg`, a `semgrep` scan or a verbose unredacted
`gitleaks` over a tree that holds one (the tree is walked, at most 20 000 entries), by a history
printer in a repository whose history or index tracks one with no pathspec excluding it, or as a
`curl` `file:` URL. `hass_verdict` in `cobot-rules` refuses any setting of the token variables,
refuses their expansion for read-only agents and asks on it in the main thread, and asks on
`HASS_SERVER` set and on `-s` or `-x` in a short cluster.

For the read-only agents, a segment that could write a file or run a program never matches
their read list (the scanner's `Scan.writes` holds the targets a redirection writes), and a read
whose program the repository's files choose counts only in a repository trusted by identity
whose deciding files match origin's default branch. Every git call cobot makes turns
`core.fsmonitor` off.

The scanner also records each pipeline stage and the stage every redirection, here-document and
here-string belongs to. From that, text written into a file through the shell is refused, and a
write it cannot trace for certain asks (spec gate-f36-f40-f44, story 6). Some commands are
judged on a canonical form rather than as written: `git config` (scope, read or write, keys that
run code), credential printers, and gcloud without its release track. The claims are bounded to
the forms named in configuration.md.

Each rule, with the asks it costs and what it does not cover, has one home in
[configuration.md](configuration.md): [Rules](configuration.md#rules) for protected paths,
braces, globs, `${…}`, `$"…"` and options before the verb;
[What the read lists never cover](configuration.md#what-the-read-lists-never-cover) and
[Repository configuration and trust](configuration.md#repository-configuration-and-trust) for
the agents' read lists. The specs behind them: `.agent/specs/gate-expansion.md`,
`gate-findings.md`, `gate-repo-config.md` and `gate-residuals.md`.

MCP tools are judged by name: a read (`list`, `get`, `describe`, `search`, `read` first, and no
write word joined to it as in `get_or_create`) and the desktop app's own UI tools are silent;
every other MCP tool asks, a browser server's clicks and navigation included, since it acts with
the owner's sign-ins. An owner or project `ask` outranks a read; `never` outranks everything.
On Google Cloud servers registered as `gcp-*`, default `never` rules refuse the write tools by
verb, since a personal project cannot hold the IAM deny policy that would refuse them. The Cloud
CLI server's `run_gcloud_command` and `run_bq_command` are refused under any server name. MCP
calls never consult the grant store, so a session grant covers Bash only. Registering a server
asks (`claude mcp add|remove`, `--mcp-config`, `--settings`, an edit of `~/.claude.json` or
`.mcp.json`, or a shell word naming one: an `ask` file row protects a literal word the way a
`never` row does, while a glob that only could name it stays silent):
whether a repository uses Google's servers at all is its `gcp-mcp:` line, asked once in the main
thread (decision 37).

Hooks run as the user. An untrusted repository's `.agent/` is never injected into the session;
that protection is advisory for the model's own reads.

Under agy the project layer comes from every `workspacePaths` entry, never from the model's
`Cwd`; every word is also read as a path in the `Cwd` and in each folder a `cd` reaches, and a
command whose `Cwd` is inside a protected folder asks, naming it, and a write through a
symlinked customization root is judged by the root's name. agy 1.5.3 ran the call when a hook
failed and 1.5.9 stops at one, so the shim does not rely on its exit code: its last word is
always a decision line. Its settings, config, grants and every customization root's hook and
plugin files are `never` rows in the default layer, for both runtimes: a hook written there
would run outside the gate.
