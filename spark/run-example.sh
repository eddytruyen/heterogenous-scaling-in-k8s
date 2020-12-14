PARTITIONS=${1:-5}

EXAMPLE_JAR=$(kubectl exec -ti --namespace default my-release-spark-worker-0 -- find examples/jars/ -name 'spark-example*\.jar' | tr -d '\r')

kubectl exec -ti --namespace default my-release-spark-worker-0 -- spark-submit  --master spark://my-release-spark-master-svc:7077 --class org.apache.spark.examples.SparkPi $EXAMPLE_JAR $PARTITIONS
