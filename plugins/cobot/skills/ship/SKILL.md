---
name: ship
description: Design and write the delivery pipeline of a repository at the end of a work stream, from its verified commands and profile. Writes ci.yml (PR, merge and weekly triggers with one aggregator job), release.yml (verify, attest, publish without rerunning tests) and, for a service with a Dockerfile, the image workflow (buildx, metadata tags, SBOM, cosign, Trivy), every action pinned by SHA from expert-gha, every command run locally first, then audited by /cobot:consult gha. Invoke deliberately, never at the start of a project; it changes workflow files only and proposes nothing outward.
argument-hint: [ci | release | image | all]
---

# /cobot:ship — the pipeline, proportionate and proven

You run in the main thread. Pipelines run the commands the owner runs: CONTEXT.md's verified
table is the only source of commands. A job that invents its own invocation drifts from local
reality and fails where nobody can reproduce it. Nothing here pushes, tags or publishes.

1. **Ground.** The forge is CONTEXT.md's `forge:` when set; else detect it offline, in this
   order: `.gitea/` present → Gitea; `.gitlab-ci.yml` or `.gitlab/` present → GitLab; `.github/`
   present → GitHub; the `origin` host contains `gitea` → Gitea, `gitlab` → GitLab, `github.com` →
   GitHub; else ask the owner once and record `forge:` in CONTEXT.md. A Gitea repository may keep
   `.github/workflows` (Gitea reads it when `.gitea/workflows` is absent): `forge: gitea` decides. Read
   CONTEXT.md (profile, `forge`, verified commands, constraints; `runs:` is how the owner runs
   them locally, so CI runs the verified commands bare, never with its prefix), the existing pipeline files
   (`.github/workflows/*`, `.gitea/workflows/*` or `.gitlab-ci.yml`), `Dockerfile*` and
   `compose*.y*ml`, and the forge's expert: `expert-gha` with its `references/actions.md` (for
   Gitea too, plus `expert-gitea` for what Gitea ignores), or `expert-gitlab-ci` with its
   `references/snippets.md` and `versions.md` (image digests younger than 30 days; a digest you
   did not resolve today is not written). In foreign mode (memory outside the tree) stop: the workflows belong
   to the maintainers and changes to them travel through `/cobot:contribute`. A repository
   that already has workflows gets a `/cobot:consult gha` audit and a proposed patch to the existing
   files (the diff shown, the owner approves), never a rewrite or a second pipeline beside the
   first; say what you keep. Rows in `actions.md` older than 30 days (the brief flags them) are
   re-resolved with `gh api repos/<o>/<r>/releases/latest` and `git/ref/tags/<tag>` before use;
   a SHA you did not resolve today, or a line that is only `reported`, is not written.

   Then three checks, before any job is planned:
   - **Toolchains.** Run `cobot-deps check`. Each `toolchain:` row names a floating channel
     (`stable`, `lts`, a major alone): propose a pin to the release the local proof ran on, since
     CI would otherwise take a newer one. List every pin Dependabot cannot see, each with its
     update path: a binary fetched with its sha256, `install-action` tool versions, a scanner's
     version, a container digest.
   - **The remote.** Run `git remote get-url origin` first, and say so when there is no origin.
     Then run `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes' timeout 20 git
     ls-remote --symref origin HEAD`:
     - exit 0 with no output is an **empty** remote: say so, and propose pushing the default
       branch first, before any branch or PR;
     - any failure, the timeout included, is **unreachable**, never empty.

     Name the base branch, and say when the work sits on a branch not yet merged.
   - **Absent tools.** An audit tool a job needs but the machine lacks is printed in the owner's
     install route (`cobot-env`, decision 29) and never run. Its version comes from a verified
     knowledge line or a release you resolved today, with the source named; with neither, name
     the tool without a version and say so. The job installs it in CI.
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
   on GitLab `glab ci get --branch <main>` / `glab ci status` on the tag's commit; on GitHub
   `gh run list --workflow ci.yml --event push --branch <main> --commit <sha> --status success
   --json conclusion` (the job needs `actions: read`; the merge run, not a PR run); on Gitea the
   runs API through `gt api` with the job's token. It runs in an `environment: release` with a
   required reviewer (on Gitea 28, which ignores `environment:`, the release stays a manual tag
   push by the owner and the workflow says so), rebuilds or reuses the artifact
   reproducibly, attests, publishes; it never reruns tests. Changed-area selection names a tool
   only when the language skill verified one (`vitest run --changed <base>`, `cargo test -p`,
   `go list -deps`); Python runs the full pytest on PRs and the workflow says why. Weekly: full matrix and the
   dependency audit. One aggregator job `ci-ok` (`needs:` every job, `if: always()`) fails when a
   needed job failed or was cancelled and passes when one was legitimately skipped; it is the one
   required check. A `push` to the default branch and a `pull_request` on the same commit must
   not both run the PR set: the PR trigger carries the PR set, the push trigger the merge set.
4. **Challenge.** Before writing, hand the plan (jobs, triggers, pins, permissions, omissions)
   to `cobot:challenger` as data (`run_in_background: false` where the host offers it;
   wait for every hand-back; under Antigravity `invoke_subagent` with unprefixed `challenger`);
   fold the verdict or record the owner's acceptance.
5. **Write** the workflows with the `expert-gha` non-negotiables: SHA pins with the version
   comment, `permissions: contents: read` at the top and write scopes per job with a comment,
   `persist-credentials: false`, `timeout-minutes`, `concurrency`, cache keyed on the lockfile
   hash, no cache restore in release builds, secrets in an `environment:` with reviewers for
   publish and deploy jobs, Dependabot `github-actions` entry with a cooldown. For the image
   workflow follow `expert-containers`: buildx with provenance and SBOM, `docker/metadata-action`
   tags, GHCR login with `packages: write`, keyless cosign on the digest, Trivy as a gate on
   CRITICAL and HIGH with `--ignore-unfixed`. On Gitea 28 write no `environment:` gate, no
   `id-token` job and no keyless cosign (ignored or unsupported until 29.0): name what is
   missing in the report and keep the publishing step for the owner.
6. **Prove.** `cobot-memory stamp` must answer `ok`: the pipeline describes a tree the last wrap
   verified. Then run every command the workflows run, locally, from the verified table; a command
   that fails locally does not ship. Run `zizmor --offline` and `actionlint` when present. Then
   run `/cobot:consult gha` (with `containers` when an image workflow was written) on the
   result and fold the findings.
7. **Report** and remember:

   ```text
   WORKFLOWS   <files written or changed>
   GATES       <job: the failure it prevents>
   TRIGGERS    <PR / merge / release / weekly: what runs>
   RUNTIME     <expected wall-clock per trigger>
   OMITTED     <what was left out, and why>
   UNVERIFIED  <what could not be run locally, with the command that would>
   REMOTE      <origin: empty | unreachable | default branch> · base <branch> · committed by <who>
   PINS        <toolchain pins proposed; pins outside Dependabot, each with its update path>
   ```

   Update the README's CI section when behaviour changed, journal one entry, and leave the
   commit to the build flow (one task, one commit). Secrets, environments and branch protection
   are the owner's: list them as the setup steps the owner performs, with the exact names.
