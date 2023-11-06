import math
import random
import jaydebeapi


def _stress(stress_size, max_tenants, tenant_group, host,conn):



# Genereer willekeurig een nummer tussen 1 en max_tenants
  tenant = str(random.randint(1, max_tenants))

  cursor = conn.cursor()

  sql=f"select c1,c2,c3 from global_temp.kmeans{tenant} where c1 < 1 and c2 < 1 and c3 < 5"

  cursor.execute(sql)
  cursor.close()
   
  #columns=r['output']['data']['application/json']
  #sample_columns=random.sample(columns, random.randint(0, len(columns)-1))
  #selected_columns = ", ".join(sample_columns)sample_queries=[]
  #if stress_size == 0:
  #  sample_queries=random.sample(columns, random.randint(0, len(columns)-1))
  #else:
  #  sample_queries=random.sample(columns, stress_size)
  #sample_values=[random.uniform(-0.1, 0.1) for _ in sample_queries]

  #selected_evaluations= " and ".join([f"{string} < {value}" for string, value in zip(sample_queries,sample_values)])

  #command = textwrap.dedent(f"""
  #val sqlDF = spark.sql("SELECT {selected_columns} FROM kmeans{tenant} WHERE {selected_evaluations}")
  #sqlDF.show()
  #""")
  #sqlDF.write.mode("overwrite").csv("file:///opt/bitnami/spark/spark_data/spark-bench-test/output/output.csv")

  #invoke(command, host, session_id, headers)

class Stress:
    def __init__(self, stress_size,stress_function, max_tenants, tenant_group, host, headers):
        self.stress_size = stress_size
        self.stress_function = stress_function
        self.max_tenants=max_tenants
        self.tenant_group=tenant_group
        self.host=host
        self.headers=headers


    def runTest(self):
        self.stress_function(self.stress_size, self.max_tenants, self.tenant_group, self.host, self.headers)

class StressSpark(Stress):
	def __init__(self,stress_size=0, max_tenants=15, tenant_group="g7", host = "http://172.22.8.106:30898", headers = {'Content-Type': 'application/json'}, stress_function=_stress):
		Stress.__init__(self, stress_size, stress_function,max_tenants, tenant_group,host, headers)



