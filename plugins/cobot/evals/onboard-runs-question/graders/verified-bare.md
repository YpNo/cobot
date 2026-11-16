---
type: regex
target:
  source: file
  path: .agent/CONTEXT.md
pattern: "`(podman|docker) (run|exec)[^`]*unittest|`distrobox enter[^`]*unittest"
match: not_contains
---
