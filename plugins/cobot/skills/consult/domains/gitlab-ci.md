# Consult: gitlab-ci

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, commit nothing, run no pipeline. Read `skills/expert-gitlab-ci/SKILL.md`
and its references first; they are the baseline. Network use is limited to `glab` reads and
documentation fetches.

## Procedure

1. **Inventory.** `.gitlab-ci.yml`, every `include:` (local files, templates, components with
   their version form), `.gitlab/` (merge request templates, CODEOWNERS). No pipeline file →
   say so in one line and stop.
2. **Lint.** `glab ci lint` when `glab` is on PATH and authenticated (it validates against the
   instance, including includes); absent → say so and do steps 3–8 by hand with the keyword
   reference.
3. **Pipelines.** A `workflow:rules` block that admits merge requests, the default branch and
   tags and excludes branches with an open merge request; `only`/`except` anywhere → finding;
   a rule set that can produce no pipeline on a merge request → finding ("Pipelines must
   succeed" then blocks every merge).
4. **Images and tools.** Every `image:` and `services:` entry pinned by `@sha256:` digest;
   components pinned by tag or SHA, not `~latest`; `release-cli` in use (deprecated 18.0).
5. **Bounds.** `timeout` on every job; `interruptible: true` on build and test jobs and false on
   release and deploy; `resource_group` on deployments; `cache:key:files` on a lockfile with at
   most two files; `artifacts:expire_in` set; `artifacts:reports:junit` or `coverage_report`
   present when tests run.
6. **Credentials.** `id_tokens` with an explicit `aud` instead of stored cloud keys; variables
   that look like secrets referenced in `script:` arguments or echoed; `CI_JOB_JWT` references
   (removed in 17.0); job token allowlist opened wider than the documented need; `set -x` near
   a secret.
7. **Injection.** `$CI_MERGE_REQUEST_TITLE`, `$CI_COMMIT_MESSAGE`, `$CI_COMMIT_REF_NAME` or
   inputs interpolated into `script:` without quoting; `eval` of pipeline variables.
8. **Security scanning.** `Jobs/SAST.gitlab-ci.yml` and `Jobs/Secret-Detection.gitlab-ci.yml`
   included (or an equivalent job); on a Free project, a dependency audit job of the stack's own
   tool, since Dependency Scanning is Ultimate.

## Report

```text
scope: <files and includes read, glab available or not, instance tier if known>

findings:
1. <HIGH|MEDIUM|LOW> · <file>:<line> · <what> · fix: <the keyword change>
…

not covered: <includes not resolvable offline, components not fetched>

knowledge_delta (optional, JSON, only facts verified during the audit and absent from the references):
{"topic": "gitlab-ci", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

Never report a finding you did not anchor to a file and line; never fix anything. The
orchestrator decides what becomes a task.
