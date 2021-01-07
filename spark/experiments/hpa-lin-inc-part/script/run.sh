#!/bin/bash

nrofTenants=$1
startingTenantId=${2:-1}
executorMemory=${3:-0}

lastTenantId=$(((2 * $nrofTenants) - $startingTenantId))
tenantGroup=2
clientmode=`grep '\/\/deploy' header | wc -l` 
for i in `seq $startingTenantId $lastTenantId`
do
  nrOfPartitions=$(($i * 2))
  #2 cores per tenant
  if [ $clientmode -eq 0 ]
  then
    replicas=$(($i + 1))
    #one replica is added for the driver
  else
     replicas=$i
  fi
  echo "scaling to $replicas replicas..."
  kubectl scale statefulset my-release-spark-worker --replicas=$replicas
  echo "calculating sleeptime for $replicas replicas to come up"
  sleeptimeFor1Replica=60
  if [ $i -eq $startingTenantId ] 
  then
    sleeptime=$(($replicas * $sleeptimeFor1Replica)) 
  else
    sleeptime=$sleeptimeFor1Replica
  fi
  echo "sleeping for $sleeptime seconds..."
  sleep $sleeptime
  echo "generating script for $i tenants"
  ./generate_script.sh $i $executorMemory $nrOfPartitions $tenantGroup "output.conf"
  sudo cp output.conf /mnt/nfs-disk-2/spark-bench/examples
  echo "executing script for $i tenants"
  t1=`date +%s` 
  kubectl exec -it my-release-spark-worker-0 -- runuser -u spark spark_data/spark-bench/bin/spark-bench.sh spark_data/spark-bench/examples/output.conf 2> /dev/null
  t2=`date +%s`
  period=$(($t2 - $t1))
  if [ $period -lt 120 ]; then echo "sleeping for 5400 sec"; sleep 5400; fi	 
done
