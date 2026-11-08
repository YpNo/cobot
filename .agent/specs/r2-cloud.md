# Spec — R2 slice 3: Google Cloud, Kubernetes and the service mesh

size: large · profile: library · owner: YpNo · date: 2026-11-08 · parent: `.agent/specs/r2.md` · branch `feat/r2-cloud` on `main`

## Goal

Three domains join the bench as knowledge skills with their read-only audits: `expert-gcp`
(project and organisation structure, IAM least privilege and Workload Identity Federation, the
`google` Terraform provider 8.x idiom with the universe facts of the legacy `gcd-universe`
skill re-verified, GKE Autopilot and Workload Identity, Artifact Registry, Cloud Build against
GitHub Actions OIDC, logging and cost levers), `expert-kubernetes` (manifests, Kustomize, Helm,
Gateway API, Pod Security Standards, requests and limits, probes, NetworkPolicy, GKE specifics)
and `expert-service-mesh` (Istio ambient and sidecar modes, mTLS, AuthorizationPolicy,
telemetry, Cloud Service Mesh as the managed plane on GCP), each with a `consult-<x>` fork of
the consultant. The gate learns the read forms of `gcloud`, `kubectl`, `helm`, `kustomize`,
`kubeconform` and `istioctl` for the consultant and the learner without opening a way to execute
repository content, and asks on the `gcloud` mutations decision 26 named but the rows missed.
What does not change: every knowledge line carries a status, a source and a date; outward and
mutating actions ask; builders never commit; the agent listing stays under 600 tokens; the skill
description total stays under 15 000 characters; the SessionStart payload under 10 000.

## Principles check

- Proportionality: six skills with references, three eval cases, one decision row and one ADR,
  rule rows, one Python change in `cobot-rules` (a canonical form for `gcloud` and for the flags
  and variables that make a read command execute a program), description trims on the six
  longest existing skills; no new dependency; no new agent (consults fork the consultant); no
  second plugin (decision 28 below).
- Rules before autonomy: the consultant's and the learner's read lists gain only the forms that
  read (`gcloud … list|describe|get-iam-policy|get-value|read|ls`, `gcloud config list`,
  `kubectl get|describe|logs|diff|explain|top|events|api-resources|api-versions|version|
  cluster-info|auth can-i|config view|config current-context|config get-contexts|kustomize|
  rollout status|rollout history`, `helm template|lint|list|ls|status|show|search|history|
  env|version|verify|dependency list|get notes|get metadata|get hooks`, `kustomize build`,
  `kubeconform`, `istioctl analyze|proxy-status|proxy-config|version|verify-install`); these
  reads are silent for the read-only agents the way `gh api repos/*` already is (the consults
  say so and name a current context as the precondition; no "owner's yes" sentence promises a
  prompt the gate does not give). A segment that could execute repository content never
  matches an agent-scoped `allow`, whatever the command: any leading assignment or `env`
  argument outside a short cosmetic allowlist (`NO_COLOR`, `LANG`, `LC_ALL`, `TZ`, `TERM`,
  `COLUMNS`), `git -c` or `--exec-path`, `--kubeconfig` on `kubectl`, `helm` or `istioctl`
  (and `-c` on `istioctl`) in any position, `--post-renderer`, `--enable-exec`,
  `--enable-alpha-plugins`, `--enable-helm`, `--helm-command`; `env` followed by an option
  (`env -S`, `env -i`) is opaque. Secret values never reach a read-only agent: `never
  Bash(kubectl get *[sS][eE][cC][rR][eE][tT]*)`, `never Bash(kubectl get * -f *)` and the
  `-k`, `--filename`, `--kustomize` forms, `never Bash(kubectl config view*--raw*)`, all
  `@consultant` and `@learner`; `helm get values|manifest|all`, `gcloud secrets versions
  access` and `gcloud auth print-access-token` are not read forms. Mutating verbs that had no
  row ask on the main thread (decision 26): `gcloud` `add-*`, `remove-*`, `set-*`, `attach-*`,
  `detach-*`, `restore*`, `deploy`, `submit`, `enable`, `disable`, `import`, `export`, `apply`,
  `promote`, `rollback`, `resize`, `start`, `stop`, `reset`, `suspend`, `resume`, `restart`,
  `move`, `undelete`, `destroy`, `upgrade`, `patch`, `clone`, `failover`, `pause`, `cancel`,
  `replace`, `invoke`, `install`, `cp`, `mv`, `rm`, `rsync`, `publish`, `execute`, `call`,
  `run` as a verb, `login`, `revoke`, `activate-service-account`; `kubectl run|debug|cp|
  expose|autoscale|rollout pause|rollout resume|certificate approve|certificate deny`;
  `helm plugin install|registry login`; `istioctl waypoint apply|waypoint delete|tag set|
  tag remove|create-remote-secret`. The list is a denylist and says so in Risks. Builds,
  templates, lint and reads stay silent on the main thread, a post-renderer included: the
  main thread runs `make` and `npm test` already.
