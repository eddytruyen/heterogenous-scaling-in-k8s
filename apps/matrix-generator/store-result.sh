#$1 directory exp
#$2 namespace/sla name
#$3 number of tenants to be updated

x=`pwd`
cd Results/$1/$2/
rm results1.json
rm results2.json
for i in `seq $3`; do for j in 0 1 2 3; do cat ${i}_tenants-ex${j}/op/results.json >> results1.json; done; done
sed "s/false}}\]\[{\"bench/false}},{\"bench/g" results1.json | sed "s/true}}\]\[{\"bench/true}},{\"bench/g"  > results2.json
cd $x

