#!/bin/bash
namespace=$1
valuesFile="/tmp/k8-resource-optimizer/charts/silver-spark/values.yaml"
fileName="/tmp/values.yaml"

cp $valuesFile $fileName

function str_to_int {
  echo $(( 0x$(echo -n "$1" | sha1sum | cut -d " " -f 1) % $2 ))
}

#cat $fileName
#cpu_size=0
kubectl get pod spark-client-0 -n $namespace -o yaml > old_pod.yaml
old_memory_size=$(grep 'memory: .*Gi' old_pod.yaml | head -1 | cut -d ":" -f2)
echo "Old memory size: " $old_memory_size
memory_size=0
for i in `seq 4`
        do
                keyName1=worker$i
		keyName2=replicaCount
		value=$(yq -r ".${keyName1}.${keyName2}" $fileName) 
                replicas=$((value))
                if [ $replicas -gt 0 ]
                then
                        #cpuKeyName=worker$i.resources.requests.cpu
                        #valueCpu=$(grep $cpuKeyName $fileName | cut -d ":" -f2)
                        #cpu_size=$((valueCpu))
                        memKeyName=worker$i
                        valueMemory=$(yq -r ".${memKeyName}.resources.requests.memory" $fileName)
                        memory_size=${valueMemory}
			echo $memory_size
                fi
        done
echo "New memory size: " $memory_size
if [ ! ${memory_size} == $old_memory_size ]
then
	#sed "s/cpu: 2/cpu: $valueCpu/g" spark-client/spark-client.yaml | sed "s/memory: 2/memory: $valueMemory/g" > tmp.yaml
	kubectl get statefulset spark-client -n $namespace -o yaml > old_ss.yaml
	sed "s/memory: 2Gi/memory: $memory_size/g"  old_ss.yaml > tmp.yaml
	#kubectl delete pod spark-client-0 -n silver
	kubectl replace -f tmp.yaml -n $namespace
	kubectl wait --for=delete  pod/spark-client-0 -n $namespace --timeout=120s
	sleep 5
	kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
	rm old_ss.yaml
	rm tmp.yaml
fi
rm $fileName
rm old_pod.yaml
