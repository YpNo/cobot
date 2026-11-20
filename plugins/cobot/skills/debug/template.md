# Debug — <title>

status: open | resolved | unresolved · date: <YYYY-MM-DD> · owner: <who> · rounds: <n>

## Symptom

<what was seen, by whom, the first time>

## Target

<context, project, cluster, branch or path; production confirmed by the owner: yes | no | n/a>

## Timeline

- <time> — <event: deploy, bump, config change, first error>

## Reproduction

- `<command>` → exit <n>

  ```text
  <excerpt: at most 20 lines and 2000 characters, secrets replaced by <redacted>>
  ```

Or: waived — <why>.

## Hypotheses

| # | hypothesis | skill | verdict | evidence |
|---|---|---|---|---|
| 1 | <one sentence> | <expert-*> | confirmed / refuted / inconclusive | `<command>` → exit <n> |

## Root cause

<the cause and the evidence that proves it, or what is known, ruled out and still to collect>

## Remedy

Printed for the owner, never run here:

- `<command>` · inverse: `<command>`

Code or config: <build path (tiny or small) | /cobot:spec (medium or larger) | none>.

## Follow-ups

- <finding, eval, knowledge gap, or none>
