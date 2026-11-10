---
name: expert-service-mesh
description: >-
  Istio and Cloud Service Mesh: ambient and sidecar modes, STRICT mTLS, AuthorizationPolicy (default
  deny, by principal, the empty-rule trap), RequestAuthentication, Telemetry, egress, canary
  revisions, the istioctl forms that ask. Use on istio/ and mesh/ folders and PeerAuthentication or
  AuthorizationPolicy files.
paths:
  - "**/istio/**"
  - "**/istio-system/**"
  - "**/mesh/**/*.y*ml"
  - "**/*istio*.y*ml"
  - "**/*-mesh*.y*ml"
  - "**/*peerauthentication*.y*ml"
  - "**/*authorizationpolicy*.y*ml"
user-invocable: false
---

# expert-service-mesh

Versions, dates and sources: `references/versions.md`. Policies ready to copy (STRICT
mesh-wide, default deny, allow by principal, JWT, waypoint enrolment, Telemetry defaults):
`references/policies.md`. Re-verify a line the brief flags stale (versions after 30 days,
idiom after 90). Workload manifests are `expert-kubernetes`'s, the GKE cluster and fleet are
`expert-gcp`'s. `istioctl analyze`, `proxy-status`, `proxy-config`, `version` are silent;
`install`, `upgrade`, `uninstall`, `waypoint apply|delete`, `tag set`, `x precheck`,
`gcloud container fleet mesh update` ask (decision 26).

- [verified 2026-11-08 · src: https://api.github.com/repos/istio/istio/releases/latest] Istio 1.31.4 and 1.30.8 (2026-11-06, security releases); 1.31 is supported on Kubernetes 1.32 to 1.37; 1.32.0 is at rc.2.

## Non-negotiables

1. Mesh-wide `PeerAuthentication` named `default` in the root namespace with `mtls.mode:
   STRICT`; `PERMISSIVE` only as a dated migration step per namespace, never the end state,
   because plaintext traffic in PERMISSIVE bypasses authentication and authorization.
2. A default-deny `AuthorizationPolicy` (`spec: {}`, ALLOW with no rules) per namespace, then
   allows by `source.principals` (SPIFFE identities), never by IP; identity fields need STRICT.
3. No `DestinationRule` with `tls.mode: DISABLE` inside the mesh; `ISTIO_MUTUAL` is the only
   mesh-internal mode and Istio sets it by default.
4. `rules: - {}` allows everything: an empty rule is always matched. Review every
   AuthorizationPolicy for an empty rule, an extra `-` before `from:` (two rules, OR), an
   HTTP-only field on a TCP port (never matches), and a JWT rule without
   `source.requestPrincipals` (a request without a token is accepted).
5. New meshes run in ambient mode; sidecars only where a feature ambient lacks is needed
   (multi-cluster, multi-network, VMs, sidecar-to-waypoint interop). One mode per namespace,
   never both. L7 policy in ambient needs a waypoint; without one the policy silently applies
   at L4 only.
6. Every namespace names its control plane: `istio.io/rev=<revision>` (or the managed channel
   label on Cloud Service Mesh), `istio.io/dataplane-mode=ambient` for ambient; revision names
   carry no dots (`1-31-4`); upgrades are canary revisions moved with `istioctl tag set`.
7. Egress is explicit: `outboundTrafficPolicy.mode: REGISTRY_ONLY` with a `ServiceEntry`
   (`resolution: DNS`) per external host, or an egress gateway; `ALLOW_ANY` is the default and
   lets every pod reach the internet.
8. Telemetry through the Telemetry API (metrics overrides, access-log filters, tracing
   sampling), never `EnvoyFilter`, which is unversioned configuration that can destabilise the
   mesh and must be re-validated at every proxy upgrade.

- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/peer_authentication/] Modes UNSET (inherit, else PERMISSIVE), DISABLE, PERMISSIVE, STRICT; the mesh-wide policy lives in the root namespace without a selector; `portLevelMtls` keys are workload ports.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/tasks/security/authentication/mtls-migration/] Istio defaults to PERMISSIVE; in PERMISSIVE plaintext traffic "bypasses authentication and authorization checks by default".
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/authorization-policy/] `rules` unset: "the match will never occur" (allow nothing); "An empty rule is always matched" (`rules: - {}` allows all); evaluation: CUSTOM deny, then any DENY, then no ALLOW policy means allow, then an ALLOW match, otherwise deny.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/request_authentication/] "A request that does not contain any authentication credentials will be accepted"; requiring a token needs an AuthorizationPolicy with `source.requestPrincipals: ["*"]`.

