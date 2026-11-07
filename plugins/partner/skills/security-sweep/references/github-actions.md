# GitHub Actions / CI rule pack

Loads for `.github/workflows/*` and composite actions, and applies by analogy to equivalent GitLab/CircleCI config.
Rule ids are `CI-<CAT>-<nn>`. CI is the highest-value target in most repos: it holds deployment credentials and
executes code on every push, so a workflow bug is a supply-chain compromise.

## Untrusted-input execution

- **CI-INJECT-01** `${{ }}` interpolation of attacker-controllable context directly into a `run:` block. The
  expression is substituted before the shell parses the script, so `github.event.issue.title`,
  `pull_request.title`/`body`, `head_ref`, `comment.body`, commit messages and author names give arbitrary command
  execution on the runner, with `GITHUB_TOKEN` and every secret in scope. CRITICAL. Fix: pass through `env:` and
  reference `"$VAR"` in the script.
- **CI-INJECT-02** The same interpolation into an `actions/github-script` body (JS injection) or into a `with:`
  input that the action shells out with.

## Trigger safety

- **CI-TRIG-01** `pull_request_target` combined with a checkout of the PR head
  (`ref: ${{ github.event.pull_request.head.sha }}`): runs fork-authored code with secrets and a write token.
  CRITICAL, the classic CI takeover. Use `pull_request` (no secrets), or check out only the base and never execute
  PR code.
- **CI-TRIG-02** `workflow_run` triggered by an untrusted workflow, then downloading and executing its artifact.
- **CI-TRIG-03** `issue_comment` / `issues` trigger running a build without verifying `author_association`.
- **CI-TRIG-04** Self-hosted runner on a public repository: fork PRs execute on your infrastructure, and runners
  are not sandboxed between jobs.

## Token & secret scope

- **CI-TOKEN-01** No top-level `permissions:` block: the workflow inherits the repository default, historically
  read-write on all scopes. Set `permissions: contents: read` at the top and widen per job.
- **CI-TOKEN-02** `permissions: write-all`, or `contents: write` / `id-token: write` / `packages: write` on a job
  that does not publish.
- **CI-TOKEN-03** `secrets: inherit` on a reusable-workflow call: passes every secret rather than the ones needed.
- **CI-TOKEN-04** Long-lived cloud credentials in secrets where OIDC (`id-token: write` plus a federated role) is
  available. With OIDC, check the cloud-side trust policy pins `repository` and `ref`/environment: a subject
  condition of just `repo:org/*` lets any branch assume the role.
- **CI-TOKEN-05** Secret used in a job that also runs untrusted code (a fork PR build, a third-party action).
- **CI-TOKEN-06** Production deploy without an `environment:` gate and required reviewers.

## Secret leakage

- **CI-LEAK-01** Secret echoed, written to a file uploaded as an artifact, or passed as a command-line argument.
  GitHub masks exact-match values only: a transformed value (base64, JSON-embedded, substring) is not masked.
- **CI-LEAK-02** `ACTIONS_STEP_DEBUG` enabled, or a step run with `set -x` while secrets are in the environment.
- **CI-LEAK-03** Secret placed in an output, a cache key or a job summary.
- **CI-LEAK-04** Artifact upload with a broad glob (`path: .`) that sweeps up `.git`, `.env` or credential files.
- **CI-LEAK-05** Cache poisoning: a cache written by a fork-triggered job and consumed by a trusted one.

## Action supply chain

- **CI-SUP-01** Third-party action referenced by tag or branch (`@vN`, `@main`) rather than a full commit SHA. Tags
  are mutable: the author, or anyone who compromises them, can change what the tag points at after your review.
  Pin to a 40-character SHA with the version in a trailing comment (`actions/*` and `github/*` are lower risk but
  should still be pinned for anything that touches secrets).
- **CI-SUP-02** Action from an unvetted namespace with access to secrets or a write token.
- **CI-SUP-03** Docker-based action referencing a mutable image tag.
- **CI-SUP-04** `curl | sh` or an unverified binary download inside a workflow.
- **CI-SUP-05** Dependency install without a lockfile, or with `--force` / `--legacy-peer-deps` masking an
  unresolved tree.

## Pipeline integrity

- **CI-GATE-01** Security checks (`audit`, SAST, secret scan) present but `continue-on-error: true`, `|| true`, or
  in a job nobody requires: a gate that cannot fail is not a gate.
- **CI-GATE-02** Coverage or lint threshold declared in policy but not enforced in the workflow.
- **CI-GATE-03** No secret-scanning or dependency-audit step at all.
- **CI-GATE-04** Deploy job triggerable manually (`workflow_dispatch`) by anyone with write access, with no
  environment protection.
- **CI-GATE-05** Release artifacts built without provenance/attestation where consumers rely on them.
- **CI-GATE-06** Branch protection assumptions the repo settings do not enforce; state as an assumption to verify,
  since the workflow file cannot show this.

## Hazards

- **CI-HAZ-01** No `timeout-minutes`: a hung job holds a runner for 6 hours.
- **CI-HAZ-02** No `concurrency` group on a deploy workflow: concurrent deploys race.
- **CI-HAZ-03** Matrix without `fail-fast: false` where partial results matter, or so large it is a self-inflicted DoS.
- **CI-HAZ-04** Scheduled workflow with no failure notification: silently broken for months.

## Verification commands (read-only)

```bash
grep -rnE '\$\{\{ *github\.(event|head_ref)' .github/workflows/     # CI-INJECT-01
grep -rn 'pull_request_target' -A20 .github/workflows/              # CI-TRIG-01
grep -rn 'uses:' .github/workflows/ | grep -vE '@[0-9a-f]{40}'      # CI-SUP-01
grep -rLn 'permissions:' .github/workflows/*.yml                    # CI-TOKEN-01
grep -rn 'continue-on-error\|secrets: inherit\||| true' .github/workflows/
actionlint                                                          # if installed
zizmor .github/workflows/                                           # if installed
```
