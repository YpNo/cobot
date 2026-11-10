---
name: security-sweep
description: Read-only audit of a whole repository, every language it contains, by the consultant agent in a fresh context. Invoke for a periodic security pass, before production or handover, or on a repository you did not write; for pending changes use /security-review instead. Loads the core rule pack plus one pack per language and infrastructure kind present, honours .agent/accepted-risks.md, and returns at most ten findings with severity, confidence, file and line, the untrusted path and a concrete fix, plus what it did not cover.
argument-hint: [path or subsystem]
context: fork
agent: cobot:consultant
user-invocable: true
disable-model-invocation: true
---

# security-sweep

Read-only. Change nothing, commit nothing, run no fixer. You are one consultant on the whole
tree: enumerate before judging, anchor every finding to a file and line, stop at ten findings and
say what you did not cover. The argument, when given, narrows the tree to one path.

## Procedure

1. **Inventory, not findings.** Languages by file count and manifest, the shape (`service`,
   `library`, `cli`, `infra`, `embedded`, from CONTEXT.md when present), and the trust
   boundaries with file and line: network listeners and routes, subprocess and shell-out sites,
   filesystem paths built from input, deserialisation (JSON, YAML, pickle, gob, XML), crypto
   and randomness, authn and authz decisions, logging sinks, every place a secret is read, held
   or forwarded. A library has no CORS, a CLI no session handling, IaC no injection but a
   privilege blast radius: audit what the shape calls for.
2. **Packs.** Read `references/core.md` always, then one pack per kind present: `go.md`,
   `python.md`, `ts-js.md`, `rust.md`, `shell.md`, `dockerfile.md`, `terraform.md`,
   `github-actions.md`. A language without a pack: derive its idiom for the eight core
   categories from the repository first, audit against that, and say so under *Not covered*.
3. **Tools as hints.** When on PATH and on your read list, run the read-only forms:
   `gitleaks detect --no-git --report-format json`, `semgrep --config auto --json` (offline
   rules only), `trivy fs --scanners vuln,secret,misconfig .`, `govulncheck ./...`,
   `pip-audit`, `npm audit --json`, `cargo-deny check advisories`, `hadolint Dockerfile`,
   `zizmor --offline .github`. Their output is a lead, never the report: confirm each hit in the
   file. The sweep must produce a complete report with no tool installed.
4. **History.** `git log --all --diff-filter=A --name-only --pretty=format:` filtered for
   `.env`, `.pem`, `.key`, `.p12`, `.pfx`, `.jks`, `credentials`, `secret`: a secret file that
   was committed and later deleted is still CRITICAL, the object is in the history.
5. **Accepted risks.** Read `.agent/accepted-risks.md` (`cobot-memory risks list`). A finding
   whose rule id, file and symbol (function, resource or step name) match an unexpired row is
   listed under *Accepted*, not under findings; an expired row is reported as expired with its
   finding re-checked. Lines move, symbols do not: name the symbol in every finding.
6. **Verify and rank.** Keep a finding only when you can name the file and line and either
   trace the untrusted input to it (`CONFIRMED`) or show the pattern with reachability unproven
   (`PLAUSIBLE`). Merge duplicates across files into one finding listing the locations. Rank:
   CRITICAL (exploitable now by an outsider: secrets in VCS, auth bypass, RCE, injection on a
   reachable path), HIGH (plausible precondition, or a CVE with a reachable call path), MEDIUM
   (real weakness, no demonstrated path), LOW (hygiene), HAZARD (not a vulnerability: a
   correctness defect that causes incidents, its own section).

## Report

```text
scope: <paths audited, languages, packs loaded, tools run or absent, what was skipped>

findings:
1. <severity> · <confidence> · <rule id> · <file>:<line> · <what> · path: <how untrusted input reaches it, or unproven> · fix: <concrete change>
…

hazards:
- <file>:<line> · <defect> · <fix>

accepted:
- <R-nn> <rule · file · symbol> · expires <date> (<ok | expired>)

to accept (the orchestrator runs these only after the owner's yes):
- cobot-memory risks add <rule> <file> <symbol> --why "<reason>" --days <n ≤ 90>

not covered: <units not read, languages without a pack, tools that would have helped>

knowledge_delta (optional, JSON, only facts verified during the sweep and absent from the packs):
{"topic": "security", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

Never report the absence of a feature the shape does not call for; never report a finding you
cannot anchor; never fix anything. The orchestrator decides what becomes a task, an issue the
owner may open, or an accepted-risk row through `cobot-memory risks add` after the owner's
yes. Rule ids come from the packs (`CORE-SECRET-01`, `CORE-INJECT-02`, `CORE-CRYPTO-06`,
`GO-…`, `PY-…`, `TS-…`, `RS-…`, `SH-…`, `DOCKER-…`, `TF-…`, `GHA-…` as each file names them).
