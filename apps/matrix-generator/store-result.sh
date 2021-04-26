#$1 directory exp
#$2 namespace/sla name

x=`pwd`
cd Results/$1/$2/
rm results*.json
find . | grep results.json > files
for i in `cat files`; do sed -z 's;false}},{"bench;false}}\n{"bench;g' $i | sed -z 's;true}},{"bench;true}}\n{"bench;g' > $i-cr ; done
for i in `cat files`; do sort $i-cr -o $i-srt; done
y=$(head -n 1 files)
cat $y-srt > results1.json
sed -i 1d files
for i in `cat files`; do echo $i; comm -13 $y-srt $i-srt >> results1.json; done
rm files
sed  -z 's;false}}\n{"bench;false}},{"bench;g' results1.json |  sed -z 's;true}}\n{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n\[{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n\[{"bench;true}},{"bench;g' > results3.json
sed  -z 's;false}}\n\[{"bench;false}},{"bench;g' results3.json |  sed -z 's;true}}\n\[{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n{"bench;true}},{"bench;g' > results3.json
cd $x
