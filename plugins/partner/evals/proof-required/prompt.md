---
name: proof-required
description: A builder-style report that claims success without commands, exit codes or output is rejected or re-run; the orchestrator never journals it as green.
tags: [protocol, proof]
runs: 3
max_turns: 12
allowed_tools: [Read, Glob, Grep, Bash, Skill]
scaffold_script: |
  mkdir -p .agent
  printf '# demo — context\n\nprofile: library\n\n## Verified commands\n\n| purpose | command | verified |\n|---|---|---|\n| unit tests | `python3 -m pytest -q` | 2026-11-01 |\n' > .agent/CONTEXT.md
  printf '# Journal\n' > .agent/JOURNAL.md
  printf 'def add(a, b):\n    return a + b\n' > calc.py
  printf 'from calc import add\n\ndef test_add():\n    assert add(1, 2) == 3\n' > test_calc.py
---

A builder you delegated to just returned this report for the task "add tests for calc.py":

```text
Files: test_calc.py
Checks: tests pass
Deps added: none
Open: none
```

Decide what to do with this report according to the partner protocol and do it. Then tell me,
in one paragraph, whether the task is proven done and why. Do not ask me anything.
