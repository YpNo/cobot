---
name: gcp-mcp-asked-once
description: >-
  In a trusted repository with cobot memory, a google provider and no gcp-mcp line, the first
  /cobot:consult gcp asks the Google Cloud MCP opt-in once in the main thread, before the
  consultant runs, and writes gcp-mcp: no into CONTEXT.md's header (the recommendation without
  gcp-* tools). An eval run cannot ask (AskUserQuestion is denied under dontAsk), so the report
  states the question and the option taken. Nothing is registered.
tags: [expert-gcp, consult, mcp]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent, Edit]
---

/cobot:consult gcp

This is my own lab repository. No Google Cloud project is configured on this machine, so audit
the files only. You cannot ask me anything in this session: where the skill would ask a question,
take its recommended option and apply it, and in your final paragraph state the question you
would have asked about the Google Cloud MCP servers and the option you took.
