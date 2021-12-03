#!/bin/bash
namespace=$1
nb_of_tenants=$2
completion_time=${3:-0}
previous_tenant_nb=${4:-0}
previous_conf=${5:-"no"}
workload=${6:-sql}
csv_output=${7:-csv_output_file.csv}
exit_program=${8:-1}
fileName=values.json
resourcePlannerURL=http://172.17.13.119:80
alphabetLength=$((4))

function str_to_int {
  echo $(( 0x$(echo -n "$1" | sha1sum | cut -d " " -f 1) % $2 ))
}
start=0
#curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=149&previoustenants=2&previousconf=2_0_0_0"
if [ ! $previous_conf == "no" ]
then
	echo "previous_conf"
	curl "$resourcePlannerURL/conf?namespace=$namespace&tenants=$nb_of_tenants&completiontime=$completion_time&previoustenants=$previous_tenant_nb&previousconf=$previous_conf" > $fileName
else
	curl "$resourcePlannerURL/conf?namespace=$namespace&tenants=$nb_of_tenants" > $fileName
	start=1	
fi
sed -i 's/\"//g' $fileName
sed -i 's|,|\n|g' $fileName
sed -i 's/{//g' $fileName
sed -i 's/}//g' $fileName
cat $fileName
#cpu_size=0
kubectl get statefulset spark-client -n $namespace -o yaml > old_pod.yaml
old_memory_size_client=$(grep 'memory: .*Gi' old_pod.yaml | head -1 | cut -d ":" -f2 |  tr -d '"' | xargs)
echo 
echo Old memory size spark_client: $old_memory_size_client
memory_size=0
old_conf=""
new_conf=""
old_resource_size=""
for i in `seq $alphabetLength`
	do
		kubectl get statefulset $namespace-spark-worker$i -n $namespace -o yaml > old_ss$i.yaml
		value=$(grep 'replicas: .*' old_ss$i.yaml | head -1 | cut -d ":" -f2 | tr -d '"')
		old_replicas=$((value))
		#get number of replicas of ss
                if [ $i -eq $alphabetLength ]
                then
                        old_conf=$old_conf${old_replicas}
                else
                        old_conf=$old_conf${old_replicas}_
                fi

		value=$(grep 'cpu: .*' old_ss$i.yaml | head -1 | cut -d ":" -f2 | tr -d '"')
		old_cpu_size=$((value))
		#get cpu size 
		old_memory_size=$(grep 'memory: .*Gi' old_ss$i.yaml | head -1 | cut -d ":" -f2 | tr -d '"' | xargs)
		old_resource_size=${old_resource_size}c${old_cpu_size}m${old_memory_size}_
		#get memory of ss 	
                keyName=worker$i.replicaCount
                value=$(grep $keyName $fileName | cut -d ":" -f2)
                replicas=$((value))
		new_conf=${new_conf}${replicas}_
                if [ $replicas -gt 0 ]
                then
                        cpuKeyName=worker$i.resources.requests.cpu
                        valueCpu=$(grep $cpuKeyName $fileName | cut -d ":" -f2)
                        cpu_size=$((valueCpu))
                        memKeyName=worker$i.resources.requests.memory
                        valueMemory=$(grep $memKeyName $fileName | cut -d ":" -f2 | xargs)
                        memory_size=$valueMemory
			if [ ! $previous_conf == "no" ]  
			#&& [ $old_replicas -eq 0 ]
			# && [ $nb_of_tenants -gt $previous_tenant_nb 
			then	
				echo "cpu size: $old_cpu_size -> $cpu_size"
                                echo "memory size: ${old_memory_size} -> ${memory_size}Gi"
				replace=false
				if [ $cpu_size -ne $old_cpu_size ]
				then	
					echo "Replacing CPU"
					replace=true
					sed -i "s/cpu: \"$old_cpu_size\"/cpu: \"$cpu_size\"/g" old_ss$i.yaml
				fi
				if [ ${memory_size}Gi != ${old_memory_size} ]
                                then
					echo "Replacing memory"
					replace=true
                                        sed -i "s/memory: ${old_memory_size}/memory: ${memory_size}Gi/g" old_ss$i.yaml
                                fi
				if [ $replace = true ]
				then
					echo "Vertical scaling of worker$i"
					echo "cpu size: $old_cpu_size -> $cpu_size"
					echo "memory size: ${old_memory_size} -> ${memory_size}Gi"
					kubectl replace -f old_ss$i.yaml
				fi
				#rm old_ss.yaml
			fi
        	fi        
	done
if [ $start -ne 1 ]
then
	old_resource_size=${old_resource_size::-1}
	echo ${workload},${namespace},${previous_tenant_nb},${previous_conf},${old_resource_size},${completion_time} >>  $csv_output
	if [ $((exit_program)) -eq 1 ]
	then
		exit
	fi
fi

echo "New memory size: " $memory_size
if [ $memory_size -ne 0 ] && [ ${memory_size}Gi != $old_memory_size_client ]
then
	#sed "s/cpu: 2/cpu: $valueCpu/g" spark-client/spark-client.yaml | sed "s/memory: 2/memory: $valueMemory/g" > tmp.yaml
	kubectl get statefulset spark-client -n $namespace -o yaml > ss_client.yaml
	sed "s/memory: .*Gi/memory: ${memory_size}Gi/g" ss_client.yaml > tmp.yaml
	kubectl replace -f tmp.yaml -n $namespace
	kubectl wait --for=delete  pod/spark-client-0 -n $namespace --timeout=120s
	kubectl wait --for=condition=Ready  pod/spark-client-0 -n $namespace  --timeout=120s
	rm ss_client.yaml
	rm tmp.yaml
fi
for i in `seq $alphabetLength`
	do
		keyName=worker$i.replicaCount
		value=$(grep $keyName $fileName | cut -d ":" -f2)
		replicas=$((value))
		old_replicas_str=$(echo $old_conf | cut -d "_" -f$i)
		old_replicas=$((old_replicas_str))
		if [ ! $replicas -eq $old_replicas ]
		then
			echo "Horizontal scaling worker$i: $old_replicas -> $replicas"
			kubectl scale statefulset $namespace-spark-worker$i --replicas=$replicas -n $namespace
			if [ $start -eq 1 ] && [ ! $replicas -eq 0 ]
			then
				echo Starting up...
				kubectl wait --for=condition=Ready  pod/$namespace-spark-worker$i-$((replicas-1)) -n $namespace  --timeout=120s
			fi

		fi
	done
rm $fileName
rm old_pod.yaml
echo ${new_conf::-1} > new_previous_conf
