current_dir=`pwd`
scriptdir="$(dirname "$0")"
cd "$scriptdir"

namespace=$1
releasename=$2
workload=$3
tenantgroup=$4
outputdir=$5
rm -r results-$workload-g$tenantgroup-t-*.csv
mr=`cat /etc/podinfo/mem_request`
exec_overhead_gb=$(($mr / 10))
exec_mem=$(($mr - ${exec_overhead_gb}))
sed "s/executor-memory = \".*G\"/executor-memory = \"${exec_mem}G\"/g" output.conf | sed "s/Release-master-svc.Namespace/$releasename-master-svc.$namespace/g" > tmp.conf
exec_overhead_mb=$((${exec_overhead_gb} * 1024))
sed  -i "s/spark.executor.memoryOverhead = \".*\"/spark.executor.memoryOverhead = \"${exec_overhead_mb}\"/g" tmp.conf
./bin/spark-bench.sh tmp.conf  2> run.log
if [ ! -d $outputDir ] 
then
	mkdir $outputDir
fi
cp -r results-$workload-g$tenantgroup-t-*.csv $outputdir
cd "$current_dir"
