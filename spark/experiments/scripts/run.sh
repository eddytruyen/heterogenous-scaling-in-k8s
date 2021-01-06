#!/bin/bash

nrofTenants=$1
startingTenantId=${2:-1}

lastTenantId=$(($nrofTenants + ($startingTenantId - 1)))
nrofPartitions=0
tenantGroup=2
for i in `seq $startingTenantId $lastTenantId`
do
  kubectl scale stateful my-release-spark-worker --replicas=$i
  sleep 60
  ./generate_script $i $nrOfPartitions $tenantGroup output.conf
  sudo cp output.conf /mnt/nfs-disk-2/spark-bench/examples
  kubectl exec -it my-release-spark-worker-0 -- runuser -u spark spark_data/spark-bench/bin/spark-bench.sh spark_data/spark-bench/examples/output.conf
  sleep 5400  
done
