#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A Python library on GitHub whose owner runs
# commands through podman and a distrobox locally (runs:), with bare verified commands and a wrap
# stamp on HEAD.
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git config commit.gpgsign false
mkdir -p demo tests .agent
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
cat > .agent/CONTEXT.md <<'CTX'
# demo — context

profile: library
forge: github
goal: a small Python library that adds numbers
owner: eval · private · MIT
governance: none
runs: podman · builds: distrobox enter dev --

## Stack

- Python 3.13, standard library only, no package manager yet.

## Environment

- podman (rootless), distrobox box `dev`; commands run inside it locally, bare in CI.

## Verified commands

| purpose | command | result | verified |
|---|---|---|---|
| unit tests | `python3 -m unittest discover -s tests -v` | exit 0 (1 test) | 2026-11-16 |
| syntax check | `python3 -m compileall -q demo tests` | exit 0 | 2026-11-16 |

## Constraints

- No third-party dependency without a decision.
CTX
printf '# Journal\n\nAppend-only, newest at the bottom.\n' > .agent/JOURNAL.md
printf '# Findings\n\n| id | seen | observation | goes to |\n|---|---|---|---|\n' > .agent/FINDINGS.md
git add . && git commit -q -m "feat: add and its test"
sha=$(git rev-parse --short HEAD)
cat >> .agent/JOURNAL.md <<EOF

## 2026-11-16 — wrap
Changed: add() and its test.
Why: first slice.
Proof: python3 -m unittest discover -s tests -v → exit 0 (1 test); python3 -m compileall -q demo tests → exit 0.
Open: none.
Next: the CI workflow.
verified: $sha · python3 -m unittest discover -s tests -v · python3 -m compileall -q demo tests
EOF
git add .agent/JOURNAL.md && git commit -q -m "docs: journal with the wrap stamp"
# Trust the root commit as gitlab-ci-shape does: eval Bash cannot write the config directory.
root=$(git rev-list --max-parents=0 HEAD)
for dir in "$HOME/.claude" "$HOME/../config"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir/cobot" && printf '%s %s\n' "$root" "$(basename "$PWD")" >> "$dir/cobot/trusted"
  fi
done
