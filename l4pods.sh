namespace=$1
label=$2

for c in `kubectl get pods -n $namespace -l $label | sed 's/|/ /' | awk '{print $1, $8}' | tail -n +2`; do kubectl logs -n $namespace $c; done > l
