---
name: ship-ground
description: >-
  Before planning a pipeline, /cobot:ship reads its ground: it flags rust-toolchain.toml's floating
  stable channel and proposes a pin, and it reads the remote, finds it empty, and says so before
  proposing any push or pull request (spec memory-and-ship, F-37 and F-43).
tags: [ship, ground]
runs: 1
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill, Agent]
---

This is my own small Rust library; its root commit is already trusted and the project is hosted
on GitHub (CONTEXT.md says so). Plan its delivery pipeline with `/cobot:ship`. Before you write
anything, tell me in a few lines what you found about the toolchain and about the remote, and
what you would push first. Do not ask me anything.
