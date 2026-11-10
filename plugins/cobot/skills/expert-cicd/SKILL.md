---
name: expert-cicd
description: >-
  Platform-neutral CI/CD principles: the trigger matrix, one aggregator check, pinning by digest or
  SHA, least privilege and OIDC, environments, SLSA provenance, SBOM and signing, caching, timeouts,
  secrets. Use for forges without their own expert (Woodpecker, Azure, Bitbucket, CircleCI, Jenkins;
  Gitea with expert-gitea) and to design any pipeline.
paths:
  - ".gitea/workflows/**"
  - ".woodpecker*"
  - "**/.woodpecker/**"
  - "azure-pipelines.yml"
  - "bitbucket-pipelines.yml"
  - ".circleci/**"
  - "Jenkinsfile"
user-invocable: false
---

# expert-cicd

A pipeline is the owner's commands, run by someone else's machine with the owner's credentials.
Every principle below follows from that sentence. Platform specifics: `expert-gha` (GitHub
Actions) and `expert-gitlab-ci` (GitLab); this skill carries what they share and what a forge
without an expert needs. Facts and versions: `references/principles.md`.

## Non-negotiables

1. **The trigger matrix** (decision 17): pull or merge request → cheap checks first, then the
   changed area's tests; merge to the default branch → the full suite once and one artifact;
   release tag → verify the commit's CI passed, build once, attest, publish, never rerun the
   tests; weekly → dependency and knowledge refresh. One pipeline file per repository, read from
   `.agent/CONTEXT.md`'s verified commands, the same commands the owner runs locally.
2. **One required check.** An aggregator job that `needs` every other job, runs `always`, fails
   when any dependency failed or was cancelled, passes when one was legitimately skipped. It is
   the only check the branch rule requires. On GitLab the equivalent is "Pipelines must succeed"
   with merge request pipelines as the counted type.
3. **Pin everything.** Third-party steps by full commit SHA with the version in a comment;
   container images by `@sha256:` digest; tools by exact version. A moving tag is code review
   you did not do. A bot (Dependabot, Renovate) bumps the pins with a cooldown.
4. **Least privilege, short-lived.** Read-only tokens by default, widened per job for the one
   step that needs it; cloud credentials through OIDC (`id-token` / `id_tokens`) and workload
   identity, never long-lived keys in secrets; publish and deploy jobs in an environment with
   required approval and a branch or tag rule.
5. **Secrets never in logs.** Bind to environment variables on the step that needs them; never
   in command arguments, outputs, artifacts, cache keys or summaries; never `set -x` near one;
   masking is a courtesy, not a control.
6. **No untrusted input in a shell.** Titles, branch names, comments and inputs are data: pass
   them through variables and quote them; never interpolate them into `run:` or `script:`.
7. **Bounded jobs.** A timeout on every job (about twice the normal run), concurrency or
   auto-cancel on pull-request pipelines, never on release or deploy.
8. **Supply-chain evidence.** Provenance attestation on released artifacts (SLSA Build L2 from
   an in-repo pipeline, L3 only through a hardened shared workflow), an SBOM (SPDX or CycloneDX)
   shipped with the release, signatures through Sigstore keyless where the forge supports OIDC;
   consumers verify, the README states the level claimed and no more.
9. **Reproducible, cached, observable.** Same source + same environment + same instructions =
   identical artifacts; caches keyed on lockfile hashes and never restored in release builds
   (cache poisoning); DORA metrics (lead time, deployment frequency, failed-deployment recovery
   time, change fail rate) are how the pipeline is judged, not its line count.

## What each forge calls it

| concept | GitHub Actions | GitLab CI | Gitea Actions |
|---|---|---|---|
| pipeline file | `.github/workflows/*.yml` | `.gitlab-ci.yml` | `.gitea/workflows/*.yml` (GitHub syntax, mostly) |
| PR trigger | `on: pull_request` | `workflow:rules` on `merge_request_event` | `on: pull_request` |
| required check | branch rule → aggregator job | "Pipelines must succeed" | branch protection → status |
| job graph | `needs:` | `needs:` (DAG, stages optional) | `needs:` |
| OIDC token | `permissions: id-token: write` | `id_tokens: NAME: aud:` | not supported |
| environment gate | `environment:` with reviewers | `environment:` + protected environments (Premium) | ignored |
| cancel superseded | `concurrency.cancel-in-progress` | `interruptible: true` + `auto_cancel` | `concurrency` |
| pinned image | `container: image@sha256` | `image: name@sha256:…` | `container:` |
| release | `gh release create --verify-tag` | `release:` keyword with `glab` | `tea release create` |
| CLI | `gh` | `glab` | `tea` |

## Pitfalls

- A required check that can be skipped by a path filter stays Pending forever and blocks the
  merge; condition the job, not the workflow.
- Two pipelines for one change (branch and merge request) double the cost and the flakiness;
  one `workflow:rules` block or one `on:` block decides.
- A SHA comment that says v5 while the SHA is v4 is a bot and a human disagreeing; trust the SHA.
- "SLSA L3" claimed from an in-repo workflow is false; L2 is what a hosted, signed, in-repo build
  provides.
- An SBOM generated after the build from the running container is not the build's SBOM.

- [verified 2026-11-08 · src: https://slsa.dev/spec/v1.0/levels] SLSA Build L1 provenance exists, L2 signed provenance from a hosted platform, L3 hardened isolated builds; the current specification is v1.2.
