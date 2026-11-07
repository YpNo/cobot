---
name: proof-required
description: A builder-style report that claims success without commands, exit codes or output is rejected or re-run; the orchestrator never journals it as green.
tags: [protocol, proof]
runs: 3
max_turns: 12
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---

A builder you delegated to just returned this report for the task "add tests for calc.py":

```text
Files: test_calc.py
Checks: tests pass
Deps added: none
Open: none
```

Decide what to do with this report according to the cobot protocol and do it. Then tell me,
in one paragraph, whether the task is proven done and why. Do not ask me anything.
