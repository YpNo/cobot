---
name: sweep-every-pack
description: >-
  /cobot:security-sweep on an infra repository with one bootstrap script loads the shell pack
  beside the Terraform pack and reports the script's piped installer, changing nothing.
tags: [security-sweep, packs]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

/cobot:security-sweep
