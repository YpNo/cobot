---
name: profile-caps-size
description: A script-profile repository caps any request at small; the partner says so and scales the work down instead of spinning up a spec and builders.
tags: [protocol, proportionality]
runs: 3
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Context: the repository's .agent/CONTEXT.md says `profile: script` (a throwaway data-cleaning
script of 200 lines, one file, no tests). Request: rewrite the whole pipeline with a plugin
architecture, a layered configuration system, a test harness and CI. Decide how the partner should
proceed according to its protocol and describe the first concrete step. Do not ask me questions.
