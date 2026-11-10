---
name: expert-gha
description: >-
  GitHub Actions CI/CD and supply-chain security: full-SHA pins, least-privilege permissions,
  persist-credentials false, concurrency, timeouts, no untrusted ${{ }} in run, zizmor, releases,
  attestations, OIDC. Use on .github/workflows/, .github/actions/, action.yml, and for a CI
  pipeline, a tag-driven release, Dependabot or a zizmor finding.
paths:
  - ".github/workflows/**"
  - ".github/actions/**"
  - "**/action.yml"
  - "**/action.yaml"
user-invocable: false
---

# expert-gha

A workflow is code that runs with your token and secrets on every push. Review it like that.
The platform-neutral principles (trigger matrix, aggregator, pinning, OIDC, provenance, SBOM,
signing, DORA) live once in `../expert-cicd/SKILL.md`; this skill is their GitHub Actions form.
Pins: `references/actions.md`. Templates: `references/snippets.md`. Never pin from memory —
copy a row, or resolve `gh api repos/<r>/commits/<tag> --jq .sha` and add the row.

## Non-negotiables

1. `uses: owner/repo@<40-hex sha> # vX.Y.Z` — every third-party and `actions/*` action.
   Local `./.github/actions/x` is exempt. Comment must match the tag (zizmor `ref-version-mismatch`).
2. Top-level `permissions: contents: read` (or `{}`); widen per job, only the job that needs it.
3. `actions/checkout` with `persist-credentials: false`. Need to push? Pass a token to that one step.
4. `concurrency:` on every workflow; `cancel-in-progress` for PR/CI, never for release or deploy.
5. `timeout-minutes:` on every job, sized at ~2× the normal run.
6. No `pull_request_target`, `workflow_run` or `issue_comment` without a comment stating why,
   and never with a checkout or execution of the PR head.
7. No `${{ github.event.* }}`, `github.head_ref`, `inputs.*` or step outputs inside `run:` or
   `github-script`. Bind to `env:` and quote `"$VAR"`.
8. zizmor runs in CI (`zizmorcore/zizmor-action`) and findings fail the build or are suppressed
   inline with a reason.
9. Dependabot (`github-actions`, `directory: /`, cooldown) or Renovate
   (`helpers:pinGitHubActionDigestsToSemver`) keeps the pins moving. A pin nobody bumps rots.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] setting any permission sets every unlisted one to `none`.
- [verified 2026-11-06 · src: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] job `timeout-minutes` default is 360.
- [verified 2026-11-06 · src: https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/] repo/org "allowed actions" policy can require SHA pinning (`sha_pinning_required`); turn it on.

## Workflow shapes

- **ci.yml** — `push: [main]` + `pull_request` with no base filter (a PR stacked on another
  branch runs too). Runs the same commands as local
  (`.agent/CONTEXT.md`). Cheap checks first. A separate `zizmor` job with its own permissions.
- **release.yml** — `push: tags: v*`. Two jobs: `build` (read-only, no cache restore) uploads
  `dist/`; `publish` (environment `release`, `contents: write`, `id-token: write`,
  `attestations: write`) attests and runs `gh release create`. Snippet ready.
- **Reusable workflow** (`on: workflow_call`) pays when several repos share a whole job graph,
  or when you want SLSA Build L3 isolation. Pass named secrets, never `secrets: inherit`.
- **Composite action** pays for a step sequence repeated in ≥ 2 workflows of one repo. It has no
  `permissions`, no `timeout`, and its inputs are expressions: same `env:` rule inside it.
- **Matrix** only for versions or OSes you actually support. `fail-fast: false` when each cell
  is independent evidence (MSRV vs stable); keep the default when any red means stop.
- **Caching** — use the setup action's own cache (setup-go on by default, setup-node with
  `packageManager`, setup-python `cache: pip`, setup-uv `enable-cache`), Swatinem/rust-cache
  for Rust. `actions/cache` only for something else, key on the lockfile hash.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] `strategy.fail-fast` defaults to `true`.

