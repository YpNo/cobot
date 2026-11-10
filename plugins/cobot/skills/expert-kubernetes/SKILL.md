---
name: expert-kubernetes
description: >-
  Kubernetes workloads: manifests, Kustomize, Helm 4, Gateway API, restricted Pod Security, requests
  and limits, probes, NetworkPolicy, PDB, GKE specifics, the kubectl and helm forms that ask. Use on
  kustomization.yaml, Chart.yaml, values*.yaml, helmfile, and k8s/, kubernetes/ or manifests/
  folders.
paths:
  - "**/kustomization.y*ml"
  - "**/Chart.yaml"
  - "**/Chart.lock"
  - "**/values*.y*ml"
  - "**/helmfile*.y*ml"
  - "**/skaffold*.y*ml"
  - "**/k8s/**"
  - "**/kubernetes/**"
  - "**/manifests/**/*.y*ml"
  - "**/*.k8s.y*ml"
user-invocable: false
---

# expert-kubernetes

Versions, dates and sources: `references/versions.md`. Ready manifests (restricted Deployment,
HTTPRoute, default-deny NetworkPolicy, PDB): `references/manifests.md`. Re-verify a line the
brief flags stale (versions after 30 days, idiom after 90). Images are `expert-containers`'s,
the cluster and its IAM `expert-gcp`'s, the mesh `expert-service-mesh`'s. Renders, lint and
reads are silent; `apply`, `delete`, `patch`, `scale`, `rollout restart`, `exec`,
`port-forward`, `helm install|upgrade|uninstall` ask (decision 26).

- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes/kubernetes/releases] Kubernetes 1.37.2, 1.36.6, 1.35.10 (2026-10-28); Helm 4.3.1; kustomize 5.8.3; Gateway API 1.7.0; kubeconform 0.8.0.

## Non-negotiables

1. Every container declares `resources.requests` (CPU and memory) and a memory limit; a CPU
   limit only when throttling is wanted (batch, noisy neighbours). Guaranteed QoS
   (limits equal requests) for anything that must not be evicted first.
2. `readinessProbe` and `livenessProbe` that touch the real dependency, `startupProbe` for a
   slow start (`failureThreshold × periodSeconds` covers the worst case); never a liveness
   probe that fails on a downstream outage (it restarts a healthy process).
3. Images by digest (`image: repo/app@sha256:…`) or an immutable tag plus
   `imagePullPolicy: IfNotPresent`; never `:latest`, never no tag.
