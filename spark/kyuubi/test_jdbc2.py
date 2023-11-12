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
hive_conf = {"user": principal, "password": ""}
conn=jaydebeapi.connect(driver, url, hive_conf,'kyuubi-hive-jdbc-shaded-1.7.3.jar')
cursor = conn.cursor()

tenant=7

x=0
while x < 100000000000:
   cursor.execute(f"describe global_temp.kmeans{tenant}")
   columns=list(map(lambda x: x[0],cursor.fetchall()))
   print(columns)

   sample_columns=random.sample(columns, random.randint(1, len(columns)-1))

   selected_columns = ", ".join(sample_columns)

   print(selected_columns)

   sample_queries=random.sample(columns, random.randint(0, len(columns)-1))
   sample_values=[random.uniform(-0.1, 0.1) for _ in sample_queries]

   selected_evaluations= " and ".join([f"{string} < {value}" for string, value in zip(sample_queries,sample_values)])

   print(selected_evaluations)


   sql=f"SELECT {selected_columns} FROM global_temp.kmeans{tenant} WHERE {selected_evaluations}"
   cursor.execute(sql)
   print(cursor.fetchall())
   x = x+1
cursor.close()
conn.close()
#print(results)
