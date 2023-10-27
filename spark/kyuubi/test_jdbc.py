import jaydebeapi
import random
import time

database='default'
driver='org.apache.kyuubi.jdbc.KyuubiHiveDriver'
server='10.101.146.220'
principal='anonymous' #change it to your sql user
port=10009
session_id=0

# JDBC connection string
url="jdbc:hive2://" + server + ":" + str(port)

#Connect to HiveServer2
conn=jaydebeapi.connect(driver, url, [principal,""],'kyuubi-hive-jdbc-shaded-1.7.3.jar')
cursor = conn.cursor()

table_id=random.sample([12], 1)[0]

# Execute SQL query
x=0
while x < 100000000000:
    sql=f"select c1,c2,c3 from global_temp.kmeans{table_id} where c1 < 1 and c2 < 1 and c3 < 5"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    #results = cursor.fetchall()
    x = x+1
    #time.sleep(1)
conn.close()
print(results)
