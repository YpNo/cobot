# Containers — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale expert-containers`).

## Engines and tools

- [verified 2026-11-07 · src: https://api.github.com/repos/moby/moby/releases/latest] Docker Engine 29.9.3 (2026-11-03).
- [verified 2026-11-07 · src: https://api.github.com/repos/moby/buildkit/releases/latest] BuildKit v0.34.2 (2026-11-03).
- [verified 2026-11-07 · src: https://api.github.com/repos/docker/compose/releases/latest] Docker Compose v5.7.0 (2026-11-02); the v2 line is history.
- [verified 2026-11-07 · src: https://api.github.com/repos/containers/podman/releases/latest] Podman v6.1.4 (2026-10-12); buildah v1.46.0 (2026-10-21).
- [verified 2026-11-07 · src: https://api.github.com/repos/aquasecurity/trivy/releases/latest] Trivy v0.76.2 (2026-11-05); `trivy image` documents `--exit-code`, `--severity` and `--ignore-unfixed`.
- [verified 2026-11-07 · src: https://api.github.com/repos/anchore/grype/releases/latest] grype v0.121.2 (2026-11-05); syft v1.57.0 (2026-11-05, `syft <image> -o spdx-json=./spdx.json`).
- [verified 2026-11-07 · src: https://api.github.com/repos/hadolint/hadolint/releases/latest] hadolint v2.15.1 (2026-07-31).
- [verified 2026-11-07 · src: https://api.github.com/repos/goodwithtech/dockle/commits?per_page=1] dockle's last release is v0.4.15 (2025-01-06), last commit 2026-07-02: low activity, not abandoned.
- [verified 2026-11-07 · src: https://api.github.com/repos/sigstore/cosign/releases/latest] cosign v3.1.4 (2026-10-20).

## Dockerfile frontend

- [verified 2026-11-07 · src: https://hub.docker.com/v2/repositories/docker/dockerfile/tags] Newest stable `docker/dockerfile` frontend is 1.28.0 (2026-10-07); the `1` and `latest` tags still point at 1.27.1.
- [verified 2026-11-07 · src: https://docs.docker.com/reference/dockerfile/] `# syntax=docker/dockerfile:1` is the recommended directive; `COPY --link` needs syntax 1.4, `COPY --chmod` and `RUN --mount` (cache, secret) need 1.2; `RUN <<EOF` heredocs and `FROM --platform` are documented.
- [verified 2026-11-07 · src: https://docs.docker.com/build/checks/] Build checks (`docker build --check`, shorthand for `--call=check`) need frontend 1.8+ and Buildx 0.15.0+.
- [verified 2026-11-07 · src: https://docs.docker.com/build/building/multi-platform/] `docker buildx build --platform linux/amd64,linux/arm64` and the `FROM --platform=$BUILDPLATFORM … AS build` cross-compilation pattern are documented.
- [verified 2026-11-07 · src: https://docs.docker.com/build/metadata/attestations/] `--sbom=true` opts in to SBOM attestations; provenance defaults to `mode=min`, `--provenance=mode=max` opts in.

## Base images

- [verified 2026-11-07 · src: https://raw.githubusercontent.com/GoogleContainerTools/distroless/main/README.md] Distroless images are based on Debian 13: `static-debian13`, `base-debian13`, `cc-debian13`, … with tags `latest`, `nonroot`, `debug`, `debug-nonroot`; the unsuffixed name selects `-debian13`.
- [verified 2026-11-07 · src: https://gcr.io/v2/distroless/static-debian12/manifests/latest] `static-debian12:latest` still resolves (5 platforms); `static-debian13:latest` resolves with 6 platforms including riscv64.
- [verified 2026-11-07 · src: https://images.chainguard.dev/directory/image/static/overview] `cgr.dev/chainguard/static` and `cgr.dev/chainguard/wolfi-base` are listed as free starter images; only `latest` is implied free.
- [verified 2026-11-07 · src: https://www.debian.org/releases/] Debian stable is 13 "trixie", oldstable 12 "bookworm"; `trixie-slim`, `bookworm-slim`, `13-slim` (13.7), `12-slim` (12.15) and `stable-slim` exist on Docker Hub.
- [verified 2026-11-07 · src: https://alpinelinux.org/releases/] Alpine 3.24.4 (branch v3.24, 2026-06-09) is `alpine:latest`.

## Signing and attestation

- [verified 2026-11-07 · src: https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_sign.md] `cosign sign --yes` skips the prompts; the README says to sign images by digest (`@sha256:…`).
- [verified 2026-11-07 · src: https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_verify.md] `cosign verify --certificate-identity-regexp` and `--certificate-oidc-issuer` are documented.
- [verified 2026-11-07 · src: https://raw.githubusercontent.com/actions/attest/main/README.md] `actions/attest-build-provenance` v4 wraps `actions/attest`; the container example uses `subject-name` (no tag), `subject-digest` (`sha256:hex`), `push-to-registry: true` with `id-token: write`, `attestations: write`, `packages: write`, `contents: read`, `artifact-metadata: write`.
- [verified 2026-11-07 · src: https://docs.github.com/en/actions/publishing-packages/publishing-docker-images] The GHCR example uses `packages: write` (plus `contents: read`, `attestations: write`, `id-token: write`) and `docker/login-action` with `password: ${{ secrets.GITHUB_TOKEN }}`.
- [verified 2026-11-07 · src: https://raw.githubusercontent.com/docker/metadata-action/master/README.md] `type=semver,pattern={{version}}` (v1.2.3 → 1.2.3) and `type=sha` (prefix `sha-`, 7 chars) are documented.
- [verified 2026-11-07 · src: https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/] `docker buildx imagetools inspect` shows manifest, digest, platforms and, with `--format`, provenance and SBOM.

## Podman and Compose

- [verified 2026-11-07 · src: https://docs.podman.io/en/latest/markdown/podman-run.1.html] `--userns=keep-id` maps the current user's UID:GID to the same values in the container.
- [verified 2026-11-07 · src: https://github.com/containers/podman/releases/tag/v4.4.0] Quadlet arrived in Podman 4.4.0; `.container` units are documented in `podman-systemd.unit(5)`; `podman generate systemd` is deprecated in favour of Quadlet.
- [verified 2026-11-07 · src: https://docs.podman.io/en/latest/markdown/podman-compose.1.html] `podman compose` is a thin wrapper around an external provider (docker-compose first, then podman-compose).
- [verified 2026-11-07 · src: https://docs.docker.com/reference/compose-file/version-and-name/] The top-level `version` key is obsolete and only warns; Compose validates with the latest schema.
- [verified 2026-11-07 · src: https://docs.docker.com/reference/compose-file/services/] `depends_on` long syntax supports `condition: service_started | service_healthy | service_completed_successfully`; `develop.watch` supports sync, rebuild and sync+restart (Compose 2.23.0+).
