#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. One workflow with a floating tag.
set -euo pipefail
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YML'
name: CI
on:
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - run: echo ok
YML
