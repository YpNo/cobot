# agentic-partner

## Overview

A Claude Code plugin marketplace that turns the main thread into a governed orchestrator: a
conceptor that writes one spec, a fresh-context challenger, per-language builders, experts as
skills, committed memory, and a rules gate that decides every outward action with `never`, `ask`
or `allow`. Built for small personal and open-source repositories where efficiency matters more
than ceremony. The design is in [docs/02-design.md](docs/02-design.md); decisions are in
[docs/adr](docs/adr).

Release 0 (this version) ships the repository bootstrap: manifests, the challenger agent, the
rules gate in its built-in-rules form, the installer and CI. Skills, builders and memory arrive in
release 1.

## Architecture

One plugin, `partner`, under `plugins/`. Agents exist only for isolation (`challenger`,
`consultant`, builders); knowledge is a skill. Enforcement is a `PreToolUse` hook
(`hooks/gate.sh` → `bin/partner-rules`) that never widens permissions and blocks on any failure.
Memory lives in `.agent/` of each repository. See design sections 3 to 7 and ADR-0001.

## Prerequisites

- Claude Code 2.1.285 or newer (`claude --version`).
- Python 3.12 or newer on PATH as `python3` (the gate is standard library only).
- POSIX `sh`. For development: `ruff`, `pytest`, `pytest-cov`, `shellcheck`.

## Installation

Three paths; none touches `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills` or
`~/.claude/settings.json` (ADR-0003).

```bash
./install.sh --dev
```

Prints a session-only alias using `claude --plugin-dir`; nothing is written.

```bash
./install.sh --project /path/to/repo
```

Registers the marketplace (from this checkout, or from GitHub with `--source github`) and installs
the plugin at project scope in that repository. Use `--local` in a repository you do not own.

```bash
./install.sh --check
```

Reports Claude Code, the marketplace, installed scopes, the legacy scaffold and name overlaps.
`--uninstall [scope]` reverses an install. `--user` is reserved for the switch described in
[docs/03-switch-plan.md](docs/03-switch-plan.md).

## Configuration

| Variable | Type | Default | Effect |
|---|---|---|---|
| `CLAUDE_CONFIG_DIR` | path | `~/.claude` | where `--check` looks for the legacy scaffold |
| `PARTNER_GATE_LOG` | path | unset | when set, the gate appends one JSON line per judged command (spikes and debugging only) |

Rule files and layers arrive in release 1.

## Usage

With the plugin loaded, the gate judges every Bash command: `git push` asks, any force push is
denied, everything else is left to Claude Code's own permissions. Dry-run a command:

```bash
plugins/partner/bin/partner-rules check "cargo test && git push --force"
```

The `partner:challenger` agent red-teams a spec or plan and returns `SOUND` or ranked objections.

## Testing

```bash
pytest --cov=plugins/partner/bin --cov-fail-under=85
```

```bash
shellcheck install.sh plugins/partner/hooks/gate.sh
```

```bash
claude plugin validate plugins/partner --strict
```

## CI/CD

`ci.yml` runs on every push and pull request: ruff, shellcheck, plugin and marketplace validation,
pytest with the coverage gate, markdownlint and zizmor. Every action is pinned to a commit SHA
and the workflow token is read-only. Releases are tagged by hand; `release.yml` arrives in
release 1.

## Security

The gate is argv and pattern matching: it stops honest and careless attempts, not determined
obfuscation. The hard guarantee is a `permissions.deny` block the owner installs from the rendered
rules (release 1). Hooks run as the user. Report a vulnerability through a private GitHub security
advisory on this repository.

## Contributing

Branches `feat/`, `fix/`, `docs/`, `chore/`, `security/`; Conventional Commits; one concern per
pull request; tests with every behaviour change. The design and ADRs are the source of truth for
scope.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) (Keep a Changelog, semantic versions).

## License

MIT, see [LICENSE](LICENSE).
