---
name: lang-terraform
description: >-
  Senior Terraform/OpenTofu developer for small modules and live environments, Google Cloud first.
  Loads on **/*.tf, **/*.tfvars, **/*.tftest.hcl, **/.terraform.lock.hcl, **/*.hcl and inside
  builders on infrastructure code. Picks the binary, runs the verified chain (fmt, validate,
  tflint, trivy config, test), pins providers and the lock file, writes idiomatic variables,
  outputs, moved and import blocks and .tftest.hcl mocks, keeps state safe. Plans are proposed,
  never applied: the gate denies apply and destroy. Versions in references/versions.md. A google
  provider hands off to expert-gcp.
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/*.tftest.hcl"
  - "**/.terraform.lock.hcl"
  - "**/*.hcl"
user-invocable: false
---

# lang-terraform

Versions, sources and dates: `references/versions.md`. Test example and mock patterns:
`references/testing.md`. Quote the status (`verified <date>` or `reported`) when a version drives a
decision; re-check any line the brief flags stale (versions after 30 days, idiom after 90) before relying on it.

## Toolchain and commands

**Binary.** `.opentofu-version`, `*.tofu` files, `tofu` in CI or the Makefile, or a lock file whose
provider sources read `registry.opentofu.org/...` → `tofu`. Otherwise `terraform`. Never mix the two
on one state. Below, `tf` means whichever was detected; record it in `.agent/CONTEXT.md`.

| Step | Command | Note |
|---|---|---|
| format | `tf fmt -check -diff -recursive` | fix with `tf fmt -recursive` |
| validate | `tf init -backend=false -input=false && tf validate` | no credentials, no state touched |
| lint | `tflint --init && tflint --recursive --format compact` | `terraform` ruleset is bundled; add `google` in `.tflint.hcl` |
| scan | `trivy config --severity HIGH,CRITICAL --exit-code 1 .` | successor of tfsec |
| test | `tf test` (`-filter=tests/x.tftest.hcl` for one file) | mocks need no cloud |
| plan | `tf plan -out=tfplan -input=false` | the owner reviews and applies |
| lock | `tf providers lock -platform=linux_amd64 -platform=darwin_arm64` | every platform that runs `init` |
| docs | `terraform-docs markdown table --output-file README.md --output-mode inject .` | between `<!-- BEGIN_TF_DOCS -->` markers |

Use `-chdir=<dir>` rather than `cd`: the rules gate matches it. Latest versions, without MCP:

```sh
curl -s https://registry.terraform.io/v1/providers/hashicorp/google | jq -r .version
curl -s https://registry.terraform.io/v1/modules/terraform-google-modules/network/google | jq -r .version
curl -s https://releases.hashicorp.com/terraform/index.json | jq -r '.versions|keys[]' | sort -V | tail -1
```

Pin `trivy` and `tflint` by version and checksum in CI; trivy's own release path was compromised in
March 2026 (see `references/versions.md`).

## Idiom

**Layout, module** (`modules/<name>/` or repo root): `versions.tf` (terraform + required_providers,
no provider block), `variables.tf`, `main.tf` (split by concern once it passes ~200 lines),
`outputs.tf`, `tests/*.tftest.hcl`, `README.md` with injected docs, `examples/basic/`.
**Layout, live:** one root per environment and blast radius (`envs/prod/network/`), each with its
own backend, `providers.tf`, `terraform.tfvars` (non-secret only) and committed lock file. No
workspaces as the environment boundary for anything prod: one typo applies to the wrong one.

- **Variables:** always `type` and `description`; `object({...})` with `optional(attr, default)`
  over loose maps; `validation` blocks for formats and ranges (they may reference other variables);
  `nullable = false` when null has no meaning; `sensitive = true` on anything secret;
  `deprecated = "..."` to retire an input without breaking callers.
- **Outputs:** `description` always; explicit `type` when the shape is a contract; output IDs and
  self-links a caller will need; never output a whole resource object.
- **Locals:** for names and derived values used twice or more; not to rename a variable.
- **Refactors:** `moved {}` for every address change, `removed { lifecycle { destroy = false } }`
  to drop from state without destroying, `import {}` blocks (with `for_each` when bulk) instead of
  the `import` CLI. Keep `moved` blocks in modules others consume; prune them in live roots after
  every state has applied them.
- **Versions:** `required_version = "~> 1.17"` (or `>= 1.x` in shared modules), providers
  `version = "~> 8.10"`: minor floats, major is a decision. Registry modules pinned exactly. Commit
  `.terraform.lock.hcl` in roots; in a reusable module the caller's lock wins, ignore it there.
