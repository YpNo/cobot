#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. Mesh policies with the findings the consult
# must name: PERMISSIVE mesh-wide, an allow-all AuthorizationPolicy, a DestinationRule that
# disables TLS.
set -euo pipefail
mkdir -p mesh
cat > mesh/peer-authentication.yaml <<'YAML'
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: PERMISSIVE
YAML
cat > mesh/authz.yaml <<'YAML'
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: api-access
  namespace: shop
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: api
  action: ALLOW
  rules:
    - {}
YAML
cat > mesh/destination-rule.yaml <<'YAML'
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: api
  namespace: shop
spec:
  host: api.shop.svc.cluster.local
  trafficPolicy:
    tls:
      mode: DISABLE
YAML
cat > mesh/namespace.yaml <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: shop
  labels:
    istio-injection: enabled
YAML
