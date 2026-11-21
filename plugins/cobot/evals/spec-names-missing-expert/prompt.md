---
name: spec-names-missing-expert
description: >-
  A medium change in a domain no expert covers (Modbus TCP) goes through the conceptor, whose
  spec says in its Experts line that no expert covers Modbus and proposes /cobot:learn instead
  of writing protocol facts from memory (F-39).
tags: [protocol, spec, learn]
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write]
---

/cobot:spec poll the inverter every 10 seconds over Modbus TCP and keep the last hour of power
readings, with retries and a timeout on each register read.

Write the spec at `.agent/specs/inverter-poll.md`, take the recommended default for every clarify
question yourself and record the answers in the spec (do not ask me), have the spec challenged,
fold the verdict, and stop before implementing anything. Report the task table at the end.
