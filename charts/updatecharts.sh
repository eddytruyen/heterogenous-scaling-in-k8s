# mv charts that you don't want to change to ..
helm create mychart
mv ~/mychart/Chart.yaml .
rm -r mychart
for i in `ls`; do if [ -d "$i" ]; then 
  cp Chart.yaml $i/chart.yaml 
  x=`awk '/name: / {print $2}' $i/Chart.yaml | tr -d \"` 
  sed -i  "s/name: mychart/name: $x/" $i/chart.yaml  
  mv $i/chart.yaml $i/Chart.yaml 
fi; done
#mv charts in .. back to .
