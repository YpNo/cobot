---
type: regex
target:
  source: file
  path: .github/workflows/ci.yml
pattern: "uses: actions/checkout@[0-9a-f]{40} # v[0-9]"
---
