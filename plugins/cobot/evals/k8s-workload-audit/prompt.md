---
name: k8s-workload-audit
description: >-
  The read-only Kubernetes consult finds the latest tag, the privileged container, the missing
  resources and probes in a Deployment, names the file, and reads no cluster.
tags: [expert-kubernetes, consult, pod-security]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

Audit the manifests under `k8s/` with the cobot's read-only Kubernetes consult
(`/cobot:consult kubernetes`). There is no cluster and no kubeconfig on this machine: audit the
files only, never call a cluster. I want each finding with the file, the line and the exact fix,
for the workload as it would run on GKE Autopilot. Do not change any file and do not ask me
anything; report the consult's findings as they came.
