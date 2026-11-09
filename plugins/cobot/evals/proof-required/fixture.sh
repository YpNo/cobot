#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. The verified command uses the standard
# library's unittest, so a rerun works in the eval sandbox, which has no pytest.
set -euo pipefail
mkdir -p .agent
# shellcheck disable=SC2016  # the backticks are Markdown, not command substitution
printf '# demo — context\n\nprofile: library\n\n## Verified commands\n\n| purpose | command | result | verified |\n|---|---|---|---|\n| unit tests | `python3 -m unittest -v` | exit 0 | 2026-11-01 |\n' > .agent/CONTEXT.md
printf '# Journal\n' > .agent/JOURNAL.md
printf 'def add(a, b):\n    return a + b\n' > calc.py
printf 'import unittest\n\nfrom calc import add\n\n\nclass AddTest(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n' > test_calc.py