## Ambient against sidecar

| | Ambient | Sidecar |
|---|---|---|
| L4 (mTLS, L4 authz, L4 telemetry) | ztunnel per node, no pod restart to enrol | Envoy per pod, restart to inject |
| L7 (routing, L7 authz, L7 telemetry, retries) | a waypoint per namespace or service, deployed on purpose | every pod pays Envoy |
| Enrol | `istio.io/dataplane-mode=ambient` on the namespace or pod | `istio-injection=enabled` or `istio.io/rev=<rev>` |
| Not yet | multi-cluster, multi-network, VMs, sidecar-to-waypoint interop, EnvoyFilter, tracing at L4 | — |
| Cost | ztunnel DaemonSet plus waypoints where chosen | one proxy per pod, CPU and memory per replica |

Migration order: install ambient beside the sidecar revision, move a namespace at a time (label
swap, no restart), add a waypoint where L7 policy or routing exists (`istioctl waypoint apply
-n <ns> --enroll-namespace`), verify with `istioctl ztunnel-config workload` and the policy
checks, then remove the sidecar label and restart the workloads once.

- [verified 2026-11-08 · src: https://istio.io/latest/docs/ambient/overview/] ztunnel is a per-node Rust proxy scoped to L4 over HBONE; waypoints are Envoy L7 proxies outside application pods, enabled per namespace; traffic management, L7 authorization, L7 telemetry and VirtualService routing need a waypoint.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/overview/dataplane-modes/] Not yet in ambient: sidecar-to-waypoint interoperability, multi-cluster, multi-network, VMs; extensibility is WebAssembly on waypoints only and "EnvoyFilter API not supported"; both modes may coexist in one mesh per namespace.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/ambient/usage/waypoint/] A waypoint is a Gateway with `gatewayClassName: istio-waypoint`; enrolment is the `istio.io/use-waypoint=<name>` label on a namespace, Service or pod; Gateway API CRDs must be installed first.

## mTLS and identity

- Identity is the SPIFFE URI `spiffe://<trust-domain>/ns/<namespace>/sa/<service-account>`,
  derived from the workload certificate (24 h lifetime, renewed at half): one Kubernetes
  service account per workload, or authorization cannot tell them apart.
- STRICT mesh-wide, then per-port exceptions through `portLevelMtls` for the one legacy client,
  dated and tracked; the migration task locks one namespace first and watches
  `istio_requests_total{connection_security_policy="none"}` drop to zero before the mesh-wide
  policy lands.
- `DestinationRule` `tls.mode: SIMPLE` or `MUTUAL` is for hosts outside the mesh (a
  `ServiceEntry`); inside the mesh `ISTIO_MUTUAL` is implicit.
- Certificates: Mesh CA on Cloud Service Mesh, or Istio CA with a root you rotate; `istioctl
  proxy-config secret <pod>` shows what a proxy holds.

- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/authorization-policy/] Peer identities are `<TRUST_DOMAIN>/ns/<NAMESPACE>/sa/<SERVICE_ACCOUNT>` derived from the peer certificate, which requires mTLS.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/commands/pilot-agent/] Workload certificate lifetime `SECRET_TTL` defaults to 24h, renewed at half (`SECRET_GRACE_PERIOD_RATIO` 0.5).
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/networking/destination-rule/] DestinationRule `tls.mode` DISABLE, SIMPLE, MUTUAL, ISTIO_MUTUAL (Istio certificates, every other TLS field empty).

