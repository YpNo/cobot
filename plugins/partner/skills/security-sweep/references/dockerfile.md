# Dockerfile / container rule pack

Loads for `Dockerfile*` and `*.containerfile`, and also covers `docker-compose.yml`. Rule ids are `DK-<CAT>-<nn>`.

## Base image & provenance

- **DK-BASE-01** Base image tagged `latest` or a floating major tag: non-reproducible, and a rebuild silently
  changes the contents. Pin by digest (`image:tag@sha256:...`) for anything that ships.
- **DK-BASE-02** Base image from an unofficial or unverified registry namespace.
- **DK-BASE-03** Full OS base (`ubuntu`, `debian`) where `-slim`, `alpine`, `distroless` or `scratch` would do:
  every extra package is attack surface and CVE noise. For a static Go binary, `scratch`/`distroless` is the baseline.
- **DK-BASE-04** No multi-stage build: compilers, package managers and build secrets shipped in the runtime image.
- **DK-BASE-05** Known CVEs in the image: run `trivy image` or `grype` if installed; otherwise note the base image age.

## Privilege

- **DK-PRIV-01** No `USER` instruction: the container runs as root. Add a non-root `USER` with a numeric UID
  (numeric so Kubernetes `runAsNonRoot` can verify it).
- **DK-PRIV-02** `USER root` at the end of the file, or a later stage that resets to root after dropping.
- **DK-PRIV-03** setuid/setgid binaries left in the image, or `chmod +s`.
- **DK-PRIV-04** Files owned by or writable to the running user where they need not be: a writable application
  directory allows self-modification.

## Secrets

- **DK-SEC-01** Secret in an `ENV` or `ARG`: both are baked into image layers and readable via `docker history`
  forever, even if later unset. CRITICAL.
- **DK-SEC-02** `COPY` of a `.env`, key or credentials file; `COPY . .` with no `.dockerignore` excluding `.git`,
  `.env`, keys and CI configs. Check `.dockerignore` exists and covers them: a copied `.git` ships the history.
- **DK-SEC-03** Secret fetched during build with `curl -u` or a token in a URL: it lands in the layer and the build
  log. Use BuildKit `--mount=type=secret`.
- **DK-SEC-04** `RUN` that writes a credential to a file in an earlier layer and deletes it later: the earlier
  layer still contains it.

## Build hygiene

- **DK-BUILD-01** `curl ... | sh` in a `RUN`: unverified remote code at build time. Require a pinned checksum.
- **DK-BUILD-02** Package install without version pinning (`apt-get install foo` vs `foo=<version>`), `apk add`
  without `--no-cache`, or `apt-get` without cleaning `/var/lib/apt/lists` (bloat, stale CVE data).
- **DK-BUILD-03** `ADD` with a remote URL: no checksum verification, and `ADD` auto-extracts archives. Use `COPY`,
  or `RUN curl` with a verified hash.
- **DK-BUILD-04** `--no-check-certificate`, `--insecure`, `GOINSECURE`, `PIP_TRUSTED_HOST`, or
  `npm config set strict-ssl false` during build.
- **DK-BUILD-05** `apt-get upgrade`/`dist-upgrade` in a build: makes the image non-reproducible.

## Runtime posture

- **DK-RUN-01** No `HEALTHCHECK` on a long-running service.
- **DK-RUN-02** Shell-form `CMD`/`ENTRYPOINT` (`CMD foo`): the process runs under `sh -c` as PID 1 and receives no
  signals, so the container never shuts down gracefully. Use exec form (`CMD ["foo"]`).
- **DK-RUN-03** `EXPOSE` of an admin, debug or metrics port alongside the service port with no note of how it is
  restricted.
- **DK-RUN-04** Writable root filesystem where the app needs none; pair with `readOnlyRootFilesystem` in the
  orchestrator.

## docker-compose

- **DK-COMP-01** `privileged: true`, `network_mode: host`, `pid: host`, or `cap_add: [SYS_ADMIN]`.
- **DK-COMP-02** Docker socket mounted (`/var/run/docker.sock`): equivalent to root on the host. CRITICAL unless the
  container is the orchestrator and that is stated.
- **DK-COMP-03** Host path mounted read-write where read-only would do; sensitive host paths (`/`, `/etc`, `/proc`)
  mounted at all.
- **DK-COMP-04** Secrets in `environment:` blocks rather than `secrets:` or a gitignored env file. A committed
  `docker-compose.yml` with a real password is CRITICAL.
- **DK-COMP-05** Port published as `0.0.0.0:5432:5432`: a database exposed on every interface. Bind to `127.0.0.1`
  unless external access is intended.
- **DK-COMP-06** No `restart` policy, no resource limits (`mem_limit`, `cpus`).

## Verification commands (read-only)

```bash
hadolint Dockerfile              # if installed
trivy config .                   # if installed; scans Dockerfile + compose
trivy image <tag>                # if the image is built locally
docker history --no-trunc <tag> | grep -iE 'secret|token|password|key'
grep -nE '^(USER|ENV|ARG|ADD|RUN)' Dockerfile
test -f .dockerignore || echo "MISSING .dockerignore"
```
