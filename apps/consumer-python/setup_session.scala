import org.apache.spark.sql.SparkSession

spark.stop()
sc.stop()

val spark = SparkSession.builder().config("spark.sql.thriftserver.singleSession", "false").config("spark.sql.warehouse.dir", "file:///opt/bitnami/spark/spark_data/").config("spark.master", "spark://silver-spark-master-svc.silver.svc.cluster.local:7077").config("spark.sql.thriftserver.thriftDriver.client", "true").config("spark.driver.allowMultipleContexts", "true").config("hive.server2.thrift.port", "9999").config("spark.cores.max", 4).getOrCreate()

import spark.implicits._


val df = spark.read.format("csv").option("header", "true").load("spark_data/spark-bench-test/kmeans-data-g7-1.csv")

df.createOrReplaceGlobalTempView("kmeans1")

val sqlDF = spark.sql("SELECT c1 FROM global_temp.kmeans1")
sqlDF.show()


import org.apache.spark.SparkConf
import org.apache.spark.SparkContext

val conf = new SparkConf().setMaster("spark://silver-spark-master-svc.silver.svc.cluster.local:7077").setAppName("test")

conf.set("spark.scheduler.mode", "FAIR")

sc.stop()

val sc = new SparkContext(conf)
