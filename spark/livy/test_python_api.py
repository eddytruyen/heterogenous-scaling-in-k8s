from __future__ import print_function
import requests
import json
import random
import pprint
import textwrap

import sys

from livy.client import HttpClient

max_tenants=15
tenant_group="g7"
host = "http://172.22.8.106:30898"

def invoke(command, host, session_id):
    response=requests.post(f"{host}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)
    statement_url = host + response.headers['Location']
    r = requests.get(statement_url, headers=headers)
    status=(r.json())['state']
    while status != "available" :
       r = requests.get(statement_url, headers=headers)
       status=(r.json())['state']
    pprint.pprint(r.json())
    return r

# Definieer de URL van de Livy-server

response = requests.get(f"{host}/sessions", headers={'Content-Type': 'application/json'})
sessions = response.json()['sessions']

headers = {'Content-Type': 'application/json'}

active_sessions=[]
if len(sessions) > 0:
  # Gebruik de eerste actieve sessie
  active_sessions = list(filter(lambda x: x['state']=='idle' or x['state']=='starting',sessions))

if len(active_sessions) > 0:
    session_id=active_sessions[0]['id']
else: 
  data = {'kind': 'pyspark', 'executorMemory': 6442450944, 'executorCores': 4}
  #  {{ .Files.Get "livy.conf" | indent 4 }}
  r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
  session_id = r.json()['id']


print(session_id)




# Wacht tot de sessie actief is
session_url = f"{host}/sessions/{session_id}"
r = requests.get(session_url, headers=headers)
status = r.json()['state']
while status != 'idle':
  r = requests.get(session_url, headers=headers)
  status = r.json()['state']
  print(status)


client = HttpClient(session_url)

def simple_spark_sql_job(context):
    max_tenants=15
    tenant_group="g7"
    tenant = str(random.randint(1, max_tenants))
    table_name = f"file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-{tenant_group}-{tenant}.csv"
    sql_ctx = context.sql_ctx
    df1 = sql_ctx.read.format("csv").option("header", "true").load(table_name)
    df1.createOrReplaceTempView("kmeans" + tenant)
    df1.show()
    return 1 

types = client.submit(simple_spark_sql_job).result()

print(types)

#command = f"""
#sqlDF = spark.sql('SELECT c0, c6 FROM kmeans{tenant} WHERE c6 < 0.9')
#sqlDF.show()
#"""

#invoke(command, host, session_id)



#table_name = "file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-1.csv"

#command = """
#df = spark.read.format("csv").option("header", "true").load("file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-1.csv")
#df.show()
#"""

#command = """
#df = spark.read.format("csv").option("header", "true").load("table_name"))
#df.createOrReplaceTempView("kmeans")
#sqlDF = spark.sql('SELECT * FROM kmeans')
#sqlDF.show()
#""".replace("table_name", table_name)



