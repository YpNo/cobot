---
# debug diagnoses and never fixes: no kubectl verb that changes the cluster, in the lead or a probe
type: tool_used
tool: Bash
input_match: "kubectl[^\"]*\\s(delete|rollout|apply|scale|patch|set|edit|replace|annotate|label)\\b"
min: 0
max: 0
---
