#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold.
set -euo pipefail
mkdir -p .agent
# shellcheck disable=SC2016  # the backticks are Markdown, not command substitution
printf '# demo — context\n\nprofile: library\n\n## Verified commands\n\n| purpose | command | verified |\n|---|---|---|\n| unit tests | `python3 -m pytest -q` | 2026-11-01 |\n' > .agent/CONTEXT.md
printf '# Journal\n' > .agent/JOURNAL.md
printf 'def add(a, b):\n    return a + b\n' > calc.py
printf 'from calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n' > test_calc.py
