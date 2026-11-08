# cicd — knowledge (project scope: research delta for expert-cicd, expert-gitlab-ci and Gitea, gathered 2026-11-08)

Format: `- [status date · src: url] claim`. `verified` = primary source read that day; `reported` = secondary.

## GitLab platform and glab

- [verified 2026-11-08 · src: https://docs.gitlab.com/releases/19/gitlab-19-5-released/] GitLab 19.5 released 15 October 2026 (headline: GitLab MCP server generally available); 19.6 is the upcoming release.
- [verified 2026-11-08 · src: https://docs.gitlab.com/policy/maintenance/] Minor releases monthly on the third Thursday; major releases in May (GitLab 20.0 scheduled 20 May 2027); patch releases twice monthly.
- [verified 2026-11-08 · src: https://gitlab.com/api/v4/projects/gitlab-org%2Fcli/releases?per_page=3] `glab` v1.128.0 released 2026-11-03.
- [verified 2026-11-08 · src: https://gitlab.com/gitlab-org/cli/-/raw/main/docs/installation_options.md] Install: Homebrew (officially supported), binaries on the releases page, mise (`glab = "latest"` under `[tools]`), asdf, snap, dnf, pacman, apk, Nix, Docker `gitlab/glab`; no GitLab-hosted apt repository.
- [verified 2026-11-08 · src: https://docs.gitlab.com/cli/] Start with `glab auth login`; OAuth or personal access token; all tiers.

## .gitlab-ci.yml keywords

- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/workflow/] `workflow:rules` controls when pipelines are created and is evaluated before jobs; when no rule matches, no pipeline runs; `when` there is `always` or `never` only.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/workflow/] Duplicate pipelines (branch + merge request) are avoided with `workflow:rules`: `if: $CI_PIPELINE_SOURCE == "merge_request_event"`, then `if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS` with `when: never`, then `if: $CI_COMMIT_BRANCH`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `workflow:rules:auto_cancel:on_new_commit`: `conservative` (default), `interruptible`, `none`; `on_job_failure`: `all` or `none`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/] Merge request pipelines need a job or workflow rule matching `merge_request_event`; rules in included files do not count; they run on the source branch content; all tiers.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/jobs/job_rules/] Rules are evaluated in order until the first match; negation with `!` since GitLab 18.11.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `rules:if` adds the job when true (`when: never` removes it); `rules:changes` up to 50 patterns, `compare_to` needs `paths`; `rules:exists` up to 50 patterns; `when`: `on_success` (default), `delayed`, `always`, `never`, `manual`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/] Merged results pipelines and merge trains are Premium and Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/needs/] `needs:` builds a DAG; `stage` and `stages` may be omitted entirely; `needs: []` starts a job immediately; `optional: true` depends on a job only if it exists; up to 50 needs.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] Default stages when `stages` is absent: `.pre`, `build`, `test`, `deploy`, `.post`; a job without `stage` is in `test`; a pipeline with only `.pre`/`.post` jobs does not run.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/components/] `include: - component: $CI_SERVER_FQDN/<path>/<component>@<version>` with `inputs:`; components come from the same instance; templates in `templates/`; up to 100 components per project; version priority commit SHA > tag > branch > `~latest` or partial semver (`1`, `1.2`); `~latest` excludes pre-releases; Catalog GA in 17.0, all tiers; publishing needs the Catalog toggle, a README, a description and a `release:` created by a job with a semver tag.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `spec:inputs` are mandatory unless `default`; referenced as `$[[ inputs.name ]]`; `include:inputs` GA in 17.0.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `id_tokens`: required `aud` (string, array or variables); allowed in `default`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/secrets/id_token_authentication/] ID token: RS256 JWT, `aud` defaults to the instance domain, `sub` is `project_path:{group}/{project}:ref_type:{type}:ref:{branch}`, `exp` = job timeout or 5 minutes.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/cloud_services/] `CI_JOB_JWT` and `CI_JOB_JWT_V2` were removed in GitLab 17.0; keys at `https://gitlab.com/oauth/discovery/keys`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `cache:key:files` up to 2 files (10 behind a 19.5 flag); fallback key `default`; `cache:policy` `pull`, `push`, `pull-push` (default).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/artifacts_reports/] `artifacts:reports` includes `junit`, `coverage_report` (Cobertura or JaCoCo), `codequality`, `sast`, `secret_detection`, `dotenv`, `terraform` in all tiers; `cyclonedx`, `dependency_scanning`, `container_scanning`, `dast`, `sarif` are Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] Report artifacts always upload regardless of job result; `artifacts:when` `on_success` (default), `on_failure`, `always`; `expire_in` defaults to the instance setting.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `interruptible: true` cancels a job when a new pipeline starts on the same ref; set it only on jobs safe to cancel (builds, tests).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/pipelines/settings/] Project job timeout default 60 minutes (10 minutes to one month); job `timeout` in natural language, not allowed in `default`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/resource_groups/] `resource_group` runs one job at a time per key; process modes `unordered` (default), `oldest_first` (safer for continuous deployment), `newest_first`, `newest_ready_first`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/environments/] `environment:deployment_tier`: `production`, `staging`, `testing`, `development`, `other`; `auto_stop_in`, `on_stop`, `action` (`prepare`, `verify`, `access`, `stop`); protected environments are Premium and Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/project/releases/release_cli/] `release-cli` deprecated in GitLab 18.0, removal planned in 20.0; the `release:` keyword needs `glab` on the PATH (recommended image `registry.gitlab.com/gitlab-org/cli:latest`); `release:tag_name` required.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/docker/using_docker_images/] Images may be referenced as `<name>@<digest>`; GitLab verifies the digest and refuses a modified image.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `default:` accepts `after_script`, `artifacts`, `before_script`, `cache`, `hooks`, `id_tokens`, `image`, `interruptible`, `retry`, `services`, `tags`; it does not merge with job configuration.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/deprecated_keywords/] Global `image`, `services`, `cache`, `before_script`, `after_script` are deprecated in favour of `default`; `only` and `except` are deprecated in favour of `rules` (no removal milestone).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/yaml_optimization/] `!reference [.job, script]` reuses keyword configuration across included files (anchors cannot); nests up to 10 levels; prefer `extends` where possible.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/includes/] `include:rules` supports `if`, `exists`, `changes`; up to 150 nested includes.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/variables/] Protected variables reach only protected branches and tags; masked variables must be one line, 8+ characters; masked output shows `[MASKED]` and is not a security guarantee; default visibility is Masked since 18.3; hidden variables cannot be revealed again.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/jobs/ci_job_token/] `CI_JOB_TOKEN` inbound allowlist contains only the project itself by default; groups allowed since 17.0; limits 200 groups and 200 projects; JWT format by default from 19.0.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/project/merge_requests/auto_merge/] "Pipelines must succeed": a merge request with no pipeline cannot merge; when several pipeline types run, only merge request pipelines count (GitLab's equivalent of one required check).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `trigger:strategy: mirror` since 18.2 (`depend` not recommended); `secrets` is Premium and Ultimate; `secrets:gitlab_secrets_manager` since 19.0.

## GitLab security templates

- [verified 2026-11-08 · src: https://docs.gitlab.com/user/application_security/sast/] Include `template: Jobs/SAST.gitlab-ci.yml`; open-source SAST runs in Free and Premium with a downloadable JSON report; vulnerability management, the MR widget and Advanced SAST are Ultimate; `stable` template for production, `latest` for new features.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/application_security/secret_detection/pipeline/] Include `template: Jobs/Secret-Detection.gitlab-ci.yml`; scans and JSON reports in any tier; MR findings and dashboards are Ultimate.
- [verified 2026-11-08 · src: https://gitlab.com/gitlab-org/gitlab/-/raw/master/lib/gitlab/ci/templates/Security/SAST.gitlab-ci.yml] The `Security/*` templates moved to `Jobs/*` in GitLab 14.0 and now only include them.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/application_security/dependency_scanning/dependency_scanning_sbom/] Dependency Scanning is Ultimate; the recommended template is `Jobs/Dependency-Scanning.v2.gitlab-ci.yml` (since 18.5) or the component `$CI_SERVER_FQDN/components/dependency-scanning/main@1` (GA 18.8); SBOM-based scanning GA in 19.0; Gemnasium deprecated in 17.9.

## Platform-neutral principles

- [verified 2026-11-08 · src: https://slsa.dev/spec/v1.0/levels] SLSA Build track: L1 provenance exists, L2 signed provenance from a hosted build platform (tampering after the build), L3 hardened builds (tampering during the build, runs isolated from one another).
- [verified 2026-11-08 · src: https://slsa.dev/spec/] The current SLSA specification is version 1.2 (approved); v1.2 adds a Source track.
- [verified 2026-11-08 · src: https://slsa.dev/spec/v1.0/provenance] Provenance is an in-toto Statement v1 with predicate `https://slsa.dev/provenance/v1`.
- [verified 2026-11-08 · src: https://github.com/sigstore/cosign/releases] cosign v3.1.4 (2026-10-20); the 2.x line is still maintained (v2.6.5).
- [verified 2026-11-08 · src: https://blog.sigstore.dev/cosign-3-0-available/] Cosign v3 (8 October 2025): new bundle format, `--trusted-root`, signing config on by default.
- [verified 2026-11-08 · src: https://docs.sigstore.dev/cosign/signing/overview/] Keyless signing binds an ephemeral key to an OIDC identity through a short-lived Fulcio certificate, logged in Rekor; the identity token's `aud` must contain `sigstore`; `cosign sign $IMAGE` with no `--key` is keyless.
- [verified 2026-11-08 · src: https://github.com/spdx/spdx-spec/releases/tag/3.0.1] SPDX 3.0 released 15 April 2024; 3.0.1 on 17 December 2024; SPDX is ISO/IEC 5962:2021.
- [verified 2026-11-08 · src: https://cyclonedx.org/specification/overview/] CycloneDX 1.7 is current (2025-10-21); 1.6 (9 April 2024) added CBOM and attestations; ECMA-424 2nd edition December 2025.
- [verified 2026-11-08 · src: https://reproducible-builds.org/docs/definition/] A build is reproducible if, given the same source, build environment and instructions, any party can recreate bit-by-bit identical artifacts.
- [verified 2026-11-08 · src: https://trunkbaseddevelopment.com/short-lived-feature-branches/] Trunk-based development: everyone commits to trunk at least daily; a feature branch lasts a couple of days at most, one developer (two if pairing), merged then deleted.
- [verified 2026-11-08 · src: https://dora.dev/guides/dora-metrics-four-keys/] DORA metrics: change lead time, deployment frequency, failed deployment recovery time (replaced MTTR), change fail rate, plus deployment rework rate.
- [verified 2026-11-08 · src: https://dora.dev/research/2025/dora-report/] The 2025 report is "State of AI-assisted Software Development 2025"; the 2024 report is "Accelerate State of DevOps 2024".
- [verified 2026-11-08 · src: https://github.com/re-actors/alls-green] Aggregator pattern: one `check` job lists every other job in `needs` and is the only required check; it must run with `if: always()` or a skipped dependency reports `skipped`, not `failed`.
- [verified 2026-11-08 · src: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks] GitHub: path-filtered required workflows stay Pending and block merging; jobs skipped by conditionals report Success; use `always()` with `needs` for required checks.
- [verified 2026-11-08 · src: https://registry-1.docker.io/v2/library/python/manifests/3.13-slim] `python:3.13-slim` index digest on 2026-11-08: `sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc` (linux amd64, arm64, arm, 386, ppc64le).

## Gitea

- [verified 2026-11-08 · src: https://github.com/go-gitea/gitea/releases] Gitea v28.3.0 (2026-11-01); 28.0.0 (30 September 2026) dropped the historical `1.` version prefix.
- [verified 2026-11-08 · src: https://gitea.com/gitea/tea/releases] `tea` CLI v0.16.0 (2026-09-10).
- [verified 2026-11-08 · src: https://docs.gitea.com/usage/actions/comparison] Gitea Actions is mostly compatible with GitHub Actions workflow syntax (hard fork of nektos/act); workflows live in `.gitea/workflows/`; actions without a host are fetched from GitHub by default; `environment`, problem matchers and the `statuses`, `checks`, `id-token` permission scopes are unsupported.
- [verified 2026-11-08 · src: https://gitea.com/gitea/runner/releases/tag/v1.0.0] `act_runner` was renamed `gitea-runner` (v1.0.0, 2026-05-05); latest runner v5.4.1 (2026-11-05); labels `docker://<image>`, `kubernetes://<image>`, `host`.

## unverified

- `id_tokens` introduction version; OIDC discovery URL; `only/except` removal milestone; whether Gitea reads `.github/workflows/`; the `glab ci` subcommand list (`glab --help` not run: `glab` is not installed on this machine).
