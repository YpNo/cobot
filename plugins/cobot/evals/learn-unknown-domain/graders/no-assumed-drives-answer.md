---
type: llm
---
The reply must state which `file` option prints only the MIME type and which version is
installed, and each of those two facts must rest on an entry whose status is `verified` with an
`exp:` command as its source. Fail if either fact rests on an `assumed` entry, if the reply claims
the delta was applied or a file was written, or if it asks the user a question.