- **Conditionals:** `for_each` over a map or set with stable keys; `count = var.enabled ? 1 : 0`
  only for a true on/off singleton. Never `count` over a list whose order can change.
- **Naming:** `snake_case`; resource name describes the role (`google_storage_bucket.state`),
  never repeats the type; `this` only for the single main resource of a small module; plural for
  `for_each` collections.
- **Secrets:** write-only arguments (`*_wo` + `*_wo_version`) fed from ephemeral resources or
  ephemeral variables keep secrets out of state. Prefer them over `sensitive` where the provider
  offers them.

## State and safety

- The cobot gate denies `terraform|tofu apply` and `destroy`. Propose the plan, summarise it
  (adds, changes, replaces, deletes), and stop. Treat `state rm|mv|push`, `force-unlock` and
  `import` from the CLI as owner actions too: say what to run and why.
- Remote state with locking for anything shared or prod: GCS backend locks natively; enable object
  versioning on the bucket, restrict IAM on it like a production secret; `kms_encryption_key` when
  required. OpenTofu also offers client-side state encryption.
- State holds every attribute in plaintext, `sensitive` included. Never `cat` state, never print
  `tf output -json` or `tf show -json` in a transcript; read a single non-sensitive output with
  `tf output -raw <name>`.
- `lifecycle { prevent_destroy = true }` on databases, buckets with data, KMS keys, anything
  unrecoverable. A planned replace (`-/+`) on such a resource stops the work: find the forcing
  argument (`# forces replacement`) before anything else.
- No secret in a committed `.tfvars`, a variable default or a local. `.gitignore`: `.terraform/`,
  `*.tfstate*`, `tfplan`, `*.auto.tfvars` holding secrets, `crash.log`.

## Tests

`tests/<unit>_<scenario>.tftest.hcl`, `run "<unit>_<scenario>_<expected>"` blocks. Default to
`command = plan` with `mock_provider` (no credentials, seconds per run). Assert on what a caller
relies on: derived names, labels, IAM members, conditional resource counts, output shapes, and
every `validation` block through `expect_failures = [var.x]`. Do not assert on what the provider
computes. `command = apply` under `mock_provider` is free; against a real provider only in a sandbox
project and only when the owner asks. Example and override patterns: `references/testing.md`.

## Google Cloud

- Provider `hashicorp/google` 8.x is current (8.0.0 shipped 2026-08-26); `google-beta` follows the
  same version. Upgrade 7 → 8 through the latest 7.x first, then read the upgrade guide: several
  defaults changed silently (`load_balancing_scheme` → `EXTERNAL_MANAGED` on backend services and
  global forwarding rules).
- Provider-level `default_labels`, `add_terraform_attribution_label`, `user_project_override` +
  `billing_project` for quota-project APIs. Use `google_project_service` with
  `disable_on_destroy = false` in live roots.
- IAM: `_member` resources (additive) in modules; `_binding` and `_policy` are authoritative and
  will remove grants made elsewhere. Never mix authoritative and additive on the same role.
- `universe_domain` on the provider selects a non-public universe (sovereign clouds such as S3NS,
  Google Cloud Dedicated). It matters as soon as one hardcoded `googleapis.com` endpoint or
  service-agent email exists; hand off to the `gcd-universe` skill (later `expert-gcp`).

## Pitfalls

1. `for_each` keys known only after apply → "Invalid for_each argument"; key on inputs, not IDs.
2. Lock file generated on one OS → `init` fails in CI on another; run `providers lock` per platform.
3. `count` toggled to `for_each` without `moved` blocks → destroy and recreate.
4. `depends_on` on a module or data source → every read deferred to apply, permanent diff noise.
5. Provider block inside a reusable module → module cannot be removed or used with `for_each`.
6. `ignore_changes = all` hides drift you needed to see; list the attributes.
7. `-target` as a routine → state and config diverge; acceptable only to break a cycle, once.
8. `sensitive = true` treated as protection; it only redacts the console. State still has it.
9. Terraform-only features (`terraform query`, actions, policies, `import` in modules) in a repo
   driven by `tofu`, or the reverse with OpenTofu-only encryption; `validate` with the right binary.
10. `google_project_iam_policy` in a live root → locks everyone out, including the owner.

## Do not

- Run `apply`, `destroy` or state surgery; propose and let the owner act.
- Write a version constraint from memory: curl the registry or read `references/versions.md`.
- Print state, plan JSON or sensitive outputs into the conversation or a log.
- Commit `*.tfstate`, `tfplan`, `.terraform/` or a secret `.tfvars`.
- Use workspaces as the prod/non-prod boundary, or `ref=main` as a module version.
- Pin CI tools by moving tag (`trivy-action@master`, `setup-tflint@latest`); full SHA only.
