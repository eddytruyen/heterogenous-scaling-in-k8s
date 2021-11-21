#!/bin/bash

nrofTenants=$1
new_csv_file=${2:-0}
startingTenantId=${3:-1}
executorMemory=${4:-0}
namespace=${5:-silver}
workload=${6:-sql}
new_csv_file=${6:-0}
csv_output=csv_output_file.csv
lastTenantId=$((($nrofTenants - 1) + $startingTenantId))
tenantGroup=2
clientmode=`grep '\/\/deploy' $workload/header | wc -l` 
#kubectl create -f spark-client/ -n $namespace
#kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
if [ $new_csv_file -eq 1 ]
then
	echo "workload,namespace,nb_of_tenants,config,resource_size,completion_time" > $csv_output
fi
for i in `seq $startingTenantId $lastTenantId`
do
  #nrOfPartitions=$(($i * 2))
  nrOfPartitions=0
  #2 cores per tenant
  if [ $i -eq $startingTenantId ]
     then 
         ./rescale.sh $namespace $i
     else
	 previous_conf=`cat new_previous_conf`
	 ./rescale.sh $namespace $i $period $((i-1)) $previous_conf $workload $csv_output
  fi
  #if [ $clientmode -eq 0 ]
  #then`
  #  replicas=$(($i + 1))
  #  #one replica is added for the driver
  #else
  #   replicas=$i
  #fi
  #echo "scaling to $replicas replicas..."
  #kubectl scale statefulset my-release-spark-worker --replicas=$replicas
  #echo "calculating sleeptime for $replicas replicas to come up"
  #sleeptimeFor1Replica=60
  #if [ $i -eq $startingTenantId ] 
  #then
  #   sleeptime=$(($replicas * $sleeptimeFor1Replica)) 
  #else
  #  sleeptime=$sleeptimeFor1Replica
  #fi
  #echo "sleeping for $sleeptime seconds..."
  #sleep $sleeptime
  echo "generating script for $i tenants"
  ./$workload/generate_script.sh $i $executorMemory $nrOfPartitions $tenantGroup "output.conf"
  sudo cp ./$workload/output.conf /mnt/nfs-disk-2/spark-bench/
  echo "executing script for $i tenants"
  client=spark-client-0
  t1=`date +%s` 
  kubectl exec -it -n $namespace $client -- runuser -u spark spark_data/spark-bench/run-bench.sh $namespace silver-spark $workload $tenantGroup
  t2=`date +%s`
  period=$(($t2 - $t1))
  ./parse-results.sh /mnt/nfs-disk-2/spark-bench/ $workload $tenantGroup results-tenants-$i/ $i 
  success=`cat success`
  if [ $success != "true" ]
  then
	  period=999999999
  fi

  #if [ $period -lt 120 ]; then echo "sleeping for 5400 sec"; sleep 5400; fi	 
done
#kubectl delete  -f spark-client/ -n $namespace
