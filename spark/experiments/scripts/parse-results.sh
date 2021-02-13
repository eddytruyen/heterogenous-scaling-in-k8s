#!/bin/sh
benchpath=$1
workload=$2
tenantgroup=$3
outputdir=$4
if [ ! -d $outputDir ]
then
        mkdir $outputDir
fi
echo cp -r ${benchpath}results-$workload-g$tenantgroup-t-*.csv $outputdir
cp -r ${benchpath}results-$workload-g$tenantgroup-t-*.csv $outputdir

