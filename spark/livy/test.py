import requests
import json
import random
import pprint

# Definieer de URL van de Livy-server
host = "http://172.22.8.106:30898"

data = {'kind': 'pyspark'}
headers = {'Content-Type': 'application/json'}
r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
r.json()


# Wacht tot de sessie actief is
session_url = host + r.headers['location']
r = requests.get(session_url, headers=headers)
status = r.json()['state']
while status != 'idle':
  r = requests.get(session_url, headers=headers)
  status = r.json()['state']
  print(status)

import pdb; pdb.set_trace()
# Definieer de naam van de tabel
table_name = "spark_data/spark-bench-test/kmeans-data-g7-1.csv"

# Lees de tabel in als een DataFrame
command = textwrap.dedent("""
df = spark.read.format("csv").option("header", "true").load(table_name)
""")
requests.post(f"{livy_url}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)

# Genereer willekeurig een nummer tussen 1 en 3
operation = random.randint(1, 3)

if operation == 1:
  # Selecteer willekeurig een kolom
  column = random.choice(df.columns)
  # Genereer de SQL-query om de geselecteerde kolom te selecteren
  command = f"query = f'SELECT {column} FROM {table_name}'"

elif operation == 2:
  # Selecteer willekeurig twee kolommen
  columns = random.sample(df.columns, 2)
  # Genereer de SQL-query om de geselecteerde kolomm
  command = f"query = f'SELECT {column} FROM {table_name}'"

