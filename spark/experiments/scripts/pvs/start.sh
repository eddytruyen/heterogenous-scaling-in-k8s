#!/bin/bash
current_dir=`pwd`
scriptdir="$(dirname "$0")"
cd "$scriptdir"
namespace=${1:-default}
min_nodes=${3:-1}

./create-pvs.sh $namespace $min_nodes
kubectl create -f local-volume-provisioner.generated.yaml
cd "$current_dir"
