#!/bin/bash
namespace=$1
nb_of_tenants=$2
fileName=values.json
resourcePlannerURL=http://172.17.13.119:30681

function str_to_int {
  echo $(( 0x$(echo -n "$1" | sha1sum | cut -d " " -f 1) % $2 ))
}

curl "$resourcePlannerURL/conf?namespace=$namespace&tenants=$nb_of_tenants" > $fileName 
sed -i 's/\"//g' $fileName
sed -i 's|,|\n|g' $fileName
for i in `seq 4`
	do
		keyName=worker$i.replicaCount
		value=$(grep $keyName $fileName | cut -d ":" -f2)
		replicas=$((value))
		echo $replicas
		kubectl scale statefulset $namespace-spark-worker$i --replicas=$replicas -n $namespace
	done
rm $fileName	
