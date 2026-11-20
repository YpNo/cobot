---
name: expert-gcp
description: >-
  Google Cloud: org and project structure, IAM least privilege, Workload Identity Federation, the
  google Terraform provider 8.x, universes, GKE Autopilot, Artifact Registry, Cloud Build or GitHub
  OIDC, cost, the gcloud forms that ask. Use on cloudbuild*.yml, gcp/ folders and any google
  provider block.
paths:
  - "**/cloudbuild*.y*ml"
  - "**/*.gcp.y*ml"
  - "**/gcp/**"
  - "**/google-cloud/**"
  - "**/*.gcloud"
user-invocable: false
---

# expert-gcp

Versions, dates and sources: `references/versions.md`. Roles, federation snippets and the
service-agent table: `references/iam.md`. Universes (sovereign clouds, Google Cloud Dedicated):
`references/universe.md`. Google's remote MCP servers (setup, guard, proof):
`references/mcp.md`. Re-verify a line the brief flags stale (versions after 30 days, idiom
after 90). Terraform idiom and the check chain are `lang-terraform`'s; this skill is what the
`google` provider needs on top. A Terraform apply runs only from a saved plan, at the owner's
prompt; `gcloud` reads are silent, anything that creates, changes, deletes, deploys, enables,
grants or logs in asks (decision 26), unless a session grant covers it (below).

- [verified 2026-11-08 · src: https://registry.terraform.io/v1/providers/hashicorp/google] hashicorp/google and google-beta 8.10.0 (2026-11-03); gcloud 592.0.0 (2026-11-03).

## Non-negotiables

1. No service-account keys. CI authenticates through Workload Identity Federation (pool,
   provider, attribute condition on the organisation or group), pods through Workload Identity
   Federation for GKE, humans through their own identity with impersonation when a service
   account must act. `google_service_account_key` in a module is a finding, not a convenience.
2. No basic roles in production (`roles/owner`, `roles/editor`, `roles/viewer`): predefined roles
   per service, custom roles only when no predefined one fits, conditions for scope and time,
   deny policies as guardrails, Privileged Access Manager for break-glass.
3. In a module, IAM is additive: `google_project_iam_member`. `_binding` and `_policy` are
   authoritative and remove grants made elsewhere; they belong to a project factory that owns
   the whole policy, never to a shared module. Never both on one role.
4. Service agents come from the API, never from a string: `google_project_service_identity`
   (google-beta) exports `member`; a hand-built `service-<number>@…gserviceaccount.com` breaks
   in a universe and races the agent's creation.
5. One project per workload and environment, folders by environment and team, a project factory
   (Cloud Foundation Fabric's `modules/project` is the reference shape), shared VPC with the
   host project in the networking folder, organisation policies set once at the top
   (`iam.disableServiceAccountKeyCreation`, `iam.automaticIamGrantsForDefaultServiceAccounts`,
   `compute.requireOsLogin`, `storage.uniformBucketLevelAccess`).
6. `service` and `infra` profiles: CMEK where the data is regulated, Data Access audit logs on
   the services that hold the data, a budget with alerts on every billing account, labels from
   `default_labels` so cost reports mean something.
7. A universe is a configuration, not a fork: `universe_domain` on the provider, no hardcoded
   `googleapis.com` endpoint or service-agent email, project IDs parsed on the last colon
   (`references/universe.md`).

- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts] "We recommend that you avoid using service account keys whenever possible"; alternatives are an attached service account, Workload Identity Federation and impersonation.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/roles-overview] "In production environments, do not grant basic roles unless there is no alternative"; basic roles carry thousands of permissions across all services.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/r/google_project_iam.html.markdown] `_policy` replaces the whole policy, `_binding` is authoritative for one role, `_member` is non-authoritative; binding and member coexist only on different roles.

## Provider 8.x idiom

```hcl
provider "google" {
  project                         = var.project_id
  region                          = var.region
  universe_domain                 = var.universe_domain      # null in the public universe
  default_labels                  = { env = var.env, owner = var.owner, app = var.app }
  add_terraform_attribution_label = true                     # goog-terraform-provisioned
  user_project_override           = true                     # quota project for the APIs that need it
  billing_project                 = var.project_id
  impersonate_service_account     = var.terraform_sa         # humans impersonate, never a key
}
```