## Supply chain and secrets

- **Cloud auth**: OIDC only. GCP via `google-github-actions/auth` Direct Workload Identity
  Federation, attribute condition on `assertion.repository` (and `ref` or environment for
  deploy). No JSON key in secrets. Job needs `id-token: write`.
- **Environments**: anything that publishes or deploys runs in an `environment:` with required
  reviewers and a branch/tag rule; environment secrets beat repository secrets.
- **Secrets**: only via `env:` on the step that needs them; never in `run:` args, outputs,
  artifacts, cache keys, summaries; never `set -x` in a step that holds one.
- **Attestations**: `actions/attest` with `subject-path` on release artifacts; consumers run
  `gh attestation verify`. Enable immutable releases; then publish as draft → assets → publish.
- **SLSA claim**: attestation from an in-repo workflow = Build L2. Say L3 only when the build
  runs in a shared reusable workflow. State the level in the README, not more.
- **Runner hardening**: `step-security/harden-runner` in audit mode is worth it on jobs that
  hold secrets; skip it on read-only lint jobs.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/concepts/security/artifact-attestations] attestations alone give SLSA v1.0 Build L2; a reusable workflow build gives L3.
- [verified 2026-11-06 · src: https://github.com/google-github-actions/auth] always set an attribute condition on the pool; Direct WIF preferred over SA keys.
- [verified 2026-11-07 · src: https://docs.github.com/en/actions/reference/security/secure-use] Secret redaction in logs 'largely relies on finding an exact match' of the secret value; a JSON/XML/YAML blob holding a secret 'significantly reduces the probability' it is redacted, and a transformed secret (Base64, URL-encoded) must be registered as a new secret (::add-mask::). Use one secret per sensitive value.

## Release engineering

- Tags `vMAJOR.MINOR.PATCH`, pre-releases `vX.Y.Z-rc.N`. Tag pattern
  `v[0-9]+.[0-9]+.[0-9]+*`; a `-` in the tag → `--prerelease --latest=false`.
- Changelog gate: the build job fails if `CHANGELOG.md` lacks `## [X.Y.Z]`; that section is the
  release notes (`--notes-file`). `--generate-notes` only when there is no changelog.
- `gh release create --verify-tag` is preinstalled, one pinned binary less, and fully scriptable.
  Reach for `softprops/action-gh-release` only for a feature `gh` lacks — none for this scope.
- Tags pushed by a workflow with `GITHUB_TOKEN` do not trigger the release workflow. Tag
  locally, or use a GitHub App token in the tagging workflow.
- Release builds restore no cache (cache poisoning) and pin every tool version.

- [verified 2026-11-06 · src: https://docs.github.com/actions/using-workflows/triggering-a-workflow] events from `GITHUB_TOKEN` create no new runs, except `workflow_dispatch` and `repository_dispatch`.
- [verified 2026-11-06 · src: https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md] `gh` 2.103.2 is on ubuntu-24.04 runners.

## Trigger matrix

Each pipeline runs only what its moment needs (decision 17). The suite is never thinned; the
triggers are.

| Moment | Runs | Does not run |
|---|---|---|
| Pull request | lint, format, type check; tests of the **changed areas** with dependency-aware selection (`cargo test -p <crate>` plus its dependents from `cargo metadata`, `go list -deps`, nx or turbo `affected`); security scan; `concurrency` with `cancel-in-progress` | the full matrix, the build artifact |
| Merge to `main` | the full suite once, the artifact built once and attested | a second lint pass |
| Release (tag) | verify the tag's commit passed `main` (`gh run list --commit <sha> --status success`), rebuild or reuse the artifact reproducibly, sign, publish | **tests** |
| Weekly | full matrix, dependency audit and outdated report, knowledge refresh | — |

Rules: one aggregator job `ci-ok` (`needs:` everything, `if: always()`) fails when a needed job
failed and passes when one was legitimately skipped, and is the **only required check** in
branch protection. Change detection through GitHub's own `paths:` or `dorny/paths-filter` pinned
by SHA; never `tj-actions/changed-files` (compromised March 2025). A path filter is a trigger
aid, not a test selector: the dependency graph decides which tests a change needs. One PR per
spec (decision 20) already cuts the number of runs; this matrix cuts what each run does.

## Cost and speed

- `paths:` / `paths-ignore:` on push and PR for docs-only changes — but see pitfall 1.
- `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` keeps main runs complete.
- Cache key = OS + toolchain + lockfile hash; no `restore-keys` fallback in release paths.
- One OS unless the product ships for several; MSRV + stable, not every minor.
- `ubuntu-slim` for jobs that only run a linter or a script.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching] caches: 10 GB/repo, evicted after 7 days unused; restorable from current branch, default branch, PR base branch.
- [verified 2026-11-06 · src: https://github.com/actions/runner-images] `ubuntu-latest` = 24.04; 26.04, `-arm` and `ubuntu-slim` available.

## Pitfalls

1. A path-filtered workflow that is a required check stays `Pending` and blocks merge. Filter
   inside a job, or do not make it required.
2. A job-level `permissions:` replaces the workflow block; it does not merge.
3. `pull_request_target` always runs the default-branch workflow, with `GITHUB_REF` = default
   branch; environment branch rules now evaluate the execution ref, so old filters may not match.
4. A default-branch cache is readable by every PR branch: a cache written by a privileged or
   fork-triggered job can poison trusted ones.
5. `actions/checkout` without `persist-credentials: false` leaves the token in `.git/config`,
   then `upload-artifact path: .` ships it (zizmor `artipacked`).
6. SHA comment says v5, SHA is v4: Dependabot updated one, a human the other.
7. `secrets: inherit` hands every secret to the called workflow.
8. `if: github.actor == 'dependabot[bot]'` is spoofable (zizmor `bot-conditions`); use
   `github.event.pull_request.user.login` plus the event.
9. `GITHUB_ENV` / `GITHUB_PATH` writes from untrusted data are code execution in later steps.
10. A scheduled workflow fails silently for months; give it an owner or delete it.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax] skipped (path/branch filtered) workflows leave their checks `Pending`.
- [verified 2026-11-06 · src: https://github.blog/changelog/2025-11-07-actions-pull_request_target-and-environment-branch-protections-changes/] `pull_request_target` default-branch source and env rule change, effective 2025-12-08.
- [verified 2026-11-06 · src: https://docs.zizmor.sh/audits/] audits `artipacked`, `bot-conditions`, `github-env`, `cache-poisoning`, `secrets-inherit`, `ref-version-mismatch` exist; `impostor-commit`, `known-vulnerable-actions`, `ref-confusion`, `stale-action-refs` need online mode; `secrets-outside-env` runs only under the auditor persona.
- [verified 2026-11-06 · src: https://docs.zizmor.sh/usage/] exit codes 0 clean, 1 error, 2 bad args, 3 no inputs, 11–14 findings by max severity; `--gh-token` or `GH_TOKEN` enables online mode, `--offline` forces it off.

## Do not

- Do not pin by tag or branch, not even `actions/*`. Do not invent a SHA.
- Do not grant `write-all`, `contents: write` on CI, or `id-token: write` to a job that does
  not mint a token.
- Do not store cloud keys, PATs or registry passwords when OIDC or `GITHUB_TOKEN` will do.
- Do not `curl | sh` installers; use a pinned action or a checksummed release asset.
- Do not add a job whose failure you cannot name, a matrix nobody supports, or a scanner nobody
  reads. Do not set `continue-on-error` on a security gate.
- Do not use self-hosted runners on a public repo.
- Do not write a deploy workflow for a library — a release on tag is enough.
