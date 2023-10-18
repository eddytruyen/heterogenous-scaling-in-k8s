 sbin/start-thriftserver.sh --executor-memory 4g --hiveconf hive.server2.thrift.port=9999 --master spark://silver-spark-master-svc.silver.svc.cluster.local:7077 --conf spark.sql.warehouse.dir=file:///opt/bitnami/spark/spark_data/ --conf spark.sql.hive.thriftserver.singleSession=false --conf spark.cores.max=4
bin/beeline -u "jdbc:hive2://localhost:9999"
beeline -u "jdbc:hive2://localhost:10090" --hiveconf livy.server.sessionId=0
