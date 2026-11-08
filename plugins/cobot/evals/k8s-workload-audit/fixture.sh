#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A Deployment with the findings the consult
# must name: a latest tag, a privileged container, no resources, no probes, and no NetworkPolicy.
set -euo pipefail
mkdir -p k8s
cat > k8s/deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: shop
  labels:
    app.kubernetes.io/name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: web
  template:
    metadata:
      labels:
        app.kubernetes.io/name: web
    spec:
      containers:
        - name: web
          image: nginx:latest
          ports:
            - containerPort: 80
          securityContext:
            privileged: true
YAML
cat > k8s/service.yaml <<'YAML'
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: shop
spec:
  selector:
    app.kubernetes.io/name: web
  ports:
    - port: 80
      targetPort: 80
YAML
cat > k8s/namespace.yaml <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: shop
YAML
