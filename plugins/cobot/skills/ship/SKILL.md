---
name: ship
description: Design and write the delivery pipeline of a repository at the end of a work stream, from its verified commands and profile. Writes ci.yml (PR, merge and weekly triggers with one aggregator job), release.yml (verify, attest, publish without rerunning tests) and, for a service with a Dockerfile, the image workflow (buildx, metadata tags, SBOM, cosign, Trivy), every action pinned by SHA from expert-gha, every command run locally first, then audited by consult-gha. Invoke deliberately, never at the start of a project; it changes workflow files only and proposes nothing outward.
argument-hint: [ci | release | image | all]
---

# /cobot:ship — the pipeline, proportionate and proven

You run in the main thread. Pipelines run the commands the owner runs: CONTEXT.md's verified
table is the only source of commands. A job that invents its own invocation drifts from local
reality and fails where nobody can reproduce it. Nothing here pushes, tags or publishes.

1. **Ground.** Read CONTEXT.md (profile, verified commands, constraints), the existing
   `.github/workflows/*`, `Dockerfile*` and `compose*.y*ml`, and `expert-gha` with its
   `references/actions.md`. In foreign mode (memory outside the tree) stop: the workflows belong
   to the maintainers and changes to them travel through `/cobot:contribute`. A repository
   that already has workflows gets a `consult-gha` audit and a proposed patch to the existing
   files (the diff shown, the owner approves), never a rewrite or a second pipeline beside the
   first; say what you keep. Rows in `actions.md` older than 30 days (the brief flags them) are
   re-resolved with `gh api repos/<o>/<r>/releases/latest` and `git/ref/tags/<tag>` before use;
   a SHA you did not resolve today, or a line that is only `reported`, is not written.
2. **Scope by profile**, then name for every job the failure it prevents; a job with no answer
   is dropped:

   | profile | pipeline |
   |---|---|
   | `library`, `cli` | lint, type check, tests with the coverage gate the repo holds today, audit; release on tag; `cli` adds the platform matrix and artifacts |
   | `service` | the above plus the image workflow (`expert-containers`) and a deploy only when CONTEXT.md names the target and its rollback |
   | `infra` | fmt, validate, tflint or equivalent, security scan, `plan` on PR as a comment artifact; `apply` is never automatic (the gate denies it) |
   | `spike`, `script` | lint and the one test command, or nothing; say so |

3. **Trigger matrix** (decision 17, the table in `expert-gha`): PR runs lint, format, type
   check, the tests of the changed areas with dependency-aware selection (`cargo test -p` plus
   dependents, `go list -deps`, `pytest --testmon` or `-k` by module only when such a tool is
   verified, otherwise the full suite with a note), the security scan, `concurrency` with
   `cancel-in-progress`. Merge to the default branch runs the full suite once and builds the
   artifact once. Release verifies the tag's commit passed on the default branch:
   `gh run list --workflow ci.yml --event push --branch <main> --commit <sha> --status success
   --json conclusion` (the job needs `actions: read`; the merge run, not a PR run), runs in an
   `environment: release` with a required reviewer, rebuilds or reuses the artifact
   reproducibly, attests, publishes; it never reruns tests. Changed-area selection names a tool
   only when the language skill verified one (`vitest run --changed <base>`, `cargo test -p`,
   `go list -deps`); Python runs the full pytest on PRs and the workflow says why. Weekly: full matrix and the
   dependency audit. One aggregator job `ci-ok` (`needs:` every job, `if: always()`) fails when a
   needed job failed or was cancelled and passes when one was legitimately skipped; it is the one
   required check. A `push` to the default branch and a `pull_request` on the same commit must
   not both run the PR set: the PR trigger carries the PR set, the push trigger the merge set.
4. **Challenge.** Before writing, hand the plan (jobs, triggers, pins, permissions, omissions)
   to `cobot:challenger` as data; fold the verdict or record the owner's acceptance.
5. **Write** the workflows with the `expert-gha` non-negotiables: SHA pins with the version
   comment, `permissions: contents: read` at the top and write scopes per job with a comment,
   `persist-credentials: false`, `timeout-minutes`, `concurrency`, cache keyed on the lockfile
   hash, no cache restore in release builds, secrets in an `environment:` with reviewers for
   publish and deploy jobs, Dependabot `github-actions` entry with a cooldown. For the image
   workflow follow `expert-containers`: buildx with provenance and SBOM, `docker/metadata-action`
   tags, GHCR login with `packages: write`, keyless cosign on the digest, Trivy as a gate on
   CRITICAL and HIGH with `--ignore-unfixed`.
6. **Prove.** Run every command the workflows run, locally, from the verified table; a command
   that fails locally does not ship. Run `zizmor --offline` and `actionlint` when present. Then
   fork `consult-gha` (and `consult-containers` when an image workflow was written) on the
   result and fold the findings.
7. **Report** and remember:

   ```text
   WORKFLOWS   <files written or changed>
   GATES       <job: the failure it prevents>
   TRIGGERS    <PR / merge / release / weekly: what runs>
   RUNTIME     <expected wall-clock per trigger>
   OMITTED     <what was left out, and why>
   UNVERIFIED  <what could not be run locally, with the command that would>
   ```

   Update the README's CI section when behaviour changed, journal one entry, and leave the
   commit to the build flow (one task, one commit). Secrets, environments and branch protection
   are the owner's: list them as the setup steps the owner performs, with the exact names.
