# expert-service-mesh — versions and dated facts

Format: `- [status date · src: url] claim`. The brief flags version lines after 30 days, idiom
after 90. Refresh: `curl -s https://api.github.com/repos/istio/istio/releases/latest | jq -r .tag_name`,
`https://istio.io/latest/docs/releases/supported-releases/`, the Cloud Service Mesh release
notes (`docs.cloud.google.com/service-mesh/docs/release-notes`).

## Istio

| Series | Released | End of life | Kubernetes |
|---|---|---|---|
| 1.31 (1.31.4) | 2026-08-27 (patch 2026-11-06) | ~February 2027 | 1.32 to 1.37 |
| 1.30 (1.30.8) | 2026-05-14 (patch 2026-11-06) | ~December 2026 | 1.32 to 1.36 |
| 1.29 | 2026-02-16 | 2026-10-15 (ended) | — |
| 1.32.0 | rc.2 on 2026-11-06 | — | — |

- [verified 2026-11-08 · src: https://api.github.com/repos/istio/istio/releases/latest] Istio 1.31.4 and 1.30.8 released 2026-11-06; 1.32.0-rc.2 the same day.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/releases/supported-releases/] Supported: 1.31 (2026-08-27, EOL expected February 2027, Kubernetes 1.32 to 1.37) and 1.30 (2026-05-14, EOL expected December 2026, Kubernetes 1.32 to 1.36); 1.29 reached EOL 2026-10-15; a minor is supported until six weeks after the N+2 minor; minors ship about quarterly; the control plane may be one version ahead of the data plane, never behind.
- [verified 2026-11-08 · src: https://istio.io/latest/news/releases/1.31.x/announcing-1.31/] 1.31: `istio-agentgateway-waypoint` GatewayClass, weighted canary waypoints, zone-aware load balancing by default, mesh-wide connection pool and outlier detection baseline, trust-domain matching in AuthorizationPolicy, strict gateway merging on by default; GCP-hosted artifact locations deprecated (images stay on Docker Hub).
- [verified 2026-11-08 · src: https://istio.io/latest/news/releases/1.31.x/announcing-1.31.4/] 1.31.4 fixes GHSA-rr2c-p22p-6r9r (8.2: in ambient a port-level STRICT PeerAuthentication could be skipped, allowing plaintext), GHSA-cxwg-46mx-q8hf (7.4: stale conntrack entry bypassed the sidecar), GHSA-635j-qv98-9275 (7.7: malformed xDS debug request crashed istiod), GHSA-9gqj-583v-mpqp (5.6: `ipBlocks` matched the internal listener so DENY rules failed open), GHSA-7m6f-j3gp-2r53 (host-header `when` conditions were case-sensitive).
- [verified 2026-11-08 · src: https://gateway-api.sigs.k8s.io/implementations/] Istio is Conformant for Gateway and Mesh at Gateway API conformance v1.6.0 (Istio 1.31.0 report).

## Ambient and sidecar mechanics

- [verified 2026-11-08 · src: https://istio.io/latest/docs/ambient/architecture/traffic-redirection/] ztunnel runs as a DaemonSet in `istio-system`; the istio-cni node agent redirects outbound TCP to 15001, inbound plaintext to 15006 and inbound HBONE to 15008; ambient works beside any CNI.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/ambient/usage/waypoint/] `istioctl waypoint apply -n NS --enroll-namespace` creates the waypoint and labels the namespace; `istio.io/waypoint-for` is `service` (default), `workload`, `all` or `none`; cross-namespace use needs the Gateway's `allowedRoutes` plus `istio.io/use-waypoint-namespace`.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/ambient/usage/add-workloads/] `istio.io/dataplane-mode=ambient` on a namespace or pod enrols without a restart; a pod with a sidecar is not placed in ambient; mixing modes in one namespace is not recommended.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/setup/upgrade/canary/] `istioctl install --set revision=1-31-4` (no dots); namespaces move with `istio.io/rev` after removing `istio-injection`, which takes precedence; `istioctl tag set default --revision 1-31-4`; `istioctl uninstall --revision <old> -y`.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/setup/additional-setup/sidecar-injection/] `istio-injection=enabled` injects at pod creation; existing pods must be recreated; `sidecar.istio.io/inject: "false"` opts a pod out.

## Security and telemetry APIs

- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/authorization-policy/] Actions ALLOW (default), DENY, AUDIT, CUSTOM; `source.principals` and `source.namespaces` from the peer certificate; `to.operation` `hosts` (HTTP only), `ports`, `methods`, `paths` (`{*}`, `{**}`); `when` keys such as `request.auth.claims[iss]`; `targetRefs` (Gateway, GatewayClass, Service on waypoints, ServiceEntry) exclusive with `selector`; a root-namespace policy applies mesh-wide.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/security/request_authentication/] JWTRule fields issuer, audiences, jwksUri, jwks, fromHeaders, fromParams, forwardOriginalToken, outputPayloadToHeader, outputClaimToHeaders, timeout.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/ops/common-problems/security-issues/] The workload certificate SAN is `spiffe://cluster.local/ns/<ns>/sa/<sa>`, inspectable with `istioctl proxy-config secret`; `istioctl x authz check` lists the policies applied to a pod.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/tasks/traffic-management/egress/egress-control/] `meshConfig.outboundTrafficPolicy.mode` defaults to `ALLOW_ANY`; `REGISTRY_ONLY` blocks hosts without a Service or ServiceEntry; external hosts are declared with a ServiceEntry (`resolution: DNS`, `location: MESH_EXTERNAL`).
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/config/telemetry/] Telemetry `targetRefs` supports Gateway, GatewayClass, Service (waypoints) and ServiceEntry; one selector-less Telemetry per namespace; `customTags` replace the parent's.

