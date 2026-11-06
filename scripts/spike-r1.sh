#!/bin/sh
# Release 1 spikes (spec T00). Run from an authenticated shell: sh scripts/spike-r1.sh
# A harmless owner-layer probe rule makes the model call Bash, so the hook (not the model) decides:
#   D  hook deny on a command the model has no reason to refuse (echo partner-deny-probe)
#   E  the same command from a subagent's Bash: does the hook fire for subagents, and what agent_type arrives
#   F  a context: fork skill (consult-gha) resolves agent: partner:consultant
set -eu
repo=$(cd "$(dirname "$0")/.." && pwd)
plugin="$repo/plugins/partner"
scratch=${SPIKE_DIR:-${TMPDIR:-/tmp}/partner-spike-r1-$$}
mkdir -p "$scratch/work/.github/workflows"
cat > "$scratch/work/.github/workflows/ci.yml" <<'YML'
name: ci
on: [push]
jobs:
  t:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "${{ github.event.head_commit.message }}"
YML
printf 'never Bash(echo partner-deny-probe*)\n' > "$scratch/probe.rules"
PARTNER_RULES_OWNER="$scratch/probe.rules"
PARTNER_GATE_LOG="$scratch/gate.log"
export PARTNER_RULES_OWNER PARTNER_GATE_LOG
cd "$scratch/work"
git init -q -b main . && git add -A && git -c user.email=s@x -c user.name=s commit -qm init

echo "=== D: hook deny in the main thread"
claude --plugin-dir "$plugin" --model haiku --max-turns 3 -p \
  "Use the Bash tool to run exactly: echo partner-deny-probe-main . Report the tool result verbatim." || true

echo "=== E: hook deny through a subagent (partner:builder)"
claude --plugin-dir "$plugin" --model haiku --max-turns 4 -p \
  "Spawn the partner:builder subagent with this exact task: 'Use the Bash tool to run exactly: echo partner-deny-probe-sub . Report the tool result verbatim.' Then report what the subagent returned, verbatim." || true

echo "=== F: forked consult skill resolves partner:consultant"
claude --plugin-dir "$plugin" --model haiku --max-turns 6 -p \
  "Invoke the /partner:consult-gha skill on this repository and report its findings. Also state which agent type ran it if you can tell." || true

echo "=== gate log: $PARTNER_GATE_LOG"
cat "$PARTNER_GATE_LOG" 2>/dev/null || echo "no log written: the hook did not fire"
echo "expect: one deny line with agent null (D), one deny line with a non-null agent (E), and allow/ask lines from a consultant agent (F)."
echo "scratch kept at $scratch"
