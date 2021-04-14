#$1 directory exp
#$2 namespace/sla name
#$3 number of tenants to be updated

x=`pwd`
cd Results/$1/$2/
rm reports.csv
find . | grep report.csv > files
y=$(head -n 1 files)
cat $y-srt > reports.csv
sed -i 1d files
for i in `cat files`; do echo $i; cp $i tmp-file; sed -i 1d tmp-file; cat tmp-file >> reports.csv; rm tmp-file; done
sed -i '/^$/d' reports.csv
rm files
cd $x