- Credentials: Application Default Credentials in CI come from the federation step
  (`google-github-actions/auth`, GitLab `id_tokens`); `external_credentials` beats
  `credentials`; never `credentials = file("key.json")`.
- 8.0 changed defaults silently: `load_balancing_scheme` is `EXTERNAL_MANAGED` on backend
  services and global forwarding rules (set `EXTERNAL` for a classic LB), `enable_components`
  are sets, `name_prefix` allows 31 characters, `secret_data_wo_version` is a string.
- `google_project_service` with `disable_on_destroy = false` in live roots; `google_project_iam_audit_config`
  for Data Access logs; `google_logging_project_bucket_config` for retention; `google_billing_budget`.
- Write-only attributes (`*_wo` + `*_wo_version`) for secrets fed into resources; nothing
  secret in state when the provider offers the pair.

- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/provider_reference.html.markdown] `universe_domain` "Specify the GCP universe to deploy in"; `user_project_override` defaults to false and selects the quota project; `add_terraform_attribution_label` defaults to true; `request_timeout` 120s; `impersonate_service_account` needs `roles/iam.serviceAccountTokenCreator`.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/version_8_upgrade.html.markdown] 8.0 removed the BeyondCorp app resources, `google_iap_brand`, `google_iap_client`, `google_ml_engine_model`, the `google_notebooks_*` resources and `google_vertex_ai_schedule`; the provider block itself has no breaking change.

## IAM and federation

- Grant to groups or to a workload identity, not to users; conditions on resource name, tag or
  time; `roles/iam.serviceAccountTokenCreator` on the one account humans impersonate; deny
  policies for the permissions nobody may hold (`iam.googleapis.com/roles.delete` outside the
  platform team); Privileged Access Manager entitlements for the roles that must exist but
  must not be held.
- Workload Identity Federation: one pool per external environment, one provider per issuer,
  `google.subject=assertion.sub` plus the attributes the condition needs, a condition that
  names the organisation or group by numeric id (`assertion.repository_owner_id`,
  `assertion.namespace_id`), direct resource access over impersonation, principals with the
  project number. Snippets for GitHub and GitLab: `references/iam.md`.
- Default service accounts: never used, their automatic Editor grant disabled by policy; one
  dedicated account per application; Compute Engine default replaced on every node pool and
  every Cloud Build trigger.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines] GitHub issuer `https://token.actions.githubusercontent.com/`, GitLab issuer `https://gitlab.com`; a condition restricting the organisation is required; the numeric `*_id` claims are advised because names can be reused.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/deny-overview] IAM checks deny policies before allow policies; up to 500 deny policies per resource; only some permissions can be denied.

## GKE

- Autopilot by default; Standard only for a documented need (privileged DaemonSets, host
  paths beyond `/var/log`, specific node images). Regular channel unless a release note says
  otherwise; Extended only for a workload that cannot follow minors.
- Private nodes with Cloud NAT, the DNS-based control-plane endpoint, authorised networks when
  the IP endpoint stays on; Shielded nodes; Binary Authorization when images are signed
  (`expert-containers` signs them).
- Workload Identity Federation for GKE with direct IAM bindings on the Kubernetes service
  account principal; no `iam.gke.io/gcp-service-account` linking unless an API refuses the
  principal form; `hostNetwork` pods do not get it.
- Gateway API through the GKE Gateway controller (`gke-l7-global-external-managed`,
  `gke-l7-regional-external-managed`, `gke-l7-rilb`); manifests and policies are
  `expert-kubernetes`'s; Cloud Service Mesh is `expert-service-mesh`'s.
- Config Connector exists for Kubernetes-native resource management; this bench manages
  Google Cloud with Terraform and keeps Config Connector for clusters that already run it.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-security] Autopilot blocks privileged containers, host namespaces, `hostNetwork`, SSH to nodes and `spec.externalIPs`; hostPath only read-only `/var/log`; `CAP_NET_RAW` dropped.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity] Direct IAM principal identifiers are the recommended method; cluster `--workload-pool=PROJECT_ID.svc.id.goog`, node pool `--workload-metadata=GKE_METADATA`.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/release-notes] Defaults on 2026-11-03: Rapid 1.37.1, Regular 1.36.4, Stable 1.35.8 (gke patch suffixes in versions.md).

