#!/bin/sh
namespace=$1
releasename=$2
workload=$3
tenantgroup=$4
outputdir=$5
if [ ! -d $outputDir ]
then
        mkdir $outputDir
fi
kubectl cp $releasename-worker-0:spark_data/spark-bench/results-$workload-g$tenantgroup-t-*.csv" "$outputdir" -n $namespace

