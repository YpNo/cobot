#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A custom integration with the findings the
# consult must name: no manifest version, an exact pin on a package Home Assistant ships,
# config_flow true without config_flow.py, strings.json instead of translations/, hassfest at a
# branch ref, and a tracked secrets.yaml (it holds only an !env_var reference: no secret here).
set -euo pipefail
git init -q -b main .
git config user.email eval@example.invalid
git config user.name eval
git config commit.gpgsign false
mkdir -p custom_components/demo_light .github/workflows
cat > custom_components/demo_light/manifest.json <<'JSON'
{
  "domain": "demo_light",
  "name": "Demo Light",
  "codeowners": ["@example"],
  "documentation": "https://example.invalid/demo_light",
  "issue_tracker": "https://example.invalid/demo_light/issues",
  "iot_class": "local_polling",
  "config_flow": true,
  "requirements": ["aiohttp==3.9.0"]
}
JSON
cat > custom_components/demo_light/__init__.py <<'PY'
"""Demo Light: a custom integration for the eval."""

DOMAIN = "demo_light"
PY
cat > custom_components/demo_light/strings.json <<'JSON'
{"config": {"step": {"user": {"title": "Demo Light"}}}}
JSON
cat > hacs.json <<'JSON'
{"name": "Demo Light"}
JSON
cat > .github/workflows/validate.yaml <<'YAML'
name: Validate
on: [push, pull_request]
permissions:
  contents: read
jobs:
  hassfest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: home-assistant/actions/hassfest@master
YAML
cat > secrets.yaml <<'YAML'
demo_host: !env_var DEMO_HOST
YAML
git add -A
git commit -q -m "chore: demo light"
