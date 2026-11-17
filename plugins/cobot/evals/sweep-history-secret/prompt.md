---
name: sweep-history-secret
description: >-
  /cobot:security-sweep finds a .env file that was committed and later deleted, with neutral
  commit messages: only the history step can see it, and it is CRITICAL.
tags: [security-sweep, history]
runs: 1
max_turns: 25
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

/cobot:security-sweep
