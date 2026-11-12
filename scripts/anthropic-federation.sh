#!/usr/bin/env bash
# Workload identity federation for a GitHub Actions step that runs Claude Code: no stored API key.
# Source it on its own line (the step's `bash -e` then stops on a failure), then run claude in
# the same step:
#
#   . scripts/anthropic-federation.sh
#   claude -p ...
#
# It checks the four federation identifiers (environment variables of the job's GitHub
# environment), writes a GitHub OIDC token to a file Claude Code reads
# (ANTHROPIC_IDENTITY_TOKEN_FILE), and keeps that file fresh in the background: a GitHub token
# lives 300 s and Anthropic grants at most twice what is left of it, while an eval run lasts up
# to 45 minutes. The job needs `permissions: id-token: write`. The token is never printed.
# The federation rule must match `repo:<owner>@<id>/<repo>@<id>:environment:<name>` (GitHub's
# immutable subject) plus `ref: refs/heads/main`.

readonly FEDERATION_AUDIENCE="https://api.anthropic.com"
readonly FEDERATION_REFRESH_S=60 # a fresh token always has >= 240 s left

federation_fail() {
  echo "::error::anthropic-federation: $1"
  return 1
}

federation_fetch() { # $1 = token file; atomic, so claude never reads half a token
  local token
  token=$(curl -sSf --max-time 20 -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
    "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=$FEDERATION_AUDIENCE" | jq -r '.value // empty') || return 1
  [ -n "$token" ] || return 1
  echo "::add-mask::$token"
  printf '%s' "$token" > "$1.tmp" && mv -f "$1.tmp" "$1"
}

federation_start() {
  local name
  for name in ANTHROPIC_FEDERATION_RULE_ID ANTHROPIC_ORGANIZATION_ID ANTHROPIC_SERVICE_ACCOUNT_ID \
    ANTHROPIC_WORKSPACE_ID; do
    [ -n "${!name:-}" ] || federation_fail "$name is empty: set it on this job's environment" || return 1
  done
  [ -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}" ] \
    || federation_fail "no OIDC endpoint: the job needs permissions: id-token: write" || return 1
  # a key or an auth token outranks federation and would silently win
  unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
  export ANTHROPIC_IDENTITY_TOKEN_FILE="${RUNNER_TEMP:?}/anthropic-oidc-token"
  federation_fetch "$ANTHROPIC_IDENTITY_TOKEN_FILE" || federation_fail "GitHub refused an OIDC token" || return 1
  (
    # sleep must not hold the step's output open, or the step waits for it after claude ends
    while sleep "$FEDERATION_REFRESH_S" > /dev/null 2>&1; do
      federation_fetch "$ANTHROPIC_IDENTITY_TOKEN_FILE" || echo "::warning::anthropic-federation: refresh failed, retrying"
    done
  ) &
  FEDERATION_REFRESH_PID=$!
  trap 'kill "$FEDERATION_REFRESH_PID" 2> /dev/null' EXIT
}

federation_start
