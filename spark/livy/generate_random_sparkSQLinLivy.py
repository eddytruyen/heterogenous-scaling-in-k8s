import requests
import json
import random

# Definieer de URL van de Livy-server
livy_url = "http://localhost:8998"

# Maak een sessie aan
data = {'kind': 'spark'}
headers = {'Content-Type': 'application/json'}
response = requests.post("{livy_url}/sessions", data=json.dumps(data), headers=headers)

# Sla de sessie-ID op
session_id = response.json()['id']

# Wacht tot de sessie actief is
status = response.json()['state']
while status != 'idle':
  #response = requests.get(f"{livy_url}/sessions/{session_id}", headers=headers)
  status = response.json()['state']

# Lees de tabel in als een DataFrame
command = """
df = spark.read.format("csv").option("header", "true").load("tabel.csv")
"""
requests.post(f"{livy_url}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)

# Definieer de naam van de tabel
table_name = "mijn_tabel"

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
  # Genereer de SQL-query om de geselecteerde kolommen te updaten
  command = f"query = f'UPDATE {table_name} SET {columns[0]} = 'value1', {columns[1]} = 'value2''"

else:
  # Selecteer willekeurig een kolom
  column = random.choice(df.columns)
  # Genereer de SQL-query om een rij te verwijderen met een bepaalde waarde in de geselecteerde kolom
  command = f"query = f'DELETE FROM {table_name} WHERE {column} = 'value''"

# Voer de query uit
response = requests.post(f"{livy_url}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)

# Sluit de sessie
requests.delete(f"{livy_url}/sessions/{session_id}", headers=headers)

