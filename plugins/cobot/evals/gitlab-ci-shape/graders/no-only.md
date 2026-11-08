---
type: regex
target:
  source: file
  path: .gitlab-ci.yml
pattern: "^\\s*only:"
flags: m
match: not_contains
---
