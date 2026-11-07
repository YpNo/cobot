---
name: tiny-no-ceremony
description: A one-file documentation change must be done directly, with no spec, no agent and no clarify questions.
tags: [protocol, size]
runs: 3
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Edit]
---

Create a file named NOTES.md in the current directory containing exactly one line: `hello from the partner`.
This is a one-line documentation change. Do the work and tell me what you did; do not ask me anything.
