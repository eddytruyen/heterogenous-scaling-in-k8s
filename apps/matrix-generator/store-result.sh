#!/bin/sh
#$1 directory exp
#$2 namespace/sla name

x=`pwd`
cd Results/$1/$2/
rm results*.json
for i in `find . | grep 'results.*-srt'`; do echo "removing $i"; rm $i; done
for i in `find . | grep 'results\.json.*-cr'`; do echo "removing $i"; rm $i; done
find . | grep results.json > files
for i in `cat files`; do echo "cutting $i"; sed -z 's;false}},{"bench;false}}\n{"bench;g' $i | sed -z 's;true}},{"bench;true}}\n{"bench;g' > $i-cr ; done
for i in `cat files`; do echo "sorting $i"; sort $i-cr -o $i-srt; done
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
echo "Storing aggregated results.json"
mv Results/$1/$2/results3.json results.json
echo "Moving the output of the matrix-generator to /tmp/matrix-generator-results"
if [ ! -d /tmp/matrix-generator-results ]
then	
	mkdir /tmp/matrix-generator-results
fi
rm -r /tmp/matrix-generator-results/*
mv Results/$1/$2/* /tmp/matrix-generator-results
