#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. More than SWEEP_SMALL_FILES (200) Terraform
# files, one shell script and one world-readable bucket, so the sweep splits into units and the
# checking pass has a MEDIUM-or-worse finding to check (spec security-auditor, story 3).
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
mkdir -p modules/bucket bin
for n in $(seq 1 210); do
  mkdir -p "live/env$n"
  printf 'module "bucket" {\n  source = "../../modules/bucket"\n  name   = "demo-env%s"\n}\n' "$n" > "live/env$n/main.tf"
done
cat > modules/bucket/main.tf <<'TF'
variable "name" {
  type        = string
  description = "Bucket name."
}

resource "google_storage_bucket" "this" {
  name                        = var.name
  location                    = "EU"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "public" {
  bucket = google_storage_bucket.this.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
TF
cat > bin/bootstrap.sh <<'SH'
#!/usr/bin/env bash
# Creates the state bucket.
read -r -p "bucket: " bucket
eval "gcloud storage buckets create gs://$bucket"
SH
chmod +x bin/bootstrap.sh
printf '# demo platform\n\nOne bucket module, many environments.\n' > README.md
git add . && git commit -q -m "init"
