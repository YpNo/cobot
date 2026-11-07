---
name: consult-containers
description: >-
  Read-only audit of a repository's Dockerfiles, Containerfiles, compose files and image
  workflows by the consultant agent. Invoke before publishing an image, after changing a base
  image or a build stage, when a scanner or a reviewer flags the image, or from /cobot:ship
  after writing the image workflow. Checks every non-negotiable of expert-containers, runs
  hadolint, docker build --check and Trivy when present, and returns at most ten ranked findings
  plus a knowledge_delta for anything newly verified.
context: fork
agent: cobot:consultant
user-invocable: true
---

# consult-containers

Read-only. Change nothing, build nothing that pushes, log in nowhere. Read the sibling skill
`../expert-containers/SKILL.md` and its `references/versions.md` first: they are the baseline.

## Procedure

1. **Inventory.** `Dockerfile*`, `Containerfile*`, `*.dockerfile`, `.dockerignore`,
   `compose*.y*ml`, `docker-compose*.y*ml`, `*.container` (Quadlet), and the workflows that
   build or push images. None → say so in one line and stop.
2. **Tools as hints.** When on PATH and on the read list: `hadolint <file>`, `docker build
   --check .` (no push, no run), `trivy config .` and, for an image already built locally,
   `trivy image --severity CRITICAL,HIGH --ignore-unfixed <ref>`; `docker compose config -q`.
   Keep rule ids (DL3xxx, SC2xxx, AVD-xxx) as evidence; absent tools → audit by hand and say so.
3. **Dockerfile, per file.** Syntax directive present and current; multi-stage with a minimal
   final base (distroless, Chainguard static, slim) pinned by digest; `USER` non-root in the
   final stage; no `ADD` from URLs; no secrets through `ARG`/`ENV`; package installs cleaned in
   the same layer and `--no-install-recommends`; lockfile copied before sources; cache and secret
   mounts where a package manager or a credential appears; `ENTRYPOINT` exec form; a real
   `HEALTHCHECK`; `.dockerignore` present and excluding `.git`, env files, keys, caches.
4. **Compose.** No obsolete `version:`; `build:` absent from production files; images by digest;
   healthchecks with `depends_on: condition: service_healthy`; no host network or privileged
   mode without a written reason; secrets from `env_file` or compose `secrets`, not literals.
5. **Podman.** Quadlet units over generated systemd files; `--userns=keep-id` only where files
   are shared; no `--privileged`.
6. **Workflows.** `expert-gha` pins; `packages: write` only on the publishing job; push gated on
   non-PR events; SBOM and provenance on; cosign keyless on the digest; a Trivy gate with
   `--exit-code 1` on CRITICAL and HIGH; no cache write from the release path; tags from
   `metadata-action`, never a bare `latest`.
7. **Rank.** Ten findings at most; merge duplicates across files.

Severity: `critical` = secret in a layer or history, root plus privileged, unsigned image
deployed from `latest`; `high` = mutable base in production, scanner gate missing on a published
image, secrets via `ARG`; `medium` = missing non-root, missing `.dockerignore`, no healthcheck,
no SBOM; `low` = hygiene (layer cleanup, exec form, labels).

Confidence: `high` = seen in the file and confirmed by a tool or the registry; `medium` = seen in
the file, impact depends on the deployment you cannot read; `low` = inferred.

## Report

```text
summary: <one line — files audited, tools run or absent, worst severity>

findings:
1. <severity> · <file>:<line> · <what> · fix: <exact change, digest or SHA from references> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-containers
{"topic": "containers", "skill": "expert-containers", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

No finding without a file and line. Registry settings you cannot read (retention, immutability,
required signatures) go in the summary as "not verifiable from the tree". Zero findings is a
valid result; say what was checked.
