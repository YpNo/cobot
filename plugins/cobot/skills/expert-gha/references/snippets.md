# Snippets

SHAs from `actions.md` (2026-11-06). Replace `make …` with the project's verified commands.

## ci.yml — push to main and PRs

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version-file: go.mod
      - run: make lint test
  zizmor:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      security-events: write   # SARIF upload; drop with advanced-security: false
      actions: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: zizmorcore/zizmor-action@45d7276c9ca790aabd705e31ca99c6185c3e76dd # v0.8.1
```

## release.yml — tag, changelog gate, attestation, gh release

```yaml
name: Release
on:
  push:
    tags: ["v[0-9]+.[0-9]+.[0-9]+*"]
permissions: {}
concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - name: Changelog gate
        env:
          TAG: ${{ github.ref_name }}
        run: |
          v="${TAG#v}"
          awk -v v="$v" 'index($0, "## [" v "]") == 1 {f=1; next} /^## \[/ {f=0} f' CHANGELOG.md > release-notes.md
          test -s release-notes.md || { echo "::error::no CHANGELOG.md section for $v"; exit 1; }
      - run: make dist          # no cache restore in release builds
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: dist
          path: |
            dist/
            release-notes.md
          if-no-files-found: error
  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment: release      # required reviewers live here
    permissions:
      contents: write
      id-token: write
      attestations: write
    steps:
      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: dist
      - uses: actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6 # v4.2.2
        with:
          subject-path: dist/*
      - name: Publish
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          TAG: ${{ github.ref_name }}
        run: |
          pre=(); [[ "$TAG" == *-* ]] && pre=(--prerelease --latest=false)
          gh release create "$TAG" --verify-tag --draft --title "$TAG" \
            --notes-file release-notes.md "${pre[@]}" dist/*
          gh release edit "$TAG" --draft=false
```

Consumer check: `gh attestation verify <file> -R <owner>/<repo>`.

## OIDC to Google Cloud (Direct Workload Identity Federation)

```yaml
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093 # v3.0.0
        with:
          project_id: my-project
          workload_identity_provider: projects/123456789/locations/global/workloadIdentityPools/github/providers/my-repo
```

Pool side: map `attribute.repository` and `attribute.ref`, set
`--attribute-condition="assertion.repository == 'owner/repo' && assertion.ref == 'refs/heads/main'"`,
grant IAM to `principalSet://…/attribute.repository/owner/repo`, never to the whole pool.

## Composite action — `.github/actions/<name>/action.yml`

```yaml
name: setup-toolchain
description: Install pinned tools
inputs:
  version:
    required: true
runs:
  using: composite
  steps:
    - shell: bash
      env:
        VERSION: ${{ inputs.version }}
      run: ./scripts/install-tools.sh "$VERSION"
```

## .github/dependabot.yml

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
    groups:
      actions:
        patterns: ["*"]
```

Renovate equivalent: extend `helpers:pinGitHubActionDigestsToSemver`.

- [verified 2026-11-06 · src: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations] attestation needs `id-token: write`, `attestations: write`, `contents: read` (+ `packages: write` for images); verify with `gh attestation verify`.
- [verified 2026-11-06 · src: https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases] immutable releases: create as draft, attach assets, then publish; tag and assets then locked, a release attestation is generated.
- [verified 2026-11-06 · src: https://cli.github.com/manual/gh_release_create] `--verify-tag` aborts if the tag is not on the remote; `--latest=false`, `--prerelease`, `--draft`, `--notes-file`, `--generate-notes`, `--fail-on-no-commits` exist.
- [verified 2026-11-06 · src: https://github.com/google-github-actions/auth] Direct WIF is preferred; service-account impersonation only when access/ID tokens are needed; always set an attribute condition; claims must be mapped before use in a condition.
- [verified 2026-11-06 · src: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference] github-actions uses `directory: /` (scans `.github/workflows` and root `action.yml`); `cooldown.default-days` supported (semver-*-days not for actions); default cooldown 3 days.
- [reported 2026-11-07 · src: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference (page lists groups options with no github-actions exclusion; no official github-actions groups example found; a community example at git.cynarski.dev/Awesome/awesome-copilot shows github-actions with patterns ["*"))] Dependabot `groups` with `patterns` applies to github-actions — section not read in full.
- [verified 2026-11-06 · src: https://docs.renovatebot.com/presets-helpers/] `helpers:pinGitHubActionDigestsToSemver` pins digests and keeps SemVer comments.
- [verified 2026-11-06 · src: https://github.com/actions/download-artifact/releases/tag/v8.0.0] download-artifact v8 fails on digest mismatch by default (`digest-mismatch`); upload-artifact v7 adds `archive: false` for single unzipped files.
