mr=`cat /etc/podinfo/mem_request`
exec_overhead_gb=$(($mr / 10))
exec_mem=$(($mr - ${exec_overhead_gb}))
sed "s/executor-memory = \".*G\"/executor-memory = \"${exec_mem}G\"/g" examples/output.conf > examples/tmp.conf
exec_overhead_mb=$((${exec_overhead_gb} * 1024))
sed  -i "s/spark.executor.memoryOverhead = \".*\"/spark.executor.memoryOverhead = \"${exec_overhead_mb}\"/g" examples/tmp.conf
./bin/spark-bench.sh examples/tmp.conf
