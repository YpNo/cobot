---
name: ship-runs-bare
description: >-
  CONTEXT.md says commands run locally through podman and a distrobox (runs: header) while the
  verified commands are bare; the ship skill writes a GitHub workflow that runs the bare commands,
  so no local prefix (distrobox enter, podman run) reaches CI.
tags: [ship, environment]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill]
---

This is my own small Python library on GitHub; it has no remote yet and its root commit is
already trusted. Design and write its CI workflow with `/cobot:ship`. Write the workflow file,
then tell me in a few lines what it runs. Do not ask me anything.
