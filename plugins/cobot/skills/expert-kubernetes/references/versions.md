# expert-kubernetes — versions and dated facts

Format: `- [status date · src: url] claim`. The brief flags version lines after 30 days, idiom
after 90. Refresh: `curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest | jq -r .tag_name`
for kubernetes/kubernetes, helm/helm, kubernetes-sigs/kustomize, kubernetes-sigs/gateway-api,
yannh/kubeconform; the GKE release notes for channel defaults.

## Toolchain

| Tool | Current | Released |
|---|---|---|
| Kubernetes | 1.37.2 (1.36.6, 1.35.10, 1.34.13) | 2026-10-28 |
| Helm | 4.3.1 (3.22.1 last 3.x) | 2026-10-15 |
| kustomize | 5.8.3 | 2026-10-08 |
| Gateway API | 1.7.0 | 2026-10-29 |
| kubeconform | 0.8.0 | 2026-06-04 |
| helm-diff plugin | 3.15.15 | 2026-09-26 |
| kind | 0.33.0 | 2026-08-26 |
| GKE default Rapid / Regular / Stable | 1.37.1 / 1.36.4 / 1.35.8 | notes to 2026-11-03 |

- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes/kubernetes/releases] Latest patches v1.37.2, v1.36.6, v1.35.10, v1.34.13, all 2026-10-28.
- [verified 2026-11-08 · src: https://kubernetes.io/releases/] Release branches are kept for the three most recent minors (1.37, 1.36, 1.35); end of life 1.37 on 2027-10-28, 1.36 on 2027-06-28, 1.35 on 2027-02-28, 1.34 on 2026-10-27.
- [verified 2026-11-08 · src: https://kubernetes.io/releases/version-skew-policy/] kubectl is supported within one minor of kube-apiserver; kubelet may be up to three minors older and never newer; kube-apiserver never skips a minor on upgrade.
- [verified 2026-11-08 · src: https://kubernetes.io/releases/patch-releases/] Monthly patch cadence (next 2026-11-10, 2026-12-15, 2027-01-12); a patch series is supported about fourteen months.
- [verified 2026-11-08 · src: https://api.github.com/repos/helm/helm/releases/latest] Helm v4.3.1 (2026-10-15); newest 3.x v3.22.1 (2026-10-15); 4.4.0 scheduled 2027-01-13 and no further Helm 3 minor releases.
- [verified 2026-11-08 · src: https://helm.sh/blog/helm-4-released/] Helm 4.0.0 shipped 2025-11-12; Helm 3 security fixes until 2026-11-11.
- [verified 2026-11-08 · src: https://helm.sh/docs/topics/version_skew/] Helm 4.3.x supports Kubernetes 1.34 to 1.37 (n-3).
- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest] kustomize/v5.8.3 (2026-10-08); kyaml and api v0.21.3.
- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes-sigs/gateway-api/releases/latest] Gateway API v1.7.0 (2026-10-29): HTTPRoute Retries in Standard; Kubernetes dependencies v0.37.
- [verified 2026-11-08 · src: https://api.github.com/repos/yannh/kubeconform/releases/latest] kubeconform v0.8.0 (2026-06-04).
- [verified 2026-11-08 · src: https://api.github.com/repos/databus23/helm-diff/releases/latest] helm-diff v3.15.15 (2026-09-26).
- [verified 2026-11-08 · src: https://api.github.com/repos/kubernetes-sigs/kind/releases/latest] kind v0.33.0 (2026-08-26).
- [verified 2026-11-08 · src: https://docs.cloud.google.com/kubernetes-engine/docs/release-notes] GKE defaults for new clusters: Rapid 1.37.1-gke.1697000, Regular 1.36.4-gke.2046003, Stable 1.35.8-gke.1439001; minors 1.34 to 1.37 on Rapid and Regular, 1.34 to 1.36 on Stable, 1.32 to 1.37 on Extended.

## Pod security and scheduling

- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/security/pod-security-admission/] Pod Security Admission is stable since v1.25; labels `pod-security.kubernetes.io/<enforce|audit|warn>: <privileged|baseline|restricted>` with optional `…-version`; enforce rejects, audit annotates, warn warns.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/security/pod-security-standards/] Baseline forbids host namespaces, privileged containers, hostPath, seccomp Unconfined and most capability adds; Restricted adds the volume allowlist, `allowPrivilegeEscalation: false`, `runAsNonRoot: true`, an explicit seccomp profile and drop ALL.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/] `allowPrivilegeEscalation` defaults to true when unset and cannot be false with `privileged` or CAP_SYS_ADMIN; container-level securityContext overrides pod-level; an omitted `runAsGroup` means primary group root.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/] QoS Guaranteed (limits equal requests on every container), Burstable, BestEffort; eviction order BestEffort, Burstable, Guaranteed; pod-level resources beta since v1.34.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/] A failed liveness probe restarts the container, a failed readiness probe removes the pod from endpoints; HTTP 200 to 399 is success; readiness runs for the whole lifetime; gRPC probes are plaintext by default.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/] `topologySpreadConstraints` fields `maxSkew`, `topologyKey`, `whenUnsatisfiable` (`DoNotSchedule` default), `labelSelector`, `minDomains`, `matchLabelKeys`; cluster defaults spread by hostname (maxSkew 3) and zone (maxSkew 5) with ScheduleAnyway; not re-balanced on scale-down.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/services-networking/network-policies/] NetworkPolicy needs an enforcing plugin; pods are non-isolated by default; `podSelector: {}` selects every pod in the namespace; `policyTypes` defaults to Ingress plus Egress when egress rules exist; it cannot express TLS, Service names, cluster-wide defaults, logging or explicit denies.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/concepts/configuration/overview/] Prefer Deployments to naked Pods, YAML, one file per set of related objects, omit defaults, `kubectl apply -f dir/ --server-side`.

