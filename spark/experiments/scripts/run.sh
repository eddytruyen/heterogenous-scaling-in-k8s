#!/bin/bash

nrofTenants=$1
startingTenantId=${2:-1}
executorMemory=${3:-2}
namespace=${4:-silver}
workload=${5:-sql}
release=${6:-silver-spark}
lastTenantId=$((($nrofTenants - 1) + $startingTenantId))
tenantGroup=2
#clientmode=`grep '\/\/deploy' header | wc -l` 
rm timings.csv 
for i in `seq $startingTenantId $lastTenantId`
do
  #nrOfPartitions=$(($i * 2))
  nrOfPartitions=0
  #2 cores per tenant
  #if [ $clientmode -eq 0 ]
  #then
  #  replicas=$(($i + 1))
    #one replica is added for the driver
  #else
  replicas=$i
  #fi
  echo "scaling to $replicas replicas..."
  kubectl scale statefulset $release-worker --replicas=$replicas -n $namespace
  echo "calculating sleeptime for $replicas replicas to come up"
  sleeptimeFor1Replica=120
  if [ $i -eq $startingTenantId ] 
  then
     sleeptime=$(($replicas * $sleeptimeFor1Replica)) 
  else
    sleeptime=$sleeptimeFor1Replica
  fi
  echo "sleeping for $sleeptime seconds..."
  sleep $sleeptime
  echo "generating script for $i tenants"
  ./$workload/generate_script.sh $i $executorMemory $nrOfPartitions $tenantGroup "output.conf"
  sudo cp ./$workload/output.conf /mnt/nfs-disk-2/spark-bench/
  echo "executing script for $i tenants"
  t1=`date +%s` 
  kubectl exec -it -n $namespace spark-client-0 -- runuser -u spark spark_data/spark-bench/run-bench.sh $namespace $release $workload $tenantGroup
  t2=`date +%s`
  period=$(($t2 - $t1))
  echo Duration for $i tenants: $period
  echo $period >> timings.csv
done
