#!/bin/bash

namespace=${1:-default}
round=$2
echo $namespace
kubectl create -f storageclass.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq $nodes`; do sed "s/local-pv/local-pv-$namespace-$round-$i/g" persistentvolume_client.yaml > pv.yaml; kubectl create -f pv.yaml; done
