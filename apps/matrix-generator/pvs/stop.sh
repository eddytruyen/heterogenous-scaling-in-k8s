#!/bin/bash
current_dir=`pwd`
scriptdir="$(dirname "$0")"
cd "$scriptdir"
namespace=${1:-default}
release=${2:-my-release}
min_nodes=${3:-1}

./delete-pvs.sh $namespace $release $min_nodes 
kubectl delete -f local-volume-provisioner.generated.yaml
cd "$current_dir"
