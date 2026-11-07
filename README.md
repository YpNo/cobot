# agentic-partner

## Overview

A Claude Code plugin marketplace that turns the main thread into a governed orchestrator. One
plugin, `partner`, brings a conceptor that writes one spec, a fresh-context challenger,
per-language builders, experts as skills, committed memory per repository, and a rules gate that
decides every outward action with `never`, `ask` or `allow`. Built for small personal and
open-source repositories where efficiency matters more than ceremony. Design:
[docs/02-design.md](docs/02-design.md); decisions: [docs/adr](docs/adr); release plan in the
design, section 15.

Release 1 (0.1.0) is the dogfood release: everything below works from a checkout through
`install.sh --dev` or `--project`. Release 1.1 adds the learner and knowledge staleness, the
dependency check and the weekly refresh, `ship`, `contribute`, `security-sweep`, journal
compaction, the Python and TypeScript stacks with their builders and the containers expert.

## Architecture

| Layer | What | Where |
|---|---|---|
| Protocol | ≤ 3k-char orchestrator rules injected at session start | `plugins/partner/protocol.md` |
| Gate | `PreToolUse` hook on Bash, Edit, Write, NotebookEdit and MCP tools; three rule layers; never widens; blocks on failure | `hooks/gate.sh` → `bin/partner-rules`, `rules/default.rules` |
| Memory | `.agent/CONTEXT.md`, `JOURNAL.md`, `FINDINGS.md`, `specs/`, `knowledge/`; trusted repositories only; foreign mode keeps memory outside the tree | `bin/partner-memory`, `bin/partner-session` |
| Learning | dated knowledge lines with a status and a source; staleness in the brief (versions 30 days, idiom 90); deltas applied by `partner-memory learn`, promoted into this repository by `learn --promote`; a weekly refresh PR | `bin/_partner_knowledge.py`, `agents/learner.md`, `skills/learn`, `.github/workflows/knowledge-refresh.yml` |
| Currency | how far the lockfiles are behind and whether advisories exist, through the ecosystems' own tools, cached per repository; one line in the brief | `bin/partner-deps` |
| Agents | `challenger` (red team), `consultant` (read-only experts), `learner` (read-only research), `builder`, `rust-builder`, `go-builder`, `python-builder`, `typescript-builder`, `terraform-builder` | `agents/` |
| Workflow skills | `/partner:onboard`, `/partner:spec`, `/partner:build`, `/partner:wrap`, `/partner:rules`, `/partner:learn`, `/partner:ship`, `/partner:contribute`, `/partner:security-sweep` | `skills/` |
| Knowledge skills | `lang-rust`, `lang-go`, `lang-python`, `lang-typescript`, `lang-terraform`, `lang-fallback`, `expert-gha`, `expert-containers` (path-gated), `consult-gha`, `consult-containers` (forked audits) | `skills/` |

Knowledge is a skill, isolation is an agent. Only the orchestrator writes memory, through
`partner-memory`. Builders never commit. See ADR-0001 to ADR-0003.

## Prerequisites

- Claude Code 2.1.285 or newer (`claude --version`).
- Python 3.12 or newer on PATH as `python3`; the scripts use the standard library only.
- POSIX `sh`, `git`. For development: `uv` (runs pinned `ruff`, `pytest`, `shellcheck`), `npx` for markdownlint.

## Installation

None of these touch `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills` or
`~/.claude/settings.json` (ADR-0003). The legacy scaffold can stay until the switch described in
[docs/03-switch-plan.md](docs/03-switch-plan.md).

```bash
./install.sh --dev
```

Prints a session-only alias using `claude --plugin-dir`; nothing is written.

```bash
./install.sh --project /path/to/repo
```

Registers the marketplace (from this checkout, or from GitHub with `--source github`) and installs
the plugin at project scope in that repository. Use `--local` in a repository you do not own.
The install is a copy pinned to the plugin version: after editing this checkout, run
`./install.sh --refresh /path/to/repo` (uninstall and reinstall at the scope found there, project or local), because `claude plugin update`
only acts on a version change.

```bash
./install.sh --check
```

Reports Claude Code, the marketplace, installed scopes, the legacy scaffold and name overlaps.
`--uninstall [scope]` reverses an install. `--user` is reserved for the switch.

## Configuration

| Setting | Type | Default | Effect |
|---|---|---|---|
| `~/.claude/partner.rules` | rule file | absent | owner layer: `allow` lines silence a default `ask`; `never` and `ask` tighten |
| `.agent/partner.rules` | rule file | absent | project layer: `never` and `ask` only |
| `~/.claude/partner/identities` | `host/owner` per line | absent | repositories whose every remote belongs to one of these owners are trusted |
| `~/.claude/partner/trusted` | `<root commit> <name>` per line | absent | repositories trusted by root commit (no remote, or a fork with foreign remotes) |
| `CLAUDE_CONFIG_DIR` | path | `~/.claude` | where the owner files above live |
| `XDG_DATA_HOME` | path | `~/.local/share` | foreign-mode memory under `agentic-partner/repos/<host>/<owner>/<repo>` |
| `PARTNER_RULES_OWNER`, `PARTNER_RULES_PROJECT_DIR` | paths | unset | override the owner file and the project directory (tests, spikes) |
| `PARTNER_GATE_LOG` | path | unset | append one JSON line per judged call: tool, decision, first 120 chars |

