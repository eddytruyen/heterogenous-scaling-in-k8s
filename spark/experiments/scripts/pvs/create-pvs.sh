#!/bin/bash

namespace=${1:-default}
min_nodes=${2:-1}
echo $namespace
kubectl create -f storageclass.yaml -n $namespace
count=`kubectl get nodes | wc -l`
nodes=$(( $count - ( $min_nodes + 1)))
for i in `seq $nodes`; do sed "s/local-pv/local-pv-$namespace-$i/g" persistentvolume.yaml > pv.yaml; kubectl create -f pv.yaml; done
rm pv.yaml