## Artifact Registry

- One regional Docker repository per project and purpose in the region of the cluster;
  `--immutable-tags` on release repositories; a cleanup policy that keeps the last N tagged
  versions and deletes untagged images older than 30 days (`--dry-run` first); remote
  repositories in front of Docker Hub and ghcr.io so builds never pull upstream directly;
  a virtual repository as the single endpoint when several feed one consumer.
- Auth: `gcloud auth configure-docker <region>-docker.pkg.dev` locally, the federation token in
  CI (`docker login -u oauth2accesstoken --password-stdin`), never `_json_key`.
- Container Registry is gone (shut down 2025-03-18); `gcr.io` names that still resolve are
  Artifact Registry behind an alias.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/artifact-registry/docs/repositories/cleanup-policy] Cleanup policies are Delete or Keep rules on tag state, prefixes, age and `mostRecentVersions.keepCount`; keep wins over delete; applied with `set-cleanup-policies --dry-run` then `--no-dry-run`; effective within about a day.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/artifact-registry/docs/transition/transition-from-gcr] Container Registry is shut down since 2025-03-18; `mirror.gcr.io` keeps working.

## Cloud Build against GitHub Actions

| Need | Pick | Why |
|---|---|---|
| Repository on GitHub or GitLab, pipeline already in `expert-gha` or `expert-gitlab-ci` shape | the forge's CI with OIDC to Google Cloud | one pipeline, one place for pins and attestations; `google-github-actions/auth@v3` direct federation |
| Build must run inside the VPC, read private sources or push to a registry without egress | Cloud Build with a 2nd-gen connection and a user-specified service account | the build identity is a Google Cloud principal with no token in the forge |
| Both | the forge runs tests and attestations, Cloud Build only the step that needs the network | never two pipelines that both deploy |

`cloudbuild.yaml`: `steps` with pinned builder images (`@sha256`), `serviceAccount` set,
`options.logging: CLOUD_LOGGING_ONLY`, `availableSecrets.secretManager` for anything secret,
`timeout` explicit, `images` for what it pushes.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/build/docs/cloud-build-service-account-updates] Cloud Build runs as the Compute Engine default service account unless a user-specified account is set on the trigger, which is the recommended option.
- [verified 2026-11-08 · src: https://cloud.google.com/build/pricing] 2 500 free build-minutes per billing account per month on e2-standard-2, then $0.006 per minute.

## Logging, audit, cost

- `_Required` keeps Admin Activity and System Event logs 400 days for free; `_Default` keeps
  the rest 30 days: set its retention per project on purpose, add exclusions for the noise
  (load-balancer health checks, GKE system logs you do not read), route security logs to an
  aggregated sink in a dedicated project. Data Access logs cost: enable them per service that
  holds data, not organisation-wide.
- Cost levers in order of yield: delete idle resources (the recommenders name them), Autopilot
  requests right-sized (billing is per request), regional over multi-regional storage and the
  right class with its minimum duration, committed-use discounts once usage is flat, log
  exclusions and shorter retention, a budget with 50/90/100 % alerts and a Pub/Sub channel that
  pages someone.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/logging/docs/audit] Admin Activity and System Event audit logs are always on and free; Data Access logs are off by default except BigQuery and cost when enabled.
