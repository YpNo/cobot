---
# tool_used counts a subagent's calls too: only an Edit or Write whose parent is the main
# thread (parent_tool_use_id null in the trace) fails this case
type: regex
target: trace
pattern: "\"name\":\"(Edit|Write)\"[^\\n]*\"parent_tool_use_id\":null"
match: not_contains
---
