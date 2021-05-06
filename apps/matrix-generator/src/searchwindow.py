import math

class ScalingFunction:
	def __init__(self, coef_a, coef_b, coef_c, cpu, mem, cpu_is_dominant, nodes):
		self.CoefA = coef_a
		self.CoefB = coef_b
		self.CoefC = coef_c
		self.eval  = lambda x: self.CoefA*math.exp(self.CoefB*x) + self.CoefC
		self.Cpu = cpu
		self.Mem = mem
		self.Nodes = nodes
		self.CpuIsDominant = cpu_is_dominant 


	def maximum(self,x1,x2):
		fprojection=[self.eval(x) for x in range(x1,x2+1,1)]
		fprojectionmax=max(fprojection)
		fdomainmax=fprojection.reverse().index(fprojectionmax)
		return [fdomainmax,fprojectionmax]

	def minimum(self,x1,x2):
                fprojection=[self.eval(x) for x in range(x1,x2+1,1)]
                fprojectionmin=min(fprojection)
                fdomainmin=fprojection.index(fprojectionmin)
                return [fdomainmin,fprojectionmin]

	def minimum(self,x1,x2):
		return min([self.eval(x) for x in range(x1,x2+1,1)])

	def derivative(self,x1,x2):
		return (self.eval(x2)-self.eval(x1))/(x2-x1)

	def get_gradient(self,x1,x2):
		x_fmax=self.maximum(x1,x2)
		x_fmin=self.minimum(x1,x2)
		return (x_fmax[1]-x_fmin[1])/math.abs(x_fmax[0]-x_fmin[0])


	def target(self,slo,tenants):
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
		return dict


	def scale_worker_down(workers, worker_index, nb_of_units):
		worker=workers[worker_index]
		if self.CpuIsDominant:
			worker.scale(worker.cpu-nb_of_units,worker.memory)
		else:
			worker.scale(worker.cpu, worker.memory-nb_of_units)
		return workers

	def scale_worker_up(workers, worker_index, nb_of_units):
                worker=workers[worker_index]
                if self.CpuIsDominant:
                        worker.scale(worker.cpu+nb_of_units,worker.memory)
                else:
                        worker.scale(worker.cpu, worker.memory+nb_of_units)
                return workers


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
