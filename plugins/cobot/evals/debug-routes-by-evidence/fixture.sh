#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A Deployment whose env key is misspelled
# (DATABSE_URL), and what the owner captured from the `lab` context: describe shows
# CrashLoopBackOff, the previous logs say DATABASE_URL is not set. No cluster, no kubeconfig.
set -euo pipefail
mkdir -p k8s evidence
cat > k8s/deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: shop
  labels:
    app.kubernetes.io/name: api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: api
    spec:
      containers:
        - name: api
          image: europe-docker.pkg.dev/lab/shop/api:1.8.0
          env:
            - name: DATABSE_URL
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: database-url
          resources:
            requests: {cpu: 100m, memory: 128Mi}
            limits: {memory: 256Mi}
YAML
cat > evidence/describe-api.txt <<'TXT'
$ kubectl describe pod api-7d9f8c6b5-x2k4q -n shop --context lab
Name:             api-7d9f8c6b5-x2k4q
Namespace:        shop
Status:           Running
Containers:
  api:
    Image:          europe-docker.pkg.dev/lab/shop/api:1.8.0
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
    Ready:          False
    Restart Count:  14
Events:
  Type     Reason   Age                  From     Message
  Warning  BackOff  2m (x61 over 15m)    kubelet  Back-off restarting failed container api
TXT
cat > evidence/logs-previous.txt <<'TXT'
$ kubectl logs api-7d9f8c6b5-x2k4q -n shop --context lab --previous --tail 20
2026-11-20T08:14:03Z info  api 1.8.0 starting
2026-11-20T08:14:03Z fatal config: DATABASE_URL is not set
TXT
