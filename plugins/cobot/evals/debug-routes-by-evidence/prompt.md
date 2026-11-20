---
name: debug-routes-by-evidence
description: >-
  An unknown cause goes to the debug path: the lead reads a CrashLoopBackOff from the captured
  evidence, sends a read-only investigator with the Kubernetes expert, names the cause and
  prints the remedy for the owner.
tags: [debug, expert-kubernetes, investigator]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
---

/cobot:debug The `api` Deployment in namespace `shop` has been crash-looping on our `lab`
cluster since this morning's deploy, and I don't know why. Nothing else changed that I know of. There is no cluster
and no kubeconfig on this machine: what I captured from the `lab` context is under `evidence/`,
and the manifests are under `k8s/`. Context `lab` is not production. Find the root cause, with
the evidence that proves it, and tell me what to run to fix it. Do not ask me anything.
