{{- range $index, $val := .Values.consumer }}    
apiVersion: extensions/v1beta1
kind: Deployment
namespace: {{.Values.namespace}}
metadata:
  name: consumer-{{$index}}
  namespace: {{.Values.namespace}}
spec:
  replicas: {{.Values.workerReplicas}}
  template:
    metadata:
      labels:
        app: consumer
    spec:
      containers:
      - name: consumer
        image: matthijskaminski/consumer:latest
        imagePullPolicy: Always
        resources:
          requests:
            cpu: {{$val.cpu}}
          limits:
            cpu: {{$val.cpu}}
        env:
        - name: DNS_NAMESPACE
          value: {{.Values.namespace}}
---
{{ end -}}
