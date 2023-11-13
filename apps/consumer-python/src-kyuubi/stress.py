import math
import random
import jaydebeapi
import logging

def _stress(stress_size, max_tenants, tenant_group, cursor):



# Genereer willekeurig een nummer tussen 1 en max_tenants
   tenant = str(random.randint(1, max_tenants))
   cursor.execute(f"describe global_temp.kmeans{tenant}")
   columns=list(map(lambda x: x[0],cursor.fetchall()))

   sample_columns=random.sample(columns, random.randint(1, len(columns)-1))

   selected_columns = ", ".join(sample_columns)

   if stress_size == 0:
      sample_queries=random.sample(columns, random.randint(1, len(columns)-1))
   else:
      sample_queries=random.sample(columns, stress_size)


   sample_values=[random.uniform(-0.1, 0.1) for _ in sample_queries]

   selected_evaluations= " and ".join([f"{string} < {value}" for string, value in zip(sample_queries,sample_values)])



   sql=f"SELECT {selected_columns} FROM global_temp.kmeans{tenant} WHERE {selected_evaluations}"


   logging.debug("Getting column data from Kyuubi")
   cursor.execute(sql)
   results=cursor.fetchall()
   

class Stress:
    def __init__(self, stress_size,stress_function, max_tenants, tenant_group, cursor):
        self.stress_size = stress_size
        self.stress_function = stress_function
        self.max_tenants=max_tenants
        self.tenant_group=tenant_group
        self.cursor=cursor


    def runTest(self):
        self.stress_function(self.stress_size, self.max_tenants, self.tenant_group, self.cursor)

class StressSpark(Stress):
	def __init__(self,stress_size=0, max_tenants=15, tenant_group="g7", cursor=None, stress_function=_stress):
		Stress.__init__(self, stress_size, stress_function,max_tenants, tenant_group,cursor)



