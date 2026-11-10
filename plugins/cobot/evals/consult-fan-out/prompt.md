---
name: consult-fan-out
description: >-
  /cobot:consult with no domain detects the GitHub Actions workflow and the Dockerfile and
  launches one consultant per domain in a single message, each auditing read-only.
tags: [consult, parallel]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Run the cobot's read-only expert audit on this repository with `/cobot:consult` and no domain,
so it picks the domains itself. Do not change any file and do not ask me anything; report the
findings as they came, grouped by domain.
