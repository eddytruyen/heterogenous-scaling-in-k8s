POD=$(kubectl get pods | grep -o  "k8-resource-optimizer-................")
kubectl cp default/$POD:/exp/Results ./Results
