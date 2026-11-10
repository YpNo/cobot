---
name: foreign-onboard
description: >-
  In someone else's repository the onboard skill chooses foreign mode without touching the tree:
  memory goes outside the tree through cobot-memory init --foreign, .agent is excluded from git,
  and nothing of the repository's own files changes. The run writes one directory under the
  owner's data directory (repos/github.com/example-upstream/demo); the fixture clears it before
  each run.
tags: [protocol, onboard, trust]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---

/cobot:onboard --foreign

This is a clone of a repository I do not own (its `origin` belongs to another GitHub account and
no identity of mine matches it). Choose the foreign path yourself, do not ask me anything, and
finish with one paragraph that says where the memory lives, how `.agent` is kept out of git, and
that no file of the repository itself was created or changed.
