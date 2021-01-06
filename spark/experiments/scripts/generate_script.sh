#!/bin/bash

nrOfTenants=$1
partitions=${2:-0}
tenantGroup=${3:-2}
outputFile=${4:-output.conf}

if [ -f "$outputFile" ]
then
 rm $outputFile
fi

iterations=$(($nrOfTenants - 1))
cat header >> tmp
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

