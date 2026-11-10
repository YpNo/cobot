#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. Two domains to detect: a workflow on a
# floating tag (gha) and an image on a moving tag running as root (containers).
set -euo pipefail
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YML'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 -m unittest
YML
cat > Dockerfile <<'DOCKER'
FROM python:latest
COPY . /app
CMD ["python3", "-m", "http.server"]
DOCKER
