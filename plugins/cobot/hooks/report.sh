#!/bin/sh
# cobot builder report check (PostToolUse on Agent). Unlike the gate, a failure here must never
# strand a session: every failure path exits 0 and allows.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
if ! command -v python3 >/dev/null 2>&1; then
  echo "cobot report: python3 not found; allowing" >&2
  exit 0
fi
python3 -I "$root/bin/cobot-rules" report || echo "cobot report: check exited $?; allowing" >&2
exit 0
