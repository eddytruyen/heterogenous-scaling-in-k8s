#!/bin/sh
benchpath=$1
workload=$2
tenantgroup=$3
outputdir=$4
nrOfTenants=$5
echo "wait till distributed file system is synchronised"
sleep 60
if [ ! -d $outputDir ]
then
        mkdir $outputDir
fi
ls ${benchpath}results-$workload-g$tenantgroup-t-*.csv/_SUCCESS
count=`ls ${benchpath}results-$workload-g$tenantgroup-t-*.csv/_SUCCESS | wc -l`
if [ ! $count -eq $nrOfTenants ] 
then    
	rm -r ${benchpath}results-$workload-g$tenantgroup-t-*.csv
	exit 1
else
	echo cp -r ${benchpath}results-$workload-g$tenantgroup-t-*.csv $outputdir 
	rm -r $outputdir*
	mv ${benchpath}results-$workload-g$tenantgroup-t-*.csv $outputdir
fi

