import math
import random
import jaydebeapi
import logging


def _stress(stress_size, max_tenants, tenant_group, conn):



# Genereer willekeurig een nummer tussen 1 en max_tenants
  tenant = str(random.randint(1, max_tenants))

  logging.debug("Creating JDBC statement for Kyuubi")

  cursor = conn.cursor()

  sql=f"select c1,c2,c3 from global_temp.kmeans{tenant} where c1 < 1 and c2 < 1 and c3 < 5"
  logging.debug("Sending sql query to Kyuubi")
  cursor.execute(sql)
  results=cursor.fetchall()
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
    def __init__(self, stress_size,stress_function, max_tenants, tenant_group, conn):
        self.stress_size = stress_size
        self.stress_function = stress_function
        self.max_tenants=max_tenants
        self.tenant_group=tenant_group
        self.conn=conn


    def runTest(self):
        self.stress_function(self.stress_size, self.max_tenants, self.tenant_group, self.conn)

class StressSpark(Stress):
	def __init__(self,stress_size=0, max_tenants=15, tenant_group="g7", conn=None, stress_function=_stress):
		Stress.__init__(self, stress_size, stress_function,max_tenants, tenant_group,conn)



