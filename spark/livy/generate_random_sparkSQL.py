import pyspark
from pyspark.sql import SparkSession
import random

# Maak een SparkSession
spark = SparkSession.builder.appName("RandomQueryGenerator").getOrCreate()

# Lees de tabel in als een DataFrame
df = spark.read.format("csv").option("header", "true").load("tabel.csv")

# Definieer de naam van de tabel
table_name = "mijn_tabel"

# Genereer willekeurig een nummer tussen 1 en 3
operation = random.randint(1, 3)

if operation == 1:
  # Selecteer willekeurig een kolom
  column = random.choice(df.columns)
  # Genereer de SQL-query om de geselecteerde kolom te selecteren
  query = f"SELECT {column} FROM {table_name}"

elif operation == 2:
  # Selecteer willekeurig twee kolommen
  columns = random.sample(df.columns, 2)
  # Genereer de SQL-query om de geselecteerde kolommen te updaten
  query = f"UPDATE {table_name} SET {columns[0]} = 'value1', {columns[1]} = 'value2'"

else:
  # Selecteer willekeurig een kolom
  column = random.choice(df.columns)
  # Genereer de SQL-query om een rij te verwijderen met een bepaalde waarde in de geselecteerde kolom
  query = f"DELETE FROM {table_name} WHERE {column} = 'value'"

# Voer de query uit
spark.sql(query)

# Sluit de SparkSession
spark.stop()

