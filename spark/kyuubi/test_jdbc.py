import jaydebeapi
import random
import time
import textwrap

database='default'
driver='org.apache.kyuubi.jdbc.KyuubiHiveDriver'
server='172.22.8.106'
principal='anonymous' #change it to your sql user
port=30009
session_id=0

# JDBC connection string
url="jdbc:hive2://" + server + ":" + str(port)

#Connect to HiveServer2
conn=jaydebeapi.connect(driver, url, [principal,""],'kyuubi-hive-jdbc-shaded-1.7.3.jar')
cursor = conn.cursor()

table_id=random.sample([12], 1)[0]
#table_name = f"file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-{table_id}.csv"

#command=textwrap.dedent(f"""
#  SET `kyuubi.operation.language`=`scala`;
#  """)

#cursor.execute(command)

#command=textwrap.dedent(f"""
#  val df = spark.read.format("csv").option("header", "true").load("{table_name}")
#  val e = df.columns
#  e
#  """)

#cursor.execute(command)
#results=cursor.fetchone()
#print(len(results))

# Execute SQL query
x=0
while x < 100000000000:
    sql=f"select c1,c2,c3 from global_temp.kmeans{table_id} where c1 < 1 and c2 < 1 and c3 < 5"
    cursor.execute(sql)
    x = x+1
cursor.close()
conn.close()
#print(results)
