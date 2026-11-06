# lang-terraform — versions and dated facts

Format: `- [status date · src] claim`. Re-verify lines older than 180 days. Refresh without MCP:
`curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest | jq -r .tag_name`, the
registry API (`/v1/providers/<ns>/<name>`, `/v1/modules/<ns>/<name>/<provider>`) and
`https://releases.hashicorp.com/terraform/index.json`.

## Toolchain

| Tool | Current | Released |
|---|---|---|
| terraform | 1.17.1 | 2026-10-28 |
| opentofu | 1.13.9 | 2026-11-05 |
| hashicorp/google, google-beta | 8.10.0 | 2026-11-03 |
| tflint | 0.65.0 | 2026-10-22 |
| tflint-ruleset-google | 0.41.0 | 2026-10-25 |
| trivy | 0.76.2 | 2026-11-05 |
| terraform-docs | 0.24.0 | 2026-05-10 |

- [verified 2026-11-06 · src: https://releases.hashicorp.com/terraform/index.json] Terraform 1.17.1 is the latest stable; 1.18.0 is unreleased.
- [verified 2026-11-06 · src: https://github.com/opentofu/opentofu/releases] OpenTofu 1.13.9 is the latest release.
- [verified 2026-11-06 · src: https://registry.terraform.io/v1/providers/hashicorp/google] hashicorp/google 8.10.0, published 2026-11-03; google-beta at the same version.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform-provider-google/releases/tag/v8.0.0] google provider 8.0.0 released 2026-08-26.
- [verified 2026-11-06 · src: https://github.com/terraform-linters/tflint/releases] tflint 0.65.0; the `terraform` ruleset is bundled, other plugins install with `tflint --init`.
- [verified 2026-11-06 · src: https://github.com/terraform-linters/tflint-ruleset-google/releases] tflint-ruleset-google 0.41.0.
- [verified 2026-11-06 · src: https://github.com/aquasecurity/trivy/releases] trivy 0.76.2.
- [verified 2026-11-06 · src: https://github.com/aquasecurity/tfsec] tfsec is folded into Trivy; `trivy config` is the IaC scanner.
- [verified 2026-11-06 · src: https://github.com/terraform-docs/terraform-docs/releases] terraform-docs 0.24.0 (2026-05-10); last commit 2026-08-01, maintained but slow.

## Supply chain

- [verified 2026-11-06 · src: https://github.com/advisories/GHSA-69fq-xp46-6x23] CVE-2026-33634 (critical): on 2026-03-19 a malicious trivy v0.69.4 was published and most `trivy-action` and all `setup-trivy` tags were force-pushed to credential-stealing commits; malicious Docker Hub images v0.69.5/v0.69.6 followed on 2026-03-22. Pin actions by full SHA, binaries by version and checksum.
- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`.

## Terraform language, by version (what a `required_version` floor buys)

- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.7.0] 1.7: `mock_provider`/`override_*` in tests, `removed` blocks, `import` with `for_each`.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.9.0] 1.9: variable `validation` may reference other objects in the module.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.10.0] 1.10: ephemeral resources and ephemeral variables/outputs.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.11.0] 1.11: write-only resource attributes (not persisted to state); google exposes them as `*_wo` + `*_wo_version`.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.14.0] 1.14: `terraform query` with `*.tfquery.hcl` list resources; `action` blocks.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.15.0] 1.15: `deprecated` on variables and outputs; typed `output` blocks; variables/locals in module `source`/`version`; `validate` checks the `backend` block.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.16.0] 1.16: `import` blocks inside modules; `terraform_data` `store` block for ephemeral/sensitive values across plan and apply.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.17.0] 1.17: variables and locals in provider requirements; `-minimal-refresh`; Terraform Policy (`-policies`) GA; `mock_provider` covers ephemeral resources.
- [verified 2026-11-06 · src: https://github.com/opentofu/opentofu/releases/tag/v1.7.0] OpenTofu has had client-side state encryption since 1.7; Terraform has none.

## Google Cloud

- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform-provider-google/blob/main/website/docs/guides/version_8_upgrade.html.markdown] 8.0 upgrade path: latest 7.x first, clean plan, then `~> 8.0`. `load_balancing_scheme` default is now `EXTERNAL_MANAGED` on `google_compute_backend_service` and `google_compute_global_forwarding_rule`; set `EXTERNAL` explicitly to keep a classic LB. BeyondCorp app connector/connection/gateway and `google_iap_client` removed.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform-provider-google/blob/main/website/docs/guides/provider_reference.html.markdown] provider arguments `universe_domain`, `default_labels`, `add_terraform_attribution_label`, `prefer_regional_endpoints`, `prefer_global_endpoints` exist.
- [verified 2026-11-06 · src: https://developer.hashicorp.com/terraform/language/backend/gcs] GCS backend supports state locking; object versioning is highly recommended; `kms_encryption_key` or `encryption_key` (CSEK) encrypt state.
- [verified 2026-11-06 · src: https://registry.terraform.io/v1/modules/terraform-google-modules/network/google] terraform-google-modules/network/google 18.3.1 (example of the module endpoint).
