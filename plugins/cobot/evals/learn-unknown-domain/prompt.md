---
name: learn-unknown-domain
description: A question no lang-* or expert-* skill covers goes to the learner, which returns a knowledge delta whose lines carry a status and a source, verified from read-list commands, with nothing written.
tags: [protocol, learn]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash]
---

No expert in this cobot knows the `file` command-line utility. Learn, without network access
and without writing anything, which version of `file` is installed here and which option prints
the MIME type only, through the cobot's learning path (the learner agent, not your own
memory). Return the knowledge delta as the learner produced it, with every entry's status and
source, and stop there: do not apply it, do not create or edit any file, and do not ask me
anything.
