import math

class ScalingFunction:
	def __init__(self, coef_a, coef_b, coef_c,cpu,mem):
		self.CoefA = coef_a
		self.CoefB = coef_b
		self.CoefC = coef_c
		self.eval  = lambda x: self.CoefA*math.exp(self.CoefB*x) + self.CoefC
		self.Cpu = cpu
		self.Mem = mem


	def maximum(self,x1,x2):
		return max([self.eval(x) for x in range(x1,x2,1)])

	def minimum(self,x1,x2):
		return min([self.eval(x) for x in range(x1,x2,1)])

	def derivative(self,x1,x2):
		return (self.eval(x2)-self.eval(x1))/(x2-x1)

	def target(self,slo,tenants):
		y=self.eval(tenants)
		if y <= slo:
			dict = {
				"cpus": math.ceil(tenants*self.Cpu-((slo-y)*tenants*self.Cpu)/y), 
				"mems": math.ceil(tenants*self.Mem-((slo-y)*tenants*self.Mem)/y)
			}
			return dict
		else:
                        dict = {
                                "cpus": math.ceil(((y-slo)*tenants*self.Cpu)/y + tenants*self.Cpu),
                                "mems": math.ceil(((y-slo)*tenants*self.Mem)/y + tenants*self.Mem)
                        }
                        return dict


	
	


class ResourceSize:
	def __init__(self,cpu,mem):
		self.Cpu=cpu
		self.Mem=mem


