---
name: expert-gitlab-ci
description: >-
  GitLab CI/CD knowledge, current as of 2026-11-08: .gitlab-ci.yml keywords and shapes
  (workflow:rules against duplicate pipelines, rules, needs DAG, components, id_tokens, cache,
  reports, interruptible, resource_group, environments, release with glab, digest-pinned images,
  default, !reference, job token allowlist, variables, security templates and tiers), the glab
  commands and their gate verdicts, pitfalls. Loads when .gitlab-ci.yml or .gitlab/ is touched;
  pipelines in references/snippets.md, versions in references/versions.md.
paths:
  - ".gitlab-ci.yml"
  - "**/.gitlab-ci*.yml"
  - ".gitlab/**"
user-invocable: false
---

# expert-gitlab-ci

The principles are in `../expert-cicd/SKILL.md`; this is their GitLab form. Pipelines:
`references/snippets.md`. Versions and digests: `references/versions.md` (a row older than 30
days is re-resolved before it is written anywhere). Quote the status of what you rely on.

## Non-negotiables

1. **One `workflow:rules` block** decides which pipelines exist: merge request pipelines, the
   default branch, tags; branches with an open merge request are `when: never` so a change never
   runs twice. A job or workflow rule on `merge_request_event` is what makes merge request
   pipelines exist at all; rules in included files do not count.
2. **`rules:`, never `only/except`** (deprecated). Rules evaluate in order to the first match;
   `changes:` for area-scoped jobs, `exists:` for optional tooling; `when: manual` only with
   `allow_failure: false` when the gate matters.
3. **`needs:` is the graph.** Omit `stages` unless a stage boundary carries meaning; `needs: []`
   starts a job at once; cap fan-in at the 50-needs limit.
4. **Pin images by digest**: `image: python:3.13-slim@sha256:…` from a dated row; GitLab verifies
   the digest and refuses a modified image. `default:` holds the image, `interruptible: true`,
   `id_tokens` and the cache; globals outside `default` are deprecated.
5. **OIDC through `id_tokens`** with an explicit `aud`; no long-lived cloud keys in variables;
   `CI_JOB_JWT*` are gone since 17.0. Variables that matter are protected (protected refs only)
   and masked (8+ characters, one line); masking is not a security boundary.
6. **Job token allowlist** stays "only this project" unless a documented cross-project need adds
   one group or project.
7. **Cancel superseded work**: `interruptible: true` on build and test jobs,
   `workflow:rules:auto_cancel:on_new_commit: interruptible`; never on release or deploy jobs,
   which use `resource_group` (`oldest_first` for deployments) instead.
8. **Timeouts** on every job (`timeout: 20 minutes`, about twice the normal run), `cache:key:
   files:` on the lockfile, `artifacts:reports:junit` and `coverage_report` so the merge request
   shows results, `expire_in` set.
9. **Release through the `release:` keyword with `glab`** on the runner
   (`registry.gitlab.com/gitlab-org/cli`), triggered by a tag whose commit's pipeline passed;
   `release-cli` is deprecated (18.0) and removed in 20.0.
10. **Security scanning** by `include: template: Jobs/SAST.gitlab-ci.yml` and
    `Jobs/Secret-Detection.gitlab-ci.yml` (reports in every tier; dashboards are Ultimate);
    Dependency Scanning is Ultimate only, so a Free project runs its own `pip-audit`,
    `npm audit`, `cargo audit` or `govulncheck` job instead.

## `glab` under the gate

| command | verdict | why |
|---|---|---|
| `glab auth status`, `glab repo view`, `glab ci status\|list\|get\|trace\|lint`, `glab mr view\|list\|diff`, `glab release list\|view`, `glab api <GET path>` | silent for the consultant and the learner | reads |
| `glab mr create\|update`, `glab ci run\|retry\|cancel\|delete`, `glab variable set\|delete`, `glab release delete`, `glab api` POST/PUT/PATCH (a body flag without `-X` is a POST) | ask | outward or mutating |
| `glab mr merge` | ask | merges are the owner's |
| `glab release create`, `glab repo delete`, `glab api -X DELETE`, `glab mr create\|update … Generated with …` | never | publishes, destroys, or names an AI as author (decision 18) |

`glab ci view` is an interactive terminal UI: use `glab ci get` or `glab ci status` in a session.

## Pitfalls

- Branch pipelines plus merge request pipelines without `workflow:rules` run everything twice.
- "Pipelines must succeed" refuses a merge request that produced no pipeline: a `workflow:rules`
  block that excludes merge requests blocks every merge.
- `rules:changes` on a merge request pipeline compares with the target; on a branch pipeline
  with no previous push it matches everything. Scope with `compare_to` when it matters.
- `cache:key:files` accepts two files (ten behind a flag); a third is silently ignored.
- `timeout` is not accepted under `default:`; set it per job.
- A component referenced as `~latest` moves; pin a tag or SHA in anything reproducible.

- [verified 2026-11-08 · src: https://docs.gitlab.com/ci/yaml/workflow/] `workflow:rules` is evaluated before jobs; when no rule matches, the pipeline does not run; the documented fix for duplicate pipelines excludes `$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS`.