- Knowledge is a skill: every version and fact in the nine references comes from the research
  delta gathered 2026-11-08 from primary sources (cloud.google.com, registry.terraform.io and
  the provider's upgrade guide, kubernetes.io, helm.sh, kubectl.docs.kubernetes.io for
  Kustomize, gateway-api.sigs.k8s.io, istio.io, the GKE and Cloud Service Mesh docs, GitHub
  release APIs), persisted first as `.agent/knowledge/cloud.md` (task 0) so a fresh session can
  build from it; the legacy `gcd-universe` facts are re-verified against the provider 8.x docs
  and the Cloud Foundation Fabric source before they are copied, and stay `reported` where the
  page does not say it; nothing unreached is written.
- Proof: `check-plugin` (paths, dated lines, the two budgets), strict validation, markdownlint,
  pytest on the canonical forms and every new row, three eval cases single-arm, a gate dry run
  of every row named in the stories.
- Delivery: tasks below are the commits; one PR with base `main` (PRs 4 to 7 merged while this
  slice was built; the unpushed branch was rebased onto `main` once, before its first push;
  after the push, review changes reach it by `git merge`, never by a rebase).

## Decision 28 (drafted here, confirmed by the challenger pass): skill pairs, not `cobot-gcp`

The design (§3, §12, §15) and ADR-0001 name a domain plugin `cobot-gcp` and give its criterion:
a domain plugin exists so that a repository outside the domain does not pay for what the domain
needs, "each with its own `.mcp.json`". This slice ships no MCP server (decisions 25 and 26:
CLIs over MCP, because the gate judges argv) and no agent (the consults fork the consultant),
and a path-gated skill costs one listing line and nothing more until its files are touched. The
costs a second plugin would add are real: a second marketplace entry and `plugin.json`, a second
`check-plugin` and validation target in CI and in `install.sh`, a cross-plugin `agent:
cobot:consultant` reference whose behaviour is unverified (the mechanics reference records
same-plugin forks only), and an eval that could not load the consultant without the first plugin
installed. The one thing a second plugin would buy, a listing the owner can leave disabled on
non-GCP repositories, is worth less than the per-skill description caps already enforced:
`check-plugin` holds the total under 15 000 characters, and this slice trims the six longest
existing descriptions (lang-terraform, lang-fallback, expert-containers, lang-python,
lang-typescript, expert-gha: each to ≤ 600 characters, same triggers, fewer words) to make room
(13 782 today; the six new descriptions are capped at 420 for an expert and 270 for a consult;
`lang-go` and `lang-rust` are trimmed to ≤ 600 as well). The arithmetic holds by about 100
characters: slice 4 brings at least six skills and must argue its own room in its spec, by one
`consult` skill with an `argument-hint` replacing the seven `consult-<x>` entries (about 2 400
characters), by further trims, or by a higher cap. Decision 28 does not remove that choice, it
moves it to the slice that needs it.

Decision: the three domains are skill pairs inside `plugins/cobot`. `cobot-gcp` is created the
day a GCP MCP server or a GCP-only agent is adopted, and then holds the server and that agent,
not the skills. Design §3, §12 and §15 and the R2 umbrella spec are reworded; the `gcd-universe`
user skill is superseded by `expert-gcp/references/universe.md` and `lang-terraform` hands off
to `expert-gcp` instead. Recorded as decision 28 and ADR-0006.