## AuthorizationPolicy

- Order of evaluation: CUSTOM (deny wins), then any DENY match denies, then a workload with no
  ALLOW policy allows, then an ALLOW match allows, otherwise deny. So the first policy in a
  namespace is the allow-nothing one; DENY policies are for the exceptions that must hold even
  when an ALLOW is added later (`to.operation.paths: ["/admin*"]` from anything but the admin
  principal).
- Scope: a policy in the root namespace is mesh-wide; `selector` for sidecars; `targetRefs`
  (Gateway, Service on a waypoint) for ambient and gateways, exclusive with `selector`.
- JWT: `RequestAuthentication` validates, `AuthorizationPolicy` requires
  (`source.requestPrincipals: ["<issuer>/<subject>"]` or `["*"]`); claims through
  `when: key: request.auth.claims[groups]`.
- `istioctl x authz check <pod>` lists the policies a proxy applies; `istioctl analyze` catches
  selectors that match nothing (IST0101) and conflicting policies.

- [verified 2026-11-08 · src: https://istio.io/latest/docs/concepts/security/] A workload with no authorization policy allows all; the recommended start is an "allow-nothing" ALLOW policy, then incremental allows; identity fields need STRICT mTLS.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/ops/common-problems/security-issues/] An extra `-` before `from:` makes a separate rule (rules are OR); HTTP-only fields never match raw TCP ports; AUDIT never denies.

## Telemetry

- One `Telemetry` resource in the root namespace sets the mesh defaults (providers from
  MeshConfig `extensionProviders`: Prometheus metrics, `envoy` access logs with a CEL filter
  such as `response.code >= 400`, a tracing provider with `randomSamplingPercentage` set on
  purpose, the default is 0); a namespace resource overrides the whole parent; one selector-less
  resource per namespace.
- On GCP: Cloud Monitoring and Cloud Logging receive mesh metrics and logs by default
  (`istio.io/service/server/request_count` on `istio_canonical_service`); Cloud Trace is off
  until a Telemetry resource names the `stackdriver` provider (1 % sampling by default).
- Dashboards: Kiali in self-managed meshes (`istioctl dashboard kiali` opens a port-forward
  and asks), the Cloud Service Mesh pages on GKE.

- [verified 2026-11-08 · src: https://istio.io/latest/docs/tasks/observability/telemetry/] Telemetry scope: root namespace (mesh defaults, one resource), namespace (overrides the parent), workload (selector); providers come from MeshConfig `extensionProviders`; built-ins `prometheus`, `stackdriver`, `envoy`.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/telemetry/] `tracing.randomSamplingPercentage` defaults to 0; metrics `overrides` with `disabled` and `tagOverrides`; access logging `filter.expression` in CEL.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/networking/envoy-filter/] EnvoyFilter "must be used with care, as incorrect configurations could potentially destabilize the entire mesh" and must be re-checked across proxy upgrades.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/observability/accessing-traces] Cloud Trace is disabled by default; a Telemetry resource in `istio-system` with the `stackdriver` provider enables it, 1 % sampling by default.

## Cloud Service Mesh on GKE

- The managed control plane is the recommended form: `gcloud services enable
  mesh.googleapis.com`, `gcloud container fleet mesh enable --project P` once, then `gcloud
  container fleet mesh update --management automatic --memberships M --location REGION
  --project P` per cluster (asks); `gcloud container fleet mesh describe` shows
  `controlPlaneManagement: ACTIVE` and the implementation (`TRAFFIC_DIRECTOR`; `ISTIOD` is
  deprecated, support ends 2028-03-01).
- Namespaces use `istio-injection=enabled` (recommended) or the channel label
  `istio.io/rev=asm-managed|asm-managed-rapid|asm-managed-stable`, fixed to the cluster's GKE
  channel at provisioning; the managed data plane restarts sidecars after upgrades.
- What the managed plane does not do (feature table, 2026-11-08): ambient mode (no statement
  of support since 2024), WasmPlugin, Istio Operator, multi-network, primary-remote
  multi-cluster, the Telemetry API beyond access logs and tracing, `istioctl proxy-status`;
  Mesh CA and CA Service are the certificate authorities, Istio CA is not; STRICT mTLS is an
  optional feature to enable. Ingress is the GKE Gateway (`gke-l7-*` classes), not an Istio
  ingress gateway.
- Billing: standalone Cloud Service Mesh bills per client (sidecar pod, Cloud Run instance,
  proxyless gRPC) at about $0.50 per month; included with GKE Enterprise (`reported`).
- An ambient mesh on GKE is therefore self-managed Istio today; say so when the owner asks for
  ambient plus managed.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/onboarding/provision-control-plane] `gcloud container fleet mesh enable --project P` once, then `gcloud container fleet mesh update --management automatic --memberships M --project P --location REGION` per cluster; roles `gkehub.admin` and `serviceusage.serviceUsageAdmin`; the managed data plane restarts sidecars within about two weeks of an upgrade.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/supported-features-mcp] Managed control plane (TRAFFIC_DIRECTOR): EnvoyFilter partly, Kubernetes Gateway API "No" in this table, Telemetry API a subset, WasmPlugin no, Istio Operator no, multi-network no; Mesh CA and CA Service yes, Istio CA no; STRICT mTLS as an optional feature; `istioctl ps` not supported; ambient not covered.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/release-notes] 2026-09-28: in-cluster and managed ISTIOD on GKE deprecated, support ends 2028-03-01; 2026-10-19: managed sidecar images 1.21.6-asm.93 (rapid), 1.20.8-asm.143 (regular), 1.19.10-asm.132 (stable); ambient "is not supported" (2024-07-25, no later statement); Gateway API data plane GA on Rapid 2025-02-03.
