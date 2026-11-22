---
type: regex
target: trace
pattern: "secrets\\.yaml[\\s\\S]{0,200}(tracked|committed|gitignore|git ls-files)"
flags: i
---
