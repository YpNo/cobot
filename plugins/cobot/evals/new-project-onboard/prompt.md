---
name: new-project-onboard
description: >-
  On a new repository (one commit with a README, no remote) the onboard skill asks for nothing it
  was given and guesses nothing: the goal is the owner's words, the profile goes through init
  --profile, the root commit is trusted, the language is left to the first spec, the verified
  table says none yet, nothing is scaffolded, and the next step is /cobot:spec, not a second
  onboard. The run leaves one line in ~/.claude/cobot/trusted naming a root commit unique to the
  run (the fixture's README carries a random token), so no other repository can match it.
tags: [protocol, onboard, new-project]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---

/cobot:onboard a command-line tool that turns a folder of Markdown notes into a static HTML site

This is a new repository of mine: one commit with a README, no remote yet. Do not ask me anything:
the profile is cli, the licence MIT, the forge other (no remote yet), and trust its root commit.
Finish with one paragraph that says what you wrote and what I should do next.
