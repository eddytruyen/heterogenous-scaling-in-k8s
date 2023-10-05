import math
import random
import textwrap


max_tenants=15
tenant_group="g7"
host = "http://172.22.8.106:30898"
headers = {'Content-Type': 'application/json'}



def _stress(stress_size):

  session_id=get_session(self.host, self.headers)


# Genereer willekeurig een nummer tussen 1 en max_tenants
  tenant = str(random.randint(1, self.max_tenants))

  table_name = f"file:///opt/bitnami/spark/spark_data/spark-bench-test/kmeans-data-{tenant_group}-{tenant}.csv"

  command =textwrap.dedent(f"""
  val df = spark.read.format("csv").option("header", "true").load("{table_name}")
  df.createOrReplaceTempView("kmeans{tenant}")
  df.cache()
  val e = df.columns
  %json e
  """)


  r=invoke(command, self.host, session_id, self.headers)
  columns=r['output']['data']['application/json']
  sample_columns=random.sample(columns, random.randint(0, len(columns)-1))
  selected_columns = ", ".join(sample_columns)


  sample_queries=[]
  if stress_size == 0:
    sample_queries=random.sample(columns, random.randint(0, len(columns)-1))
  else:
    sample_queries=random.sample(columns, stress_size)
  sample_values=[random.uniform(-0.1, 0.1) for _ in sample_queries]

  selected_evaluations= " and ".join([f"{string} < {value}" for string, value in zip(sample_queries,sample_values)])

  command = textwrap.dedent(f"""
  val sqlDF = spark.sql("SELECT {selected_columns} FROM kmeans{tenant} WHERE {selected_evaluations}")
  sqlDF.show()
  """)
  #sqlDF.write.mode("overwrite").csv("file:///opt/bitnami/spark/spark_data/spark-bench-test/output/output.csv")

  invoke(command, self.host, session_id, self.headers)

class Stress:
	def __init__(self, stress_size,stress_function, max_tenants, tenant_group, host, headers):
		self.stress_size = stress_size
		self.stress_function = stress_function
        self.max_tenants=max_tenants
        self.tenant_group=tenant_group
        self.host=host
        self.headers=headers


	def runTest(self):
		self.stress_function(self.stress_size)

class StressCPU(Stress):
	def __init__(self,stress_function=stress,stress_size=100, max_tenants=15, tenant_group="g7", host = "http://172.22.8.106:30898", headers = {'Content-Type': 'application/json'}):
		Stress.__init__(self, stress_size, stress_function)



