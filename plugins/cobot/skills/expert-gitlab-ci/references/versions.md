# GitLab — verified versions and facts

Format: `- [verified|reported YYYY-MM-DD · src: <url>] claim`. Version lines are flagged after 30
days, idiom after 90 (`cobot-memory knowledge --stale expert-gitlab-ci`).

## Platform and CLI

- [verified 2026-11-08 · src: https://docs.gitlab.com/releases/19/gitlab-19-5-released/] GitLab 19.5 is the current release (15 October 2026); 19.6 is upcoming.
- [verified 2026-11-08 · src: https://docs.gitlab.com/policy/maintenance/] Minor releases on the third Thursday of each month; GitLab 20.0 is scheduled for 20 May 2027; patches twice a month.
- [verified 2026-11-08 · src: https://gitlab.com/api/v4/projects/gitlab-org%2Fcli/releases?per_page=3] `glab` v1.128.0 (2026-11-03) is the latest release.
- [verified 2026-11-08 · src: https://gitlab.com/gitlab-org/cli/-/raw/main/docs/installation_options.md] Install: Homebrew (official), release binaries, mise (`glab = "latest"` under `[tools]`), snap, dnf, pacman, apk, Nix, Docker `gitlab/glab`; no GitLab-hosted apt repository.

## Images

| image | digest (multi-arch index) | resolved | source |
|---|---|---|---|
| `python:3.13-slim` | `sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc` | 2026-11-08 | registry-1.docker.io/v2/library/python/manifests/3.13-slim |
| `registry.gitlab.com/gitlab-org/cli:latest` | resolve before use (`docker buildx imagetools inspect`) | — | docs.gitlab.com/ci/yaml/ (`release:` recommends it) |

- [verified 2026-11-08 · src: https://registry-1.docker.io/v2/library/python/manifests/3.13-slim] `python:3.13-slim` index digest on 2026-11-08 is `sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc`.

## Keywords (semantics verified 2026-11-08 on docs.gitlab.com)

- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/needs/] `needs:` builds a DAG; `stage`/`stages` may be omitted; `needs: []` starts a job immediately; `optional: true` tolerates a missing job; up to 50 needs.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] Default stages when `stages` is absent: `.pre`, `build`, `test`, `deploy`, `.post`; a job without `stage` is in `test`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/components/] `include: component:` with `inputs:`; version priority SHA > tag > branch > `~latest`/partial semver; up to 100 components per project; Catalog GA in 17.0, all tiers.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `id_tokens` need `aud`; allowed in `default`; `CI_JOB_JWT*` removed in 17.0 (<https://docs.gitlab.com/ci/cloud_services/>).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `cache:key:files` takes 2 files (10 behind a 19.5 flag); `cache:policy` `pull`, `push`, `pull-push`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/artifacts_reports/] `artifacts:reports` `junit`, `coverage_report` (Cobertura or JaCoCo), `codequality`, `sast`, `secret_detection`, `dotenv`, `terraform` in all tiers; `cyclonedx`, `dependency_scanning`, `container_scanning`, `dast`, `sarif` Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/] `interruptible` defaults to false; `workflow:rules:auto_cancel:on_new_commit` `conservative` (default), `interruptible`, `none`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/pipelines/settings/] Project job timeout default 60 minutes; job `timeout` in natural language, not allowed under `default`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/resource_groups/] `resource_group` process modes `unordered` (default), `oldest_first`, `newest_first`, `newest_ready_first`.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/environments/] `deployment_tier` values `production`, `staging`, `testing`, `development`, `other`; protected environments are Premium and Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/project/releases/release_cli/] `release-cli` deprecated in 18.0, removal planned in 20.0; the `release:` keyword needs `glab` on the PATH.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/docker/using_docker_images/] `image: name@sha256:<digest>` is verified by the runner; a modified image is refused.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/deprecated_keywords/] Global `image`, `services`, `cache`, `before_script`, `after_script` and `only`/`except` are deprecated (no removal milestone).
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/variables/] Protected variables reach protected refs only; masked variables one line, 8+ characters, shown as `[MASKED]`; default visibility Masked since 18.3.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/jobs/ci_job_token/] Job token allowlist contains only the project by default; 200 groups and 200 projects at most; JWT format by default from 19.0.
- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/] Merged results pipelines and merge trains are Premium and Ultimate.
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/application_security/sast/] `Jobs/SAST.gitlab-ci.yml` and `Jobs/Secret-Detection.gitlab-ci.yml` run in every tier with JSON reports; dashboards, MR widgets and Advanced SAST are Ultimate; Dependency Scanning is Ultimate (`Jobs/Dependency-Scanning.v2.gitlab-ci.yml` recommended).
- [verified 2026-11-08 · src: https://docs.gitlab.com/user/project/merge_requests/auto_merge/] "Pipelines must succeed" refuses a merge request with no pipeline and counts only merge request pipelines when several types run.
