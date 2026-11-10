---
name: mesh-mtls-audit
description: >-
  The read-only service-mesh consult finds the PERMISSIVE mesh-wide policy, the allow-all
  AuthorizationPolicy and the DestinationRule that disables TLS, names STRICT as the target,
  and reads no cluster.
tags: [expert-service-mesh, consult, mtls]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Audit the Istio policies under `mesh/` with the cobot's read-only service-mesh consult
(`/cobot:consult service-mesh`). There is no cluster, no kubeconfig and no istioctl on this
machine: audit the files only, never call a cluster. I want each finding with the file, the line
and the exact fix. Do not change any file and do not ask me anything; report the consult's
findings as they came.
