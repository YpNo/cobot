# lang-terraform — tests

- [verified 2026-11-06 · src: https://developer.hashicorp.com/terraform/language/tests/mocking] `mock_provider "<name>" { mock_resource "<type>" { defaults = {...} } }`; shared mocks live in `*.tfmock.hcl` and load with `source = "./dir"`; `override_resource`, `override_data`, `override_module` (with `target`, `values` or `outputs`) go at file root or inside a `run`; `override_during = plan|apply`.
- [verified 2026-11-06 · src: https://github.com/hashicorp/terraform/releases/tag/v1.7.0] mocked providers let `command = apply` run without credentials.

## Example (`tests/bucket_naming.tftest.hcl`)

- [verified 2026-11-06 · exp: `terraform test` on 1.16.2 against a one-bucket module, 2 passed] both runs below.

```hcl
mock_provider "google" {}
run "bucket_name_default_suffixedWithProject" {
  command = plan
  variables { name = "logs" }
  assert {
    condition     = google_storage_bucket.this.name == "logs-p-test"
    error_message = "bucket name must be <name>-<project>"
  }
}
```

Validation, same file: `run "bucket_name_uppercase_rejected" { command = plan; variables { name = "UP" }; expect_failures = [var.name] }`
(one attribute per line in real HCL; `terraform fmt` aligns them).

## Patterns

- Computed values a later run needs (IDs, self-links): `override_resource` with `values`, not a
  real apply.
- Module under test from a fixture root: `module { source = "./tests/fixtures/basic" }` in the run.
- One file per unit; runs share state in order within a file, so keep them independent unless the
  chaining is the point.
