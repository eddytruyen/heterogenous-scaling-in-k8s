import math
from . import generator

MINIMUM_CPU=1
MINIMUM_MEMORY=2
SCALING_DOWN_TRESHOLD=1.15
SCALING_UP_THRESHOLD=1.15
OPT_IN_FOR_RESTART = False


UNDO_SCALE_ACTION =  8544343532
REDO_SCALE_ACTION = 999767537
NO_COST_EFFECTIVE_RESULT = 553583943
COST_EFFECTIVE_RESULT = 50240434322
NO_RESULT = 9880593853
RETRY_WITH_ANOTHER_WORKER_CONFIGURATION = 15845949549
NO_COST_EFFECTIVE_ALTERNATIVE = 111994848484



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



class AdaptiveScaler:

	
	def __init__(self, workers, scalingFunction):
		self.ScalingDownPhase = True
		self.ScalingUpPhase = False
		self.ScaledDown = False
		self.ScaledUp = False
		self.ScalingFunction = scalingFunction
		self.FailedScalings = []
		self.ScaledWorkerIndex=-1
		self.failed_scaled_worker=None
		self.workers = workers
		self.tipped_over_confs = []
		self.current_tipped_over_conf = None

	def reset(self):
		self.FailedScalings = []
		self.ScaledWorkerIndex=-1
		self.failed_scaled_worker=None
		if self.ScalingDownPhase:
			self.ScalingDownPhase = False
			self.ScalingUpPhase = True
			self.current_tipped_over_conf = None
		elif self.ScalingUpPhase and (not self.tipped_over_confs):
			self.ScalingDownPhase = True
			self.ScalingUpPhase = False
		self.ScaledDown=False
		self.ScaledUp=False

	def validate_result(self,result,conf,slo):
		


		def undo_scale_action():
			if self.ScaledUp:
				self.failed_scaled_worker=self.ScalingFunction.undo_scaled_up(self.workers)
				self.ScaledUp=False
			elif self.ScaledDown:
				self.failed_scaled_worker=self.ScalingFunction.undo_scaled_down(self.workers)
				self.ScaledDown=False
			self.ScaledWorkerIndex=-1
			self.FailedScalings.append(self.failed_scaled_worker.worker_id)

		def tag_tested_workers(conf):
                        for k,v in enumerate(conf):
                                if v > 0:
                                        self.workers[k].tested()

		tag_tested_workers(conf)
		states = []

		if result and slo > float(result['CompletionTime']) * SCALING_DOWN_TRESHOLD:
			states+=[NO_COST_EFFECTIVE_RESULT]
			self.failed_scaled_worker=None
			if self.ScaledDown or self.ScaledUp:
				states+=[UNDO_SCALE_ACTION]
				undo_scale_action()
			return states
		elif result:
			if self.ScaledDown:
				self.ScaledDown=False
				self.ScaledWorkerIndex=-1
			elif self.ScaledUp:
				self.ScaledUp=False
				self.ScaledWorkerIndex=-1
			self.FailedScalings=[]
			states+=[COST_EFFECTIVE_RESULT]
			return states
		else:
			states += [NO_RESULT]
			if self.ScaledDown or self.ScaledUp:
				states+=[UNDO_SCALE_ACTION]
				undo_scale_action()
			return states

	def find_cost_effective_config(self, opt_conf, slo, tenant_nb, scale_down=True, only_failed_results=False):

		def isTestable(worker, conf):
                      if worker.isTested():
                          return True
                      else:
                          w = largest_worker_of_conf(conf)
                          return worker.worker_id >= w.worker_id


		def smallest_worker_of_conf(conf):
                      for k,v in enumerate(reversed(conf)):
                          print(v)
                          if v > 0:
                               return self.workers[len(self.workers)-k-1]

		def largest_worker_of_conf(conf):
                      for k,v in enumerate(conf):
                           if v > 0:
                               return self.workers[k]

		def involves_worker(conf, worker_index):
                      if worker_index < 0 or worker_index >= len(self.workers):
                               return True
                      if conf[worker_index] > 0:
                               return True
                      else:
                               return False

		def equal_workers(workersA, workersB):
                      if len(workersA) != len(workersB):
                               return False
                      for a,b in zip(workersA,workersB):
                               if not a.equals(b):
                                       return False
                      return True

		def difference(conf_cost, total_cost):
                        nonlocal scale_down
                        if scale_down:
                                print("SCALE DOWN DIFF")
                                return conf_cost-total_cost - 1
                        else:
                                print("SCALE UP DIFF")
                                return total_cost + 1 - conf_cost

		def is_worker_scaleable(worker_index):
                        nonlocal scale_down
                        if scale_down:
                                return self.workers[worker_index].cpu > MINIMUM_CPU if self.ScalingFunction.CpuIsDominant else self.workers[worker_index].memory > MINIMUM_MEMORY
                        else:
                                max_cpu = self.ScalingFunction.maxCPU
                                max_mem = self.ScalingFunction.maxMem
                                if self.CpuIsDominant:
                                        return self.workers[worker_index].cpu < max_cpu
                                else:
                                        return self.workers[worker_index].memory < max_mem

		def scale_worker(workers, worker_index, nb_of_scaling_units):
                        nonlocal scale_down
                        if scale_down:
                                self.ScalingFunction.scale_worker_down(workers, worker_index, nb_of_scaling_units)
                                self.ScaledWorkerIndex=self.workers[wi].worker_id-1
                                self.ScaledDown = True
                        else:
                                self.ScalingFunction.scale_worker_up(workers, worker_index, nb_of_scaling_units)
                                self.ScaledUp = True


		def redo_scale_action(nb_of_scaling_units):
                        nonlocal scale_down
                        if scale_down:
                                self.ScalingFunction.scale_worker_down(self.workers, self.failed_scaled_worker.worker_id-1, nb_of_scaling_units)
                        else:
                                self.ScalingFunction.scale_worker_up(self.workers, self.failed_scaled_worker.worker_id-1, nb_of_scaling_units)

		def is_scaled():
			nonlocal scale_down
			return self.ScaledDown if scale_down else self.ScaledUp

		def set_scaled():
			nonlocal scale_down
			if scale_down:
				self.ScaledDown=True
			else:
				self.ScaledUp=False


		states=[]
		totalcost = self.ScalingFunction.target(slo,tenant_nb)
		new_workers=[w.clone() for w in self.workers]
		for w in self.workers:
			print(w.cpu,w.memory)
		diff=difference(generator.resource_cost(self.workers, opt_conf), totalcost['cpu'] + totalcost['memory'])
		print("difference between resource_cost optimal conf and predicted total cost -1")
		print(diff)
		worker_index=1
		L=len(self.workers)
		while diff > 0 and (worker_index <= L) and not is_scaled():
			wi=L-worker_index
			if not (self.workers[wi].isFlagged() and not OPT_IN_FOR_RESTART) and isTestable(self.workers[wi],opt_conf) and is_worker_scaleable(wi):
				if not self.workers[wi].worker_id in self.FailedScalings:
					scale_worker(new_workers, wi, 1)
					diff = difference(generator.resource_cost(self.workers, opt_conf), totalcost['cpu'] + totalcost['memory'])
					print("Rescaling worker " + str(self.workers[wi].worker_id))
					self.ScaledWorkerIndex=self.workers[wi].worker_id-1
					set_scaled()
				else:
					print("Passing over worker in previously failed scaling")
			worker_index += 1
		if is_scaled() and not equal_workers(self.workers, new_workers):
			self.workers=new_workers
			for w in self.workers:
				print(w.cpu,w.memory)
			states+=[RETRY_WITH_ANOTHER_WORKER_CONFIGURATION]
		else:
			states+=[NO_COST_EFFECTIVE_ALTERNATIVE]
			if self.failed_scaled_worker and not only_failed_results:
				states+=[REDO_SCALE_ACTION]
				redo_scale_action(1)
			self.reset()
		return states



	def set_tipped_over_failed_confs(self, results, slo):
		if not self.tipped_over_confs:
                	self.tipped_over_confs = [generator.get_conf(self.workers,r) for r in generator.sort_results([r for r in results if float(r['CompletionTime']) > slo and float(r['CompletionTime']) <= slo * SCALING_UP_THRESHOLD])]
		return self.tipped_over_confs

	def find_cost_effective_tipped_over_conf(self, slo, tenant_nb):
                conf_index = 0
                while len(self.tipped_over_confs) > 0:
                        states=adaptive_scaler.find_cost_effective_result(tipped_over_confs[conf_index], slo, tenant_nb, scale_down=False, only_failed_results=True)
                        copy_of_states=states[:]
                        state=states.pop(0)
                        if state == RETRY_WITH_ANOTHER_WORKER_CONFIGURATION:
                                self.current_tipped_over_conf=tipped_over_confs[conf_index]
                                return copy_of_states
                        elif state == NO_COST_EFFECTIVE_ALTERNATIVE:
                                self.tipped_over_confs.pop(0)
                return copy_of_states

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