## istioctl

- [verified 2026-11-08 · src: https://istio.io/latest/docs/ops/diagnostic-tools/istioctl-analyze/] File-only analysis is `istioctl analyze --use-kube=false <files>`; messages carry codes (IST0101 referenced selector not found, IST0102, IST0174); `--failure-threshold` defaults to Error; suppress with `--suppress "IST0102=Namespace x"`.
- [verified 2026-11-08 · src: https://istio.io/latest/docs/reference/commands/istioctl/] `proxy-status` shows every proxy's xDS sync; `proxy-config` dumps bootstrap, cluster, endpoint, listener, route, secret; `install` applies a manifest (`upgrade` is its alias); `uninstall`; `x precheck` inspects the cluster for install requirements; `waypoint apply|delete|generate|list|status`; `ztunnel-config`; `dashboard` opens web UIs through a port-forward; `bug-report` writes an archive; `tag set` manages revision tags.

## Cloud Service Mesh

- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/overview] On GKE Cloud Service Mesh uses the Istio APIs; the managed control plane is recommended; the in-cluster control plane with Istio APIs is deprecated; data planes are Envoy sidecars or proxyless gRPC.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/managed/release-channels] Channel labels `istio.io/rev=asm-managed-rapid|asm-managed|asm-managed-stable` follow the cluster's GKE channel (no channel maps to Regular) and are fixed at provisioning; `istio-injection=enabled` is the recommended label; the table lists Cloud Service Mesh versions Rapid 1.21, Regular 1.20, Stable 1.19.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/release-notes] 2026-11-02: preview of sidecar `GCPAuthzPolicy` scoped to the Gateway API; 2026-10-19: in-cluster 1.28 no longer supported; 2026-10-12: in-cluster 1.31.1-asm.16 with the features of Istio 1.31.1.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/service-mesh/docs/troubleshooting/troubleshoot-observability] Cloud Monitoring and Cloud Logging are enabled by default with the mesh; metrics such as `istio.io/service/server/request_count` on `istio_canonical_service`; sidecars call the Logging API about every ten seconds.
- [reported 2026-11-08 · src: https://cloud.google.com/service-mesh/pricing] GKE Enterprise customers are not billed separately for the mesh (search snippet, not in the fetched page text).
