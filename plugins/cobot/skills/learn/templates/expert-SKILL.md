---
name: {{SKILL}}
description: >-
  {{DESCRIPTION}} Use {{WHEN}}. Learned skeleton ({{DATE}}), reported until promoted.
paths:
{{PATHS}}
user-invocable: false
---

# {{SKILL}}

Skeleton expert for {{TOPIC}}, created on {{DATE}} by the learner through
`cobot-memory learn --promote`. Status: **reported** until it has served twice.

Knowledge lines: `references/learned.md`. Quote the status of every line you rely on; an
`assumed` line may be shown but may not drive a decision, a command or a version. When a line is
older than its threshold (versions 30 days, idiom 90 days) or a question falls outside the lines,
say so and propose `/cobot:learn {{TOPIC}} <question>` instead of guessing.

To become a full expert this skill needs: a `when_to_use` paragraph with the files it applies to,
the non-negotiables of the domain, the verified commands, and one eval case under `evals/`.