- [verified 2026-11-08 · src: https://cloud.google.com/stackdriver/pricing] Logging $0.50 per GiB after 50 GiB per project per month; retention $0.01 per GiB-month beyond 30 days; the `_Required` bucket is free.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/compute/docs/instances/committed-use-discounts-overview] Compute flexible CUDs give 28 % (one year) and 46 % (three years) on general-purpose series, GKE Standard and Autopilot and Cloud Run.

## Google Cloud MCP servers

The owner registers Google's remote servers (`https://<service>.googleapis.com/mcp`) as
`gcp-<service>`; cobot ships none (`references/mcp.md`). Use their read tools from the main
thread for live state: `list_log_entries`, `list_k8s_events`, `get_k8s_cluster_health`,
`list_clusters`. Under a `gcp-*` name the gate refuses their write tools by known verb
(`create_`, `update_`, `delete_`, `apply_`, …) and asks on any other tool that is not a read,
because a personal project without an organisation cannot hold the IAM deny policy that would
refuse them server-side. Propose the change as a plan or a `gcloud` command instead. A consultant has
no MCP tools: it audits files, and you query live data.

## gcloud: what asks

Silent: `list`, `describe`, `get-iam-policy`, `get-value`, `config list`, `auth list`,
`logging read`, `storage ls`, `version`. Ask: `create`, `delete`, `update`, `add-*`, `set-*`,
`remove-*`, `deploy`, `submit`, `enable`, `disable`, `import`, `export`, `start`, `stop`,
`resize`, `upgrade`, `patch`, `destroy`, `cp`, `mv`, `rm`, `rsync`, `publish`, `run`, `ssh`,
`login`, `container fleet mesh *`. Denied everywhere, the owner runs them: `print-access-token`,
`print-identity-token`, `config-helper`, `secrets versions access`, `projects delete`,
`set-iam-policy`, `iam service-accounts keys create`, and a delete of a `*tfstate*` object or
bucket. Not on the read-only agents' list: `container clusters get-credentials`.
`--impersonate-service-account` on a read is fine; `--project` is stripped before matching.

## gcloud: session grants (main thread only)

A lab or a demo on one sandbox project can run without a prompt per write. Ask the owner once,
as the protocol says: this command only, every `gcloud` (or `gcloud-delete`) on `<project>`
this session, or no. On the second answer run `cobot-rules grant gcloud --target <project>`;
the owner's prompt on it is the grant, and `cobot-rules grant --list` shows it. A grant covers
`create`, `update` and `deploy` (`gcloud`) or `delete` (`gcloud-delete`) under `compute`
(instances, disks, networks, subnets, firewall-rules, addresses, routers, instance-templates),
`run` (services, jobs), `pubsub` (topics, subscriptions), `functions`, `artifacts repositories`,
`dns` (managed-zones, record-sets) and `container` (clusters, node-pools). The command must be
plain (no pipe, `&&`, substitution or assignment), name `--project <project>` once, and hold
no `projects/`, `gs://` or URL argument and none of `--flags-file`, `--configuration`,
`--account`, `--impersonate-service-account`, `--access-token-file`. Anything else asks as
before; `gcloud storage` and IAM bindings are not grantable. A builder never holds a grant.

The lab log, `.agent/labs/<slug>.md` (Edit): the project, then one line per granted or approved
command with its exit code and its inverse (`run deploy x` → `run services delete x`). It ends
with the teardown, run and logged, and the agent proposes a budget alert on the project
(`gcloud billing budgets create`, which asks). `cobot-rules grant --revoke` ends the grant early.

## Pitfalls

1. `google_project_iam_binding` in a module removes the owner's own grant on first apply.
2. A key created "for a quick test" is the credential that leaks; the policy that forbids key
   creation exists for that test.
3. A federation provider without an attribute condition accepts every repository on GitHub.
4. `user_project_override` left false: the API bills the wrong project and some calls fail
   with a quota error that reads like a permission error.
5. Autopilot rejects a `privileged: true` pod at admission, not at plan time.
6. `gcloud container clusters get-credentials` writes a kubeconfig whose `exec` plugin is the
   auth plugin; a kubeconfig in a repository can name any binary (which is why the read-only
   agents never pass `--kubeconfig`).
7. A regional Artifact Registry repository in a different region than the cluster pays egress
   on every pull.
8. Data Access logs enabled at the organisation level on Cloud Storage cost more than the
   storage.

## Do not

- Do not create, download or store a service-account key; propose federation.
- Do not grant a basic role, even to a service account, even in `dev`.
- Do not write a provider block inside a reusable module, nor an endpoint or a service-agent
  email by hand.
- Do not run `gcloud` writes, `gcloud auth login` or `get-credentials` from a builder or a
  consultant; propose the command. On the main thread a write asks, or runs under a grant.
