# expert-kubernetes — manifests ready to copy

Dated lines live in `versions.md`. Replace the image digest from the registry, never invent one.

## Namespace with the restricted profile

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

## Deployment that passes `restricted`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: app
  labels: { app.kubernetes.io/name: api, app.kubernetes.io/part-of: shop }
spec:
  replicas: 3
  revisionHistoryLimit: 3
  strategy: { type: RollingUpdate, rollingUpdate: { maxUnavailable: 0, maxSurge: 1 } }
  selector:
    matchLabels: { app.kubernetes.io/name: api }
  template:
    metadata:
      labels: { app.kubernetes.io/name: api, app.kubernetes.io/version: "1.4.2" }
    spec:
      serviceAccountName: api
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        runAsGroup: 65532
        fsGroup: 65532
        seccompProfile: { type: RuntimeDefault }
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app.kubernetes.io/name: api } }
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app.kubernetes.io/name: api } }
      containers:
        - name: api
          image: europe-west1-docker.pkg.dev/proj/images/api@sha256:REPLACE_WITH_DIGEST
          imagePullPolicy: IfNotPresent
          ports: [{ name: http, containerPort: 8080 }]
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits: { memory: 256Mi }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: [ALL] }
          startupProbe:
            httpGet: { path: /healthz, port: http }
            periodSeconds: 5
            failureThreshold: 24          # 2 minutes for the slowest start
          readinessProbe:
            httpGet: { path: /readyz, port: http }   # touches the dependency the pod serves from
            periodSeconds: 10
          livenessProbe:
            httpGet: { path: /healthz, port: http }  # the process only, never a downstream
            periodSeconds: 20
            timeoutSeconds: 2
          volumeMounts:
            - { name: tmp, mountPath: /tmp }
      volumes:
        - { name: tmp, emptyDir: { sizeLimit: 64Mi } }
---
apiVersion: v1
kind: ServiceAccount
metadata: { name: api, namespace: app }
automountServiceAccountToken: false
---
apiVersion: v1
kind: Service
metadata: { name: api, namespace: app }
spec:
  selector: { app.kubernetes.io/name: api }
  ports: [{ name: http, port: 80, targetPort: http }]
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api, namespace: app }
spec:
  minAvailable: 2
  unhealthyPodEvictionPolicy: AlwaysAllow
  selector: { matchLabels: { app.kubernetes.io/name: api } }
```

## Default deny, then DNS and the one ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: app }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: app }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-ingress, namespace: app }
spec:
  podSelector: { matchLabels: { app.kubernetes.io/name: api } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: gateway } }
      ports: [{ protocol: TCP, port: 8080 }]
```

## HTTPRoute on a shared Gateway (GKE)

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: external, namespace: gateway }
spec:
  gatewayClassName: gke-l7-global-external-managed
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls: { mode: Terminate, certificateRefs: [{ name: shop-tls }] }
      allowedRoutes:
        namespaces: { from: Selector, selector: { matchLabels: { gateway-access: "true" } } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api, namespace: app }
spec:
  parentRefs: [{ name: external, namespace: gateway }]
  hostnames: [api.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /v1 } }]
      backendRefs: [{ name: api, port: 80 }]
```

A route whose `backendRefs` name a Service in another namespace needs a `ReferenceGrant` in
that namespace (`from: HTTPRoute in app`, `to: Service`).

## Kustomize overlay

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: app
resources: [../../base]
components: [../../components/pdb]
images:
  - name: europe-west1-docker.pkg.dev/proj/images/api
    digest: sha256:REPLACE_WITH_DIGEST
patches:
  - path: replicas.yaml
    target: { kind: Deployment, name: api }
configMapGenerator:
  - name: api-config
    files: [config.yaml]
```

Validate: `kustomize build overlays/prod | kubeconform -strict -summary -schema-location default -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'`.

## Helm release in a pipeline (Helm 4)

```sh
helm lint ./chart -f values-prod.yaml
helm template api ./chart -f values-prod.yaml --kube-version 1.36.0 | kubeconform -strict -summary
helm diff upgrade api ./chart -n app -f values-prod.yaml          # plugin; the owner reads it
helm upgrade --install api ./chart -n app --create-namespace -f values-prod.yaml \
  --rollback-on-failure --wait=watcher --timeout 10m --history-max 10   # asks under the gate
```
