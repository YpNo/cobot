#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A GKE module with the four findings the
# consult must name: a provider block inside the module, roles/owner, a service-account key and
# a hand-built service-agent email.
set -euo pipefail
mkdir -p modules/gke
cat > modules/gke/variables.tf <<'TF'
variable "project_id" {
  type        = string
  description = "Project that hosts the cluster."
}

variable "project_number" {
  type        = string
  description = "Numeric project id, used for the service agent email."
}

variable "region" {
  type        = string
  description = "Cluster region."
  default     = "europe-west1"
}
TF
cat > modules/gke/main.tf <<'TF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.10"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  gke_agent = "service-${var.project_number}@container-engine-robot.iam.gserviceaccount.com"
}

resource "google_service_account" "deployer" {
  account_id   = "gke-deployer"
  display_name = "GKE deployer"
}

resource "google_service_account_key" "deployer" {
  service_account_id = google_service_account.deployer.name
}

resource "google_project_iam_member" "deployer_owner" {
  project = var.project_id
  role    = "roles/owner"
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_kms_crypto_key_iam_member" "gke_agent" {
  crypto_key_id = "projects/${var.project_id}/locations/${var.region}/keyRings/gke/cryptoKeys/disks"
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${local.gke_agent}"
}

resource "google_container_cluster" "main" {
  name                = "main"
  location            = var.region
  enable_autopilot    = true
  deletion_protection = true
}
TF
printf '# gke module\n\nAutopilot cluster with a deployer identity.\n' > modules/gke/README.md
