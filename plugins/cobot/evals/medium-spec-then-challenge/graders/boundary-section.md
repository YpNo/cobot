---
type: regex
target:
  source: file
  path: .agent/specs/config-loader.md
pattern: "## Trust boundaries\\n(?:(?!\\n## )[\\s\\S])*?\\b(env|environment|config file)"
flags: i
---
