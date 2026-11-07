# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `partner-rules` resolves mise tasks: `mise run <task>`, the `mise <task>` shorthand and
  `mise exec … -- <cmd>` are judged as the commands behind them, and reasons and `explain` name
  the origin (`via mise run deploy`). A task with `depends`, `file`, `shell`, `dir`, templating or
  command substitution stays opaque; a `mise` global flag or unknown subcommand now asks.
- `install.sh --refresh [DIR]`: uninstall and reinstall at project scope, the only way a
  same-version edit reaches an installed copy (`claude plugin update` keeps the cache).
- The gate looks through entry wrappers and judges the command behind them: `distrobox enter …
  -- <cmd>` (and `-e`), `toolbox run`, `docker|podman exec`, `docker compose exec|run`,
  `nix develop -c`, `nix-shell --run`, `flatpak run --command=`, `chroot`, and a shell's `-c`
  string, nested up to four levels; an option a wrapper's table does not know keeps it opaque.
  Remote execution now asks: `ssh`, `mosh`, `kubectl exec`, `gcloud … ssh`, `gh codespace ssh`;
  so do `source` and `.`.
- Default rules from the owner's third review: `never` on a commit carrying `Co-Authored-By` or a
  PR body carrying `Generated with` (authorship, not a word ban); `ask` on dependency-adding
  commands (`cargo add`, `npm install <pkg>`, `pnpm add`, `yarn add`, `bun add`, `go get`,
  `uv add`, `pip install`, `poetry add`); bare installs from a lockfile stay silent.
- Cluster, mesh and image rules: mutating `kubectl` verbs (`create`, `patch`, `scale`, `rollout
  restart|undo`, `drain`, `label`, `set`, `port-forward`, …), `helm install|upgrade|uninstall|
  rollback|push|repo add`, `istioctl install|upgrade|uninstall|x`, `gcloud container fleet mesh`,
  and `docker|podman push|login|system prune|rm|rmi` ask; `helm` and `istioctl` global options
  are stripped before matching.
- Release and pin rules from the headscale dogfood: `goreleaser release` asks (it publishes
  unless `--snapshot` or `--skip=publish`; the owner layer may allow the snapshot form), and so
  do `nix flake update` and `nix flake lock` (they move dependency pins, decision 22).
- The gate resolves `make` targets by reading the Makefile (`_partner_make`): recipe lines are
  judged on their own with the origin in the reason (`ask Bash(rm -rf*) via make clean`), plain
  variables, `define` bodies through `$(call)`, `$(MAKE)`, `$@`, target prerequisites, command-line
  `VAR=value` and `.DEFAULT_GOAL` are followed; `-C`, `-f`, `-j`, `-k`, `-n` and the other flags are
  understood. `include`, pattern or suffix rules, `.SECONDEXPANSION`, `$(eval)`, targets under a
  conditional or with a target-specific variable, recipes that need a function or an unknown
  variable, a nested make under `-C`, `--eval` and unknown options keep the command opaque. make
  is never run: `$(shell …)` in a Makefile would otherwise execute at gate time.
- `partner-memory journal add [ENTRY]` and `learn [JSON]` take their payload as an argument as
  well as on stdin, and never wait on a terminal.
- `install.sh --refresh` reinstalls at whichever scope the plugin was installed in the directory,
  project or local, so a foreign repository's local-scope install refreshes too.
- `onboard` names a fork of someone else's repository as the foreign path (the trust reason lists
  the remotes that belong to no identity), and copies the maintainers' hard constraints
  (`CONTRIBUTING.md`, `AI_POLICY.md`, DCO or CLA, the project's own agent instructions) into
  CONTEXT.md for `/partner:contribute` to read.
- `spec` sizes a change as one branch and one PR with one commit per task, writes the
  architecture choice (hexagonal by profile) and justifies every new dependency; `build` commits
  each finished task and refuses an unnamed dependency; `wrap` runs the pre-PR currency check and
  opens one PR; builders report `Deps added:`; `expert-gha` carries the CI trigger matrix.

### Changed

- The untrusted-repository reason names the remotes that match no identity
  (`no identity matches every remote (ghsa -> github.com/juanfont) …`).
- The brief caps CONTEXT.md on section boundaries and names the dropped sections, and the cap
  grows into the room a short journal leaves (2 500 to 4 000 characters).

### Fixed

- The brief's hard cap could overshoot its limit by one character.
- A backslash line continuation split a command into two segments, so `git push \` followed by
  `--force` on the next line only asked. A `#` inside a word (`nix develop .#dev`) no longer
  truncates the command.

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
