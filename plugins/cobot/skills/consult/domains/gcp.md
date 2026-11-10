# Consult: gcp

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, apply nothing, authenticate to nothing. Read the sibling skill
`skills/expert-gcp/SKILL.md` and its `references/` first: they are the baseline. `gcloud … list`,
`describe`, `get-iam-policy`, `config list` and `auth list` are silent for you when an active
configuration exists; they read the live project and nothing else is silent. Never
`print-access-token`, never `secrets versions access`, never `get-credentials`; never pass an
environment assignment or `--kubeconfig` on a read (the gate would ask, and it would be right).

## Procedure

1. **Inventory.** Terraform roots and modules with a `google` or `google-beta` provider
   (`grep -rln 'provider "google' --include='*.tf'`, `required_providers`), `cloudbuild*.y*ml`,
   workflows and pipelines that authenticate to Google Cloud, scripts calling `gcloud`, any
   `*.json` that looks like a key (`"type": "service_account"`). Nothing → one line and stop.
2. **Keys and identity.** `google_service_account_key`, `gcloud iam service-accounts keys
   create`, key files in the tree or named in CI secrets (`GOOGLE_CREDENTIALS`, `GCP_SA_KEY`),
   `credentials = file(…)` in a provider; federation providers without an `attribute_condition`
   or with a condition on a name instead of a numeric id; `service_account` passed to
   `google-github-actions/auth` where direct federation would do.
3. **Roles.** `roles/owner|editor|viewer` anywhere; `*_iam_binding` or `*_iam_policy` in a
   reusable module; binding and member on the same role; grants to `allUsers` or
   `allAuthenticatedUsers` (buckets, Cloud Run, Pub/Sub); default service accounts used by node
   pools, Cloud Build triggers or functions; missing `roles/iam.serviceAccountUser` scoping.
4. **Universe portability** (`skills/expert-gcp/references/universe.md`): run the audit greps; classify every
   `googleapis.com` hit (endpoint, service name, scope, agent email); a hand-built
   `service-…@…gserviceaccount.com`; project IDs split on `:`; a provider block inside a module.
5. **GKE and workloads.** `workload_identity_config` and `GKE_METADATA` present; pods with a
   `serviceAccountName` bound by principal; `enable_legacy_abac`; public endpoint without
   authorised networks; node pools on the default service account; Autopilot-incompatible
   specs (hand the manifests to the kubernetes domain).
6. **Data and logs.** Buckets without uniform access or with public members; CMEK absent where
   CONTEXT.md names regulated data; `google_project_iam_audit_config` absent on the services
   that hold data (profile `service` or `infra`); `_Default` retention untouched when the
   constraints name one; no `google_billing_budget` in a live root.
7. **Delivery.** `cloudbuild.yaml` without `serviceAccount`, with floating builder images or
   with secrets outside `availableSecrets`; a CI job that both the forge and Cloud Build deploy.
8. **Live project** (only with an active configuration and when the audit is about one):
   `gcloud projects get-iam-policy <p> --format=json`, `gcloud iam service-accounts keys list
   --iam-account=<sa>`, `gcloud services list --enabled`, `gcloud logging sinks list`,
   `gcloud artifacts repositories list`; compare with the tree, report drift.
9. **Rank.** Ten findings at most; merge duplicates across files into one with the locations.

Severity: `critical` = a key in the tree or in CI, a public grant on data, a federation
provider open to every repository; `high` = a basic role, authoritative IAM in a module, a
default service account on a workload, a hand-built agent email that a universe target
breaks; `medium` = missing audit config or budget, floating builder images, provider block in
a module; `low` = labels, retention, hygiene.

Confidence: `high` = seen in the file and confirmed by the live project or the provider docs;
`medium` = seen in the file, impact depends on an organisation policy you cannot read; `low` =
inferred.

## Report

```text
summary: <one line — roots and modules audited, live project read or not, worst severity>

findings:
1. <severity> · <file>:<line> · <what> · fix: <exact change: resource, role, condition, or the universe rule number> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-gcp
{"topic": "gcp", "skill": "expert-gcp", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

No finding without a file and line. Organisation policies, deny policies and billing settings
you cannot read go in the summary as "not verifiable from the tree". Zero findings is a valid
result; say what was checked.
