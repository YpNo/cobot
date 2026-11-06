# Discovery — agentic-partner (2026-11-05)

Working notes from the first session. Not a design yet: findings, a candidate shape, and
the questions whose answers change the design.

## What exists today (version one)

- `workstation-starter/ai/` → `~/.agents/` → `~/.claude/` + `~/.gemini/` (ADR-0001..0003).
  Five phases (`/onboard /design /build /wrap /ship`), ten agents, four language standards
  (rust, go, python, terraform) + fallback, a router, `.agent/` memory files per repo,
  `security-sweep`, `gcd-universe`. Three sanctioned fan-out points (ADR-0001).
- In real use: cartridge-os, photo-metadata-fixer, demo-profil-matching,
  googleapis-interceptor-envoy, server-automation all have `.agent/` journals; challenger
  reviews appear in four sessions.
- Spread on top of it: speckit (10 skills) copied into three repos, mattpocock-skills
  plugin (12), three HashiCorp Terraform plugins (~15), four `rust-*` commands, repo-local
  skills. Two planning workflows coexist (speckit vs `/design` + `/build`).
- Claude Code built-ins already own: plan mode, task list, sessions/worktrees,
  `/code-review`, `/security-review`, `/simplify`, Workflow tool, persistent memory.
  Version one routes to them instead of duplicating. Version two must keep that rule.

## Work the partner must serve (from GitHub + sessions)

- Google Cloud: Terraform modules (GKE, folders, k8s objects, essential contacts),
  sovereign universe work (GCD / S3NS interceptors), gcp-platform, argocd (private).
- Rust libraries and apps: arlo-rs, imap-rs, stealthscraper-rs, cartridge-os (embedded).
- Go upstream contributions: headscale (merged PR), gitea (open PR), interceptors.
- TypeScript upstream: headplane (open PR). Python: dreame-vacuum (HA integration).
- Ansible home server (server-automation). Device/protocol reverse engineering
  (Arlo, Dreame/Xiaomi, Miyoo Mini+ hardware).

## Gaps between version one and the vision

- No per-language senior developer agents for Go, Python, TypeScript, Shell (standards only).
- No delivery experts: GitHub Actions, GitLab CI, ArgoCD, Crossplane, Ansible, OPA, Trivy.
- No Google Cloud expert beyond `gcd-universe`.
- No reverse-engineering protocol, no upstream-contribution flow.
- No "foreign repo" memory mode (cannot commit `.agent/` into headscale or gitea).
- Not a plugin (deferred in ADR-0001 until proven). No evals, no CI for the partner itself.

## Candidate shape (to confirm)

One repo (this one) as a Claude Code plugin marketplace, layered:

1. `partner-core` — orchestrator protocol: phases, proportionality, memory files, router,
   hooks (session start, rtk), templates. The orchestrator is Claude Code's main thread.
2. `partner-experts-<domain>` — narrow-tool agents that return a decision or a findings
   list: architecture, languages, security (appsec, supply chain, reverse engineering),
   delivery (CI/CD, GitOps, config management, policy), cloud (GCP incl. GDC), docs/test.
3. `partner-flows` — new phase skills: `/contribute`, `/reverse`, `/infra-review`,
   `/research`. Existing five phases kept.

`workstation-starter` keeps bootstrapping the machine and installs the plugin.
`~/.agents` survives only if Antigravity stays a target.

## Open questions

See the session message of 2026-11-05; answers go into `docs/01-decisions.md`.
