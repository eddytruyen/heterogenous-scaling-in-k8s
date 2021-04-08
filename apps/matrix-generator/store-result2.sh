#$1 directory exp
#$2 namespace/sla name
#$3 number of tenants to be updated

x=`pwd`
cd Results/$1/$2/
#rm results1.json
#rm results2.json
#find . | grep results.json-srt > files
#for i in `cat files`; do echo $i; done
#for i in $files; do sed 's;false}},{"bench;false}}\n{"bench;g' $i | sed 's;true}},{"bench;true}}\n{"bench;g' > $i-cr ; done
#for i in $files; do sort $i-cr -o $i-srt; done
#y=$(head -n 1 files)
#cat $y > results1.json
#sed -i 1d files
#for i in `cat files`; do comm -13 $y $i >> results1.json; done
#rm files
sed  -z 's;false}}\n{"bench;false}},{"bench;g' results1.json |  sed -z 's;true}}\n{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n\[{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n\[{"bench;true}},{"bench;g' > results3.json
sed  -z 's;false}}\n\[{"bench;false}},{"bench;g' results3.json |  sed -z 's;true}}\n\[{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n{"bench;true}},{"bench;g' > results3.json
cd $x

