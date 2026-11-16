---
type: regex
target:
  source: file
  path: .github/workflows/ci.yml
pattern: "python3 -m unittest discover -s tests"
---
