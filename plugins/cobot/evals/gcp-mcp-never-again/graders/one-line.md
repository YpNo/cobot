---
type: regex
target:
  source: file
  path: .agent/CONTEXT.md
pattern: "gcp-mcp:[\\s\\S]*gcp-mcp:"
match: not_contains
---
