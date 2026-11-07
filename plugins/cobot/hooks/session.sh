#!/bin/sh
# cobot SessionStart hook: injects the protocol and the memory brief. Never blocks a session.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
if ! command -v python3 >/dev/null 2>&1; then
  echo "cobot session: python3 not found; protocol not injected" >&2
  exit 0
fi
python3 -I "$root/bin/cobot-session" start || echo "cobot session: payload failed" >&2
exit 0
