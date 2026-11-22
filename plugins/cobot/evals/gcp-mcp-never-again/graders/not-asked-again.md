---
# under dontAsk a re-ask shows as a stated question: "I would have asked whether to use MCP"
type: regex
target: last_message
pattern: "would (have )?ask(ed)?[\\s\\S]{0,200}(MCP|gcp-mcp)|(MCP|gcp-mcp)[\\s\\S]{0,120}would (have )?ask"
flags: i
match: not_contains
---
