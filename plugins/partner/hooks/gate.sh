#!/bin/sh
# agentic-partner rules gate shim.
# Claude Code treats only exit code 2 as blocking, so every failure path ends in exit 2.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
if ! command -v python3 >/dev/null 2>&1; then
  echo "partner gate: python3 not found; blocking the call" >&2
  exit 2
fi
python3 -I "$root/bin/partner-rules" gate
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "partner gate: exited $rc; blocking the call" >&2
  exit 2
fi
