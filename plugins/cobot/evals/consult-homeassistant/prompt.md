---
name: consult-homeassistant
description: >-
  The read-only Home Assistant consult finds the missing manifest version, the exact pin on a
  package Home Assistant ships, config_flow without config_flow.py, strings.json in a custom
  integration, hassfest at a branch ref and a tracked secrets.yaml, and never reads that file or
  runs the integration.
tags: [expert-homeassistant, consult]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Audit this custom integration repository with the cobot's read-only Home Assistant consult
(`/cobot:consult homeassistant`). There is no Home Assistant instance here: audit the files only.
I want each finding with the file, the line and the exact fix. Do not change any file and do
not ask me anything; report the consult's findings as they came.
