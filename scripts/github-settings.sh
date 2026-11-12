#!/usr/bin/env bash
# Repository settings for the GitHub remote, as code. Idempotent.
#   scripts/github-settings.sh --check   print wanted vs current, change nothing (default)
#   scripts/github-settings.sh --apply   set every setting that differs
# Credentials are never handled here: the script prints the federation rules to create and the
# `gh variable set` / `gh secret set` commands the owner runs.
# REPO=owner/name overrides the remote's repository.
set -euo pipefail

MODE="${1:---check}"
case "$MODE" in --check | --apply) ;; *) echo "usage: $0 [--check|--apply]" >&2; exit 2 ;; esac
command -v jq > /dev/null || { echo "jq is required" >&2; exit 2; }
REPO="${REPO:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
APPLY=0; [ "$MODE" = "--apply" ] && APPLY=1
DIFFS=0
REQUIRED_CHECK="ci-ok"
ENVIRONMENTS="evals knowledge-refresh"

api() { gh api -H "Accept: application/vnd.github+json" "$@"; }

want() { # want <label> <wanted> <current> <apply-command...>
  local label="$1" wanted="$2" current="$3"; shift 3
  if [ "$wanted" = "$current" ]; then
    printf '  ok    %-34s %s\n' "$label" "$current"; return
  fi
  DIFFS=$((DIFFS + 1))
  printf '  diff  %-34s %s -> %s\n' "$label" "${current:-<unset>}" "$wanted"
  [ "$APPLY" = 1 ] && "$@" > /dev/null
  return 0
}

repo_flags() {
  local cur
  cur=$(api "repos/$REPO")
  echo "repository"
  want "delete branch on merge" true "$(jq -r .delete_branch_on_merge <<< "$cur")" \
    gh repo edit "$REPO" --delete-branch-on-merge
  # one task = one commit (decision 20): squash would fold a spec's commits into one
  want "squash merge" false "$(jq -r .allow_squash_merge <<< "$cur")" \
    gh repo edit "$REPO" --enable-squash-merge=false
  want "wiki" false "$(jq -r .has_wiki <<< "$cur")" gh repo edit "$REPO" --enable-wiki=false
  want "projects" false "$(jq -r .has_projects <<< "$cur")" gh repo edit "$REPO" --enable-projects=false
}

actions_flags() {
  local perms wf
  perms=$(api "repos/$REPO/actions/permissions")
  wf=$(api "repos/$REPO/actions/permissions/workflow")
  echo "actions"
  # every `uses:` in this repository is a full SHA; make GitHub refuse anything else
  want "SHA pinning required" true "$(jq -r .sha_pinning_required <<< "$perms")" \
    api -X PUT "repos/$REPO/actions/permissions" -F enabled=true -f allowed_actions=all \
    -F sha_pinning_required=true
  want "default token permissions" read "$(jq -r .default_workflow_permissions <<< "$wf")" \
    api -X PUT "repos/$REPO/actions/permissions/workflow" -f default_workflow_permissions=read
  want "token may open PRs" false "$(jq -r .can_approve_pull_request_reviews <<< "$wf")" \
    api -X PUT "repos/$REPO/actions/permissions/workflow" -F can_approve_pull_request_reviews=false
}

security_flags() {
  local alerts fixes
  alerts=$(api "repos/$REPO/vulnerability-alerts" > /dev/null 2>&1 && echo true || echo false)
  fixes=$(api "repos/$REPO/automated-security-fixes" --jq .enabled 2> /dev/null || echo false)
  echo "security"
  want "dependabot alerts" true "$alerts" api -X PUT "repos/$REPO/vulnerability-alerts"
  want "dependabot security PRs" true "$fixes" api -X PUT "repos/$REPO/automated-security-fixes"
}

