#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. Mostly Terraform (the infra shape) plus one
# bootstrap script: the sweep must read shell.md for it, not stop at terraform.md (gcp-platform,
# 2026-11-10, where the infra shape hid the shell pack).
set -euo pipefail
mkdir -p modules/bucket live/prod/bucket bin
cat > modules/bucket/main.tf <<'TF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.10"
    }
  }
}

variable "name" {
  type        = string
  description = "Bucket name."
}

resource "google_storage_bucket" "this" {
  name                        = var.name
  location                    = "EU"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_storage_bucket_iam_member" "public" {
  bucket = google_storage_bucket.this.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
TF
cat > live/prod/bucket/terragrunt.hcl <<'HCL'
terraform {
  source = "../../../modules/bucket"
}

inputs = {
  name = "demo-prod-assets"
}
HCL
cat > bin/bootstrap.sh <<'SH'
#!/usr/bin/env bash
# Installs the tools, then creates the state bucket.
curl -fsSL https://sdk.cloud.google.com | bash
read -r -p "bucket: " bucket
eval "gcloud storage buckets create gs://$bucket"
SH
chmod +x bin/bootstrap.sh
printf '# demo platform\n\nTerragrunt live tree and one bootstrap script.\n' > README.md
