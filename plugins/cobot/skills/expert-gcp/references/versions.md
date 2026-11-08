# expert-gcp — versions and dated facts

Format: `- [status date · src: url] claim`. The brief flags version lines after 30 days, idiom
after 90. Refresh without MCP: `curl -s https://registry.terraform.io/v1/providers/hashicorp/google | jq -r .version`,
`curl -s https://dl.google.com/dl/cloudsdk/channels/rapid/components-2.json | jq -r .version`,
the GKE release notes and the GitHub release APIs. Every `cloud.google.com/…/docs/…` URL
redirects to `docs.cloud.google.com`; Terraform Registry pages render client-side, so provider
facts cite the raw GitHub sources the Registry publishes from.

## Toolchain

| Tool | Current | Released |
|---|---|---|
| hashicorp/google, google-beta | 8.10.0 | 2026-11-03 |
| Google Cloud CLI (gcloud) | 592.0.0 | 2026-11-03 |
| google-github-actions/auth | v3 | 2025-09-03 |
| Cloud Foundation Fabric | v60.0.0 | 2026-11-05 |
| GKE default, Rapid / Regular / Stable | 1.37.1 / 1.36.4 / 1.35.8 | notes to 2026-11-03 |

- [verified 2026-11-08 · src: https://registry.terraform.io/v1/providers/hashicorp/google] hashicorp/google 8.10.0 published 2026-11-03; google-beta 8.10.0 the same day; previous 8.9.0, 8.8.1, 8.8.0, 8.7.0.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/sdk/docs/release-notes] Google Cloud CLI 592.0.0 (2026-11-03), 591.0.0 (2026-10-27), 590.0.1 (2026-10-22): weekly releases.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/sdk/docs/install-sdk] gcloud requires Python 3.10 to 3.15; install from the archive, the apt repository `packages.cloud.google.com/apt cloud-sdk main` (`google-cloud-cli`, `google-cloud-cli-gke-gcloud-auth-plugin`, `kubectl`), dnf or snap; then `gcloud init`.
- [verified 2026-11-08 · src: https://api.github.com/repos/google-github-actions/auth/releases/latest] `google-github-actions/auth` v3 (2025-09-03); pin by full SHA from `expert-gha/references/actions.md`.
- [verified 2026-11-08 · src: https://api.github.com/repos/GoogleCloudPlatform/cloud-foundation-fabric/releases/latest] Cloud Foundation Fabric v60.0.0 (2026-11-05).
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/release-notes] Defaults for new clusters: Rapid 1.37.1-gke.1697000, Regular 1.36.4-gke.2046003, Stable 1.35.8-gke.1439001, Extended 1.36.4-gke.2046003; minors 1.34 to 1.37 on Rapid and Regular, 1.34 to 1.36 on Stable, 1.32 to 1.37 on Extended.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/release-channels] Regular is the default channel; Regular lags Rapid by about two months, Stable lags Regular by three to four; Extended gives up to 24 months per minor; Rapid is outside the SLA; "No channel" is removed on 2027-06-14.

## Provider 8.x

- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/provider_reference.html.markdown] Provider arguments: `universe_domain` ("Specify the GCP universe to deploy in", no default, no stated credential validation), `default_labels`, `add_terraform_attribution_label` (default true, `goog-terraform-provisioned = true`, strategy `CREATION_ONLY` or `PROACTIVE`), `user_project_override` (default false), `billing_project`, `prefer_regional_endpoints`, `request_timeout` (120s), `request_reason`, `impersonate_service_account` and `_delegates`, `external_credentials` (beats `credentials` and `access_token`).
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/provider_reference.html.markdown] Default scopes `cloud-platform` and `userinfo.email`; credentials env precedence `GOOGLE_CREDENTIALS`, `GOOGLE_CLOUD_KEYFILE_JSON`, `GCLOUD_KEYFILE_JSON`; project env precedence `GOOGLE_PROJECT`, `GOOGLE_CLOUD_PROJECT`, `GCLOUD_PROJECT`, `CLOUDSDK_CORE_PROJECT`.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/version_8_upgrade.html.markdown] 8.0 (2026-08-26): `load_balancing_scheme` default `EXTERNAL_MANAGED` on `google_compute_backend_service` and `google_compute_global_forwarding_rule`; `google_container_cluster` `logging_config.enable_components` and `monitoring_config.enable_components` are sets; `name_prefix` on clusters and node pools allows 31 characters; `secret_data_wo_version` is a string and required beside `secret_data_wo`; `guest_accelerator` count 0 forces replacement.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/version_8_upgrade.html.markdown] Removed in 8.0: `google_beyondcorp_app_connection|connector|gateway` (use `google_beyondcorp_security_gateway[_application]`), `google_iap_brand`, `google_iap_client`, `google_ml_engine_model`, `google_notebooks_environment|instance|runtime` (use `google_workbench_instance`), `google_vertex_ai_schedule` (use `google_colab_schedule`).
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google-beta/main/website/docs/r/project_service_identity.html.markdown] `google_project_service_identity` is google-beta only; arguments `service`, `project`; exports `email` and `member`; cannot be updated, destroyed or imported; create timeout 20 minutes.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/r/google_project_iam.html.markdown] `google_project_iam_policy` replaces the whole policy and can lock you out; `_binding` is authoritative per role; `_member` is additive; `_audit_config` is authoritative per service; a `condition` block has `title`, `description`, `expression`.

