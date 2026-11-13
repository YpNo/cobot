---
name: gitlab-ci-shape
description: >-
  On a GitLab-hosted library the ship skill writes a .gitlab-ci.yml in the trigger-matrix shape
  from the verified commands: one workflow block, rules instead of only, a digest-pinned image
  from the expert's dated row, interruptible jobs, the real test command.
tags: [ship, expert-gitlab-ci]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill]
---

This is my own small Python library; it has no remote yet and its root commit is already
trusted. Design and write its delivery pipeline with `/cobot:ship`. The project is hosted on GitLab (CONTEXT.md says
so) and runs its tests with the standard library's unittest. Write the pipeline file, run the
commands it runs, and tell me in a few lines what the pipeline does and where every pinned
value came from. Do not ask me anything.
