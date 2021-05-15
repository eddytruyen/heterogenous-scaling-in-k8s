for i in `seq 1 10`
 do 
  rm -r Results/exp3/silver/*
  sed "s/indow: 1/indow: $i/g" conf/matrix-spark.yaml > conf.yaml
  #x=expr $i-1 
  #echo $x
  #mv nohup.out nohup-searchwindow$x.out
  python -u matrix.py conf.yaml > nohup-searchwindow-tc2-$i.out
  cp Results/matrix.yaml data/matrix-spark-150-tc2-shrdrpl2-searchwindow$i.yaml
  ./store-report.sh exp3 silver 
  echo `wc -l Results/exp3/silver/reports.csv` >> samples-tc2-shrdrpl2
# ./store-result.sh exp3 silver
#  mv Results/exp3/silver/results3.json dataset/results-tc3-$i.json 
  #mv nohup.out nohup-searchwindow$i.out
 done
