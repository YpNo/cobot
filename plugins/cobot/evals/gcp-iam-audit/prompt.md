---
name: gcp-iam-audit
description: >-
  The read-only Google Cloud consult finds the service-account key, the basic role and the
  hand-built service-agent email in a Terraform module, names the provider-computed identity
  as the fix, and changes nothing.
tags: [expert-gcp, consult, iam]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Audit the Terraform module under `modules/gke` for IAM least privilege and universe portability
with the cobot's read-only Google Cloud consult (`/cobot:consult gcp`). There is no Google Cloud
project configured on this machine, so audit the files only. I want each finding with the file,
the line and the exact fix. Do not change any file and do not ask me anything; report the
consult's findings as they came.
