# expert-service-mesh — policies ready to copy

Dated lines live in `versions.md`. The root namespace is `istio-system` unless the installation
set another.

## Mesh-wide STRICT, with a dated per-namespace exception

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: istio-system }
spec:
  mtls: { mode: STRICT }
---
# migration step only: remove by 2026-12-15 (ticket OPS-123)
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: legacy }
spec:
  mtls: { mode: PERMISSIVE }
---
# one legacy client on one port, dated the same way
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: finance-legacy-port, namespace: finance }
spec:
  selector: { matchLabels: { app: finance } }
  mtls: { mode: STRICT }
  portLevelMtls:
    8080: { mode: PERMISSIVE }     # workload port, not the Service port
```

## Allow nothing, then allow by principal

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: allow-nothing, namespace: app }
spec: {}                           # ALLOW with no rules: nothing matches, everything is denied
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: api-from-web, namespace: app }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: api } }
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/app/sa/web"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/v1/*"]
---
# an exception that must hold whatever ALLOW is added later
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: deny-admin-paths, namespace: app }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: api } }
  action: DENY
  rules:
    - from:
        - source:
            notPrincipals: ["cluster.local/ns/ops/sa/admin"]
      to:
        - operation:
            paths: ["/admin", "/admin/*"]
```

Never: `rules: - {}` (allows all), `source.ipBlocks` behind a load balancer, a second `- from:`
when one rule with two conditions was meant.

## Require a JWT

```yaml
apiVersion: security.istio.io/v1
kind: RequestAuthentication
metadata: { name: jwt, namespace: app }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: api } }
  jwtRules:
    - issuer: "https://accounts.example.com"
      jwksUri: "https://accounts.example.com/.well-known/jwks.json"
      audiences: ["api.example.com"]
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: require-jwt, namespace: app }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: api } }
  action: ALLOW
  rules:
    - from:
        - source:
            requestPrincipals: ["https://accounts.example.com/*"]   # without this a tokenless request passes
      when:
        - key: request.auth.claims[groups]
          values: ["customers"]
```

## Ambient namespace with a waypoint

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    istio.io/dataplane-mode: ambient
    istio.io/use-waypoint: waypoint
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: waypoint
  namespace: app
  labels: { istio.io/waypoint-for: service }
spec:
  gatewayClassName: istio-waypoint
  listeners:
    - name: mesh
      port: 15008
      protocol: HBONE
```

`istioctl waypoint apply -n app --enroll-namespace` writes the same two things (asks). L7
AuthorizationPolicies for ambient target the waypoint or the Service:

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: api-l7, namespace: app }
spec:
  targetRefs:
    - kind: Service
      group: ""
      name: api
  action: ALLOW
  rules:
    - from: [{ source: { principals: ["cluster.local/ns/app/sa/web"] } }]
      to: [{ operation: { methods: ["GET"], paths: ["/v1/*"] } }]
```

## Sidecar namespace on a revision

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    istio.io/rev: 1-31-4          # or asm-managed on Cloud Service Mesh; never beside istio-injection
```

## Telemetry defaults

```yaml
apiVersion: telemetry.istio.io/v1
kind: Telemetry
metadata: { name: mesh-default, namespace: istio-system }
spec:
  accessLogging:
    - providers: [{ name: envoy }]
      filter: { expression: "response.code >= 400" }
  tracing:
    - providers: [{ name: otel }]          # declared in meshConfig.extensionProviders; stackdriver on GCP
      randomSamplingPercentage: 1.0
  metrics:
    - providers: [{ name: prometheus }]
      overrides:
        - match: { metric: REQUEST_COUNT, mode: CLIENT_AND_SERVER }
          tagOverrides:
            request_host: { operation: REMOVE }
```

## Egress: registry only plus one external host

```yaml
# meshConfig.outboundTrafficPolicy.mode: REGISTRY_ONLY (install value), then:
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata: { name: payments-api, namespace: app }
spec:
  hosts: ["api.payments.example"]
  ports: [{ number: 443, name: https, protocol: TLS }]
  resolution: DNS
  location: MESH_EXTERNAL
```

## Checks that go with every change

```sh
istioctl analyze --use-kube=false mesh/                 # silent for the read-only agents
istioctl analyze -n app                                 # against the current context
istioctl x authz check deploy/api -n app                # which policies apply (asks: x)
istioctl proxy-config secret deploy/api -n app          # the certificate the proxy holds
```
