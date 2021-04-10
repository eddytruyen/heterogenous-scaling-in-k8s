for i in 4 5 6 7 8 9
 do 
  sed "s/indow: 1/indow: $i/g" conf/matrix-spark.yaml > conf.yaml
  #x=expr $i-1 
  #echo $x
  #mv nohup.out nohup-searchwindow$x.out
  python -u matrix.py conf.yaml > nohup-searchwindow$i.out
  cp Results/matrix.yaml data/matrix-spark-150-searchwindow$i.yaml
  #mv nohup.out nohup-searchwindow$i.out
 done
