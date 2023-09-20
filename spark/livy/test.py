import requests
import json
import random
import pprint
import textwrap

# Definieer de URL van de Livy-server
host = "http://172.22.8.106:30898"

response = requests.get(f"{host}/sessions", headers={'Content-Type': 'application/json'})
sessions = response.json()['sessions']

headers = {'Content-Type': 'application/json'}

if len(sessions) > 0:
  # Gebruik de eerste actieve sessie
  session_id = sessions[0]['id']
else:
  data = {'kind': 'pyspark'}
  #  {{ .Files.Get "livy.conf" | indent 4 }}
  r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
  session_id = r.json()['id']



# Wacht tot de sessie actief is
session_url = f"{host}/sessions/{session_id}"
r = requests.get(session_url, headers=headers)
status = r.json()['state']
while status != 'idle':
  r = requests.get(session_url, headers=headers)
  status = r.json()['state']
  print(status)

table_name = "file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-1.csv"

command = """
df = spark.read.format("csv").option("header", "true").load("file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-g7-1.csv")
df.show()
"""
response=requests.post(f"{host}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)

statement_url = host + response.headers['Location']
r = requests.get(statement_url, headers=headers)
status=(r.json())['progress']
while status != 1.0:
    r = requests.get(statement_url, headers=headers)
    status=(r.json())['progress']
pprint.pprint(r.json())

