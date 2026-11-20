# ADR-0008 — The gate may allow, in one case: a granted command under Claude Code

Status: accepted · Date: 2026-11-20 · Amends: ADR-0001 (the gate never widens), ADR-0007
decision 4 (no agy grants) · Relates to: decision 34, spec `.agent/specs/session-grants.md`

## Context

Since 0.1 the gate answered `deny`, `ask` or nothing, and never `allow`, so cobot could only
narrow what Claude Code permits. A lab or a demo on a sandbox project then costs a prompt for
every `gcloud`, `kubectl` or `helm` write, and the owner either answers twenty prompts or adds
a broad settings allow that outlives the lab (owner ideas 2026-11-11, §4). Terraform `apply`
and `destroy` were `never`, so a lab built with Terraform could not be applied from a session
at all.

The probe (spec T01, Claude Code 2.1.326) settled what a grant can rest on: a hook `ask`
prompts in every interactive mode and never runs headless; a hook `allow` loses to a settings
`ask` or `deny`; PostToolUse fires only after success; subagents send `agent_id` and the main
thread does not; `CLAUDE_CODE_SESSION_ATTENDED` is `1` only where a person answers prompts.

## Decision

1. **One `allow`.** Under `--runtime claude` the gate answers `allow` for a Bash command only
   when the verdict is an `ask` from a default row (not a `never`, not a prompt-only ask, not
   a rule-less ask), `grant_scope` names a kind and target this session holds unexpired, the
   call is from the main thread, and the owner and project layers alone have nothing to say.
   Everything else is unchanged: the project layer cannot allow, an owner `allow` only
   silences, and under agy cobot never answers `auto_approve`.
2. **Allow-lists bind the target.** Six kinds (`gcloud`, `gcloud-delete`, `kubectl`,
   `kubectl-delete`, `helm`, `helm-uninstall`); each covers named groups, verbs and options of
   a plain simple command naming its target flag (`--project`, `--context`, `--kube-context`)
   exactly once, with no resource path or URL. A form outside the lists asks.
3. **Only a person grants.** `cobot-rules grant <kind> --target <t>` writes nothing; the gate
   asks about it with an ask no rule or grant lifts, and writes a pending entry. A PostToolUse
   hook records the grant only on a matching pending entry younger than ten minutes, on the
   main thread, with `ATTENDED=1`. The store is `<config dir>/cobot/grants/<session>.json`,
   Edit, Write and shell writes to it are `never`, a grant expires after 12 hours, and
   SessionEnd removes the file.
4. **No Terraform grants.** The folder cannot bind the cloud target: the agent writes the
   config, and a saved plan carries its own backend. `apply` and `destroy` move from `never` to
   a prompt-only ask: each one is the owner's answer at the prompt, which no owner `allow` line
   and no grant silences.
5. **The hard list grows** so that no grant and no prompt reaches state surgery, credential
   printers, cluster-wide wipes, the kubeconfig or cobot's own rule and grant files.

## Consequences

- The gate's documented contract changes from "never emits allow" to "never without a grant";
  `test_gate_neverEmitsAllow_withoutAGrant` and the agy `auto_approve` pin hold it.
- A grant covers the content the agent writes: a manifest under a `kubectl` grant can create
  anything on that context. The context, not the content, is the bound.
- A settings `ask` or `deny` still wins over a grant (P3); a host program that sets
  `ATTENDED=1` and answers prompts by code is the owner's own and cobot cannot see past it.
- Grants are Claude Code only: agy sends no agent identity, so "main thread only" cannot hold
  there; `cobot-rules grant` is denied under agy.
- Not covered and left asking: `gcloud storage`, IAM bindings, `kubectl patch` without
  `--patch-file`. Workflow agents were not probed: keeping a grant from them rests on their
  sending `agent_id`, as every probed agent does.
