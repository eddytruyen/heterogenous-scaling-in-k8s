#!/bin/bash
namespace=$1
alphabetLength=$((4))


function str_to_int {
  echo $(( 0x$(echo -n "$1" | sha1sum | cut -d " " -f 1) % $2 ))
}

#cat $fileName
#cpu_size=0
kubectl get statefulset spark-client -n $namespace -o yaml > old_pod.yaml
old_memory_size_client=$(grep 'memory: .*Gi' old_pod.yaml | head -1 | cut -d ":" -f2 |  tr -d 'Gi"' | xargs)
memory_size=1000
echo "Old memory size spark_client: " $old_memory_size_client
for i in `seq $alphabetLength`
        do
                kubectl get statefulset $namespace-spark-worker$i -n $namespace -o yaml > old_ss$i.yaml
		replicas=$(grep 'replicas: .*' old_ss$i.yaml | head -1 | cut -d ":" -f2 | tr -d '"')
                if [ $replicas -gt 0 ]
                then
                        #cpuKeyName=worker$i.resources.requests.cpu
                        #valueCpu=$(grep $cpuKeyName $fileName | cut -d ":" -f2)
                        #cpu_size=$((valueCpu))
                        valueMemory=$(grep 'memory: .*Gi' old_ss$i.yaml | head -1 | cut -d ":" -f2 | tr -d 'Gi"' | xargs)
                        echo $valueMemory
			if [ $valueMemory -lt $memory_size ]
			then
				echo Setting smallest memory size to $valueMemory
				memory_size=$valueMemory
			fi
                fi
		rm old_ss$i.yaml
        done
echo "New memory size: " $memory_size
if [ $memory_size -ne $old_memory_size_client ]
then
	#sed "s/cpu: 2/cpu: $valueCpu/g" spark-client/spark-client.yaml | sed "s/memory: 2/memory: $valueMemory/g" > tmp.yaml
	kubectl get statefulset spark-client -n $namespace -o yaml > ss_client.yaml
	sed "s/memory: .*/memory: ${memory_size}Gi/g" ss_client.yaml > tmp.yaml
	
	#kubectl delete pod spark-client-0 -n silver
	kubectl replace -f tmp.yaml -n $namespace
	kubectl delete pod spark-client-0 -n $namespace --force
	kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
	rm ss_client.yaml
	rm tmp.yaml
fi
rm old_pod.yaml
