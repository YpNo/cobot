# Decisions taken with the owner — 2026-11-06

Answers to the discovery questions (docs/00-discovery.md). These are constraints for the
design, not proposals.

| # | Topic | Decision |
|---|---|---|
| 0 | Starting point | **Blank slate.** Old scaffold ideas may be reused only after being challenged, updated and stripped of dead or deprecated content. |
| 1 | Antigravity / Gemini | Out of scope for now. Claude Code only. |
| 2 | Spec-kit | Absorb its ideas into one lightweight planning path. Projects are small; efficiency over ceremony. |
| 3 | Languages, first release | Rust, Go, Python, TypeScript, HCL (Terraform). Shell and Lua through a fallback. |
| 4 | Delivery stack | GitHub Actions first, with everything around CI/CD, release and security. GitLab CI, ArgoCD, Crossplane, OPA later. |
| 5 | Cloud | Google Cloud expert first. A dedicated GDC / S3NS sovereign-cloud expert later. |
| 6 | Upstream contribution flow | Yes, governed by explicit **rules**: some actions allowed, some always asked, some never automatic. Nothing outward-facing runs on its own. |
| 7 | Reverse engineering | Confirmed. Scope: home-automation devices and IT equipment the owner operates, for interoperability. |
| 8 | Parallelism | More than the old three gated fan-out points. Mechanism (Agent fan-out, sessions, Workflow tool) is the orchestrator's choice, judged against the goal. |
| 9 | Model routing | Yes. Pick the best model per task: relevance and efficiency first, token cost second. |
| 10 | Quality bar for the partner itself | Plugin evals, hook tests, CI on this repo, public. |
| 11 | MCP servers | Wire in every server that is relevant and useful. |
| 12 | Workflow schema | The design must show how orchestrator, conceptor, builders, experts and reviewers hand work to each other. |
| 13 | Learner / teacher (2026-11-06, second review) | When no expert covers a domain, or an expert hits an unknown, the partner learns from primary sources and its own experiments, never by guessing; every expert updates its knowledge when it validates something. Write little: relevant, verified, dated. See ADR-0002. |
| 14 | Token economy | Keep rtk and use it smartly; add other savings techniques, none at the cost of quality. Design §10. |
| 15 | Legacy scaffold | **Do not touch it now.** Build the partner first, ship install methods in this repo, switch at a moment the owner picks. See ADR-0003 and docs/03-switch-plan.md. |
| 16 | crissp | Not used; reviewed for ideas. Ten taken, listed in docs/design-inputs/crissp-review.md. |
