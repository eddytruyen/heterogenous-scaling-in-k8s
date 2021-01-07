#!/bin/bash

nrofTenants=$1
startingTenantId=${2:-1}
executorMemory=${3:-0}

lastTenantId=$(($nrofTenants + ($startingTenantId - 1)))
nrofPartitions=0
tenantGroup=2
for i in `seq $startingTenantId $lastTenantId`
do
  kubectl scale statefulset my-release-spark-worker --replicas=$i
  sleep 60
  ./generate_script $i $executorMemory $nrOfPartitions $tenantGroup output.conf
  sudo cp output.conf /mnt/nfs-disk-2/spark-bench/examples
  t1=`date +%s` 
  kubectl exec -it my-release-spark-worker-0 -- runuser -u spark spark_data/spark-bench/bin/spark-bench.sh spark_data/spark-bench/examples/output.conf 2> /dev/null
  t2=`date +%s`
  period=$(($t2 - $t1))
  echo $period
  if [ $period -lt 120 ]; then echo "sleeping for 5400 sec"; sleep 5400; fi	 
done
