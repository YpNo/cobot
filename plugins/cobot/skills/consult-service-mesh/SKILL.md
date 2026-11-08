---
name: consult-service-mesh
description: >-
  Read-only Istio and Cloud Service Mesh audit by the consultant: mTLS mode, default deny,
  allow-all and IP-based AuthorizationPolicies, DestinationRule DISABLE, JWT without
  requestPrincipals, EnvoyFilters, mixed revisions, ambient without a waypoint, egress.
context: fork
agent: cobot:consultant
user-invocable: true
---

# consult-service-mesh

Read-only. Change nothing, install nothing. Read the sibling skill
`../expert-service-mesh/SKILL.md` and its `references/` first: they are the baseline.
`istioctl analyze --use-kube=false <files>` is silent for you; `istioctl analyze`,
`proxy-status`, `proxy-config` and `kubectl get` against the current context are silent too,
but you use them only when the audit is about a live mesh and the owner's request says so.
Never `x authz check` or `dashboard` (they ask), never `--kubeconfig`, `-c` or an environment
assignment on a read.

## Procedure

1. **Inventory.** Mesh resources in the tree (`PeerAuthentication`, `AuthorizationPolicy`,
   `RequestAuthentication`, `DestinationRule`, `VirtualService`, `ServiceEntry`, `Gateway`,
   `Telemetry`, `EnvoyFilter`, `WasmPlugin`, `IstioOperator`, Helm values for `istio/*`
   charts), the namespaces and their labels (`istio-injection`, `istio.io/rev`,
   `istio.io/dataplane-mode`, `istio.io/use-waypoint`), fleet or mesh configuration in
   Terraform (`google_gke_hub_feature`, `google_gke_hub_feature_membership` with `mesh`).
   Nothing → one line and stop.
2. **Static analysis.** `istioctl analyze --use-kube=false <dir>/*.yaml` when `istioctl` is
   on PATH; keep the message codes (IST0101 referenced selector not found, IST0102 namespace
   not injected, IST0174 conflicting policies) as evidence; absent → say so.
3. **mTLS.** Mesh-wide `PeerAuthentication` present in the root namespace and `STRICT`; every
   `PERMISSIVE` dated with a removal; `DISABLE` anywhere; `portLevelMtls` exceptions
   justified; a selector policy in the root namespace (ignored); `DestinationRule` with
   `tls.mode: DISABLE` for an in-mesh host, or `SIMPLE|MUTUAL` without a `ServiceEntry`.
4. **Authorization.** An allow-nothing policy per namespace that serves traffic; any policy
   with `rules: - {}` or an empty `from`/`to` entry; `source.ipBlocks` where a load balancer
   sits in front; a second `- from:` that split one rule in two; HTTP-only fields on TCP
   ports; `RequestAuthentication` without an `AuthorizationPolicy` requiring
   `requestPrincipals`; DENY policies relied on for cases an ALLOW would miss; AUDIT believed
   to deny.
5. **Modes and revisions.** `istio-injection` beside `istio.io/rev`; a namespace with no
   control-plane label at all; dots in a revision name; sidecar and ambient labels on one
   namespace; an ambient namespace with L7 policies (paths, methods, JWT) and no waypoint;
   a waypoint without `istio.io/use-waypoint` on anything.
6. **Telemetry and extensions.** `EnvoyFilter` or `WasmPlugin` where a Telemetry, DestinationRule
   or Gateway API field exists; tracing sampling left at 0 or at 100; access logs unfiltered in
   production.
7. **Egress.** `outboundTrafficPolicy` left at `ALLOW_ANY` without a written reason; external
   hosts without a `ServiceEntry` (`resolution: DNS`).
8. **Cloud Service Mesh fit.** Managed plane expected but the manifests use features the
   managed plane lacks (ambient, WasmPlugin, Istio Operator, multi-network, Istio CA); the
   fleet feature enabled but `--management automatic` missing; images or versions in a
   deprecated series (in-cluster 1.28 and earlier; ISTIOD implementation, support ending
   2028-03-01); Istio before 1.31.4 or 1.30.8 relying on port-level STRICT in ambient
   (GHSA-rr2c-p22p-6r9r).
9. **Rank.** Ten findings at most; merge duplicates across namespaces into one with the
   locations.

Severity: `critical` = `rules: - {}` or no authorization in a namespace that holds data, a
`DISABLE` DestinationRule in the mesh, JWT not required where it was meant to be; `high` =
mesh-wide PERMISSIVE or no mesh-wide policy, IP-based allows, L7 policy in ambient without a
waypoint, an unpatched series with a known bypass; `medium` = unlabelled namespaces, mixed
labels, EnvoyFilters, ALLOW_ANY egress, sampling at 0; `low` = hygiene, dates missing on
exceptions.

Confidence: `high` = seen in the file and confirmed by `istioctl analyze` or the live mesh;
`medium` = seen in the file, depends on installation values you cannot read; `low` = inferred.

## Report

```text
summary: <one line — namespaces and policies audited, analyze run or not, worst severity>

findings:
1. <severity> · <file>:<line> · <what> · fix: <exact resource and field, from references/policies.md> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-service-mesh
{"topic": "service-mesh", "skill": "expert-service-mesh", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

No finding without a file and line. Installation values, the managed channel and the CA you
cannot read go in the summary as "not verifiable from the tree". Zero findings is a valid
result; say what was checked.