## Stories and acceptance

1. **A GCP file touched loads the GCP expert.** `expert-gcp` (`paths:` `**/cloudbuild*.y*ml`,
   `**/*.gcp.y*ml`, `**/gcp/**`, `**/google-cloud/**`, `**/*.gcloud`;
   not `**/*.tf`, which belongs to `lang-terraform` and would load the GCP expert in every AWS
   module: `lang-terraform` gains one line that sends a `google` or `google-beta` provider to
   `../expert-gcp/SKILL.md`, replacing its `gcd-universe` hand-off) carries: the
   non-negotiables (no service-account keys, Workload Identity Federation for every CI and
   Workload Identity for every pod, no primitive roles, `_member` over `_binding` in modules,
   organisation policy and project factory shape, CMEK and audit logs where the profile says
   `service` or `infra`, budgets with alerts); the provider 8.x idiom (`universe_domain`,
   `default_labels`, `add_terraform_attribution_label`, `user_project_override` and
   `billing_project`, `prefer_regional_endpoints`, write-only attributes, the 8.0 upgrade
   facts); project and org structure (folders by environment and team, one project per
   workload and environment, shared VPC, the project factory from Cloud Foundation Fabric as the
   reference shape); IAM (least privilege by predefined role, conditions, deny policies,
   Privileged Access Manager for break-glass, service agents through
   `google_project_service_identity`); Workload Identity Federation (pool, provider, attribute
   mapping and condition on `assertion.repository`, direct federation over impersonation, the
   GitLab and GitHub issuers); GKE (Autopilot default, Workload Identity Federation for GKE,
   release channels, private nodes, Gateway API controller, Config Connector mentioned not
   taught); Artifact Registry (regional repositories, cleanup policies, remote and virtual
   repositories, immutable tags, `gcloud auth configure-docker <region>-docker.pkg.dev`); Cloud
   Build against GitHub Actions OIDC (when each pays, `cloudbuild.yaml` shape, the OIDC path
   through `google-github-actions/auth` from `expert-gha`); logging (log buckets, retention,
   exclusions, `_Default` sink, Audit Logs that are on and those that cost) and cost levers
   (committed use, Autopilot billing per pod, idle resources, regional over multi-regional
   storage, log exclusions, budgets); `gcloud` forms with what asks; pitfalls. References:
   `references/versions.md` (gcloud SDK, provider, GKE channels, dated), `references/iam.md`
   (roles, WIF snippets for GitHub and GitLab, the service-agent table),
   `references/universe.md` (the `gcd-universe` rules rewritten: the three things a universe
   changes, the two independent values, endpoints by owner, service-agent emails through the
   provider, prefixed project IDs and `LastIndex` parsing, what does not change, unavailable
   services, the audit greps, the test rules; every claim re-verified or marked `reported` with
   the Fabric source). Acceptance: `check-plugin` passes; the description names the files and
   the hand-off; every version line has a source; no skill hands off to `gcd-universe` any more (the
   universe reference names it once, as the superseded source).
2. **`/cobot:consult-gcp` audits read-only.** Fork of the consultant: inventory (Terraform
   roots and modules with a `google` provider, `cloudbuild*.y*ml`, workflows that authenticate to
   GCP, `gcloud` calls in scripts), then the checks: keys (`google_service_account_key`, JSON
   keys in secrets, `gcloud iam service-accounts keys create` in scripts), primitive roles
   (`roles/owner|editor|viewer`), authoritative IAM in modules (`_binding`, `_policy`),
   provider blocks inside modules, hardcoded service-agent emails and `googleapis.com`
   endpoints classified by the universe rules, project IDs parsed on `:`, missing Workload
   Identity on GKE node pools and pods, `enable_legacy_abac`, public buckets, CMEK where the
   profile asks for it, Audit Log configuration, budgets; with an active `gcloud` configuration,
   `gcloud … list|describe` and `gcloud projects get-iam-policy` read the live project (read
   forms only, silent like `gh api repos/*`; nothing else is silent for the consultant). Ten
   findings at most with file, line and fix; `knowledge_delta` as in the other consults.
   Acceptance: eval `gcp-iam-audit` (fixture module `modules/gke/main.tf` with a `provider
   "google"` block, a `google_project_iam_member` on `roles/owner`, a
   `google_service_account_key`, and a local that builds
   `service-<number>@container-engine-robot.iam.gserviceaccount.com` by hand): the trace carries
   `roles/owner`, `service_account_key`, `google_project_service_identity` and `main.tf`;
   `Skill` was used with `consult-gcp`; `Write` and `Edit` were used zero times.
