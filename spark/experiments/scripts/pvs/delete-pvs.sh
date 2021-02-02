#!/bin/bash

namespace=${1:-default}
release=${2:-my-release}
min_nodes=${3:-1}
echo $namespace
echo $release
kubectl delete -f storageclass.yaml -n $namespace
count=`kubectl get nodes | wc -l`
nodes=$(( $count - ( $min_nodes + 1)))
kubectl delete pvc spark-data-${release}-master-0 -n $namespace
for i in `seq  $nodes`; do y=$(( i-1 )); kubectl delete pvc spark-data-${release}-worker-$y -n $namespace; done
for i in  `seq $nodes`; do  sed "s/local-pv/local-pv-${namespace}-$i/g" persistentvolume.yaml > pv.yaml; kubectl delete -f pv.yaml; done
rm pv.yaml
