import math

class ScalingFunction:
	def __init__(self, coef_a, coef_b, coef_c,cpu,mem, cpu_is_dominant, nodes, alphabet):
		self.CoefA = coef_a
		self.CoefB = coef_b
		self.CoefC = coef_c
		self.eval  = lambda x: self.CoefA*math.exp(self.CoefB*x) + self.CoefC
		self.Cpu = cpu
		self.Mem = mem
		self.Nodes = nodes
		self.Alphabet=alphabet
		self.CpuIsDominant = cpu_is_dominant 


	def maximum(self,x1,x2):
		return max([self.eval(x) for x in range(x1,x2+1,1)])

	def minimum(self,x1,x2):
		return min([self.eval(x) for x in range(x1,x2+1,1)])

	def derivative(self,x1,x2):
		return (self.eval(x2)-self.eval(x1))/(x2-x1)

	def target(self,slo,tenants,element_nb):
		y=self.eval(tenants)
		print(y)
		dict={}
		if self.CpuIsDominant:
			dict = {
				"cpu": math.ceil((tenants*self.Cpu*y)/slo), 
				"memory": math.ceil((tenants*math.log(self.Mem,tenants+1)*y)/slo)
			}
		else:
                        dict = {
                                "cpu": math.ceil((tenants*math.log(self.Cpu,tenants+1)*y)/slo),
                                "memory": math.ceil((tenants*self.Mem*y)/slo)
                        }

		self.Alphabet['elements'][element_nb-1]={'size': dict}
		return dict

class AdaptiveWindow:
	def __init__(self, initial_window):
		self.original_window=initial_window



	def adapt_search_window(self, results, window, first_tenant):
		if not first_tenant:
			if results:
				self.original_window=1
			else:
				self.original_window=window
		else:
			self.original_window=window
		return self.original_window

	def get_current_window(self):
		return self.original_window