Rule syntax, one per line: `decision Tool(pattern) [@agent]`, for example
`ask Bash(git push*)`, `never Edit(~/.claude/settings*.json)`, `ask mcp__*__create*`,
`allow Bash(cargo test*)`. Precedence: `never` in any layer wins; an `allow` from the owner layer
(or an agent-scoped one from the default layer) silences the gate; `ask` prompts; otherwise
Claude Code's own permissions decide. The hard wall is a `permissions.deny` block the owner applies
from `/partner:rules sync`, rendered in plain and `rtk` forms.

## Usage

Start a session with the plugin loaded in a repository. The brief tells you whether the
repository is trusted. Then:

- `/partner:onboard` once per repository: trust, fingerprint, verified commands, memory files.
- Tiny and small work: ask directly; the orchestrator names the size and skips the ceremony.
- Medium and large work: `/partner:spec <what>` writes and challenges the spec,
  `/partner:build <slug>` implements with proof, `/partner:wrap` converges, runs the full checks,
  fans out reviews and journals with a verified stamp.
- `/partner:rules check "git push --force"` dry-runs the gate; `explain` names every matching rule;
  `sync` renders the settings block for you to apply.
- `/partner:consult-gha` audits the workflows of the current repository.
- `/partner:learn <skill or topic> [question]` sends the learner to primary sources and read-list
  commands and brings back a dated delta; the brief names the skills whose knowledge is stale.
- `partner-deps check` reports dependency currency (never upgrades); the brief shows the cached
  line and says when to run it again.
- `/partner:ship` writes the pipeline from the verified commands at the end of a work stream
  (PR, merge, release and weekly triggers, one aggregator check, the image workflow for a
  service); `/partner:contribute` prepares an upstream pull request under the maintainers'
  rules and prints the push and `gh pr create` commands; `/partner:security-sweep` audits the
  whole tree read-only against `.agent/accepted-risks.md`.

Memory commands the orchestrator uses, also available by hand:

```bash
plugins/partner/bin/partner-memory check
```

```bash
plugins/partner/bin/partner-memory findings add "ci.yml" "checkout is on a floating tag"
```

```bash
plugins/partner/bin/partner-memory knowledge --stale
```

```bash
plugins/partner/bin/partner-memory learn --promote --dry-run '{"topic": "go", "entries": []}'
```

```bash
plugins/partner/bin/partner-deps check --fresh
```

## Testing

```bash
uv run --no-project --python 3.13 --with pytest==9.2.0 --with pytest-cov==7.1.0 pytest --cov=plugins/partner/bin --cov-fail-under=85
```

```bash
uvx ruff@0.17.4 check . && uvx ruff@0.17.4 format --check .
```

```bash
uvx --from shellcheck-py shellcheck install.sh plugins/partner/hooks/*.sh scripts/*.sh
```

```bash
claude plugin validate plugins/partner --strict && python3 scripts/check-plugin.py
```

Live spikes that need a logged-in CLI: `sh scripts/spike-coexistence.sh` and
`sh scripts/spike-r1.sh`. Evals are paid sessions: `cd plugins/partner && claude plugin eval . --runs 1
--allow-tools Write Edit`; the `gate-asks` case also needs `--allow-tools Bash`, which requires the
sandbox backend (`bubblewrap` and `socat` on Linux).

## CI/CD

`ci.yml` runs on every push and pull request: ruff, shellcheck, the plugin contract check,
plugin and marketplace validation, pytest with the 85 % coverage gate, markdownlint and zizmor.
The eval job runs only on manual dispatch with the `evals` input, since each run is a paid Claude
session. `release.yml` runs on a `vX.Y.Z` tag: it checks that `plugin.json`, `marketplace.json`
and the changelog agree, then creates the GitHub release from the changelog section. Every action
is pinned to a commit SHA and tokens are read-only except the release job.
`knowledge-refresh.yml` runs weekly (and on dispatch): it picks the two stalest knowledge skills
without an open `learn/<skill>` branch, runs the learner read-only under a dollar budget, applies
the delta with `learn --promote --in-place`, runs the plugin checks and opens one pull request
per skill for the owner to review. Its secrets live in the `knowledge-refresh` environment; with
only `GITHUB_TOKEN` the PR gets no CI run (the checks ran in the job), a fine-grained PAT in
`KNOWLEDGE_REFRESH_TOKEN` restores it.

The repository settings those workflows rely on are code: `scripts/github-settings.sh --check`
prints wanted against current and `--apply` sets what differs (delete branch on merge, no squash,
SHA-pinned actions required, read-only default token, Dependabot alerts and security PRs, the
`evals` and `knowledge-refresh` environments deployable from `main` only, and the `main` ruleset
with `ci-ok` as the one required check where the plan allows rulesets). Secrets are never
handled by the script: it prints the `gh secret set` commands, one `ANTHROPIC_API_KEY` per
environment and none at repository level. `.github/dependabot.yml` groups the weekly action
updates into one PR.

## Security

The gate is argv and pattern matching: it stops honest and careless attempts, not determined
obfuscation. Interpreters running code, task runners, remote execution and command substitution
are opaque and ask. `mise` tasks, `make` targets (read from the Makefile), a shell's `-c` string and container or sandbox entry wrappers
(`distrobox enter`, `toolbox run`, `docker exec`, `nix develop -c`, …) are looked through and the
command behind them is judged.
Hooks run as the user. Untrusted repositories' `.agent/` is never injected; in release 1 that
protection is advisory for the model's own reads. Report a vulnerability through a private GitHub
security advisory on this repository.

## Contributing

Branches `feat/`, `fix/`, `docs/`, `chore/`, `security/`; Conventional Commits without
attribution trailers; one concern per pull request; tests with every behaviour change; the design
and ADRs are the source of truth for scope.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) (Keep a Changelog, semantic versions).

## License

MIT, see [LICENSE](LICENSE).
