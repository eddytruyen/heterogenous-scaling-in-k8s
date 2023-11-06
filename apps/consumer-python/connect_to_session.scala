import org.apache.spark.SparkConf
import org.apache.spark.sql.SparkSession

spark.stop()
sc.stop()

val conf = new SparkConf().setMaster("spark://silver-spark-master-svc.silver.svc.cluster.local:7077").setAppName("MyExternalApp")

val session=SparkSession.builder.master("spark://10.107.192.85:7077").config(conf).getOrCreate()

val df = session.read.format("csv").option("header", "true").load("file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-1.csv")
