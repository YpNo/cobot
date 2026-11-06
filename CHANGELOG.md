# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-06

Release 1: the governed orchestrator, dogfood-ready through `install.sh --dev` and `--project`.

### Added

- Rules engine: rule files in three layers (`rules/default.rules`, `~/.claude/partner.rules`,
  `.agent/partner.rules`), argv normalisation (wrappers, prefix commands, global options,
  combined flags, `+refspec`, `gh api` methods, heredocs), opaque runners, Edit/Write/MCP rules,
  shell access to protected files, agent scopes, `show`, `check`, `explain`, `sync`.
- Read-only command lists for `consultant` and `learner` (agent-scoped allows in the default layer).
- `partner-memory`: `init` (committed or foreign mode, identity and trusted-root enrolment),
  `trust`, `check`, `brief` (capped, prioritised), `journal add`, `findings add|list|close`,
  `learn` (filtered, de-duplicated, secret-scanned, 80-line cap).
- `partner-session` and the SessionStart hook: protocol, rule counts and the brief, ≤ 10 000 chars,
  only for trusted repositories.
- Agents: `consultant`, `builder`, `rust-builder`, `go-builder` (and `challenger` from 0.0.1).
- Workflow skills: `onboard`, `spec` (+ template), `build`, `wrap`, `rules`.
- Knowledge skills, verified upstream on 2026-11-06: `lang-rust`, `lang-go`, `lang-terraform`,
  `lang-fallback`, `expert-gha`; consult skill `consult-gha`.
- Evals (four cases), `scripts/check-plugin.py` contract check, `scripts/spike-r1.sh`,
  `release.yml`, manual eval job in CI.

### Changed

- Precedence written down: `never` (any layer) > `allow` (owner layer, or agent-scoped default) >
  `ask` > silence; the project layer tightens only.
- The gate log records tool, decision and the first 120 characters only.

## [0.0.1] - 2026-11-06

Release 0: repository bootstrap, nothing written outside this repository.

### Added

- Marketplace `agentic-partner` and plugin `partner` manifests.
- `partner:challenger` agent (read-only, fresh context, red-team verdicts).
- Rules gate: `hooks/gate.sh` shim that blocks on any failure and `bin/partner-rules` with the
  built-in `git push` (ask) and force-push (deny) rules, `rtk`-aware.
- `install.sh` with `--dev`, `--project`, `--local`, `--user`, `--check`, `--uninstall`.
- CI: ruff, shellcheck, plugin validation, pytest with an 85 % coverage gate, markdownlint, zizmor.
- Design v1.1, ADR-0001 to ADR-0003, switch plan, crissp review.