## Tools

- [verified 2026-11-08 · src: https://helm.sh/docs/topics/charts/] `Chart.yaml` `apiVersion: v2`; required fields apiVersion, name, version; `type: application|library`; `values.schema.json` validated on install, upgrade, lint and template.
- [verified 2026-11-08 · src: https://helm.sh/docs/helm/helm_template/] `helm template` renders locally and fakes in-cluster lookups; `--kube-version` and `--api-versions` set Capabilities; `--disable-openapi-validation` exists, no `--validate`.
- [verified 2026-11-08 · src: https://helm.sh/docs/topics/registries/] OCI: `helm registry login`, `helm push <chart>.tgz oci://host/repo`, `helm install x oci://host/repo/chart --version 0.1.0`.
- [verified 2026-11-08 · src: https://helm.sh/docs/chart_best_practices/values/] Values keys camelCase starting lowercase, flat over nested, strings quoted, every value documented; chart names DNS-1123; SemVer 2; two-space YAML.
- [verified 2026-11-08 · src: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/images/] `images:` entries take `name`, `newName`, `newTag`, `digest` and render `image@sha256:…`.
- [verified 2026-11-08 · src: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/configmapgenerator/] Generated ConfigMaps and Secrets get a content-hash suffix and references are rewritten; `generatorOptions.disableNameSuffixHash: true` disables it.
- [verified 2026-11-08 · src: https://kubectl.docs.kubernetes.io/guides/config_management/components/] A Component (`kustomize.config.k8s.io/v1alpha1`, `kind: Component`) is included through an overlay's `components:` list.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/] kubectl bundles kustomize since 1.14: `kubectl kustomize <dir>`, `kubectl apply -k`, `kubectl diff -k`, `kubectl delete -k`.
- [verified 2026-11-08 · src: https://github.com/yannh/kubeconform] `kubeconform -strict` (no additional properties, no duplicate keys), `-summary`, `-schema-location` (repeatable; CRD catalog `https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json`), `-ignore-missing-schemas`, `-kubernetes-version` (default `master`), `-output json|junit|pretty|tap|text`.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/] `kubectl diff` compares the live configuration with the applied result; exit 0 no differences, 1 differences, >1 error; `KUBECTL_EXTERNAL_DIFF` selects your own diff command.
- [verified 2026-11-08 · src: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_edit/] `kubectl edit` opens the editor named by `KUBE_EDITOR` or `EDITOR`.
- [verified 2026-11-08 · src: https://gateway-api.sigs.k8s.io/implementations/] GKE is Conformant at Gateway conformance v1.6.0; Istio is Conformant for Gateway and Mesh at v1.6.0 (Istio 1.31.0 report).
- [verified 2026-11-08 · src: https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/] ReferenceGrant enables cross-namespace references; without one the reference is invalid; GA since v0.6.0.
