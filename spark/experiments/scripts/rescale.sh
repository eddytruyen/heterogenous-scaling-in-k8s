#!/bin/bash
namespace=$1
nb_of_tenants=$2
completion_time=${3:-0}
previous_tenant_nb=${4:-0}
previous_conf=${5:-"no"}
fileName=values.json
resourcePlannerURL=http://172.17.13.119:80

function str_to_int {
  echo $(( 0x$(echo -n "$1" | sha1sum | cut -d " " -f 1) % $2 ))
}

#curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=149&previoustenants=2&previousconf=2_0_0_0"
if [ ! $previous_conf == "no" ]
then
	echo "previous_conf"
	curl "$resourcePlannerURL/conf?namespace=$namespace&tenants=$nb_of_tenants&completiontime=$completion_time&previoustenants=$previous_tenant_nb&previousconf=$previous_conf" > $fileName
else
	curl "$resourcePlannerURL/conf?namespace=$namespace&tenants=$nb_of_tenants" > $fileName	
fi
sed -i 's/\"//g' $fileName
sed -i 's|,|\n|g' $fileName
sed -i 's/{//g' $fileName
sed -i 's/}//g' $fileName
cat $fileName
#cpu_size=0
kubectl get pod spark-client-0 -n $namespace -o yaml > old_pod.yaml
old_memory_size=$(grep 'memory: .*Gi' old_pod.yaml | head -1 | cut -d ":" -f2)
echo "Old memory size: " $old_memory_size
memory_size=0
for i in `seq 4`
        do
		kubectl get statefulset $namespace-spark-worker$i -n $namespace -o yaml > old_ss.yaml
	        old_replicas=#get number of replicas of ss
		old_cpu_size=#get cpu of ss
		old_memory_size=#get memory of ss 	
                keyName=worker$i.replicaCount
                value=$(grep $keyName $fileName | cut -d ":" -f2)
                replicas=$((value))
                echo $replicas
                if [ $replicas -gt 0 ]
                then
                        cpuKeyName=worker$i.resources.requests.cpu
                        valueCpu=$(grep $cpuKeyName $fileName | cut -d ":" -f2)
                        cpu_size=$((valueCpu))
                        memKeyName=worker$i.resources.requests.memory
                        valueMemory=$(grep $memKeyName $fileName | cut -d ":" -f2)
                        memory_size=$valueMemory
			if [ $old_replicas -eq 0 ]
			then	
				replace=false
				if [ ! $cpu_size -eq $old_cpu_size ]
				then	
					replace=true
					sed -i "s/cpu: $old_cpu_size/cpu: $cpu_size" old_ss.yaml
				fi
				if [ ! $memory_size -eq $old_memory_size ]
                                then
					replace=true
                                        sed -i "s/memory: $old_memory_size/cpu: $memory_size" old_ss.yaml
                                fi
				if [ replace == true ]
				then
					kubectl replace -f old_ss.yaml
				fi
				rm old_ss.yaml

                fi
        done
echo "New memory size: " $memory_size
if [ ! ${memory_size}Gi == $old_memory_size ]
then
	#sed "s/cpu: 2/cpu: $valueCpu/g" spark-client/spark-client.yaml | sed "s/memory: 2/memory: $valueMemory/g" > tmp.yaml
	kubectl get statefulset spark-client -n $namespace -o yaml > ss.yaml
	sed "s/memory: 2/memory: $memory_size/g" ss.yaml > tmp.yaml
	kubectl replace -f tmp.yaml -n $namespace
	kubectl wait --for=delete  pod/spark-client-0 -n $namespace --timeout=120s
	kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
	rm ss.yaml
	rm tmp.yaml
fi
rm old_pod.yaml
new_previous_conf=""
for i in `seq 4`
	do
		keyName=worker$i.replicaCount
		value=$(grep $keyName $fileName | cut -d ":" -f2)
		if [ i -eq 4 ]
		then
			new_previous_conf=$previous_conf${value}_
		else
			new_previous_conf=$previous_conf${value}
		fi
		replicas=$((value))
		echo $replicas
		kubectl scale statefulset $namespace-spark-worker$i --replicas=$replicas -n $namespace
	done
rm $fileName
echo new_previous_conf > new_previous_conf
