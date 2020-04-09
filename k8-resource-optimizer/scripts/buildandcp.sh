cd cmd
echo "Building linux binary..."
env GOOS=linux go build -o ../bin/k8-resource-optimizer
cd ..
POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
echo "Copying binary and config to pod: "$POD"..."
kubectl cp bin/k8-resource-optimizer default/$POD:/exp
kubectl cp conf default/$POD:/exp/
echo "Done."


