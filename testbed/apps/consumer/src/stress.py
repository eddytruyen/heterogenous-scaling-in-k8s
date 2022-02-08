import math

def _cpu_stress(stress_size):
	for i in range(1000*stress_size):
		math.sqrt(i)

class Stress:
	def __init__(self, stress_size,stress_function):
		self.stress_size = stress_size
		self.stress_function = stress_function

	def runTest(self):
		if self.stress_size != 0:
			self.stress_function(self.stress_size)

class StressCPU(Stress):
	def __init__(self,stress_function=_cpu_stress,stress_size=100):
		Stress.__init__(self, stress_size, stress_function)