- [verified 2026-11-08 · src: https://cloud.google.com/service-mesh/pricing] Standalone Cloud Service Mesh bills each client at $0.0006945 per hour (about $0.50 per month); standard metrics, the managed control plane and Mesh CA certificates are included.

## Pitfalls

1. STRICT applied mesh-wide while one namespace still has sidecar-less pods: those pods lose
   every caller at once; lock down namespace by namespace.
2. `rules: - {}` written to "enable" a policy: it allows the world.
3. An ALLOW policy by `source.ipBlocks` behind a load balancer: every request has the LB's IP.
4. L7 AuthorizationPolicy in an ambient namespace without a waypoint: paths and methods are
   ignored, only the L4 part applies, and nothing warns.
5. `istio-injection=enabled` left beside `istio.io/rev`: the first wins and the canary never
   takes the namespace.
6. A DestinationRule with `tls.mode: DISABLE` added to "fix" a 503: it turned off mTLS for the
   host and the 503 was a port-name or a selector problem.
7. `EnvoyFilter` that worked on 1.29 and silently changed meaning on 1.31.
8. 1.31.3 and earlier in ambient: a port-level STRICT policy could be skipped
   (GHSA-rr2c-p22p-6r9r); patch to 1.31.4 or 1.30.8 before trusting port-level exceptions.

## Do not

- Do not install, upgrade, uninstall, apply a waypoint or set a tag from a task; propose the
  command with its revision.
- Do not write PERMISSIVE without a removal date in the same change.
- Do not write an EnvoyFilter where a Telemetry, DestinationRule or Gateway API field exists.
- Do not pass `--kubeconfig`, `-c` or an environment assignment on an `istioctl` read (the
  read-only agents' allows do not match such a segment).