environment() { # one environment, deployable from main only
  local name="$1" exists policy
  exists=$(api "repos/$REPO/environments/$name" --jq .name 2> /dev/null) || exists=""
  want "environment $name" "$name" "$exists" \
    api -X PUT "repos/$REPO/environments/$name" \
    -F "deployment_branch_policy[protected_branches]=false" \
    -F "deployment_branch_policy[custom_branch_policies]=true"
  policy=$(api "repos/$REPO/environments/$name/deployment-branch-policies" \
    --jq '.branch_policies[].name' 2> /dev/null | grep -x main) || policy=""
  want "  branch policy $name" main "$policy" \
    api -X POST "repos/$REPO/environments/$name/deployment-branch-policies" -f name=main -f type=branch
}

ruleset() { # main: no deletion, no force push, PR with the aggregator green
  local body id
  body=$(jq -n --arg check "$REQUIRED_CHECK" '{name: "main", target: "branch", enforcement: "active",
    conditions: {ref_name: {include: ["~DEFAULT_BRANCH"], exclude: []}},
    rules: [{type: "deletion"}, {type: "non_fast_forward"},
      {type: "pull_request", parameters: {required_approving_review_count: 0,
        dismiss_stale_reviews_on_push: false, require_code_owner_review: false,
        require_last_push_approval: false, required_review_thread_resolution: false}},
      {type: "required_status_checks", parameters: {strict_required_status_checks_policy: false,
        required_status_checks: [{context: $check}]}}]}')
  echo "rules"
  if ! id=$(api "repos/$REPO/rulesets" --jq '.[] | select(.name == "main") | .id' 2> /dev/null); then
    echo "  note  rulesets unavailable on this plan for a private repository; the PR rule stays convention"
    return 0
  fi
  if [ -n "$id" ]; then printf '  ok    %-34s ruleset %s\n' "main protected" "$id"; return; fi
  DIFFS=$((DIFFS + 1))
  printf '  diff  %-34s <unset> -> PR + %s, no force push, no deletion\n' "main protected" "$REQUIRED_CHECK"
  [ "$APPLY" = 0 ] && return 0
  if ! api -X POST "repos/$REPO/rulesets" --input - <<< "$body" > /dev/null 2> ruleset.err; then
    echo "  note  rulesets refused: $(tr -d '\n' < ruleset.err | cut -c1-160)"
    echo "        (private repositories need a paid plan; until then the PR rule is convention)"
  fi
  rm -f ruleset.err
}

FEDERATION_VARS="ANTHROPIC_FEDERATION_RULE_ID ANTHROPIC_ORGANIZATION_ID ANTHROPIC_SERVICE_ACCOUNT_ID ANTHROPIC_WORKSPACE_ID"

# No API key: each environment exchanges its GitHub OIDC token for a short-lived Anthropic token
# (scripts/anthropic-federation.sh). GitHub's immutable subject carries numeric IDs, so the rule's
# subject is read from the repository rather than spelled from its name.
federation_hint() {
  local prefix env var
  prefix=$(api "repos/$REPO/actions/oidc/customization/sub" --jq '.sub_claim_prefix // empty' 2> /dev/null) || prefix=""
  [ -n "$prefix" ] || prefix="repo:$REPO"
  echo "federation (owner, by hand: one Claude Console rule per environment, ids as environment variables)"
  for env in $ENVIRONMENTS; do
    echo "  rule  subject $prefix:environment:$env (exact), claim ref = refs/heads/main"
    for var in $FEDERATION_VARS; do
      echo "  gh variable set $var --repo $REPO --env $env --body <id>"
    done
  done
  echo "secrets (owner, by hand; none at repository level)"
  echo "  gh secret set KNOWLEDGE_REFRESH_TOKEN --repo $REPO --env knowledge-refresh   # optional PAT: CI on learn/* PRs"
}

echo "$REPO ($MODE)"
repo_flags
actions_flags
security_flags
echo "environments"
for env in $ENVIRONMENTS; do environment "$env"; done
ruleset
federation_hint
if [ "$APPLY" = 1 ]; then echo "applied $DIFFS change(s)"; else echo "$DIFFS change(s) pending; apply with: $0 --apply"; fi
