---
name: ui-contrast
description: >-
  The read-only UI audit computes contrast ratios instead of estimating them and names the WCAG
  criterion, the ratio and the file for each failing pair.
tags: [expert-ui, consult, accessibility]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---

Audit the user interface of this small site for accessibility with the cobot's read-only UI
consult (`/cobot:consult-ui`). I want the computed contrast ratio of every text and link colour
against its background, with the WCAG criterion each one fails or passes, and the file and line.
Do not change any file and do not ask me anything; report the consult's findings as they came.
