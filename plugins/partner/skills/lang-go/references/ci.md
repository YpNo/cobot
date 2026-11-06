# Go — minimal CI job

One job: tidy check, lint, race tests with the 85 % coverage gate, govulncheck.

- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases/tag/v7.0.1] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`
- [verified 2026-11-06 · src: https://github.com/actions/setup-go/releases/tag/v7.0.0] actions/setup-go v7.0.0 = `b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` (module cache on by default)
- [verified 2026-11-06 · src: https://github.com/golangci/golangci-lint-action/releases/tag/v9.3.0] golangci/golangci-lint-action v9.3.0 = `ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a` (needs setup-go first; `contents: read`)
- [verified 2026-11-06 · src: https://github.com/actions/runner-images] `ubuntu-24.04` = `ubuntu-latest`.

SHAs resolved with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (annotated tags dereferenced).

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  go:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version-file: go.mod
          cache-dependency-path: go.sum
      - run: go mod tidy -diff
      - uses: golangci/golangci-lint-action@ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a # v9.3.0
        with:
          version: v2.15.0
      - name: Test with coverage gate
        run: |
          go test ./... -race -count=1 -covermode=atomic -coverprofile=cover.out
          total=$(go tool cover -func=cover.out | awk '/^total:/ {sub("%","",$3); print $3}')
          echo "coverage: ${total}%"
          awk -v t="$total" 'BEGIN { exit (t + 0 < 85) }'
      - run: go run golang.org/x/vuln/cmd/govulncheck@v1.9.0 ./...
```

Notes

- Pin the golangci-lint patch (`v2.15.0`), not `latest`: a new linter release breaks CI otherwise.
- If the repo tracks govulncheck via a `tool` directive, use `go tool govulncheck ./...` instead.
- Integration tests behind `//go:build integration` need a second step `go test -tags integration ./...`
  with the services they require.
- Keep SHAs current with Dependabot (`package-ecosystem: github-actions` and `gomod`).
