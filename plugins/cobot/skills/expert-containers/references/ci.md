# Image workflow — build, scan, sign, attest, publish

Runs on the default branch (merge) and on tags; PRs build without pushing. SHAs dated below.

- [verified 2026-11-07 · src: https://api.github.com/repos/docker/setup-buildx-action/releases/latest] docker/setup-buildx-action v4.4.1 = `f87e5991a6d7451dcb8d9637bfbc97413f497069`
- [verified 2026-11-07 · src: https://api.github.com/repos/docker/setup-qemu-action/releases/latest] docker/setup-qemu-action v4.4.0 = `99012661954931238ded8c8b007157a8430204e1`
- [verified 2026-11-07 · src: https://api.github.com/repos/docker/login-action/releases/latest] docker/login-action v4.8.0 = `8aa5831fb8d48d8f76594c7ddde61ae58019f550`
- [verified 2026-11-07 · src: https://api.github.com/repos/docker/metadata-action/releases/latest] docker/metadata-action v6.2.0 = `dc802804100637a589fabce1cb79ff13a1411302`
- [verified 2026-11-07 · src: https://api.github.com/repos/docker/build-push-action/releases/latest] docker/build-push-action v7.4.0 = `c3c9e263c25d99ce0380d002d59b67737d91b0dc`
- [verified 2026-11-07 · src: https://api.github.com/repos/sigstore/cosign-installer/releases/latest] sigstore/cosign-installer v4.1.3 = `756fe2d284c7292c4e9b62c8a28f1e5629c59532`
- [verified 2026-11-07 · src: https://api.github.com/repos/anchore/sbom-action/git/tags/fffec3d851af758d56fee099cf3fbf8aa8779843] anchore/sbom-action v0.24.3 = `66cbf4bc1f1c0d2edc94016e65bc221b6bb0ad6c`
- [verified 2026-11-07 · src: https://api.github.com/repos/aquasecurity/trivy-action/git/tags/a9c7b0f06e461e9d4b4d1711f154ee024b8d7ab8] aquasecurity/trivy-action v0.36.0 = `ed142fd0673e97e23eac54620cfb913e5ce36c25`
- [verified 2026-11-07 · src: https://api.github.com/repos/actions/attest-build-provenance/releases/latest] actions/attest-build-provenance v4.2.2 = `4d101475d8b20a2381f78447822ac1eab6504dd8`
- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases/tag/v7.0.1] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`

```yaml
name: image
on:
  push:
    branches: [main]
    tags: ["v[0-9]+.[0-9]+.[0-9]+"]
  pull_request:

permissions:
  contents: read

concurrency:
  group: image-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  image:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    environment: ${{ github.event_name != 'pull_request' && 'registry' || '' }}
    permissions:
      contents: read
      packages: write # push to GHCR (login uses GITHUB_TOKEN)
      id-token: write # keyless cosign and the provenance attestation
      attestations: write # actions/attest-build-provenance
    env:
      IMAGE: ghcr.io/${{ github.repository }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: docker/setup-qemu-action@99012661954931238ded8c8b007157a8430204e1 # v4.4.0
        # only when a platform cannot be cross-compiled
      - uses: docker/setup-buildx-action@f87e5991a6d7451dcb8d9637bfbc97413f497069 # v4.4.1
      - uses: docker/login-action@8aa5831fb8d48d8f76594c7ddde61ae58019f550 # v4.8.0
        if: github.event_name != 'pull_request'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ${{ env.IMAGE }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            type=ref,event=branch
      - id: build
        uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc # v7.4.0
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          sbom: true
          provenance: mode=max
          cache-from: type=gha
          cache-to: ${{ github.event_name == 'pull_request' && 'type=gha,mode=max' || '' }} # no cache write from main or tags
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          image-ref: ${{ env.IMAGE }}@${{ steps.build.outputs.digest }}
          exit-code: "1"
          severity: CRITICAL,HIGH
          ignore-unfixed: true
      - uses: sigstore/cosign-installer@756fe2d284c7292c4e9b62c8a28f1e5629c59532 # v4.1.3
        if: github.event_name != 'pull_request'
      - if: github.event_name != 'pull_request'
        env:
          DIGEST: ${{ steps.build.outputs.digest }}
        run: cosign sign --yes "${IMAGE}@${DIGEST}"
      - uses: actions/attest-build-provenance@4d101475d8b20a2381f78447822ac1eab6504dd8 # v4.2.2
        if: github.event_name != 'pull_request'
        with:
          subject-name: ${{ env.IMAGE }}
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
```

Notes

- The `registry` environment holds no secret (GHCR uses `GITHUB_TOKEN`) but gives the owner a
  required reviewer on every publish if wanted; PR builds run outside it.
- Trivy scans the pushed digest; on a PR (no push) scan the local image with `load: true` and
  `trivy image <tag>` instead, or `trivy fs .` on the context.
- Verify from a deploy job: `cosign verify --certificate-identity-regexp '^https://github.com/<org>/<repo>/' --certificate-oidc-issuer https://token.actions.githubusercontent.com "$IMAGE@$DIGEST"`.
- Keep the SHAs current with Dependabot (`package-ecosystem: github-actions`, cooldown 7 days).
