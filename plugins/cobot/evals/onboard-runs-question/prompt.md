---
name: onboard-runs-question
description: >-
  In an existing repository of the owner's (root commit trusted, no memory yet) with a
  Containerfile, onboarding runs cobot-env detect and asks where things run in one question call
  before it runs any command, writes the runs: header, and records the verified commands bare.
  The machine must offer two engines: GitHub's ubuntu runners have docker and podman on PATH.
tags: [protocol, onboard, environment]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill, AskUserQuestion]
---

/cobot:onboard

This is my own small Python library; it has no remote yet and its root commit is already
trusted. The profile is library. If a question gets no answer, take its recommended option.
Finish with one paragraph that says where commands run here and which commands you verified.
