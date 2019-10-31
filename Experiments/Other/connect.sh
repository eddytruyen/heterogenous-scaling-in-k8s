POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
echo "Starting interactive bash shell in pod: "$POD"..."
kubectl exec -it $POD -- bin/bash