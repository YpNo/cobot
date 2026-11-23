#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A trusted repository of the owner's with
# cobot memory and a Terraform root on the google provider. CONTEXT.md has no gcp-mcp line:
# the first Google Cloud consult asks the opt-in once and records the answer (spec
# gcp-mcp-opt-in, story 1, case A; gcp-mcp-never-again is the same with the line present).
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git config commit.gpgsign false
mkdir -p infra .agent
cat > infra/main.tf <<'TF'
terraform {
  required_version = ">= 1.9"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.10"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

variable "project_id" {
  type        = string
  description = "The lab project."
}

resource "google_logging_project_bucket_config" "default" {
  project        = var.project_id
  location       = "global"
  bucket_id      = "_Default"
  retention_days = 30
}
TF
cat > .agent/CONTEXT.md <<'MD'
# lab — context

profile: infra
forge: github
goal: a Google Cloud lab project in Terraform
owner: eval · private · MIT
governance: none
runs: host

## Stack

- Terraform 1.9 · google provider 8.10

## Environment

- no gcloud configuration

## Verified commands

| purpose | command | result | verified |
|---|---|---|---|
| format | `terraform fmt -check -recursive` | exit 0 | 2026-11-22 |

## Constraints

- applies run from a saved plan only

## Shape

- infra/: one root
MD
printf '# Journal\n\n## 2026-11-22 — onboarded\nChanged: memory written.\n' > .agent/JOURNAL.md
printf '# Findings\n\n| id | seen | observation | status |\n|---|---|---|---|\n' > .agent/FINDINGS.md
git add . && git commit -q -m "chore: the lab root and its memory"
# Trust the root commit as onboard-runs-question does: eval Bash cannot write the config directory.
root=$(git rev-list --max-parents=0 HEAD)
for dir in "$HOME/.claude" "$HOME/../config"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir/cobot" && printf '%s %s\n' "$root" "$(basename "$PWD")" >> "$dir/cobot/trusted"
  fi
done
