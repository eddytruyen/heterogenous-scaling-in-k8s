import math
from . import generator
from . import utils
import copy

MINIMUM_RESOURCES={'cpu': 1, 'memory': 2}
SCALING_DOWN_TRESHOLD=1.15
SCALING_UP_THRESHOLD=1.15
OPT_IN_FOR_RESTART = False
CAREFUL_SCALING= False
SCALINGFUNCTION_TARGET_OFFSET_OF_NODE_RESOURCES={'cpu': 1.0, 'memory': 1.0}

UNDO_SCALE_ACTION =  8544343532
REDO_SCALE_ACTION = 999767537
NO_COST_EFFECTIVE_RESULT = 553583943
COST_EFFECTIVE_RESULT = 50240434322
NO_RESULT = 9880593853
RETRY_WITH_ANOTHER_WORKER_CONFIGURATION = 15845949549
NO_COST_EFFECTIVE_ALTERNATIVE = 111994848484
#OFFLINE= True


class ScalingFunction:
	def __init__(self, coef_a, coef_b, coef_c, resources, costs, dominant_resources, nodes):
		self.CoefA = coef_a
		self.CoefB = coef_b
		self.CoefC = coef_c
		self.eval  = lambda x: self.CoefA*math.exp(self.CoefB*x) + self.CoefC
		self.resources=resources
		self.costs=costs
		self.maxWeights={}
		self.minWeights={}
		for i in resources.keys():
			self.maxWeights[i]=max([c[i] for  c in self.costs])
		for i in resources.keys():
			self.minWeights[i]=min([c[i] for  c in self.costs])
		self.DominantResources=dominant_resources
		self.Nodes = nodes
		self.workersScaledDown = [] 
                # self.workersScaledDown=worker_index -> [scalinggRecord=[ nr of scaling records,{res: log of previous scale actions}] for scalingRecord in self.workersScaledDown]
		self.workersScaledUp = []
                # self.workersScaledUp:worker_index -> [scalingRecord=[ nr of scaling records,{res: log of previous scale actions}] for scalingRecord in self.workersScaledDown]
		self.Max={}
		for i in resources.keys():
			self.Max[i]=max([c[i] for c in nodes])
		self.LastScaledDownWorker = []
		self.LastScaledUpWorker = []

	def clone(self, clone_scaling_records=False):
                sc=ScalingFunction(self.CoefA, self.CoefB,self.CoefC,self.resources,self.costs,self.DominantResources, self.Nodes)
                if clone_scaling_records:
                    sc.workersScaledDown = [[scalingRecord[0],copy.deepcopy(scalingRecord[1])] for scalingRecord in self.workersScaledDown]
                    sc.workersScaledUp = [[scalingRecord[0],copy.deepcopy(scalingRecord[1])] for scalingRecord in self.workersScaledUp]
                    sc.LastScaledDownWorker = self.LastScaledDownWorker[:]
                    sc.LastScaledUpWorker = self.LastScaledUpWorker[:]
                return sc

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
		for res in self.resources.keys():
			if res in self.DominantResources:
				dict[res]=int((tenants*self.resources[res]*y)/slo)
			else:
				dict[res]=math.ceil((tenants*math.log(self.resources[res],tenants+1)*y)/slo)
		return dict

        # this function returns the worker config for which the last scaling did not yield a cost-effective result
	def undo_scaled_down(self,workers):
		if not self.LastScaledDownWorker:
			return None
		worker_index = self.LastScaledDownWorker.pop()
		scalingRecord=self.workersScaledDown[worker_index]
		worker=workers[worker_index]
		worker2=worker.clone()
		for res in worker.resources.keys():
			worker.scale(res, worker.resources[res]+scalingRecord[1][res].pop(0))
		scalingRecord[0]-=1
		return worker2

	# this function returns the worker config for which the last scaling did not yield a cost-effective result
	def undo_scaled_up(self,workers):
                if not self.LastScaledUpWorker:
                        return None
                worker_index = self.LastScaledUpWorker.pop()
                scalingRecord=self.workersScaledUp[worker_index]
                worker=workers[worker_index]
                worker2=worker.clone()
                for res in worker.resources.keys():
                        worker.scale(res, worker.resources[res]-scalingRecord[1][res].pop(0))
                scalingRecord[0]-=1
                return worker2


	def scale_worker_down(self, workers, worker_index, nb_of_units):
                scale_down={res: [] for res in self.resources.keys()}
                if not self.workersScaledDown:
                        self.workersScaledDown=[[1,{res: [] for res in self.resources.keys()}] for w in workers]
                worker=workers[worker_index]
                scaleSecondaryResource=True if self.workersScaledDown[worker_index][0] % 2 == 0 else False
                for res in self.resources.keys():
                        if (res in self.DominantResources) and worker.resources[res]-nb_of_units >= MINIMUM_RESOURCES[res]:
                            worker.scale(res, worker.resources[res]-nb_of_units)
                            self.LastScaledDownWorker+=[worker_index]
                            k=self.workersScaledDown[worker_index][1]
                            scale_down[res]=[nb_of_units] + k[res]
                        elif scaleSecondaryResource and worker.resources[res] - 1 >= MINIMUM_RESOURCES[res]:
                            worker.scale(res, worker.resources[res]-1)
                            self.LastScaledDownWorker+=[worker_index]
                            k=self.workersScaledDown[worker_index][1]
                            scale_down[res]=[1] + k[res]
                        else:
                            k=self.workersScaledDown[worker_index][1]
                            scale_down[res]=[0] + k[res]
                k=self.workersScaledDown[worker_index][0]
                self.workersScaledDown[worker_index]=[k+1, scale_down]
                return workers


	def scale_worker_up(self, workers, worker_index, nb_of_units):
		scale_up={res: [] for res in self.resources.keys()}
		if not self.workersScaledUp:
			self.workersScaledUp=[[1,{res: [] for res in self.resources.keys()}] for w in workers]
		worker=workers[worker_index]
		scaleSecondaryResource=True if self.workersScaledUp[worker_index][0] % 2 == 0 else False
		for res in self.resources.keys():
                        if (res in self.DominantResources) and worker.resources[res]+nb_of_units <= self.Max[res]:
                            worker.scale(res, worker.resources[res]+nb_of_units)
                            self.LastScaledUpWorker+=[worker_index]
                            k=self.workersScaledUp[worker_index][1]
                            scale_up[res]=[nb_of_units] + k[res]
                        elif scaleSecondaryResource and worker.resources[res] + 1 <= self.Max[res]:
                            worker.scale(res, worker.resources[res]+1)
                            self.LastScaledUpWorker+=[worker_index]
                            k=self.workersScaledUp[worker_index][1]
                            scale_up[res]=[1] + k[res]
                        else:
                            k=self.workersScaledUp[worker_index][1]
                            scale_up[res]=[0] + k[res]
		k=self.workersScaledUp[worker_index][0]
		self.workersScaledUp[worker_index]=[k+1, scale_up]
		return workers



