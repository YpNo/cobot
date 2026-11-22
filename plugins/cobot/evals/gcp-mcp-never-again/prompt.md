---
name: gcp-mcp-never-again
description: >-
  The same repository as gcp-mcp-asked-once with gcp-mcp: no already in CONTEXT.md's header:
  /cobot:consult gcp asks nothing about the Google Cloud MCP servers, leaves CONTEXT.md as it
  is, and audits the files with the consultant.
tags: [expert-gcp, consult, mcp]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent, Edit]
---

/cobot:consult gcp

This is my own lab repository. No Google Cloud project is configured on this machine, so audit
the files only. You cannot ask me anything in this session: where the skill would ask a question,
take its recommended option and apply it, and say so in your final paragraph.
