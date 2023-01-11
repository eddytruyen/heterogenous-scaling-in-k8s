#!/bin/bash

namespace=${1:-default}
name=${2:-volume}
round=$3
echo $namespace
kubectl create -f storageclass.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq $nodes`; do sed "s/local-pv/local-pv-$namespace-$round-$i/g" persistent$name.yaml > pv.yaml; kubectl create -f pv.yaml; done
