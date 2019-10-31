POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
echo "Copying config to pod: $POD"
kubectl cp ../apps/matrix-generator default/$POD:/exp/
kubectl cp ../charts/exp2app default/$POD:/exp/conf/helm
# kubectl cp ./k8-resource-optimizer default/$POD:/exp/
