# Development

For contributors, agents and architects working on cobot itself. The verified commands, with the
date each last ran, are in [`.agent/CONTEXT.md`](../.agent/CONTEXT.md).

## Prerequisites

- Claude Code 2.1.285 or newer (`claude --version`).
- Python 3.12 or newer on `PATH` as `python3`; the plugin's scripts use the standard library only.
- POSIX `sh` and `git`. For development: `uv` (runs pinned `ruff`, `pytest`, `shellcheck`) and
  `npx` (markdownlint).

## Checks

```bash
uv run --no-project --python 3.13 --with pytest==9.2.0 --with pytest-cov==7.1.0 pytest --cov=plugins/cobot/bin --cov-fail-under=85
```

```bash
uvx ruff@0.17.4 check . && uvx ruff@0.17.4 format --check .
```

```bash
uvx --from shellcheck-py shellcheck install.sh plugins/cobot/hooks/*.sh scripts/*.sh scripts/spikes/*.sh
```

```bash
npx --yes markdownlint-cli2@0.24.0 "**/*.md"
```

```bash
claude plugin validate plugins/cobot --strict && claude plugin validate . --strict && python3 scripts/check-plugin.py
```

## Evals

Evals run as Claude sessions under the logged-in account (workload identity federation in CI),
so every run costs money. `tests/test_eval_graders.py` checks the suite for free first: every grader pattern
compiles, no case has more than one judge, every fixture runs clean.

```bash
cd plugins/cobot && claude plugin eval . --trust-plugin --scaffold --allow-tools Bash Write Edit
```

A case's `allowed_tools` only lists what it may use; `Bash`, `Write` and `Edit` must also be
granted on the command line, and `Bash` needs the sandbox backend (`bubblewrap` and `socat` on
Linux). `--scaffold` runs each case's `fixture.sh` to seed the workspace; the default two-arm run
scores the plugin against a no-plugin baseline, `--ablation none` runs one arm, `--runs 1` and
`--case <glob>` keep a check cheap.

Live spikes that need a logged-in CLI, rerun when a Claude Code upgrade may change hook
behaviour: `sh scripts/spikes/spike-coexistence.sh` and `sh scripts/spikes/spike-r1.sh`.

## CI/CD

`ci.yml` runs on every push and pull request: ruff, shellcheck, the plugin contract check,
plugin and marketplace validation, pytest with the 85 % coverage gate, markdownlint and zizmor,
with one aggregator check (`ci-ok`). The eval job runs only on manual dispatch with the `evals`
input:

```bash
gh workflow run ci.yml --repo YpNo/cobot --ref main -f evals=true
```

`release.yml` runs on a `vX.Y.Z` tag: it checks that `plugin.json`, `marketplace.json` and the
changelog agree, then creates the GitHub release from the changelog section. Every action is
pinned to a commit SHA and tokens are read-only except the release job.

`knowledge-refresh.yml` runs weekly (and on dispatch): it picks the two stalest knowledge skills
without an open `learn/<skill>` branch, runs the learner read-only under a dollar budget, applies
the delta with `learn --promote --in-place`, runs the plugin checks and opens one pull request per
skill for the owner to review. Its settings live in the `knowledge-refresh` environment; with only
`GITHUB_TOKEN` the PR gets no CI run (the checks ran in the job), a fine-grained PAT in
`KNOWLEDGE_REFRESH_TOKEN` restores it.

The repository settings those workflows rely on are code: `scripts/github-settings.sh --check`
prints wanted against current and `--apply` sets what differs (delete branch on merge, no squash,
SHA-pinned actions required, read-only default token, Dependabot alerts and security PRs, the
`evals` and `knowledge-refresh` environments deployable from `main` only, and the `main` ruleset
with `ci-ok` as the one required check where the plan allows rulesets). Credentials are never
handled by the script.

No Anthropic API key is stored. The eval job and the learner source
`scripts/anthropic-federation.sh` (workload identity federation). Anthropic accepts a GitHub
token's `jti` once, and Claude Code reads `ANTHROPIC_IDENTITY_TOKEN_FILE` for every exchange
(keying its on-disk token cache by that token), so the script serves the file as a named pipe
that mints a fresh GitHub OIDC token for each read; a file refreshed on a timer failed
`jti_reused` once sessions started faster than the timer. Each environment has its own Claude Console rule,
whose subject is GitHub's immutable form with numeric IDs
(`repo:<owner>@<id>/<repo>@<id>:environment:<name>`, exact) plus the claim
`ref = refs/heads/main`; its four identifiers are environment variables, not secrets. The
settings script prints both rule subjects and the `gh variable set` commands. A rule written
from the repository's name, or one that also requires `event_name = push`, answers 401
`match_subject_prefix`; the Console's authentication history names the failed check. `.github/dependabot.yml` groups the weekly action
updates into one PR.

## Releasing

Bump `plugins/cobot/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, cut the
changelog's Unreleased section to `## [X.Y.Z] - <date>`, merge, then the owner pushes the tag
`vX.Y.Z`; `release.yml` publishes. `claude plugin update` only picks up a version change.

## Banner

`docs/assets/banner.jpg` and `social.jpg` come from `banner-source.jpg` through
`scripts/make-banner.py` (its docstring has the command); the wordmark is set in Inter 4.1
(SIL OFL 1.1), downloaded, not committed. Upload `social.jpg` under the repository's
Settings → Social preview.

## Contributing

Branches `feat/`, `fix/`, `docs/`, `chore/`, `security/`; Conventional Commits without
attribution trailers; one spec is one branch and one pull request, one task one commit; tests
with every behaviour change; the design and the ADRs are the source of truth for scope.
