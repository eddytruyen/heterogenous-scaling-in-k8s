#$1 directory exp
#$2 namespace/sla name
#$3 number of tenants to be updated

x=`pwd`
cd src
#find . | grep 'results.*json' > files
#cat files
#for i in `cat files`; do sed -z 's;false}},{"bench;false}}\n{"bench;g' $i | sed -z 's;true}},{"bench;true}}\n{"bench;g' > $i-cr ; done
#echo 2
#for i in `cat files`; do sort $i-cr -o $i-srt; done
#echo 3
#y=$(head -n 1 files)
#echo $y
#cat $y-srt > results1.json
#echo 5
#sed -i 1d files
#for i in `cat files`; do echo $i; comm -13 $y-srt $i-srt >> results1.json; done
#rm files
sed  -z 's;false}}\n{"bench;false}},{"bench;g' results1.json |  sed -z 's;true}}\n{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n\[{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n\[{"bench;true}},{"bench;g' > results3.json
sed  -z 's;false}}\n\[{"bench;false}},{"bench;g' results3.json |  sed -z 's;true}}\n\[{"bench;true}},{"bench;g' > results2.json
sed  -z 's;false}}\]\n{"bench;false}},{"bench;g' results2.json |  sed -z 's;true}}\]\n{"bench;true}},{"bench;g' > results3.json
cd $x

