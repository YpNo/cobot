#!/bin/sh
# cobot rules gate shim for the Antigravity CLI (agy), run from the plugin folder.
# agy logs a failing hook and runs the call anyway, so every failure path prints a deny, exit 0.
# CLAUDE_PLUGIN_ROOT may leak in from a Claude Code process: every tool resolves its own folder.
unset CLAUDE_PLUGIN_ROOT
DEADLINE_MAX=8 # below the 10 s timeout in hooks.json
deadline=${COBOT_GATE_DEADLINE:-$DEADLINE_MAX}
case $deadline in '' | *[!0-9]*) deadline=$DEADLINE_MAX ;; esac
[ "$deadline" -ge 1 ] && [ "$deadline" -le "$DEADLINE_MAX" ] || deadline=$DEADLINE_MAX

deny() {
  printf '{"decision": "deny", "reason": "cobot gate: %s; blocking the call"}\n' "$1"
  exit 0
}

command -v python3 >/dev/null 2>&1 || deny "python3 not found"
python3 -I -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2>/dev/null || deny "python3 older than 3.12"
root=$(cd "$(dirname "$0")/.." && pwd) || deny "plugin folder not found"
input=$(mktemp) || deny "no temporary file"
output=$(mktemp) || {
  rm -f "$input"
  deny "no temporary file"
}
trap 'rm -f "$input" "$output"' EXIT
# a background job reads /dev/null, so the payload is buffered first
cat >"$input" || deny "stdin unreadable"
python3 -I "$root/bin/cobot-rules" gate --runtime agy <"$input" >"$output" 2>/dev/null &
pid=$!
(
  sleep "$deadline"
  kill "$pid" 2>/dev/null
) >/dev/null 2>&1 &
watcher=$!
wait "$pid"
rc=$?
kill "$watcher" 2>/dev/null
[ "$rc" -eq 0 ] || deny "the gate exited $rc"
first=
IFS= read -r first <"$output"
case $first in
  '{"decision": "'*) printf '%s\n' "$first" ;;
  *) deny "no decision from the gate" ;;
esac
