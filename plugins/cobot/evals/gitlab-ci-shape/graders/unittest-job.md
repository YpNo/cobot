---
type: regex
target:
  source: file
  path: .gitlab-ci.yml
pattern: "python3 -m unittest discover -s tests"
---
