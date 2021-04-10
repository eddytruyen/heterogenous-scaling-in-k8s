#!/bin/bash
current_dir=`pwd`
scriptdir="$(dirname "$0")"
cd "$scriptdir"

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
  str="c0, " 
  str2="c0 < -0.9"
  for j in `seq $i`; do str1="$str"; str3="$str2"; k="c$(($j + 6))"; str="$str1$k, "; str2="$str3 and $k < -0.9"; done 
  sed "s/x/$tenantGroup/g" fragment | sed "s/y\./$tenantId\./g" | sed "s/c0\, /$str/g" | sed "s/c0 < -0.9/$str2/g" >> tmp  
#  sed "s/x/$tenantGroup/g" fragment | sed "s/y\./$tenantId\./g" >> tmp

done
cat footer >> tmp
if [ $partitions -gt 0 ]
then
 sed -i "s/\/\/partitions = p/partitions = $partitions/g" tmp
fi	
mv tmp $outputFile
cd "$current_dir"
