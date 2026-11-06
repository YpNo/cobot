# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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
