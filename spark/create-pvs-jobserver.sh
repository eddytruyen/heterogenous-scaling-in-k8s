#!/bin/bash

namespace=${1:-default}
echo $namespace
kubectl create -f storageclass-jobserver.yaml -n $namespace
#count=`kubectl get nodes | wc -l`
#nodes=`expr $count - 2`
for i in `seq 2`; do sed "s/local-pv/local-pv-$namespace-$i/g" persistentvolume_client-jobserver.yaml > pv.yaml; kubectl create -f pv.yaml; done
