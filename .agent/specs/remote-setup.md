# Spec — the GitHub remote and its settings

size: small · profile: library · owner: YpNo · date: 2026-11-07

## Goal

The private remote `YpNo/agentic-partner` holds `main`, runs CI on every push and pull request,
can run the evals and the weekly knowledge refresh, and carries the few settings those
workflows assume. The settings are code the owner can re-run, not clicks. Nothing outward
(push, apply, secrets, dispatch) runs without the owner's yes.

## Scope

- `scripts/github-settings.sh --check|--apply`: delete branch on merge; squash merge off (one
  task = one commit, decision 20); wiki and projects off; `sha_pinning_required` (every `uses:`
  here is a full SHA); default token read-only and no PR creation by `GITHUB_TOKEN`; Dependabot
  alerts and security PRs; environments `evals` and `knowledge-refresh` deployable from `main`
  only; the `main` ruleset (no deletion, no force push, pull request with `ci-ok` required),
  reported as unavailable on a free plan for a private repository.
- Secrets: printed as `gh secret set` commands for the owner; one `ANTHROPIC_API_KEY` per
  environment, none at repository level, so the evals job moves under `environment: evals`
  (closes the one zizmor medium).
- `.github/dependabot.yml`: `github-actions`, weekly, one grouped PR, `ci(deps)` prefix.
- Out of scope: the marketplace source switch (`03-switch-plan.md` step 2), secret scanning and
  code scanning (paid on private repositories), a CODEOWNERS file (one owner).

## Tasks

1. Settings script with a fake-`gh` test (check writes nothing; apply issues each write).
2. Dependabot config, `environment: evals`, README and changelog.
3. Owner: push `main` and this branch, open the PR, `--apply`. Owner-only phase: no secrets,
   so the eval job and the weekly refresh stay idle (`gh workflow disable knowledge-refresh.yml`
   after the push, so the schedule does not fail every Monday); evals run locally under the
   owner's subscription with `claude plugin eval plugins/partner --trust-plugin --scaffold`;
   CI runs the free checks on every push. The API secrets and the dispatch come only if the
   owner later wants the evals and the refresh to run without the workstation.

## Challenger

Skipped: small, no new dependency, no behaviour change in the plugin; the live `--check` run
against the empty remote is the proof.

## Proof

`--check` on the empty remote lists ten pending changes and the ruleset note; `pytest` 543
passed with coverage held; shellcheck, ruff, markdownlint and zizmor (offline, auditor) clean.
