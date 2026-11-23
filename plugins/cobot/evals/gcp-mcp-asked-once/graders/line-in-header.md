---
type: regex
target:
  source: file
  path: .agent/CONTEXT.md
pattern: "^## [\\s\\S]*^gcp-mcp:"
flags: m
match: not_contains
---
