#!/bin/sh
# Coexistence spikes (docs/02-design.md section 17, item 6). Run from an authenticated shell:
#   sh scripts/spikes/spike-coexistence.sh
# Builds a scratch repository with a local remote (non-bare, updateInstead: safe.bareRepository may be explicit), then starts three short, cheap
# (haiku) non-interactive Claude sessions with the plugin loaded through --plugin-dir:
#   A  do cobot:* agents appear beside the legacy set?
#   B  does the gate's "ask" prevail over an explicit allow rule for git push?
#   C  is a force push denied even with that allow rule?
# The gate log shows the exact command the gate saw (plain or rtk-rewritten).
set -eu
repo=$(cd "$(dirname "$0")/.." && pwd)
plugin="$repo/plugins/cobot"
scratch=${SPIKE_DIR:-${TMPDIR:-/tmp}/cobot-spike-$$}
mkdir -p "$scratch"
cd "$scratch"
git init -q -b main remote.git
git -C remote.git config receive.denyCurrentBranch updateInstead
git init -q work
cd work
git config user.email spike@example.invalid
git config user.name spike
echo a > a && git add a && git commit -qm init && git branch -M main
git remote add origin "$scratch/remote.git" && git push -q origin main
echo b >> a && git commit -qam second
COBOT_GATE_LOG="$scratch/gate.log"
export COBOT_GATE_LOG
before=$(git -C ../remote.git rev-parse main)

echo "=== A: agent listing"
claude --plugin-dir "$plugin" --model haiku --max-turns 2 -p \
  "Reply only with the names of the subagent types available to you whose name starts with 'cobot:' or equals 'challenger'. One per line, nothing else." \
  || { echo "A failed: is the CLI logged in? run: claude login"; exit 1; }

echo "=== B: git push with an explicit allow rule (expect the gate to ask, push refused)"
claude --plugin-dir "$plugin" --model haiku --max-turns 3 --allowedTools "Bash(git push:*)" -p \
  "Use the Bash tool to run exactly: git push origin main . Then report the tool result verbatim, including any error or permission message." || true
after_b=$(git -C ../remote.git rev-parse main)
[ "$before" = "$after_b" ] && echo "B: remote unchanged (gate prevailed)" || echo "B: REMOTE CHANGED (allow rule won over the gate)"

echo "=== C: force push with the same allow rule (expect deny)"
claude --plugin-dir "$plugin" --model haiku --max-turns 3 --allowedTools "Bash(git push:*)" -p \
  "Use the Bash tool to run exactly: git push --force origin main . Then report the tool result verbatim." || true
after_c=$(git -C ../remote.git rev-parse main)
[ "$before" = "$after_c" ] && echo "C: remote unchanged (deny held)" || echo "C: REMOTE CHANGED (deny failed)"

echo "=== gate log: $COBOT_GATE_LOG"
cat "$COBOT_GATE_LOG" 2>/dev/null || echo "no log written: the hook did not fire"
echo "scratch kept at $scratch"
