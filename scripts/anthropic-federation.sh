#!/usr/bin/env bash
# Workload identity federation for a GitHub Actions step that runs Claude Code: no stored API key.
# Source it on its own line (the step's `bash -e` then stops on a failure), then run claude in
# the same step:
#
#   . scripts/anthropic-federation.sh
#   claude -p ...
#
# It checks the four federation identifiers (environment variables of the job's GitHub
# environment) and serves ANTHROPIC_IDENTITY_TOKEN_FILE as a named pipe: every read gets a GitHub
# OIDC token minted for that read. Anthropic accepts a token's `jti` once per issuer, and Claude
# Code re-reads the file for every exchange, while an eval run starts a session every few
# seconds for up to 45 minutes; a plain file refreshed on a timer made the sessions in one
# window share a token and fail `jti_reused` (run 43316107022). The job needs
# `permissions: id-token: write`. The token is never printed.
# The federation rule must match `repo:<owner>@<id>/<repo>@<id>:environment:<name>` (GitHub's
# immutable subject) plus `ref: refs/heads/main`.

readonly FEDERATION_AUDIENCE="https://api.anthropic.com"
readonly FEDERATION_ATTEMPTS=3
# after closing, let the reader see end of file before the pipe reopens; reopening at once
# would hand that same reader the next token too
readonly FEDERATION_READER_GAP_S=0.5

federation_fail() {
  echo "::error::anthropic-federation: $1"
  return 1
}

federation_token() { # prints one freshly minted GitHub OIDC token, or fails
  local token
  token=$(curl -sSf --max-time 20 -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
    "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=$FEDERATION_AUDIENCE" | jq -r '.value // empty') || return 1
  [ -n "$token" ] && printf '%s' "$token"
}

federation_serve() { # $1 = the pipe; one fresh token per reader, until killed
  local token attempt
  set +e # a failed fetch or a reader that left must not end the server
  trap '' PIPE
  while :; do
    exec 3> "$1" # blocks until a reader opens the pipe, so the token is minted on demand
    token=""
    for attempt in $(seq "$FEDERATION_ATTEMPTS"); do
      token=$(federation_token) && break
      [ "$attempt" -lt "$FEDERATION_ATTEMPTS" ] && sleep "$attempt" > /dev/null 2>&1
    done
    if [ -n "$token" ]; then
      echo "::add-mask::$token"
      printf '%s' "$token" >&3
    else
      echo "::warning::anthropic-federation: GitHub refused an OIDC token $FEDERATION_ATTEMPTS times"
    fi
    exec 3>&-
    sleep "$FEDERATION_READER_GAP_S" > /dev/null 2>&1
  done
}

federation_start() {
  local name
  for name in ANTHROPIC_FEDERATION_RULE_ID ANTHROPIC_ORGANIZATION_ID ANTHROPIC_SERVICE_ACCOUNT_ID \
    ANTHROPIC_WORKSPACE_ID; do
    [ -n "${!name:-}" ] || federation_fail "$name is empty: set it on this job's environment" || return 1
  done
  [ -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}" ] \
    || federation_fail "no OIDC endpoint: the job needs permissions: id-token: write" || return 1
  # fail before claude starts; this token is discarded unexchanged, so its jti stays unused
  federation_token > /dev/null || federation_fail "GitHub refused an OIDC token" || return 1
  # a key or an auth token outranks federation and would silently win
  unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
  export ANTHROPIC_IDENTITY_TOKEN_FILE="${RUNNER_TEMP:?}/anthropic-oidc-token"
  rm -f "$ANTHROPIC_IDENTITY_TOKEN_FILE"
  mkfifo -m 600 "$ANTHROPIC_IDENTITY_TOKEN_FILE" || federation_fail "cannot create the token pipe" || return 1
  federation_serve "$ANTHROPIC_IDENTITY_TOKEN_FILE" &
  FEDERATION_SERVER_PID=$!
  trap 'kill "$FEDERATION_SERVER_PID" 2> /dev/null' EXIT
}

federation_start
