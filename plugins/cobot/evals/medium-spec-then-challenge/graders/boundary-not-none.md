---
type: regex
target:
  source: file
  path: .agent/specs/config-loader.md
pattern: "## Trust boundaries\\s*\\n\\s*none:"
match: not_contains
---
