#!/bin/bash

nrOfTenants=$1
executorMemory=${2:-0}
partitions=${3:-0}
tenantGroup=${4:-2}
outputFile=${5:-output.conf}

if [ -f "$outputFile" ]
then
 rm $outputFile
fi

iterations=$(($nrOfTenants - 1))
cat header >> tmp
if [ $executorMemory -gt 0 ]
then
  executorMemoryOverhead=$((($executorMemory / 10) * 1024))
  sed -i "s/executor-memory = \".*\"/executor-memory = \"${executorMemory}G\"/g" tmp
  sed -i "s/spark.executor.memoryOverhead = \".*\"/spark.executor.memoryOverhead = \"$executorMemoryOverhead\"/g" tmp
fi
for i in `seq $iterations`
do
#  if [ $i -lt $nrOfTenants ]
#  then	  
  sed -i '$s/\}/\}\,/g' tmp
  tenantId=$(($i + 1))
#  fi
  sed "s/x/$tenantGroup/g" fragment | sed "s/y\./$tenantId\./g" >> tmp  
done
cat footer >> tmp
if [ $partitions -gt 0 ]
then
 sed -i "s/\/\/partitions = p/partitions = $partitions/g" tmp
fi	
mv tmp $outputFile