4. The namespace carries `pod-security.kubernetes.io/enforce: restricted` (plus `warn` and
   `audit` at `latest`); the pod template meets it: `runAsNonRoot: true`,
   `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `seccompProfile.type:
   RuntimeDefault`, `readOnlyRootFilesystem: true` with an `emptyDir` for what must be written,
   `automountServiceAccountToken: false` unless the pod calls the API server.
5. A default-deny `NetworkPolicy` (ingress and egress) in every namespace, then explicit allows
   per workload including DNS; the CNI must enforce it (GKE Dataplane V2 does).
6. Anything with replicas has a `PodDisruptionBudget` (`unhealthyPodEvictionPolicy:
   AlwaysAllow`) and `topologySpreadConstraints` across zones and hosts.
7. New routes use Gateway API (`HTTPRoute` on a shared `Gateway`), not Ingress; cross-namespace
   references need a `ReferenceGrant`.
8. One configuration tool per application: Kustomize overlays or Helm values, never both;
   rendered output is validated in CI with `kubeconform -strict -summary` and applied with
   `--server-side`.
9. Nothing secret in a manifest or a values file: External Secrets or Secret Manager CSI feed
   `Secret`s at run time; `kubectl create secret` is a command, not a committed file.

- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/security/pod-security-standards/] Restricted: `allowPrivilegeEscalation: false`, `runAsNonRoot: true` and no `runAsUser: 0`, `seccompProfile.type` explicitly `RuntimeDefault` or `Localhost`, capabilities drop ALL and add at most NET_BIND_SERVICE, volumes limited to configMap, csi, downwardAPI, emptyDir, ephemeral, persistentVolumeClaim, projected, secret.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/] CPU limits are enforced by throttling, memory limits by OOM kills; a limit without a request copies the limit as the request.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/containers/images/] Default `imagePullPolicy` is `Always` for `:latest` or no tag, `IfNotPresent` otherwise; "You should avoid using the :latest tag when deploying containers in production".
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/services-networking/ingress/] "The Kubernetes project recommends using Gateway instead of Ingress. The Ingress API has been frozen".

## Manifest shapes

- **Deployment** for stateless services (`strategy.rollingUpdate` with `maxUnavailable: 0`
  for zero-downtime, `revisionHistoryLimit: 3`); **StatefulSet** only for identity and ordered
  storage; **Job** with `backoffLimit`, `activeDeadlineSeconds` and `ttlSecondsAfterFinished`;
  **CronJob** with `concurrencyPolicy: Forbid` and `startingDeadlineSeconds`.
- **Service** `ClusterIP` by default; `LoadBalancer` only through a Gateway on GKE; named ports
  (`http`, `grpc`) so policies and routes can reference them.
- **ServiceAccount** per workload, `automountServiceAccountToken: false` on the account, `true`
  on the one pod that needs the API; RBAC `Role` scoped to the namespace, verbs listed, never
  `*`.
- **ConfigMap** for configuration, mounted read-only; a hash suffix (Kustomize
  `configMapGenerator`, Helm `checksum/config` annotation) so a change rolls the pods.
- Labels: `app.kubernetes.io/name`, `instance`, `version`, `component`, `part-of`,
  `managed-by`; selectors are immutable, set them once.
- Probe defaults (`periodSeconds` 10, `timeoutSeconds` 1, `failureThreshold` 3) are rarely
  right for a JVM or a cold cache: set them, and let `startupProbe` own the first minutes.

- [verified 2026-11-08 · src: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/] Probe defaults: `periodSeconds` 10, `timeoutSeconds` 1, `failureThreshold` 3, `successThreshold` 1 (must be 1 for liveness and startup).
- [verified 2026-11-08 · src: https://kubernetes.io/docs/tasks/run-application/configure-pdb/] PDB `policy/v1`, exactly one of `minAvailable` or `maxUnavailable`; `unhealthyPodEvictionPolicy: AlwaysAllow` (stable since 1.31) is recommended so unhealthy pods do not block a drain.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/] `automountServiceAccountToken: false` on the ServiceAccount or the Pod (the Pod wins); projected tokens are bounded and rotated.

## Kustomize

- `kustomization.yaml` with `resources:` (never `bases:`), `patches:` (never
  `patchesStrategicMerge` or `patchesJson6902`), `replacements:` (never `vars:`), `labels:`
  (never `commonLabels:`, which rewrites selectors); `kustomize edit fix` converts old files.
- `base/` plus `overlays/<env>/`; `images:` with `digest:` per overlay; `configMapGenerator`
  and `secretGenerator` with the hash suffix on; `components/` for optional features shared by
  overlays; `namespace:` set in the overlay, not the base.
- Render with `kustomize build overlays/prod` (or `kubectl kustomize`), validate with
  `kubeconform -strict -summary -schema-location default -schema-location
  'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'`
  for CRDs; never `--enable-exec`, `--enable-alpha-plugins` or `--enable-helm` on a tree you
  did not write (they run programs), never `--load-restrictor LoadRestrictionsNone`.

- [verified 2026-11-08 · src: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/patchesstrategicmerge/] `bases` (v2.1.0), `patchesStrategicMerge`, `patchesJson6902`, `vars`, `commonLabels` (v5.0.0) are deprecated in favour of `resources`, `patches`, `replacements`, `labels`.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/kustomize/commands/build/flagsforfunctions.go] `--enable-exec` "enable support for exec functions (raw executables); do not use for untrusted configs! (Alpha)"; `--enable-alpha-plugins`, `--enable-helm` (with `--helm-command`, default `helm`) default to false; `--load-restrictor` defaults to `LoadRestrictionsRootOnly`.

## Helm

- Helm 4 (`4.3.1`): `Chart.yaml` `apiVersion: v2`, `values.schema.json` validated on lint,
  template, install and upgrade; `helm lint`, `helm template | kubeconform -strict` in CI;
  `helm upgrade --install <release> <chart> -n <ns> --create-namespace -f values-<env>.yaml
  --rollback-on-failure --wait=watcher --timeout 10m --history-max 10` (Helm 3 used
  `--atomic --wait`); charts from OCI registries (`oci://<region>-docker.pkg.dev/<p>/<repo>/<chart>
  --version x.y.z`), never a floating repository URL in production.
- `--post-renderer` runs a plugin: fine on your own chart in CI, never on a tree under audit
  (the read-only agents cannot use it at all). `helm diff upgrade` (plugin) before every
  upgrade in a pipeline; `--dry-run=server` to see what the API would validate.
- Values: camelCase keys, flat over nested, strings quoted, every value documented; secrets
  never in `values.yaml`, provided by an External Secret or `--set-file` from a vault step.
- Helm 3 receives security fixes until 2026-11-11: plan the move.

- [verified 2026-11-08 · src: https://helm.sh/docs/helm/helm_upgrade/] Helm 4.3.1 `helm upgrade`: `--install`, `--timeout` default 5m0s, `--history-max` 10; no `--atomic`: `--rollback-on-failure` rolls back and sets `--wait` to `watcher` (values watcher, hookOnly, legacy; default hookOnly); `--post-renderer` names a postrenderer plugin.
- [verified 2026-11-08 · src: https://helm.sh/blog/helm-4-released/] Helm 4.0.0 shipped 2025-11-12 (WebAssembly plugins, post-renderers as plugins, server-side apply, kstatus waiting); Helm 3 security fixes end 2026-11-11.
- [verified 2026-11-08 · src: https://helm.sh/docs/topics/version_skew/] Helm 4 is compatible with n-3 Kubernetes versions: 4.3.x supports 1.34 to 1.37.

## Gateway API

- `GatewayClass` is the platform's (GKE: `gke-l7-global-external-managed`,
  `gke-l7-regional-external-managed`, `gke-l7-rilb`; Istio: `istio`, `istio-waypoint`);
  one `Gateway` per team or environment in an infrastructure namespace; application teams own
  `HTTPRoute`s (and `GRPCRoute`s) in their namespaces, admitted through the Gateway's
  `allowedRoutes` and a `ReferenceGrant` when a route points at a Service elsewhere.
- Standard channel only in production (`GatewayClass`, `Gateway`, `HTTPRoute`, `GRPCRoute`,
  `TLSRoute`, `ReferenceGrant`); TCPRoute and UDPRoute are experimental.
- Migrate Ingress with `ingress2gateway`, then test: path rules map to HTTPRoute rules, TLS
  termination moves to the Gateway listener; annotations do not migrate.

- [verified 2026-11-08 · src: https://gateway-api.sigs.k8s.io/docs/concepts/api-overview/] GatewayClass, Gateway, HTTPRoute GA since v0.5.0, GRPCRoute since v1.1.0, TLSRoute since v1.5.0; TCPRoute and UDPRoute are alpha in the Experimental channel; a cross-namespace reference is invalid without a ReferenceGrant.
- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes-sigs/gateway-api/releases/latest] Gateway API v1.7.0 (2026-10-29): HTTPRoute Retries promoted to Standard.

## GKE specifics

- Autopilot rejects privileged containers, host namespaces, `hostNetwork`, `hostPath` beyond
  read-only `/var/log`, drops `CAP_NET_RAW`; it sets requests when missing and raises them to
  its minimums, and bills per request: right-size or pay for the default.
- Workload Identity Federation for GKE: `serviceAccountName` on the pod, the principal bound in
  IAM (`expert-gcp/references/iam.md`); no key, no annotation unless an API refuses the
  principal.
- GKE Gateway is on by default (always on Autopilot); `HTTPRoute` plus `HealthCheckPolicy`,
  `GCPBackendPolicy` and `GCPGatewayPolicy` carry what Ingress annotations used to; Dataplane
  V2 enforces NetworkPolicy and logs it.
- `kubectl` through `gke-gcloud-auth-plugin`; `gcloud container clusters get-credentials`
  writes the kubeconfig and asks for that reason.

- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-security] Autopilot blocks privileged containers, host namespaces, `hostNetwork`, `spec.externalIPs`; hostPath only read-only `/var/log`; `CAP_NET_RAW` dropped.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/how-to/deploying-gateways] Gateway API needs a VPC-native cluster; "GKE Gateway is always enabled on Autopilot clusters"; manifests use `gateway.networking.k8s.io/v1`.

## Commands: what asks

Silent: `kubectl get|describe|logs|diff|explain|top|events|api-resources|version|cluster-info|
auth can-i|config view|kustomize|rollout status|history`, `helm template|lint|list|status|show|
search|history|verify|dependency list`, `kustomize build`, `kubeconform`. Ask: `kubectl
apply|create|delete|replace|patch|edit|scale|set|label|annotate|taint|cordon|drain|rollout
restart|undo|pause|resume|exec|port-forward|run|debug|cp|expose|autoscale`, `helm
install|upgrade|uninstall|rollback|push|repo add|plugin install|registry login`. `kubectl diff`
runs a server-side dry run against the current context: it reads, it does not write.

## Pitfalls

1. `kubectl apply` on a resource created by `helm`: two owners, drift every release; pick one.
2. A liveness probe on `/health` that checks the database: one database blip restarts the
   whole fleet.
3. `commonLabels` adding a label to a selector: the Deployment cannot be updated in place.
4. `helm upgrade` without `--rollback-on-failure` (or `--atomic` on Helm 3) leaves a half-rolled
   release that the next pipeline run "fixes" by accident.
5. A NetworkPolicy without a DNS egress rule: every pod resolves nothing and the symptom looks
   like an application bug.
6. `resources.limits.cpu` on a latency-sensitive service: throttling under load that no metric
   explains until `container_cpu_cfs_throttled_seconds_total` is read.
7. `kubectl get -f dir/` or `kubectl get secret` in an audit prints live secret values into a
   transcript; the read-only agents are denied both forms on purpose.
8. `:latest` with `imagePullPolicy: Always`: two nodes run two different "latest".

## Do not

- Do not apply, delete, patch, scale, exec or port-forward from a task; propose the command.
- Do not write a Secret's value into a manifest, a values file or a kustomization.
- Do not render with `--post-renderer`, `--enable-exec`, `--enable-alpha-plugins` or
  `--enable-helm` on a repository under audit, nor pass `--kubeconfig` from the tree.
- Do not write a privileged pod for Autopilot; propose Standard with the reason, or GKE Sandbox.
