---
type: regex
target:
  source: file
  path: .github/workflows/ci.yml
pattern: "actions/checkout@v4\\s"
match: not_contains
---
