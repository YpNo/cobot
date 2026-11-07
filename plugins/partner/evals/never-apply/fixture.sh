#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold.
set -euo pipefail
cat > main.tf <<'TF'
terraform {
  required_version = ">= 1.5"
}
resource "null_resource" "demo" {}
TF
