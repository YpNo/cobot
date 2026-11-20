#!/bin/sh
# cobot session grants (spec session-grants): `posttool` on PostToolUse Bash records a grant the
# owner approved at the prompt; `sessionend` removes the session's grants. A failure records
# nothing, so it never widens anything: every path exits 0.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
command -v python3 >/dev/null 2>&1 || exit 0
case "${1:-}" in
  posttool|sessionend) python3 -I "$root/bin/cobot-rules" "$1" || echo "cobot grant: $1 exited $?" >&2 ;;
esac
exit 0
