# expert-gha — learned lines

Promoted by `partner-memory learn --promote`; move a line to its topical file at review.
Format: `- [status YYYY-MM-DD · src: <url or exp: command>] claim`.

- [verified 2026-11-07 · src: https://docs.github.com/en/actions/concepts/security/secrets] GitHub states automatic redaction 'is not guaranteed' because a secret can be transformed in many ways, and the runner can only redact secrets used within the current job.
- [verified 2026-11-07 · src: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference] In the Dependabot options reference only `groups.dependency-type` is restricted by ecosystem (bundler, composer, mix, maven, npm, pip); `patterns`, `exclude-patterns`, `update-types` and `applies-to` (version-updates default, or security-updates) carry no ecosystem restriction. `dependency-type` is therefore unusable for github-actions groups.
