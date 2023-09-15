#!/bin/bash

tenantGroup=7
startingTenantId=$1
lastTenantId=$2
namespace=$3
new_csv_file=${4:-2}
workload=${5:-sql}
executorMemory=${6:-0}
csv_output=csv_output_file.csv
matrixFile=/home/udits/githubrepos/heterogenous-scaling-in-k8s/apps/matrix-generator/conf/matrix-spark.yaml

if [ $lastTenantId -lt $startingTenantId ]
then
	increment=-1

else
	increment=1	
fi
clientmode=`grep '\/\/deploy' $workload/header | wc -l` 
#kubectl create -f spark-client/ -n $namespace
#kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
if [ $new_csv_file -eq 1 ]
then
	echo "workload,namespace,nb_of_tenants,config,resource_size,completion_time" > $csv_output
fi

for i in `seq $startingTenantId $increment $lastTenantId`
do
  #nrOfPartitions=$(($i * 2))
  echo loops... $startingTenantId $increment $lastTenantId
  nrOfPartitions=0
  #2 cores per tenant
  if [ $i -eq $startingTenantId ] && [ $new_csv_file -eq 1 ]
     then
	./$workload/generate_script.sh $i $executorMemory $nrOfPartitions $tenantGroup "output.conf"
        sudo cp ./$workload/output.conf data/output.conf
        sudo cp $matrixFile data/matrix-spark.yaml
        # get data dimensions & query complexity from output.conf
        # consult performance model & receive output as totalCPU totalMEMORY
        # 
        # rescale namespace tenantnb slo previous_tenant previous_confs workload csv exit_program totalCPU totalMEMORY
        period=`cat period`
        previous_conf=`cat new_previous_conf`
        previous_tenants=`cat previous_tenants`
	echo prediction...
        /home/udits/sw/anaconda3/envs/scale/bin/python src/predict.py $namespace $i $period $previous_tenants $previous_conf $workload $csv_output

        # ./rescale.sh $namespace $i $total_cpu $total_mem

        #sudo rm /data/output.conf
        #sudo rm /data/matrix-spark.yaml
#         ./rescale.sh $namespace $i
     else
	 period=`cat period`
	 previous_conf=`cat new_previous_conf`
	 previous_tenants=`cat previous_tenants`
	 #/home/udits/sw/anaconda3/envs/scale/bin/python src/predict.py $namespace $i $period $previous_tenants $previous_conf $workload $csv_output
	 ./rescale.sh $namespace $i $period $previous_tenants $previous_conf $workload $csv_output
  fi
  echo Waiting for workers to become ready
  sleep 30
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
  echo $i > previous_tenants
  echo "generating script for $i tenants"
  ./$workload/generate_script.sh $i $executorMemory $nrOfPartitions $tenantGroup "output.conf"
  sudo cp ./$workload/output.conf /mnt/nfs-disk-2/spark-bench/
  echo "executing script for $i tenants"
  client=spark-client-0
  t1=`date +%s` 
  kubectl exec -it -n $namespace $client -- runuser -u spark spark_data/spark-bench/run-bench.sh $namespace $namespace-spark $workload $tenantGroup
  t2=`date +%s`
  echo $(($t2 - $t1)) > period
  ./parse-results.sh /mnt/nfs-disk-2/spark-bench/ $workload $tenantGroup results-tenants-$i/ $i 
  success=`cat success`
  if [ $success != "true" ]
  then
	  echo 999999999 > period
  fi

  #if [ $period -lt 120 ]; then echo "sleeping for 5400 sec"; sleep 5400; fi	 
done
if [[ $new_csv_file -eq 0 ]]
then
	 period=`cat period`
         previous_conf=`cat new_previous_conf`
         previous_tenants=`cat previous_tenants`
	./rescale.sh $namespace $lastTenantId $period $previous_tenants $previous_conf $workload $csv_output 1
fi
#kubectl delete  -f spark-client/ -n $namespace
