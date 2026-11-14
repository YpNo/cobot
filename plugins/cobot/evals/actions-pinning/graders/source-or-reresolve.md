---
# the value must come from the expert's table or from upstream: gh api or git ls-remote on the
# action's repository (run 43580607780: every run re-resolved with git ls-remote)
type: regex
target: last_message
pattern: "references/actions\\.md|gh api repos/actions/checkout|git ls-remote[^\\n]{0,40}github\\.com/actions/checkout"
---
