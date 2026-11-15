#!/bin/sh
# cobot SessionStart hook for the Antigravity CLI (agy), run from the plugin folder: the protocol,
# the agy section and the memory brief as one injectSteps system message. Never blocks a session.
# CLAUDE_PLUGIN_ROOT may leak in from a Claude Code process: every tool resolves its own folder.
unset CLAUDE_PLUGIN_ROOT
root=$(cd "$(dirname "$0")/.." && pwd) || exit 0
if ! command -v python3 >/dev/null 2>&1; then
  echo "cobot session: python3 not found; protocol not injected" >&2
  exit 0
fi
python3 -I "$root/bin/cobot-session" start --runtime agy || echo "cobot session: payload failed" >&2
exit 0
