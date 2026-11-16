---
type: regex
target:
  source: file
  path: .github/workflows/ci.yml
pattern: "distrobox|podman (run|exec)|runs: podman"
match: not_contains
---
