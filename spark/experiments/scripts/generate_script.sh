#!/bin/bash

nrOfTenants=$1
outputFile=$2

if [ -d "$outputFile" ]
then
 rm $outputFile
fi

for i in `seq $nrOfTenants`
do
  cat header >> tmp
  if [ $i -lt 1 ]
  then	  
    sed -i '$ s/\}/\},/g' tmp
  fi    
done
cat footer >> tmp
mv tmp $outputFile

