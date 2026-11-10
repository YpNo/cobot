# Consult: kubernetes

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, apply nothing. Read the sibling skill
`skills/expert-kubernetes/SKILL.md` and its `references/` first: they are the baseline. Renders
(`kustomize build`, `helm template`, `helm lint`, `kubeconform`) are silent for you; so are
`kubectl get|describe|logs|diff` against the current context, but you use them only when the
audit is about a live cluster and the owner's request says so. Never `kubectl get secret`,
never `kubectl get -f`, never `config view --raw`, never `--post-renderer`, `--enable-exec`,
`--enable-helm` or `--kubeconfig` (the gate denies or asks; the tree may hold the program).

## Procedure

1. **Inventory.** `kustomization.y*ml`, `Chart.yaml`, `values*.y*ml`, `helmfile*.y*ml`,
   `skaffold*.y*ml`, `k8s/`, `kubernetes/`, `manifests/`, the workflows that deploy, the
   namespaces and their labels. Nothing → one line and stop.
2. **Render.** `kustomize build <overlay>` per overlay, `helm template <release> <chart> -f
   <values>` per environment, then `kubeconform -strict -summary` on the output (CRD schemas
   through the catalog location when CRDs appear; `-ignore-missing-schemas` and say so). Tools
   absent → audit the source by hand and say so. Keep kubeconform's messages as evidence.
3. **Per workload** (Deployment, StatefulSet, DaemonSet, Job, CronJob): `requests` for CPU and
   memory, a memory limit, QoS class; `readinessProbe` and `livenessProbe` present and
   distinct, `startupProbe` where the start is slow, a liveness probe that checks a dependency;
   image by digest or immutable tag, never `latest` or no tag, `imagePullPolicy`; security
   context against `restricted` (`runAsNonRoot`, `allowPrivilegeEscalation`, `capabilities`,
   `seccompProfile`, `readOnlyRootFilesystem`, `privileged`, host namespaces, `hostPath`);
   `automountServiceAccountToken`; a dedicated `serviceAccountName`; labels and immutable
   selectors; `PodDisruptionBudget` and `topologySpreadConstraints` when replicas > 1.
4. **Namespace.** `pod-security.kubernetes.io/enforce` label; a default-deny NetworkPolicy and
   a DNS egress rule; RBAC with `*` verbs or cluster-wide bindings for a namespaced need.
5. **Routing.** Ingress where a Gateway exists or is available; HTTPRoute without a
   ReferenceGrant for a cross-namespace backend; TLS not terminated at the listener.
6. **Configuration tooling.** Deprecated Kustomize fields (`bases`, `patchesStrategicMerge`,
   `patchesJson6902`, `vars`, `commonLabels`); both Kustomize and Helm on one application;
   charts without `values.schema.json`; `helm upgrade` without `--rollback-on-failure`
   (`--atomic` on Helm 3) in pipelines; floating chart repositories or versions; a
   `--post-renderer`, `--enable-exec` or `--enable-alpha-plugins` in a pipeline step.
7. **Secrets.** `kind: Secret` with `data` or `stringData` committed; tokens, passwords or keys
   in `values*.yaml`, kustomizations, env literals; a kubeconfig file in the tree.
8. **GKE fit.** Autopilot incompatibilities (privileged, host network, hostPath, `CAP_NET_RAW`
   needs); Workload Identity (pod `serviceAccountName`, no key mounted); GKE Gateway classes
   and policies; Dataplane V2 assumed for NetworkPolicy.
9. **Rank.** Ten findings at most; merge duplicates across workloads into one with the
   locations.

Severity: `critical` = a secret value committed, a privileged or host-namespace pod in
production, a kubeconfig in the tree; `high` = no resources or probes on a production
workload, `latest`, no NetworkPolicy in a namespace that faces traffic, a pipeline post-renderer
from the repository; `medium` = missing PDB or spread, missing `restricted` label, token mounted
needlessly, deprecated Kustomize fields; `low` = labels, history limits, hygiene.

Confidence: `high` = seen in the rendered output or confirmed by kubeconform; `medium` = seen
in the source, depends on the cluster's admission configuration you cannot read; `low` =
inferred.

## Report

```text
summary: <one line — overlays and charts rendered, kubeconform run or not, worst severity>

findings:
1. <severity> · <file>:<line> · <what> · fix: <exact field and value, from skills/expert-kubernetes/references/manifests.md> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-kubernetes
{"topic": "kubernetes", "skill": "expert-kubernetes", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

No finding without a file and line. Cluster settings you cannot read (admission
configuration, CNI, node pools) go in the summary as "not verifiable from the tree". Zero
findings is a valid result; say what was checked.
