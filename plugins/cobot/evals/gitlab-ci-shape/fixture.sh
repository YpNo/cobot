#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A Python library on GitLab with committed
# memory, a verified unittest command and a wrap stamp on HEAD.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
mkdir -p demo tests .agent .gitlab/merge_request_templates
cat > demo/__init__.py <<'PY'
"""demo: adds numbers."""


def add(a: int, b: int) -> int:
    return a + b
PY
cat > tests/test_demo.py <<'PY'
import unittest

from demo import add


class AddTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
PY
printf 'Describe the change and how it was tested.\n' > .gitlab/merge_request_templates/default.md
cat > .agent/CONTEXT.md <<'CTX'
# demo — context

profile: library          # spike | script | cli | library | service | infra
forge: gitlab             # github | gitlab | gitea | other — where CI runs; ship reads it

## Goal

A small Python library that adds numbers; hosted on gitlab.com under example-group/demo.

## Stack

Python 3.13, standard library only, no package manager yet.

## Verified commands

| purpose | command | verified |
|---|---|---|
| unit tests | `python3 -m unittest discover -s tests -v` | 2026-11-08 |
| syntax check | `python3 -m compileall -q demo tests` | 2026-11-08 |

## Constraints

- No third-party dependency without a decision.
- Pipeline images pinned by digest.
CTX
printf '# Journal\n\nAppend-only, newest at the bottom.\n' > .agent/JOURNAL.md
printf '# Findings\n\n| id | seen | observation | goes to |\n|---|---|---|---|\n' > .agent/FINDINGS.md
git add . && git commit -q -m "feat: add and its test"
sha=$(git rev-parse --short HEAD)
cat >> .agent/JOURNAL.md <<EOF

## 2026-11-08 — wrap
Changed: add() and its test.
Why: first slice.
Proof: python3 -m unittest discover -s tests -v → exit 0 (1 test); python3 -m compileall -q demo tests → exit 0.
Open: none.
Next: the delivery pipeline.
verified: $sha · python3 -m unittest discover -s tests -v · python3 -m compileall -q demo tests
EOF
git add .agent/JOURNAL.md && git commit -q -m "docs: journal with the wrap stamp"
# Trust the root commit as `cobot-memory init --trust-root` would: eval Bash cannot write it (the
# sandbox mounts every path read-only). A run's config directory sits beside its home and reaches
# hooks as CLAUDE_CONFIG_DIR, while Bash fell back to ~/.claude in CI, so both get the line.
root=$(git rev-list --max-parents=0 HEAD)
for dir in "$HOME/.claude" "$HOME/../config"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir/cobot" && printf '%s %s\n' "$root" "$(basename "$PWD")" >> "$dir/cobot/trusted"
  fi
done
