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
#cpu_size=0
kubectl get pod spark-client-0 -n $namespace -o yaml > old_pod.yaml
old_memory_size=$(grep 'memory: .*Gi' old_pod.yaml | head -1 | cut -d ":" -f2)
echo "Old memory size: " $old_memory_size
memory_size=0
for i in `seq 4`
        do
                keyName=worker$i.replicaCount
                value=$(grep $keyName $fileName | cut -d ":" -f2)
                replicas=$((value))
                echo $replicas
                if [ $replicas -gt 0 ]
                then
                        #cpuKeyName=worker$i.resources.requests.cpu
                        #valueCpu=$(grep $cpuKeyName $fileName | cut -d ":" -f2)
                        #cpu_size=$((valueCpu))
                        memKeyName=worker$i.resources.requests.memory
                        valueMemory=$(grep $memKeyName $fileName | cut -d ":" -f2)
                        memory_size=$((valueMemory))
                fi
        done
echo "New memory size: " $valueMemory
if [ ${valueMemory}Gi != $old_memory_size ]
then
	#sed "s/cpu: 2/cpu: $valueCpu/g" spark-client/spark-client.yaml | sed "s/memory: 2/memory: $valueMemory/g" > tmp.yaml
	sed "s/memory: 2/memory: $valueMemory/g"  spark-client/spark-client.yaml > tmp.yaml
	kubectl delete -f spark-client/spark-client.yaml -n $namespace
	kubectl wait --for=delete  pod/spark-client-0 -n $namespace --timeout=120s
	kubectl create -f tmp.yaml -n $namespace
	kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
fi
for i in `seq 4`
	do
		keyName=worker$i.replicaCount
		value=$(grep $keyName $fileName | cut -d ":" -f2)
		replicas=$((value))
		echo $replicas
		kubectl scale statefulset $namespace-spark-worker$i --replicas=$replicas -n $namespace
	done
rm $fileName	
