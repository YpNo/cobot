---
name: expert-containers
description: >-
  Container images and release engineering: Dockerfile and Containerfile idiom (BuildKit frontend,
  multi-stage, distroless and Chainguard bases, cache and secret mounts, multi-platform), compose,
  rootless Podman and Quadlet, SBOM and provenance, keyless cosign, Trivy gates, GHCR publishing
  with pinned actions. Loads on **/Dockerfile*, **/Containerfile*, **/*.dockerfile,
  **/compose*.y*ml, **/docker-compose*.y*ml, **/.dockerignore, **/*.container; what /cobot:ship
  follows for the image workflow. Versions and SHAs in references/versions.md, workflow in
  references/ci.md; audit: /cobot:consult containers.
paths:
  - "**/Dockerfile*"
  - "**/Containerfile*"
  - "**/*.dockerfile"
  - "**/compose*.y*ml"
  - "**/docker-compose*.y*ml"
  - "**/.dockerignore"
  - "**/*.container"
user-invocable: false
---

# expert-containers

Versions, dates and sources: `references/versions.md`. Re-verify a line the brief flags stale
(versions after 30 days, idiom after 90). Images are release engineering: the gate asks before
`push`, `login`, `prune`, `rm`, `rmi`; builds, `compose config`, scans and reads are silent.

- [verified 2026-11-07 · src: https://api.github.com/repos/moby/moby/releases/latest] Docker Engine 29.9.3, BuildKit v0.34.2, Compose v5.7.0, Podman v6.1.4 are current.

## Non-negotiables

1. `# syntax=docker/dockerfile:1` on line one; BuildKit features need it and `docker build
   --check` (frontend 1.8+, Buildx 0.15+) lints against the current rules.
2. Multi-stage: a build stage with the toolchain, a final stage with the artifact only. Final
   base from smallest to largest: `scratch` (static binaries), `gcr.io/distroless/static-debian13`
   or `cgr.dev/chainguard/static` (static plus certificates and tzdata), `distroless/base` or
   `cc` (dynamic), `debian:13-slim` or `alpine:3.24` when a shell or a package manager is truly
   needed. Never a full distro image in production.
3. Pin bases by digest (`image@sha256:…`) with the tag in a comment; Dependabot or Renovate move
   the digest.
4. Non-root: `USER 65532:65532` (distroless `nonroot`) or an explicit `adduser`; read-only root
   filesystem and `--cap-drop=ALL` at run time; no `sudo` in the image.
5. No secrets in layers or `ARG`s: `RUN --mount=type=secret,id=token` for build-time credentials;
   `.dockerignore` excludes `.git`, `.env*`, keys, `node_modules`, `target`.
6. Deterministic layers: `COPY` lockfiles first, install with the lockfile, then the sources;
   `RUN --mount=type=cache,target=<pkg cache>` for package managers; `COPY --link --chmod=` for
   artifacts; one process per container, `ENTRYPOINT` in exec form, a `HEALTHCHECK` that checks
   the real dependency.
7. Every published image carries an SBOM and provenance (`--sbom=true --provenance=mode=max`)
   and is signed keyless on its digest (`cosign sign --yes <image>@<digest>`); a scan gates the
   publish (`trivy image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed`).

## Dockerfile shapes

```dockerfile
# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM golang:1.27 AS build      # cross-compile from the build platform
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
ARG TARGETOS TARGETARCH
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian13:nonroot            # pin @sha256 in the real file
COPY --link --from=build /out/app /app
USER 65532:65532
ENTRYPOINT ["/app"]
```

- Node: build with `node:26-slim`, `pnpm fetch` then `pnpm install --frozen-lockfile --offline`
  under a cache mount, prune dev dependencies, final `gcr.io/distroless/nodejs26-debian13` or
  `node:26-slim` as non-root. Python: `uv sync --locked --no-dev` into a venv in the build stage,
  copy the venv to `python:3.14-slim` and set `PATH`; never `pip install` in the final stage.
- Heredocs (`RUN <<EOF … EOF`) for multi-line scripts with `set -eux`; one `RUN` per logical step.
- Multi-platform: `docker buildx build --platform linux/amd64,linux/arm64`; QEMU only for
  languages that cannot cross-compile.

## Compose

- No `version:` key (obsolete, warned); `name:` at the top; `docker compose config` validates.
- `depends_on` with `condition: service_healthy` and a healthcheck on the dependency; named
  volumes for state; `env_file` for local secrets kept out of git; `develop.watch` for dev loops;
  one compose file per environment with `-f` overrides, not `if`s in one file.
- Production runs images by digest, never `build:`; resource limits set; `restart: unless-stopped`.

## Podman

- Rootless by default; `podman run --userns=keep-id` when files are shared with the host;
  `podman compose` wraps docker-compose or podman-compose.
- Services as Quadlet units (`~/.config/containers/systemd/app.container`, since Podman 4.4):
  `podman generate systemd` is deprecated. Containerfile and Dockerfile are the same format.

## Publishing (the ship skill writes this; `references/ci.md` has the workflow)

- GHCR: `docker/login-action` with `GITHUB_TOKEN` and `packages: write`;
  `docker/metadata-action` tags `type=semver,pattern={{version}}`, `type=sha`, never `latest`
  alone; `docker/build-push-action` pushes by digest; `actions/attest-build-provenance` with
  `subject-name` (no tag) and `subject-digest`; cosign keyless from the job's OIDC token.
- Verify before deploy: `cosign verify --certificate-identity-regexp '^https://github.com/<org>/<repo>/' --certificate-oidc-issuer https://token.actions.githubusercontent.com <image>@<digest>`.
- `docker buildx imagetools inspect <image>` shows platforms, digest, SBOM and provenance.
- Images are never pushed from a laptop; the gate asks on `docker push` for that reason.

## Pitfalls

1. `latest` in `FROM` or in deploy manifests: the build is not reproducible and rollbacks lie.
2. `ADD` with a URL or an archive where `COPY` or `curl` with a checksum belongs.
3. `apt-get install` without `--no-install-recommends` and without removing the lists in the
   same layer; `pip`, `npm` caches left in the image.
4. Secrets passed through `ARG` or `ENV`: they stay in the image history.
5. `EXPOSE` believed to publish a port; it documents only.
6. A healthcheck that `curl`s a page that always answers; it must touch the dependency.
7. Running the dev compose file in production (bind mounts, `build:`, debug ports).

## Do not

- Do not push, prune, log in or delete images from a task; propose the command.
- Do not add a base image or a tool the spec does not name; distroless before alpine before
  debian, and say why when you deviate.
- Do not write a `Dockerfile` without a `.dockerignore`.
