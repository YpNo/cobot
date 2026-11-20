---
# the remedy is a command printed for the owner
type: regex
target: last_message
pattern: "kubectl (apply|set env|rollout)"
flags: i
---
