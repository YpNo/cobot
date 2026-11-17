---
name: sweep-fan-out
description: >-
  /cobot:security-sweep on a tree above the small-tree threshold (over 200 Terraform files and one
  shell script) fans out one auditor per pack plus the repo-wide unit, then has a fresh auditor
  check the world-readable bucket it finds, changing nothing.
tags: [security-sweep, fan-out]
runs: 1
max_turns: 40
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

/cobot:security-sweep
