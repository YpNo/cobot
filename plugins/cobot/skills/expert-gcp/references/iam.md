# expert-gcp — IAM, federation and service agents

Dated lines live in `versions.md`; this file is the snippets and tables the expert copies.

## Roles: what to grant instead of a basic role

| Need | Grant | Not |
|---|---|---|
| deploy to Cloud Run | `roles/run.developer` on the service + `roles/iam.serviceAccountUser` on its runtime account | `roles/editor` |
| push images | `roles/artifactregistry.writer` on the repository | `roles/storage.admin` |
| read logs | `roles/logging.viewer` (`roles/logging.privateLogViewer` for Data Access logs) | `roles/viewer` |
| Terraform in CI | per-service admin roles on the project the root manages, `roles/iam.serviceAccountTokenCreator` only when impersonating | `roles/owner` |
| GKE pods calling an API | the API's narrowest role on the `principal://…/subject/ns/NS/sa/KSA` principal | the node service account |
| break-glass | a Privileged Access Manager entitlement with a maximum duration and justification | a standing `roles/owner` |

Conditions when the scope is a subset: `resource.name.startsWith("projects/_/buckets/app-")`,
`resource.matchTag("123456789012/env", "prod")`, `request.time < timestamp("2026-12-31T00:00:00Z")`.
Not with Owner, Editor, Viewer, `allUsers` or `allAuthenticatedUsers`.

## Workload Identity Federation for GitHub Actions (Terraform)

```hcl
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.repository_id"       = "assertion.repository_id"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
    "attribute.ref"                 = "assertion.ref"
  }
  # the condition is mandatory: without it every GitHub repository may enter the pool
  attribute_condition = "assertion.repository_owner_id == '${var.github_org_id}'"
}

# direct resource access: the repository's identity gets the role, no service account in between
resource "google_artifact_registry_repository_iam_member" "ci_push" {
  repository = google_artifact_registry_repository.images.name
  location   = google_artifact_registry_repository.images.location
  role       = "roles/artifactregistry.writer"
  member     = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repo_id}"
}
```

Workflow side (`expert-gha` pins the SHA): `permissions: { contents: read, id-token: write }`,
then `google-github-actions/auth` with `workload_identity_provider:
projects/<number>/locations/global/workloadIdentityPools/github/providers/github-oidc` and no
`service_account` (direct federation). A deploy job adds `assertion.ref == 'refs/heads/main'`
or the environment claim to the condition of a second provider.

## Workload Identity Federation for GitLab CI

```hcl
resource "google_iam_workload_identity_pool_provider" "gitlab" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.gitlab.workload_identity_pool_id
  workload_identity_pool_provider_id = "gitlab-oidc"
  oidc { issuer_uri = "https://gitlab.com" }   # the instance URL on self-managed GitLab
  attribute_mapping = {
    "google.subject"         = "assertion.sub"
    "attribute.project_id"   = "assertion.project_id"
    "attribute.namespace_id" = "assertion.namespace_id"
    "attribute.environment"  = "assertion.environment"
  }
  attribute_condition = "assertion.namespace_id == '${var.gitlab_group_id}'"
}
```

Job side (`expert-gitlab-ci`): `id_tokens: GOOGLE_TOKEN: aud: https://iam.googleapis.com/projects/<number>/locations/global/workloadIdentityPools/gitlab/providers/gitlab-oidc`,
then `gcloud iam workload-identity-pools create-cred-config … --credential-source-file` and
`CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE` or `GOOGLE_APPLICATION_CREDENTIALS` pointing at it.

## Workload Identity Federation for GKE

```hcl
# the Kubernetes service account itself is the principal; no google_service_account needed
resource "google_project_iam_member" "app_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "principal://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${var.project_id}.svc.id.goog/subject/ns/${var.namespace}/sa/${var.ksa}"
}
```

Cluster: `workload_identity_config { workload_pool = "${var.project_id}.svc.id.goog" }`, node pool
`workload_metadata_config { mode = "GKE_METADATA" }` (Autopilot sets both). The pod needs
`serviceAccountName: <ksa>` and nothing else; the linking method (annotation
`iam.gke.io/gcp-service-account` plus `roles/iam.workloadIdentityUser`) stays for APIs that
refuse the principal form.

## Service agents through the provider

```hcl
resource "google_project_service_identity" "gkehub" {
  provider = google-beta
  project  = var.project_id
  service  = "gkehub.googleapis.com"
}

resource "google_project_iam_member" "gkehub_agent" {
  project = var.project_id
  role    = "roles/gkehub.serviceAgent"
  member  = google_project_service_identity.gkehub.member   # universe-correct, created on demand
}
```

| Service | agent token in the email | note |
|---|---|---|
| GKE | `container-engine-robot` | number-based; granted CMEK access on the key |
| GKE Hub / Fleet | `gcp-sa-gkehub` | prefer the resource above |
| Cloud Service Mesh | `gcp-sa-servicemesh` | prefer the resource above |
| Backup for GKE | `gcp-sa-gkebackup` | |
| Compute default SA | `<number>-compute@developer.…` | `developer`, not `gcp-sa-*`; never used by a workload |
| Google APIs agent | `<number>@cloudservices.gserviceaccount.com` | the one agent without `.iam.` in the public universe |
| App Engine | `<project-id>@appspot.…` | project-id based: strip the universe prefix |

Fallback format when a service has no identity resource: `service-<number>@<agent>.<INFIX>iam.gserviceaccount.com`
with `INFIX` empty in the public universe and `<prefix>-system.` in a universe (`universe.md`).
Mark such a string `assumed` in the module's README until an apply proved it.

## Deny and organisation policies worth setting once

| Policy | Where | Why |
|---|---|---|
| `constraints/iam.disableServiceAccountKeyCreation` | organization | rule 1 |
| `constraints/iam.disableServiceAccountKeyUpload` | organization | rule 1 |
| `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` | organization | the default accounts stop being Editor |
| `constraints/compute.requireOsLogin` | organization | SSH through IAM, auditable |
| `constraints/storage.uniformBucketLevelAccess` | organization | conditions work, ACLs cannot leak |
| `constraints/compute.vmExternalIpAccess` | folder `prod` | no public VMs |
| deny `iam.googleapis.com/roles.delete`, `resourcemanager.googleapis.com/projects.delete` outside the platform group | organization | guardrail that no allow can lift |

- [reported 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts] The page names the constraints that disable key creation, key upload and the default accounts' automatic grants and prints only the third ID (`constraints/iam.automaticIamGrantsForDefaultServiceAccounts`); `iam.disableServiceAccountKeyCreation` and `iam.disableServiceAccountKeyUpload` are the catalogue names and stay reported until read there.
- [verified 2026-11-08 · src: https://github.com/google-github-actions/auth] `google-github-actions/auth@v3`: direct Workload Identity Federation is preferred; `workload_identity_provider` is `projects/NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER`; the job needs `id-token: write`; "Always add an Attribute Condition to restrict entry into the Workload Identity Pool".
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines] GitHub claims include `repository`, `repository_id`, `repository_owner`, `repository_owner_id`; GitLab claims include `sub`, `namespace_id`, `project_id`, `user_id`, `environment`, `ref_path`; the `gcp-` prefix is reserved in pool and provider IDs.
