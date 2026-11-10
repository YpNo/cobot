---
name: api-contract-audit
description: >-
  The read-only api consult finds the token in a query string, the default-only error
  responses, the 3.0 nullable keyword in a 3.1 document, the unbounded array and the missing
  operationId in a hand-written OpenAPI document, and changes nothing.
tags: [expert-api, consult]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Audit the API contract in `api/openapi.yaml` with the cobot's read-only API consult
(`/cobot:consult api`). There is no server to call: audit the file only. I want each finding with
the file, the line and the exact fix. Do not change any file and do not ask me anything; report
the consult's findings as they came.
