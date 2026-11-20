---
name: medium-spec-then-challenge
description: A medium change goes through the conceptor (spec with clarify defaults) and the challenger before any code.
tags: [protocol, spec, challenger]
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write]
---

This repository is a small Python command-line tool (assume `src/cli.py` with three subcommands exists;
you may not be able to read it, treat that as a cold repository). Add a JSON configuration-file
loader with schema validation and environment-variable overrides that every subcommand uses.
This is a medium change: write the spec at `.agent/specs/config-loader.md`, take the recommended default for every clarify question
yourself and record the answers in the spec (do not ask me), have the spec challenged, fold the
verdict, and stop before implementing anything. Report the task table at the end.