class AdaptiveScaler:

	
	def __init__(self, workers, scalingFunction):
		self.ScalingDownPhase = True
		self.StartScalingDown = True
		self.ScalingUpPhase = False
		self.ScaledDown = False
		self.ScaledUp = False
		self.ScalingFunction = scalingFunction
		self.FailedScalings = []
		self.ScaledWorkerIndex=-1
		self.workers = workers
		self.tipped_over_confs = []
		self.current_tipped_over_conf = None
		self.failed_results=[]
		self.initial_confs=[]
		self._tested={}
		self.scale_action_re_undone=False
		self.only_failed_results=True
		for w in workers:
			self._tested[w.worker_id]=False

	def clone(self):
            a_s=AdaptiveScaler([w.clone() for w in self.workers], self.ScalingFunction.clone(clone_scaling_records=True))
            a_s.ScalingDownPhase=self.ScalingDownPhase
            a_s.StartScalingDown = self.StartScalingDown
            a_s.ScalingUpPhase=self.ScalingUpPhase
            a_s.ScaledDown=self.ScaledDown
            a_s.ScaledUp=self.ScaledUp
            a_s.FailedScalings = self.FailedScalings
            a_s.ScaledWorkerIndex=self.ScaledWorkerIndex
            a_s.tipped_over_confs=[c[:] for c in self.tipped_over_confs]
            if self.current_tipped_over_conf:
            	a_s.current_tipped_over_conf=self.current_tipped_over_conf[:] 
            else:
                a_s.current_tipped_over_conf=None
            a_s.failed_results=[c[:] for c in self.failed_results]
            a_s.initial_confs=[[dict(d[0]) if d[0] else {},d[1][:] if d[1] else [],[w.clone() for w in d[2]]] for d in self.initial_confs]
            a_s._tested=dict(self._tested)
            a_s.scale_action_re_undone=self.scale_action_re_undone
            a_s.only_failed_results=self.only_failed_results
            return a_s


	def hasScaled(self):
		return (self.ScaledWorkerIndex != -1 and (self.ScaledDown or self.ScaledUp)) or self.scale_action_re_undone

	def isTested(self, worker):
		return self._tested[worker.worker_id]

	def tested(self, worker):
		self._tested[worker.worker_id]=True

	def untest(self, worker):
                self._tested[worker.worker_id]=False

	def status(self):
                print("ScalingDownPhase, ScalingUpPhase, Tipped_over_confs, Current_tipped_over_conf, initial_confs, StartScalingDozn")
                print(self.ScalingDownPhase)
                print(self.ScalingUpPhase)
                print(self.tipped_over_confs)
                print(self.current_tipped_over_conf)
                print(self.initial_confs)
                print(self.StartScalingDown)
                for w in self.workers:
                     print(w.resources)

	def reset(self):
		self.FailedScalings = []
		self.ScaledWorkerIndex=-1
		if self.ScalingDownPhase:
			self.ScalingDownPhase = False
			self.ScalingUpPhase = True
			self.ScaledUp=False
		elif self.ScalingUpPhase:
			self.ScalingDownPhase = True
			self.ScalingUpPhase = False
			self.failed_results = []
			self.failed_scaled_workers=[]
			self.initial_confs=[]
			self.ScaledDown=False
		self.StartScalingDown=True
		self.tipped_over_confs = []
		self.current_tipped_over_conf = None
		self.only_failed_results=True


	def validate_result(self,result,conf,slo):

		def undo_scale_action(only_failed_results=False):
			if self.ScaledUp:
                                failed_worker=self.ScalingFunction.undo_scaled_up(self.workers)
                                self.ScaledUp=False
			elif self.ScaledDown:
                                failed_worker=self.ScalingFunction.undo_scaled_down(self.workers)
                                self.ScaledDown=False
			self.scale_action_re_undone=True
			self.ScaledWorkerIndex=-1
			self.FailedScalings+=[failed_worker]

		def tag_tested_workers(conf):
                        for k,v in enumerate(conf):
                                if v > 0:
                                        self.tested(self.workers[k])

		tag_tested_workers(conf)
		states = []
		self.scale_action_re_undone=False

		if not self.ScalingUpPhase:
			self.initial_confs+=[[result,conf,[w.clone() for w in self.workers]]]

		if result and slo > float(result['CompletionTime']) * SCALING_DOWN_TRESHOLD:
			states+=[NO_COST_EFFECTIVE_RESULT]
			#if not self.ScalingUpPhase:
			#	self.initial_confs+=[[result,conf,[w.clone() for w in self.workers]]]
			if self.ScaledDown or self.ScaledUp:
				states+=[UNDO_SCALE_ACTION]
				undo_scale_action(False)
			return states
		elif result:
			if self.ScaledDown:
				self.ScaledDown=False
				self.ScaledWorkerIndex=-1
			elif self.ScaledUp:
				self.ScaledUp=False
				self.ScaledWorkerIndex=-1
			#if self.ScalingUpPhase:
			#	self.ScalingUpPhase=False
			#	self.ScalingDownPhase=True
			self.StartScalingDown=True
			self.FailedScalings=[]
			self.initial_confs=[]
			self.tipped_over_conf=[]
			self.current_tipped_over_conf = None
			states+=[COST_EFFECTIVE_RESULT]
			return states
		else:
			states += [NO_RESULT]
			if self.ScaledDown or self.ScaledUp:
				states+=[UNDO_SCALE_ACTION]
				undo_scale_action(True)
			return states

	def find_cost_effective_config(self, opt_conf, slo, tenant_nb, scale_down=True, only_failed_results=False):

		def is_testable(worker, conf):
                      nonlocal scale_down
                      if scale_down:
                          if self.isTested(worker):
                                return True
                          tmp_workers=[w.clone() for w in self.workers]
                          tmp_workers[worker.worker_id-1]=worker
                          return generator.resource_cost(self.workers, opt_conf, cost_aware=True) > generator.resource_cost(tmp_workers, conf, cost_aware=True) 
                      else:
                          return involves_worker(conf, worker.worker_id-1)


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

		def difference(conf_cost, total_cost):
                        nonlocal scale_down
                        if scale_down:
                                print("SCALE DOWN DIFF")
                                return conf_cost-total_cost - 1
                        else:
                                print("SCALE UP DIFF")
                                if CAREFUL_SCALING:
                                    return total_cost + 1 - conf_cost
                                else:
                                    offset=0
                                    for res in self.ScalingFunction.Max.keys():
                                        offset+=int(SCALINGFUNCTION_TARGET_OFFSET_OF_NODE_RESOURCES[res]*float(self.ScalingFunction.Max[res]))
                                    return total_cost + 1 - conf_cost + offset 

		def is_worker_scaleable(worker):
                        nonlocal scale_down
                        if scale_down:
                                for res in self.ScalingFunction.DominantResources:
                                    if worker.resources[res] == MINIMUM_RESOURCES[res]:
                                        return False
                                return True
                        else:
                                max_resources = self.ScalingFunction.Max
                                for res in self.ScalingFunction.DominantResources:
                                    if worker.resources[res] == max_resources[res]:
                                        return False
                                return True
                
		def worker_is_notflagged_testable_and_scaleable(worker,conf):
                       if not (worker.isFlagged() and not OPT_IN_FOR_RESTART) and is_testable(worker,conf) and is_worker_scaleable(worker):
                                return True
                       else:
                                return False

		def workers_are_notflagged_testable_and_scaleable(conf):
			for w in self.workers:
				if worker_is_notflagged_testable_and_scaleable(w,conf):
					print("Worker " + str(w.worker_id) + " is still scaleable")
					return True
			return False

		def scale_worker(workers, worker_index, nb_of_scaling_units):
                        nonlocal scale_down
                        if scale_down:
                                self.ScalingFunction.scale_worker_down(workers, worker_index, nb_of_scaling_units)
                                self.ScaledWorkerIndex=self.workers[wi].worker_id-1
                                self.ScaledDown = True
                        else:
                                self.ScalingFunction.scale_worker_up(workers, worker_index, nb_of_scaling_units)
                                self.ScaledUp = True



		def is_scaled():
			nonlocal scale_down
			return self.ScaledDown if scale_down else self.ScaledUp

		def set_scaled():
			nonlocal scale_down
			if scale_down:
				self.ScaledDown=True
			else:
				self.ScaledUp=True
		if not only_failed_results:
			self.only_failed_results=False
		states=[]
		totalcost = self.ScalingFunction.target(slo,tenant_nb)
		new_workers=[w.clone() for w in self.workers]
		for w in self.workers:
			print(w.resources)
		absolute_totalcost=0
		for res in totalcost.keys():
			absolute_totalcost+=totalcost[res]
		diff=difference(generator.resource_cost(self.workers, opt_conf), absolute_totalcost)
		print("difference between resource_cost optimal conf and predicted total cost -1")
		print(diff)
		worker_index=1
		L=len(self.workers)
		scaling=True if diff >= 0 else False
		while diff >= 0 and (worker_index <= L) and not is_scaled():
			wi=L-worker_index
			if worker_is_notflagged_testable_and_scaleable(self.workers[wi],opt_conf):
				if not self.workers[wi].worker_id in [fs.worker_id for fs in self.FailedScalings]:
					scale_worker(new_workers, wi, 1)
					diff = difference(generator.resource_cost(self.workers, opt_conf), absolute_totalcost)
					print("Rescaling worker " + str(self.workers[wi].worker_id))
					self.ScaledWorkerIndex=self.workers[wi].worker_id-1
					set_scaled()
				else:
					print("Passing over worker in previously failed scaling")
			worker_index += 1
		if is_scaled() and not self.equal_workers(new_workers):
			if scale_down:
				self.StartScalingDown=False
			self.workers=new_workers
			for w in self.workers:
				print(w.resources)
			states+=[RETRY_WITH_ANOTHER_WORKER_CONFIGURATION]
		else:
			self.FailedScalings=[]
			if scale_down and scaling and workers_are_notflagged_testable_and_scaleable(opt_conf):
				self.redo_scale_action(slo)
				#self.initial_confs=[]
				if not self.only_failed_results:
					return self.find_cost_effective_config(opt_conf, slo, tenant_nb, scale_down)
			else:
				states+=[NO_COST_EFFECTIVE_ALTERNATIVE]
		return states

	def is_worker_scaleable(self,worker_index):
                        if self.ScalingDownPhase:
                                for res in self.ScalingFunction.DominantResources:
                                    if self.workers[worker_index].resources[res] == MINIMUM_RESOURCES[res]:
                                        return False
                                return True
                        else:
                                max_resources = self.ScalingFunction.Max
                                for res in self.ScalingFunction.DominantResources:
                                    if self.workers[worker_index].resources[res] == max_resources[res]:
                                        return False
                                return True

	def workers_are_scaleable(self):
		for i,w in enumerate(self.workers):
			if self.is_worker_scaleable(i):
				print("Worker " + str(i) + " is still scaleable")
				return True
		return False

	def has_initial_confs_with_valid_results(self):
            if not self.initial_confs:
                return False
            response=False if self.ScalingUpPhase else True
            if self.ScalingUpPhase:
                for v in self.initial_confs:
                    if v[0]:
                        response=True
            return response

	def redo_scale_action(self, slo):
                self.scale_action_re_undone=True
                old_workers=[]
                print("CURRENT CONFS")
                for w in self.workers:
                        print(w.str())
                        old_workers.append(w.clone())
                worker_confs=[]
                print("INITIAL CONFS:")
                print(self.initial_confs)
                copy_of_initial_confs=self.initial_confs[:]
                for v in copy_of_initial_confs:
                        if self.ScalingDownPhase or (self.ScalingUpPhase and v[0]):
                            tmp_workers=v[2]
                            worker_confs+=[tmp_workers]
                        elif self.ScalingUpPhase and not v[0]:
                            self.initial_confs.remove(v)
                if not self.initial_confs:
                    print("No initial confs left")
                for i,conf in enumerate(self.initial_confs):
                    print("Conf " + str(i)+ ":")
                    if conf[0]:
                        print(conf[0]['CompletionTime'])
                    else:
                        print("No result")
                print("INITIALS WORKER_CONFS:")
                for i in worker_confs:
                        for w in i:
                                print(w.str())
                        print("---------------------------------")
                if self.ScalingUpPhase:
                     costs=[generator.resource_cost(wcomb[0], wcomb[1][1]) for wcomb in zip(worker_confs,self.initial_confs)]
                else:
                     costs=[generator.resource_cost(wcomb, [1 for w in self.workers]) for wcomb in worker_confs]
                cheapest_worker_index=costs.index(min(costs))
                print("cheapest_worker_index: " + str(cheapest_worker_index))
                self.workers=worker_confs[cheapest_worker_index] 
                if self.ScalingUpPhase:
                    print("Going back to worker configuration with lowest cost for combination " + utils.array_to_delimited_str(self.initial_confs[cheapest_worker_index][1]) + " and result")
                    print(self.initial_confs[cheapest_worker_index][0])
                else:
                    print("Going back to worker configuration with lowest cost: ")
                for w in self.workers:
                        print(w.str())
                print("---------------------------------")
                print("Updating scaling function")
                tmp_workers=[]
                for w in self.workers:
                        print(w.str())
                        tmp_workers.append(w.clone())
                for i,w in enumerate(self.workers):
                        for res in self.ScalingFunction.DominantResources:
                                existing_amount=old_workers[i].resources[res]
                                while w.resources[res] < existing_amount:
                                        self.ScalingFunction.scale_worker_down(tmp_workers, i, 1)
                                        existing_amount=-1
                print("Double checking worker configuration:")
                for w in self.initial_confs[cheapest_worker_index][2]:
                        print(w.str())
                print("Double checking scaling function:")
                print(self.ScalingFunction.workersScaledDown)
                if self.ScalingUpPhase:
                    return self.initial_confs[cheapest_worker_index]
                else:
                    if cheapest_worker_index == 0 and self.initial_confs[0][0]['CompletionTime']:
                        completion_time=self.initial_confs[0][0]['CompletionTime']
                    else:
                        completion_time=str(float(slo)+9999999)
                    #self.initial_confs[0][0]=self.create_result(completion_time, self.initial_confs[0][1],self.initial_confs[0][0]['SLAName'])
                    return [self.create_result(completion_time, self.initial_confs[0][1],self.initial_confs[0][0]['SLAName']),self.initial_confs[0][1],self.workers]

	def create_result(self, completion_time, conf, sla_name):
                result={'config': '0'}
                for i,w in enumerate(self.workers):
                    result["worker"+str(i+1)+".replicaCount"]=str(conf[i])
                    result["worker"+str(i+1)+".resources.requests.cpu"]=str(w.resources['cpu'])
                    result["worker"+str(i+1)+".resources.requests.memory"]=str(w.resources['memory'])
                    result['score']='n/a'
                    result['best_score']='n/a'
                    result['SLAName']=sla_name
                    if completion_time == 0:
                        result['CompletionTime']= '0'
                        result['Successfull']='false'
                    else:
                        result['CompletionTime']= completion_time
                        result['Successfull']='true'
                print(result)
                return result


	def set_tipped_over_failed_confs(self):
		if not self.tipped_over_confs:
                        self.tipped_over_confs = self.failed_results[:]
                        print("TIPPED_OVER_CONFS")
                        print(self.tipped_over_confs)
		return self.tipped_over_confs

	def find_cost_effective_tipped_over_conf(self, slo, tenant_nb):
                conf_index = 0
                result_conf_and_workers=[]
                states=[]
                state=None
                while len(self.tipped_over_confs) > 0:
                        states=self.find_cost_effective_config(self.tipped_over_confs[conf_index], slo, tenant_nb, scale_down=False, only_failed_results=True)
                        copy_of_states=states[:]
                        state=states.pop(0)
                        if state == RETRY_WITH_ANOTHER_WORKER_CONFIGURATION:
                                self.current_tipped_over_conf=self.tipped_over_confs[conf_index]
                                return [[{},self.current_tipped_over_conf,self.workers],copy_of_states]
                        elif state == NO_COST_EFFECTIVE_ALTERNATIVE:
                                self.tipped_over_confs.pop(0)
                if not state:
                        states=[NO_COST_EFFECTIVE_ALTERNATIVE]
                        copy_of_states=states[:]
                        state=states.pop(0)
                        #result_and_conf=self.initial_confs[-1]
                if self.ScalingUpPhase and self.has_initial_confs_with_valid_results():
                        copy_of_states+=[REDO_SCALE_ACTION]
                        result_conf_and_workers=self.redo_scale_action(slo)
                return [result_conf_and_workers, copy_of_states]


	def equal_workers(self,workersB):
                if len(self.workers) != len(workersB):
                        return False
                for a,b in zip(self.workers,workersB):
                        if not a.equals(b):
                              return False
                return True


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
