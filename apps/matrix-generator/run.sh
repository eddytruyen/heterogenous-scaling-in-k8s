for i in `seq 10`
 do 
  sed "s/indow: 1/indow: $i/g" conf/matrix-spark.yaml > conf.yaml
  #x=expr $i-1 
  #echo $x
  #mv nohup.out nohup-searchwindow$x.out
  python -u matrix.py conf.yaml > nohup-searchwindow$i.out
  cp Results/matrix.yaml data/matrix-spark-150-b-searchwindow$i.yaml
  ./store-report.sh exp3 silver 
  echo `wc -l Results/exp3/silver/reports.csv` >> samples 
  #mv nohup.out nohup-searchwindow$i.out
 done
