---
name: actions-pinning
description: >-
  A workflow that uses a floating action tag is corrected the way the GitHub Actions expert
  prescribes: a full commit SHA with the tag in a comment, taken from the expert's pinned table or
  re-resolved when that table is stale, and zizmor named as the check.
tags: [expert-gha, security]
runs: 3
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Edit, Skill]
---

Review `.github/workflows/ci.yml` and fix what is wrong with the way it references actions. Make
the change in the file, then tell me in a few lines what you changed, where the value came from,
and which tool catches this class of mistake in CI. Do not ask me anything.