## IAM

- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/roles-overview] Three role types (basic, predefined, custom); legacy basic roles Owner, Editor, Viewer beside the newer Admin, Writer, Reader; custom roles at organization or project level only, 300 per organization and per project.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/conditions-overview] Conditions are CEL on resource type, name, tags and time; not usable with Owner, Editor, Viewer nor with `allUsers` or `allAuthenticatedUsers`; keep under 100 conditional bindings per policy.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/pam-overview] Privileged Access Manager grants just-in-time elevation through entitlements on projects, folders and organizations; the legacy basic roles are not supported.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/service-agents] Typical service-agent email `service-PROJECT_NUMBER@gcp-sa-SERVICE.iam.gserviceaccount.com`; the Google APIs Service Agent is `PROJECT_NUMBER@cloudservices.gserviceaccount.com`; "both the creation time and the email address format for service agents are subject to change".
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/create-service-agents] Agents can be created early with `gcloud beta services identity create --service=SERVICE.googleapis.com --project=P`.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/workload-identity-federation] One pool per external environment; `google.subject` required (127 characters at most), up to 50 custom attributes; direct resource access recommended, impersonation needs `roles/iam.workloadIdentityUser`; principals carry the project number.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts] Dedicated service account per application; default service accounts avoided (not recreatable once deleted); `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` disables their Editor grant; key creation and upload have their own disable constraints.

## GKE, registry, build, logging, cost

- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity] Pool `PROJECT_ID.svc.id.goog`; principal `principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NAMESPACE/sa/KSA`; namespace form `principalSet://…/namespace/NAMESPACE`; `hostNetwork` pods are excluded.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/how-to/private-clusters] `--enable-private-nodes` needs `--enable-ip-alias`; `--enable-private-endpoint`; `--master-authorized-networks`; `--enable-dns-access`; private nodes reach the internet through Cloud NAT; the DNS-based endpoint is recommended.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster] Shielded nodes and secure boot always on in Autopilot; Container-Optimized OS the default and only Autopilot image; legacy ABAC off by default; PodSecurity admission enforces the standards; Binary Authorization validates images.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/gateway-api] GatewayClasses `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, `gke-l7-rilb`, `gke-l7-gxlb`, `-mc` variants; the single-cluster controller is enabled by default; always on in Autopilot; VPC-native clusters only.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/artifact-registry/docs/overview] Standard, remote (Docker Hub, Maven Central, npm, PyPI, Go, custom HTTPS), connector and virtual repositories; regional; Artifact Analysis; VPC Service Controls.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/artifact-registry/docs/repositories/create-repos] `--immutable-tags` pins Docker tags to one digest (off by default, changeable later); `--kms-key` sets CMEK.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/artifact-registry/docs/docker/authentication] `gcloud auth configure-docker REGION-docker.pkg.dev`, `docker-credential-gcr`, or an access token through `docker login -u oauth2accesstoken --password-stdin` (60 minutes); `_json_key` is the least secure.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/build/docs/build-config-file-schema] `cloudbuild.yaml`: `steps` (name, args, env, dir, id, waitFor, entrypoint, secretEnv, script), `timeout` (default 60 minutes, max 24 hours), `options.logging`, `substitutions`, `serviceAccount`, `availableSecrets.secretManager`, `artifacts`, `images`.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/build/docs/automating-builds/github/connect-repo-github] 2nd-gen GitHub connections are regional; token in Secret Manager; Terraform `google_cloudbuildv2_connection` and `google_cloudbuildv2_repository`.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/logging/quotas] `_Required` retention 400 days, fixed; `_Default` and custom buckets 30 days by default, 1 to 3650; 200 sinks per project; 50 exclusion filters per sink.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/logging/docs/routing/overview] The `_Required` sink cannot be modified; `_Default` can be edited or disabled; destinations: log buckets, BigQuery, Cloud Storage, Pub/Sub, other projects; aggregated sinks at folder or organization level.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/billing/docs/how-to/budgets] A budget alerts at 50, 90 and 100 % by default and never caps spend; scopes by project, folder, service or label; Pub/Sub for automation.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/recommender/docs/recommenders] Cost recommenders: `google.compute.instance.MachineTypeRecommender`, `google.compute.instance.IdleResourceRecommender`, `google.compute.disk.IdleResourceRecommender`, `google.compute.address.IdleResourceRecommender`, `google.cloudsql.instance.IdleRecommender`, `google.container.DiagnosisRecommender`, `google.iam.policy.Recommender`.
- [verified 2026-11-08 · src: https://cloud.google.com/storage/pricing] Standard storage us-central1 $0.000027397 per GiB-hour against multi-region $0.000035616; Nearline, Coldline and Archive have 30, 90 and 365-day minimums.
- [verified 2026-11-08 · src: https://cloud.google.com/kubernetes-engine/pricing] Cluster fee $0.10 per hour with a $74.40 monthly credit per billing account; Autopilot general-purpose Pods $0.0445 per vCPU-hour and $0.0049225 per GiB-hour in us-central1, Spot $0.0133 per vCPU-hour; extended support adds $0.50 per cluster-hour.
