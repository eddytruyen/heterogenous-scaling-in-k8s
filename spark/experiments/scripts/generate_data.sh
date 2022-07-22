for i in `seq 1 15`
 do 
    sed "s/g0-1/g0-$i/g" data-generation.conf > data-generation-output.conf
    bin/spark-bench.sh data-generation-output.conf	 
 done

