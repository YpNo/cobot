---
name: onboard-runs-question
description: >-
  In an existing repository of the owner's (root commit trusted, no memory yet) with a
  Containerfile, onboarding runs cobot-env detect before it runs any command, writes the runs:
  header, and records the verified commands bare. An eval run cannot ask (AskUserQuestion is
  denied under dontAsk), so the report states the question onboarding would ask and the
  recommended option it took; the question-call graders wait in evals-blocked/.
tags: [protocol, onboard, environment]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---

/cobot:onboard

This is my own small Python library; it has no remote yet and its root commit is already
trusted. The profile is library. You cannot ask me anything in this session: where the skill
would ask a question, take its recommended option, and in your final paragraph state the
question you would have asked about where commands run and the option you took. Finish with
that paragraph and the commands you verified.
