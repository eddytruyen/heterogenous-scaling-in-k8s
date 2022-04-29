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

matches_nb=$((`grep -o 'y\.' fragment | wc -l`))

iterations=$(($nrOfTenants - 1))

if [ -f "tmp" ]
then
 rm tmp
fi

cat header >> tmp
if [ $executorMemory -gt 0 ]
then
  executorMemoryOverhead=$((($executorMemory / 10) * 1024))
  sed -i "s/executor-memory = \".*\"/executor-memory = \"${executorMemory}G\"/g" tmp
  sed -i "s/spark.executor.memoryOverhead = \".*\"/spark.executor.memoryOverhead = \"$executorMemoryOverhead\"/g" tmp
fi
sed -i "s/gx/g$tenantGroup/g" tmp
for i in `seq $iterations`
do
#  if [ $i -lt $nrOfTenants ]
#  then	  
  sed -i '$s/\}/\}\,/g' tmp
  tenantId=$(($i + 1))
  variables="c0, c6"
#fi
  queries="c0 < -0.9"
  str="c0, " 
  str2="c0 < -0.9"
  for j in `seq $i`; do str1="$str"; str3="$str2"; k="c$(($j + 6))"; str="$str1$k, "; str2="$str3 and $k < -0.9"; done 
  sed "s/x/$tenantGroup/g" fragment | sed "s/c0\, /$str/g" | sed "s/c0 < -0.9/$str2/g"  >> tmp  
  variables=$variables${str}
  queries=$queries${str2}
#  sed "s/x/$tenantGroup/g" fragment | sed "s/y\./$tenantId\./g" >> tmp
done



cat footer >> tmp
if [ $partitions -gt 0 ]
then
 sed -i "s/\/\/partitions = p/partitions = $partitions/g" tmp
fi	

list=()
xqueries=`shuf -i 1-10 -n $nrOfTenants`
for x in `seq 1 $nrOfTenants`
do
  stop=0
  while [ $stop -eq 0 ] 
  do
    y=`shuf -i 1-10 -n 1`
    stop=1
    for value in "${list[@]}";do
       if [ $value -eq $y ]
       then  #If c exists in sequence 
              stop=0
       fi
    done
  done
  #if [[ ! " ${list[*]} " =~ " ${y} " ]]; then
  list+=($y)
  for m in `seq 1 $matches_nb`
  do
    sed -i "0,/-y\./s/-y\./-$y\./" tmp 
  done
  sed -i "0,/datay\./s/datay\./data$y\./" tmp
  #sed -i "0,s/datax/data${y}/g" tmp
done

#sed "s/y\./$tenantId\./g"

#sed "s/c0\, /$str/g" | sed "s/c0 < -0.9/$str2/g"
mv tmp $outputFile
cd "$current_dir"
