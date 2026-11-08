# GitLab CI snippets — the trigger matrix in `.gitlab-ci.yml`

Copy, then replace the commands with CONTEXT.md's verified table and the digest with a row from
`versions.md` younger than 30 days. Semantics verified 2026-11-08 on docs.gitlab.com (see
`versions.md`).

## `.gitlab-ci.yml` — merge requests, default branch, tags, weekly

```yaml
# One pipeline per change: merge request pipelines, the default branch, tags, and the schedule.
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never                     # the merge request pipeline already runs this change
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
    - if: $CI_PIPELINE_SOURCE == "schedule"
  auto_cancel:
    on_new_commit: interruptible      # cancels build and test jobs of a superseded commit

default:
  image: python:3.13-slim@sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc # resolved 2026-11-08
  interruptible: true
  cache:
    key:
      files: [uv.lock]                # the lockfile; two files at most
    paths: [.cache/uv]
    policy: pull-push

variables:
  UV_CACHE_DIR: .cache/uv
  PIP_DISABLE_PIP_VERSION_CHECK: "1"

# cheap checks first; each job names the failure it prevents
lint:
  needs: []
  timeout: 10 minutes
  script:
    - python3 -m ruff check .         # from CONTEXT.md's verified table
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
    - when: on_success

test:
  needs: []
  timeout: 20 minutes
  script:
    - python3 -m pytest -q --junitxml=report.xml --cov --cov-report=xml
  coverage: '/TOTAL.*\s(\d+%)/'
  artifacts:
    when: always
    expire_in: 1 week
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
    - when: on_success

audit:                                 # Dependency Scanning is Ultimate; a Free project runs its own
  needs: []
  timeout: 10 minutes
  script:
    - python3 -m pip_audit            # or npm audit, cargo audit, govulncheck
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

include:
  - template: Jobs/SAST.gitlab-ci.yml                # reports in every tier
  - template: Jobs/Secret-Detection.gitlab-ci.yml

build:                                 # the default branch and tags build once
  needs: [lint, test]
  timeout: 20 minutes
  interruptible: false
  script:
    - python3 -m build
  artifacts:
    paths: [dist/]
    expire_in: 30 days
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

release:                               # the tag's pipeline passed lint, test and build above
  needs: [build]
  image: registry.gitlab.com/gitlab-org/cli:latest   # resolve a digest before shipping this line
  interruptible: false
  resource_group: release
  timeout: 10 minutes
  script:
    - echo "releasing $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    description: "See CHANGELOG.md"
    assets:
      links:
        - name: dist
          url: "$CI_PROJECT_URL/-/jobs/$CI_JOB_ID/artifacts/download"
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
```

GitLab's required check is the project setting "Pipelines must succeed" with merge request
pipelines; no aggregator job is needed because a pipeline is one unit.

## OIDC to a cloud (no stored key)

```yaml
deploy:
  needs: [build]
  interruptible: false
  resource_group: production
  environment:
    name: production
    deployment_tier: production
  id_tokens:
    GCP_ID_TOKEN:
      aud: https://iam.googleapis.com/projects/<n>/locations/global/workloadIdentityPools/<pool>/providers/<provider>
  script:
    - gcloud iam workload-identity-pools create-cred-config ... --credential-source-file=<(echo "$GCP_ID_TOKEN")
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
      allow_failure: false
```

## Weekly schedule

Create the schedule in the project (CI/CD → Schedules, weekly, on the default branch); the
`workflow:rules` entry for `schedule` above lets only the `audit` job run on it.
