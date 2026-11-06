---
name: consult-gha
description: >-
  Read-only GitHub Actions audit by the consultant agent. Invoke to audit a repository's
  workflows and composite actions, before cutting a release, after upgrading or adding
  actions, or when zizmor, Dependabot or a reviewer flags CI. Checks every non-negotiable of
  expert-gha, resolves each pinned SHA against upstream, and returns at most ten ranked findings
  plus a knowledge_delta for anything newly verified.
context: fork
agent: partner:consultant
user-invocable: true
---

# consult-gha

Read-only. Change nothing, commit nothing, push nothing; never pass `--fix` to zizmor. Read the
sibling skill `../expert-gha/SKILL.md` and its `references/actions.md` first: they are the
baseline. Network use is limited to `gh api` GETs and documentation fetches.

## Procedure

1. **Inventory.** List `.github/workflows/*.y*ml`, `.github/actions/**/action.y*ml`, root
   `action.y*ml`, `.github/dependabot.yml`, `renovate.json*`, `.github/zizmor.yml`. Note each
   workflow's triggers and jobs. No workflows → report that in one line and stop.
2. **zizmor.** If `zizmor` is on PATH, run
   `zizmor --persona auditor --gh-token "$(gh auth token)" .` when `gh` is authenticated
   (online audits: `impostor-commit`, `known-vulnerable-actions`, `ref-confusion`), else
   `zizmor --offline .`. Exit 11–14 = findings (14 = high), 1–3 = tool error. Read every finding;
   keep its audit id as evidence. Absent → say so and do steps 3–8 by hand. Run `actionlint` if
   present.
3. **Pins.** For every `uses:` that is not `./…` or `docker://…@sha256:`:
   - floating ref (tag, branch, short SHA) → finding;
   - match each SHA to a tag:
     `gh api --paginate repos/<o>/<r>/git/matching-refs/tags --jq '.[]|select(.object.sha=="<sha>")|.ref'`
     (annotated tags point at a tag object: dereference with `git/tags/<object.sha>`). No tag →
     finding; the commits API also serves fork-network commits, so only zizmor
     `impostor-commit` or a tag match proves the SHA belongs to the repo;
   - version comment ≠ resolved tag → finding;
   - `gh api repos/<o>/<r>/releases/latest` — behind by a major → finding, behind by minor
     only → mention in summary; archived repo → finding.
4. **Permissions.** Top-level block present and read-only or `{}`. Per job: each write scope
   justified by a step in that job (`contents: write` → release/push, `id-token: write` → OIDC
   or attest, `security-events: write` → SARIF, `attestations: write` → attest).
   `write-all`, missing block, `secrets: inherit` → finding.
5. **Checkout and hygiene.** `persist-credentials: false` on every checkout; `concurrency` per
   workflow (no `cancel-in-progress: true` on release/deploy); `timeout-minutes` per job;
   `continue-on-error` or `|| true` on a gate; `curl | sh`; self-hosted runner on a public repo.
6. **Injection and triggers.** `grep -rnE '\$\{\{[^}]*(github\.event\.|github\.head_ref|inputs\.|steps\.[^}]*outputs)' .github`
   inside `run:`, `script:` (github-script) and composite steps; writes of such data to
   `GITHUB_ENV`/`GITHUB_PATH`. Every `pull_request_target`, `workflow_run`, `issue_comment`:
   is there a written reason, does it check out or execute PR-controlled code, does it hold
   secrets or a write token, is the actor/association checked without `github.actor`.
7. **Updates.** Dependabot `github-actions` entry (`directory: /`, schedule, `cooldown`), or
   Renovate with digest pinning. Missing → finding. Composite actions in subdirectories need
   their own `directories:` entry.
8. **Release path.** Tag-triggered workflow: changelog or notes gate, no cache restore in the
   build (`cache-poisoning`), `actions/attest` (or `attest-build-provenance`) on the shipped
   artifacts with `id-token: write` + `attestations: write`, publish job in an `environment:`,
   `gh release create --verify-tag`, pre-release detection. Note any SLSA level claimed in the
   README against what the workflow can support (in-repo = L2, shared reusable = L3).
9. **Cloud auth.** Secrets named like `*_KEY`, `*_CREDENTIALS`, `GOOGLE_*`, `AWS_SECRET*` used
   where OIDC exists → finding. With `google-github-actions/auth`, check `workload_identity_provider`
   is used; the attribute condition lives in GCP — mark it `assumed` unless the IaC is in the repo,
   then read it.
10. **Rank.** Keep the ten most severe; merge duplicates across files into one finding listing
    the locations.

Severity: `critical` = code execution or secret exposure reachable by an outsider; `high` =
write token or secret reachable by untrusted code, floating pin on a job with secrets, missing
provenance on published artifacts users verify; `medium` = missing pin/permissions/timeout/
update config without a reachable exploit; `low` = hygiene, stale minor, comment drift.

Confidence: `high` = seen in the file and confirmed by zizmor or the API; `medium` = seen in the
file, impact depends on repo settings you cannot read; `low` = inferred.

## Report

```text
summary: <one line — workflows audited, zizmor run or not, worst severity>

findings:
1. <severity> · <file>:<line> · <what> · fix: <exact change, SHA from actions.md or the API> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-gha
  topic: gha
  entries:
    - claim: "<one sentence, with the number>"
      status: verified        # verified | reported | assumed
      source: "<url or exp: command>"
      checked: <YYYY-MM-DD>   # audit date
      scope: plugin           # plugin = belongs in expert-gha references; project = .agent/knowledge/gha.md
```

No finding without a file and line. Repository settings you cannot read (branch protection,
environment reviewers, allowed-actions policy) go in the summary as "not verifiable from the
tree", not as findings. Zero findings is a valid result; say what was checked.

- [verified 2026-11-06 · src: https://docs.zizmor.sh/usage/] exit codes 0 clean, 1 error, 2 bad args, 3 no inputs, 11–14 findings by max severity; `--gh-token` or `GH_TOKEN` enables online mode, `--offline` forces it off.
- [verified 2026-11-06 · src: https://docs.zizmor.sh/audits/] `impostor-commit`, `known-vulnerable-actions`, `ref-confusion`, `stale-action-refs` need online mode; `secrets-outside-env` runs only under the auditor persona.
