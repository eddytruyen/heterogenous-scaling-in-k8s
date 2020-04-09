POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
echo "Copying config to pod: $POD"
kubectl cp ../apps/matrix-generator default/$POD:/exp/
