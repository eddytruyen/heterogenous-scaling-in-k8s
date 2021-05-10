import math

MINIMUM_MEMORY=2

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
		self.workersScaledDown = [] 
		self.workersScaledUp = []
		self.MaxCPU = max([c[0] for c in nodes])
		self.MaxMem = max([c[1] for c in nodes])
		self.LastScaledDownWorker = []
		self.LastScaledUpWorker = []

	def maximum(self,x1,x2):
		fprojection=[self.eval(x) for x in range(x1,x2+1,1)]
		fprojectionmax=max(fprojection)
		fprojection.reverse()
		fdomainmax=fprojection.index(fprojectionmax)
		return [x2-fdomainmax,fprojectionmax]

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
		dict={}
		if self.CpuIsDominant:
			dict = {
				"cpu": int((tenants*self.Cpu*y)/slo), 
				"memory": math.ceil((tenants*math.log(self.Mem,tenants+1)*y)/slo)
			}
		else:
                        dict = {
                                "cpu": math.ceil((tenants*math.log(self.Cpu,tenants+1)*y)/slo),
                                "memory": int((tenants*self.Mem*y)/slo)
                        }
		return dict

	def undo_scaled_down(self,workers):
		if not self.LastScaledDownWorker:
			return None
		worker_index = self.LastScaledDownWorker.pop()
		scalingRecord=self.workersScaledDown[worker_index]
		worker=workers[worker_index]
		worker.scale(worker.cpu+scalingRecord[1].pop(0), worker.memory+scalingRecord[2].pop(0))
		scalingRecord[0]-=1
		return worker

	def undo_scaled_up(self,workers):
                if not self.LastScaledUpWorker:
                        return None
                worker_index = self.LastScaledUpWorker.pop()
                scalingRecord=self.workersScaledUp[worker_index]
                worker=workers[worker_index]
                worker.scale(worker.cpu-scalingRecord[1].pop(0), worker.memory-scalingRecord[2].pop(0))
                scalingRecord[0]-=1
                return worker


	def scale_worker_down(self, workers, worker_index, nb_of_units):
		if not self.workersScaledDown:
			self.workersScaledDown=[[1,[],[]] for w in workers]
		worker=workers[worker_index]
		scaleSecondaryResource=False
		if self.workersScaledDown[worker_index][0] % 2 == 0:
			scaleSecondaryResource=True
		if self.CpuIsDominant and worker.cpu-nb_of_units >= 1:
			if scaleSecondaryResource and worker.memory > MINIMUM_MEMORY:
				self.LastScaledDownWorker+=[worker_index]
				worker.scale(worker.cpu-nb_of_units,worker.memory-1)
				k=self.workersScaledDown[worker_index]
				self.workersScaledDown[worker_index]=[k[0]+1, [nb_of_units] + k[1], [1] + k[2]]

			else:
				self.LastScaledDownWorker+=[worker_index]
				worker.scale(worker.cpu-nb_of_units,worker.memory)
				k=self.workersScaledDown[worker_index]
				self.workersScaledDown[worker_index]=[k[0]+1, [nb_of_units] + k[1], [0] + k[2]]
		elif worker.memory - nb_of_units >= MINIMUM_MEMORY:
			if scaleSecondaryResource and worker.cpu > 1:
				self.LastScaledDownWorker+=[worker_index]
				worker.scale(worker.cpu-1, worker.memory-nb_of_units)
				k=self.workersScaledDown[worker_index]
				self.workersScaledDown[worker_index]=[k[0]+1, [1] + k[1], [nb_of_units] + k[2]]
			else:
				self.LastScaledDownWorker+=[worker_index]
				worker.scale(worker.cpu, worker.memory-nb_of_units)
				k=self.workersScaledDown[worker_index]
				self.workersScaledDown[worker_index]=[k[0]+1, [0] + k[1], [nb_of_units] + k[2]]
		return workers

	def scale_worker_up(self, workers, worker_index, nb_of_units):
		if not self.workersScaledUp:
			self.workersScaledUp=[[1,[],[]] for w in workers]
		worker=workers[worker_index]
		scaleSecondaryResource=False
		if self.workersScaledUp[worker_index][0] % 2 == 0:
			scaleSecondaryResource=True
		if self.CpuIsDominant and worker.cpu+nb_of_units <= self.MaxCPU:
			if scaleSecondaryResource and worker.memory < self.MaxMem:
				self.LastScaledUpWorker+=[worker_index]
				worker.scale(worker.cpu+nb_of_units,worker.memory+1)
				k=self.workersScaledUp[worker_index]
				self.workersScaledUp[worker_index]=[k[0]+1, [nb_of_units] + k[1], [1] + k[2]]
			else:
				self.LastScaledUpWorker+=[worker_index]
				worker.scale(worker.cpu+nb_of_units,worker.memory)
				k=self.workersScaledUp[worker_index]
				self.workersScaledUp[worker_index]=[k[0]+1, [nb_of_units] + k[1], [0] + k[2]]
		elif worker.memory + nb_of_units <= self.MaxMem:
			if scaleSecondaryResource and worker.cpu < self.MaxCPU:
				self.LastScaledUpWorker+=[worker_index]
				worker.scale(worker.cpu+1, worker.memory+nb_of_units)
				k=self.workersScaledUp[worker_index]
				self.workersScaledUp[worker_index]=[k[0]+1, [1] + k[1], [nb_of_units] + k[2]]
			else:
				self.LastScaledUpWorker+=[worker_index]
				worker.scale(worker.cpu, worker.memory+nb_of_units)
				k=self.workersScaledUp[worker_index]
				self.workersScaledUp[worker_index]=[k[0]+1, [0] + k[1], [nb_of_units] + k[2]]
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
