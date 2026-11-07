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

## Third review — 2026-11-07 (confirmed by the owner the same day)

Ideas raised after the cartridge-os dogfood, challenged in
[design-inputs/owner-ideas-02.md](design-inputs/owner-ideas-02.md) and **confirmed as written**.
The "Enforced by" column names where each lives; items marked *R1.1* are built in that release.

| # | Topic | Proposed rule | Enforced by |
|---|---|---|---|
| 17 | CI triggers | Trigger matrix: PR runs changed-area tests with dependency-aware selection; merge runs the full suite and builds once; release verifies the commit's CI and never reruns tests; one aggregator job is the only required check. | `expert-gha`, later `expert-cicd`; `ship` |
| 18 | Attribution | No attribution footer and no AI named as author in commits or PR bodies; not a word ban. | memory (in force), `contribute`, default rules `never` on the argv-visible forms |
| 19 | Backend architecture | Hexagonal by default for the `service` profile; plain layering for `cli`, `library`, `embedded`; host architecture always wins in contributions. | `spec` principles check, ADR template, `lang-*` shapes |
| 20 | PR granularity | One spec = one branch = one PR; one task = one commit. Small PRs only for security fixes and upstream work. | `spec`, `build`, `wrap`, `contribute` |
| 21 | Dependency currency | Cached check at onboard, at session start when stale (7 days) or the lockfile changed, and always before a PR; report, never upgrade unasked. | `partner-deps check` at `onboard` and in `wrap`; the brief reads its cache and names the command when it is older than seven days or a lockfile changed (the SessionStart hook has 30 s and no network promise, so the check itself does not run there) |
| 22 | New dependencies | Adding one is a decision: `ask` on `cargo add`, `npm install <pkg>`, `pnpm add`, `yarn add`, `go get`, `uv add`, `pip install`, `poetry add`; the spec names and justifies each. | default rules, `spec`, builder reports |
| 23 | Knowledge freshness | Staleness thresholds on dated knowledge lines (versions 30 days, idiom 90 days) surfaced in the brief; refresh by `/partner:learn` and a weekly refresh workflow opening a PR; options and recommendation, never an automatic tool swap. | `partner-memory knowledge` and the brief line, `learner` + `/partner:learn`, `learn --promote`, `knowledge-refresh.yml` (R1.1 slice 1, 2026-11-07) |
| 24 | More stacks | `lang-typescript` + `ts-builder` first, then thin `fw-react`, `fw-next`, `fw-vue`; `lang-shell` promoted from the fallback when server-automation is onboarded. | release 1.1 and after |
| 25 | More experts | Order: `expert-cicd` + GitLab CI (`glab`), Gitea (`tea`), `expert-api` (OpenAPI and web protocols), Home Assistant (`hass-cli`), IoT protocols and electronics with evidence grades, Jira and Confluence through the Atlassian MCP (writes ask), MCP builder reused after challenge. CLIs preferred over MCP where both exist, because the gate judges argv. | learner first (23), then one expert per release slice |
| 26 | Containers, Kubernetes, service mesh (added 2026-11-07) | Three experts, not one: `expert-containers` (Dockerfile and Containerfile, multi-stage and distroless images, rootless Podman, BuildKit, compose, SBOM, cosign, Trivy), `expert-kubernetes` (manifests, Kustomize, Helm, Gateway API, Pod Security, GKE Autopilot and Workload Identity), `expert-service-mesh` (Istio ambient and sidecar, mTLS and AuthorizationPolicy, telemetry, Cloud Service Mesh as the GCP managed plane). Mutating `kubectl`, `helm`, `istioctl` and image `push`/`prune`/`login` ask; builds, templates, lint and reads stay silent. CLIs over MCP. | rules now; `expert-containers` with release engineering in R1.1 `ship`; `expert-kubernetes` with `partner-gcp` in R2; `expert-service-mesh` after it, R2/R3 |