3. **A Kubernetes file touched loads the Kubernetes expert.** `expert-kubernetes` (`paths:`
   `**/kustomization.y*ml`, `**/Chart.yaml`, `**/Chart.lock`, `**/values*.y*ml`,
   `**/helmfile*.y*ml`, `**/skaffold*.y*ml`, `**/k8s/**`, `**/kubernetes/**`,
   `**/manifests/**/*.y*ml`, `**/*.k8s.y*ml`; not `**/templates/**`, which fires on the
   plugin's own skill templates and on docs generators, and not a bare `**/manifests/**`,
   which fires on Puppet modules) carries: the non-negotiables (every container with `resources.requests` and a
   memory limit, `readinessProbe` and `livenessProbe` that touch the real dependency with
   `startupProbe` for slow starts, images pinned by digest and never `latest`, Pod Security
   Standards `restricted` as the namespace label with `runAsNonRoot`, `allowPrivilegeEscalation:
   false`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`, read-only root
   filesystem, `automountServiceAccountToken: false` unless the pod calls the API, a default-deny
   `NetworkPolicy` per namespace with explicit allows, `PodDisruptionBudget` and
   `topologySpreadConstraints` for anything with replicas, Gateway API over Ingress for new
   routes, Kustomize overlays or Helm values per environment and never both on one app, Helm
   charts linted and templated in CI and rendered output validated with `kubeconform -strict`);
   the manifest shapes (Deployment, StatefulSet, Job and CronJob, Service, HTTPRoute, the
   restricted pod template); Kustomize (bases and overlays, `images:` digest pins,
   `configMapGenerator` with hash suffixes, `patches` over `patchesStrategicMerge`, components,
   `replacements` over `vars`); Helm (chart structure, `values.schema.json`, `helm lint`,
   `helm template | kubeconform`, `--rollback-on-failure --wait=watcher --timeout` on
   upgrade with Helm 4, `--atomic` on Helm 3, OCI registries, `helm diff` as a plugin); Gateway API (GatewayClass, Gateway, HTTPRoute, GRPCRoute,
   ReferenceGrant across namespaces, the GKE Gateway controller classes); GKE specifics
   (Autopilot constraints on privileged pods and host paths, Workload Identity annotation,
   `gke-l7-*` gateway classes, Backend and Frontend configs through policies, node auto
   provisioning); the `kubectl`, `helm`, `kustomize` forms with what asks; pitfalls.
   References: `references/versions.md` (Kubernetes, kubectl skew, Helm, Kustomize, Gateway
   API, kubeconform, GKE channel versions, dated), `references/manifests.md` (the restricted
   Deployment, HTTPRoute and default-deny NetworkPolicy ready to copy). Acceptance:
   `check-plugin` passes; every version line has a source.
4. **`/cobot:consult-kubernetes` audits read-only.** Inventory (manifests, kustomizations,
   charts, values files, the workflows that deploy), tools when on PATH and on the read list
   (`kustomize build <overlay>`, `helm template <release> <chart> -f <values>`, `kubeconform
   -strict -summary` over the rendered output, `kubectl diff -f` only when a current context exists
   and the audit is about a live cluster; never `--post-renderer`, never `--enable-exec`), then the checks of story
   3 per workload: resources, probes, image pins, security context against the `restricted`
   profile, service-account token mounting, NetworkPolicy presence, PDB and spread, Ingress
   versus Gateway, Kustomize and Helm hygiene, secrets as literals in values or manifests, GKE
   Autopilot incompatibilities. Acceptance: eval `k8s-workload-audit` (fixture
   `k8s/deployment.yaml`: `image: nginx:latest`, no `resources`, `privileged: true`, no probes,
   no NetworkPolicy; the prompt states there is no cluster): the trace carries `latest`,
   `privileged`, `requests|limits|resources`, `readinessProbe|livenessProbe|probe` and
   `deployment.yaml`; `Skill` used with `consult-kubernetes`; `Write` and `Edit` zero; no
   `Bash` call matching `kubectl (diff|get|describe|logs)`, so the trace is a function of the
   fixture alone even on a machine with a kubeconfig.
5. **A mesh file touched loads the service-mesh expert.** `expert-service-mesh` (`paths:`
   `**/istio/**`, `**/istio-system/**`, `**/mesh/**/*.y*ml`, `**/*istio*.y*ml`, `**/*-mesh*.y*ml`,
   `**/*peerauthentication*.y*ml`, `**/*authorizationpolicy*.y*ml`) carries: the
   non-negotiables (mesh-wide `PeerAuthentication` `STRICT` in the root namespace with
   `PERMISSIVE` only as a dated migration step, a default-deny `AuthorizationPolicy` per
   namespace then allows by principal, no `DestinationRule` with `tls.mode: DISABLE`, ambient
   for new meshes and sidecars only where L7 per-pod features need a waypoint anyway, the
   revision or the managed channel named in every namespace label, egress through a gateway or
   `REGISTRY_ONLY`, telemetry through the Telemetry API not `EnvoyFilter`); ambient against
   sidecar (ztunnel and waypoints, what each mode costs and cannot do, the migration order);
   mTLS (what `STRICT` proves, the SPIFFE identity, certificate rotation, mixed-mode
   pitfalls); AuthorizationPolicy (ALLOW, DENY, CUSTOM and AUDIT evaluation order, `source.
   principals` over IP, the empty-rule trap that allows all, JWT with `RequestAuthentication`);
   telemetry (metrics, access logs and tracing through the Telemetry API, sampling, what Cloud
   Monitoring and Cloud Trace receive on GCP); Cloud Service Mesh (managed control plane,
   `gcloud container fleet mesh update --management automatic`, the `asm-managed` channels,
   what the managed plane forbids, Istio APIs supported, GKE Gateway for ingress); `istioctl`
   forms with what asks; pitfalls. References: `references/versions.md` (Istio supported
   releases and the Kubernetes versions each supports, Cloud Service Mesh channels, dated),
   `references/policies.md` (STRICT mesh-wide, default deny, allow by principal, waypoint
   enrolment, Telemetry defaults, ready to copy). Acceptance: `check-plugin` passes; every
   version line has a source.
6. **`/cobot:consult-service-mesh` audits read-only.** Inventory (mesh resources in the tree,
   the namespaces labelled for injection or ambient, the Helm values or `IstioOperator` file,
   fleet configuration in Terraform), tools when present (`istioctl analyze --use-kube=false
   <files>`, `istioctl proxy-status` and `proxy-config` only when the audit is about a live
   mesh), then the checks of story 5: mesh-wide mode, per-namespace policies, DISABLE
   on DestinationRules, allow-all AuthorizationPolicies, policies that select by IP, missing
   RequestAuthentication beside JWT rules, EnvoyFilters, unversioned or mixed revisions,
   ambient namespaces without a waypoint while L7 policy is written, egress unbounded.
   Acceptance: eval `mesh-mtls-audit` (fixture `mesh/peer-authentication.yaml` with
   `mode: PERMISSIVE` in `istio-system`, `mesh/authz.yaml` with `action: ALLOW` and an empty
   rule, `mesh/destination-rule.yaml` with `tls.mode: DISABLE`): the trace carries
   `PERMISSIVE`, `STRICT`, `DISABLE`, `peer-authentication.yaml`; `Skill` used with
   `consult-service-mesh`; `Write` and `Edit` zero; no `Bash` call matching `istioctl
   (proxy-status|proxy-config)|kubectl (get|describe)`.
7. **The gate reads cloud CLIs the way it reads `gh api`.** In `cobot-rules`:
   (a) `canonical_gcloud`: after the global options are stripped, the form is cut after the
   first token (from the third token on, since the first two are groups) that is a known
   `gcloud` verb (read: `list`, `describe`, `get-iam-policy`, `get-value`, `get-ancestors`,
   `read`, `ls`; mutating: the list in the principles check plus `create`, `delete`, `update`,
   `ssh`, `scp`, and any token starting with `add-`, `remove-`, `set-`, `attach-`, `detach-`,
   `restore`), so `gcloud pubsub topics create list` has the canonical form `gcloud pubsub
   topics create` and no read row matches it, while `gcloud compute instances list
   --format=json` becomes `gcloud compute instances list`; a command without a known verb
   keeps its form. Because an `allow` matches only the canonical form, the read rows are
   written without a trailing star (`allow Bash(gcloud * list) @consultant`); the new ask rows
   are written the same way (`ask Bash(gcloud * destroy)`), so `describe runner-1` does not
   read as `run`. (b) `executes_foreign(tokens)`: true when the segment carries a leading
   assignment or an `env` argument naming a variable outside the cosmetic allowlist, `git -c`
   or `--exec-path`, `--kubeconfig` on `kubectl`, `helm`, `istioctl` or `-c` on `istioctl` in
   any position, or `--post-renderer`, `--enable-exec`, `--enable-alpha-plugins`,
   `--enable-helm`, `--helm-command`. `judge_bash` drops every agent-scoped `allow` from the
   matched rules of such a segment, so the read-only agents ask; `never` and `ask` rows still
   match the stripped forms, so every main-thread verdict the tests pin is unchanged by
   construction (`FOO=bar git push` asks, `RUST_LOG=debug cargo test` is silent). A segment
   whose first token after the wrappers starts with `-` (`env -S "git push --force"`, `env -i
   git log`) is opaque and asks. No hoisting, no new token order. (c) Rows: the ask rows of the
   principles check for `gcloud`, `kubectl`, `helm`, `istioctl`; the `never` secret rows for
   both agents; the read lists for both agents. Acceptance: the parametrised decision table
   gains one row per new rule; unit tests cover `create list`, the verb families, the foreign
   marker through `env`, a bare assignment, `PATH=`, `KUBECONFIG=`, `CLOUDSDK_PYTHON=`,
   `GIT_CONFIG_GLOBAL=`, `git -c core.pager=x log`, `--kubeconfig` leading and trailing,
   `--post-renderer`, `--enable-helm --helm-command`, the cosmetic allowlist (`NO_COLOR=1 git
   log` stays silent for the consultant), `env -S`; `kubectl get Secret x` and `kubectl get -f
   k8s/` deny for the consultant; `kubectl config view --raw` denies, `kubectl config view
   --minify` is silent; `cobot-rules check` dry runs quoted in the journal.
8. **The budgets hold.** `check-plugin` keeps passing: the six trims land in one commit before
   the first new skill; each new description states the files, the triggers and the hand-offs
   in its cap; the agent listing does not change (528 tokens).

## Tasks

0. Persist the research delta as `.agent/knowledge/cloud.md`; decision 28 in
   `docs/01-decisions.md`, ADR-0006, the umbrella spec's row and the design's `cobot-gcp`
   wording; fold the challenger verdict into this file.
1. `cobot-rules`: `canonical_gcloud`, `executes_foreign`, the opaque option-first segment;
   the rows of story 7; tests.
2. Description trims on the eight longest skills; `check-plugin` output quoted.
3. `expert-gcp` with its three references, `consult-gcp`, the `lang-terraform` hand-off.
4. `expert-kubernetes` with its two references, `consult-kubernetes`.
5. `expert-service-mesh` with its two references, `consult-service-mesh`.
6. Evals `gcp-iam-audit`, `k8s-workload-audit`, `mesh-mtls-audit`; run each single-arm.
7. README, changelog, design §4 roles row and the `cobot-gcp` mentions, journal entry with
   proof; `wrap` and `spec` name the three consults beside the others.

## Risks

- Knowledge rot: GKE and Istio move monthly, the provider weekly; the brief flags version lines
  after 30 days and the weekly refresh re-verifies them. Cloud Service Mesh facts come from
  cloud.google.com pages that render for a fetch; anything that does not is `reported`.
- Skill count grows from 24 to 30 and the description total approaches its cap; a later slice
  pays with trims or a higher cap argued in its spec, not silently.
- Only `kubectl` is installed on this machine (through mise); `gcloud`, `helm`, `kustomize`,
  `kubeconform` and `istioctl` are absent, so their rows are proven by the gate's dry run and
  the consults say what they could not run. The evals therefore grade what a read of the
  fixture files yields, never a tool's output.
- `canonical_gcloud` cuts the form at the first verb: a resource named like a verb
  (`gcloud pubsub topics describe create`) is read as `describe` and stays silent for the
  consultant, which is the safe direction; a mutating verb before a read verb asks.
- `executes_foreign` is an allowlist on the environment (any assignment outside six cosmetic
  names disables the agent allows) and a denylist on flags; the flag list names the ones the
  read commands document today (`--post-renderer`, `--enable-exec`, `--enable-alpha-plugins`,
  `--enable-helm`, `--helm-command`, `--kubeconfig`, `git -c`, `--exec-path`) and the spec
  says so rather than claiming a general solution. The mutating verb rows are a denylist too:
  `gcloud` has hundreds of verbs; the families (`add-*`, `set-*`, `remove-*`, `attach-*`,
  `detach-*`, `restore*`) and the named verbs cover what the challenger and the owner's
  repositories showed; a verb outside them stays silent on the main thread, as today.
- The budget holds by about 100 characters after this slice (see decision 28).
- The `gcd-universe` facts about Go client libraries and Java connectors describe code paths
  in `google.golang.org/api` v0.28x; they are copied as `reported` with the legacy skill named
  as the source unless the file is read today.

## Challenger

SOUND WITH CHANGES (2026-11-08), one blocker, four majors, two minors, all folded: the
executing-environment denylist missed `PATH=`, `KUBECONFIG=`, `CLOUDSDK_PYTHON=`,
`GIT_CONFIG_GLOBAL=` and the `GIT_CONFIG_COUNT` triple (inverted into `executes_foreign`: any
assignment outside a cosmetic allowlist and any executing flag disables the agent-scoped allows;
the hoist and its main-thread rows dropped; `env -S` opaque); `--kubeconfig` in trailing
position and `--enable-helm --helm-command` (covered by the marker in any position); secret
values through `kubectl get Secret`, `kubectl get -f`, `kubectl config view --raw` and `helm get
values|manifest|all` (case-insensitive never rows, the `-f`/`-k` forms denied, `config view`
without `--raw`, `helm get` limited to notes, metadata, hooks); the mutating verb denylist
(`destroy`, `upgrade`, `patch`, the `add-*`/`set-*`/`remove-*`/`attach-*`/`detach-*`/`restore*`
families, `kubectl run|debug|cp|expose|autoscale`, `helm plugin install|registry login`,
`istioctl waypoint|tag|create-remote-secret` added; the caveat stated in Risks); the "owner's
yes" wording that the silent read rows contradicted (struck; the evals state there is no
cluster and grade that no cluster-reading `Bash` call happened); the budget arithmetic (two more
trims, slice 4's choice named in decision 28); three globs (`**/manifests/**/*.y*ml`,
`**/mesh/**/*.y*ml`, skaffold moved to the Kubernetes expert). Checked clear: `canonical_gcloud`
against every pinned `gcloud` row, decision 28 against the design's criterion and ADR-0001, the
eval shape and the literal tokens in the fixtures, the owner's rules, the agent budget.

## Out of scope

A GCP MCP server, a `cobot-gcp` plugin, Config Connector and Crossplane, ArgoCD and Flux
(delivery of manifests is slice 4's `expert-api` neighbour or a later `expert-gitops`), Anthos
on bare metal, Linkerd and Cilium mesh beyond a comparison line, AWS and Azure, any live cluster
or project in the evals.
