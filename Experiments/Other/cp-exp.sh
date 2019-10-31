POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
echo "Copying config to pod: $POD"
kubectl cp exp1 default/$POD:/exp/
kubectl cp ./k8-resource-optimizer default/$POD:/exp/
