from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .searchwindow import AdaptiveWindow, ScalingFunction, AdaptiveScaler, COST_EFFECTIVE_RESULT, NO_RESULT, NO_COST_EFFECTIVE_RESULT, UNDO_SCALE_ACTION, REDO_SCALE_ACTION, RETRY_WITH_ANOTHER_WORKER_CONFIGURATION,NO_COST_EFFECTIVE_ALTERNATIVE, SCALING_UP_THRESHOLD
from functools import reduce

THRESHOLD = -1
NB_OF_CONSTANT_WORKER_REPLICAS = 1
MAXIMUM_TRANSITION_COST=2
MINIMUM_SHARED_REPLICAS=2
SAMPLING_RATE=1.0
SCALINGFUNCTION_TARGET_OFFSET_OF_WINDOW=-1.0
NODES=[{"cpu": 4,"memory": 8},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 16},{"cpu": 8,"memory": 16},{"cpu": 8,"memory": 16},{"cpu": 3,"memory": 6}]

def create_workers(elements, costs, base):
    resources=[v['size'] for v in elements]
    workers=[]
    for i in range(0,len(resources)):
        worker_conf=WorkerConf(worker_id=i+1, resources=resources[i], costs=costs[i], min_replicas=0,max_replicas=base-1)
        workers.append(worker_conf)
    return workers


def generate_matrix(initial_conf):

	def get_start_and_window_for_next_experiments(opt_conf=None):
                                    nonlocal result
                                    nonlocal slo
                                    nonlocal tenant_nb
                                    nonlocal retry_attempt
                                    nonlocal lst
                                    nonlocal adaptive_scaler
                                    nonlocal nr_of_experiments
                                    nonlocal adaptive_window
                                    nonlocal results
                                    nonlocal startTenant

                                    only_failed_results=False if result else True

                                    def process_states(conf_and_states):
                                        nonlocal result
                                        nonlocal slo
                                        nonlocal tenant_nb
                                        nonlocal retry_attempt
                                        nonlocal lst
                                        nonlocal adaptive_scaler
                                        nonlocal nr_of_experiments
                                        nonlocal startTenant
                                        nonlocal only_failed_results

                                        conf=conf_and_states[0]
                                        states=conf_and_states[1]
                                        state=states.pop(0)

                                        if state == RETRY_WITH_ANOTHER_WORKER_CONFIGURATION:
                                            print("RETRYING WITH ANOTHER WORKER CONFIGURATION")
                                            retry_attempt+=nr_of_experiments
                                            lst=sort_configs(adaptive_scaler.workers,lst)
                                            result={}
                                            if adaptive_scaler.ScalingDownPhase:
                                                    previous_tenant_results={}
                                                    if tenant_nb > startTenant:
                                                            previous_tenant_results=d[sla['name']]
                                                    print("Moving filtered samples in sorted combinations after the window")
                                                    print([utils.array_to_str(el) for el in lst])
                                                    start_and_window=filter_samples(lst, adaptive_scaler.workers, start, window, previous_tenant_results, startTenant, tenant_nb-1, True, adaptive_scaler.ScaledWorkerIndex)
                                                    print([utils.array_to_str(el) for el in lst])
                                                    return start_and_window
                                            else:
                                                    next_conf=adaptive_scaler.current_tipped_over_conf
                                                    return [lst.index(next_conf), 1]
                                        elif state ==  NO_COST_EFFECTIVE_ALTERNATIVE:
                                            print("NO BETTER COST EFFECTIVE ALTERNATIVE IN SIGHT")
                                            if states and states.pop(0) == REDO_SCALE_ACTION:
                                                    print("REDOING_CHEAPEST_SCALED_DOWN")
                                                    lst=sort_configs(adaptive_scaler.workers,lst)
                                                    opt_conf=conf[1] 
                                                    result=conf[0]
                                                    only_failed_results=False
                                            if adaptive_scaler.ScalingUpPhase:
                                                    remove_failed_confs(lst, adaptive_scaler.workers, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(), False, adaptive_scaler.failed_results,tenant_nb == startTenant)
                                                    if not adaptive_scaler.tipped_over_confs:
                                                            adaptive_scaler.reset()
                                                    if not only_failed_results:
                                                            d[sla['name']][str(tenant_nb)]=result
                                                            tenant_nb+=1
                                                            retry_attempt=0
                                                            next_conf=opt_conf
                                                            flag_workers(adaptive_scaler.workers,next_conf)
                                                            return [lst.index(next_conf),1]
                                                    else:
                                                            retry_attempt+=nr_of_experiments
                                                            lst=sort_configs(adaptive_scaler.workers,lst)
                                                            print("Moving filtered samples in sorted combinations after the window")
                                                            print([utils.array_to_str(el) for el in lst])
                                                            previous_tenant_results={}
                                                            if tenant_nb > startTenant:
                                                                  previous_tenant_results=d[sla['name']]
                                                            start_and_window=filter_samples(lst,adaptive_scaler.workers,0, window, previous_tenant_results, startTenant, tenant_nb-1)
                                                            print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                            print([utils.array_to_str(el) for el in lst])
                                                            return start_and_window
                                            else:
                                                    adaptive_scaler.reset()
                                                    adaptive_scaler.set_tipped_over_failed_confs(results, slo)
                                                    conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                                    return process_states(conf_and_states)

                                    if not opt_conf and result:
                                            opt_conf=get_conf(adaptive_scaler.workers, result)
                                    elif not opt_conf and not result:
                                            if not adaptive_scaler.ScalingUpPhase:
                                                    exit("No result during scaling down phase, thus explicit optimal conf needed")
                                    if adaptive_scaler.ScalingDownPhase:
                                            states=adaptive_scaler.find_cost_effective_config(opt_conf, slo, tenant_nb)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states([[],states])
                                    elif adaptive_scaler.ScalingUpPhase:
                                            adaptive_scaler.set_tipped_over_failed_confs(results, slo)
                                            conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states(conf_and_states) 
                                    for w in adaptive_scaler.workers:
                                            print(w.resources['cpu'])


	bin_path=initial_conf['bin']['path']
	chart_dir=initial_conf['charts']['chartdir']
	exp_path=initial_conf['output']
	util_func=initial_conf['utilFunc']
	slas=initial_conf['slas']

	d={}

	for sla in slas:
		alphabet=sla['alphabet']
		window=alphabet['searchWindow']
		adaptive_window=AdaptiveWindow(window)
		base=alphabet['base']
		scalingFunction=ScalingFunction(667.1840993,-0.8232555,136.4046126, {"cpu": 2, "memory": 2}, alphabet['costs'], ["cpu"],NODES)
		workers=create_workers(alphabet['elements'], alphabet['costs'], base)
                #workers=[WorkerConf(worker_id=i+1, cpu=v['size']['cpu'], memory=v['size']['memory'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
		# HARDCODED => make more generic by putting workers into an array
		workers[0].setReplicas(min_replicas=0,max_replicas=0)
		workers[1].setReplicas(min_replicas=0,max_replicas=0)
		workers[2].setReplicas(min_replicas=0,max_replicas=0)
		workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
	#	workers[0].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
		adaptive_scaler=AdaptiveScaler(workers, scalingFunction)
		lst=_sort(adaptive_scaler.workers,base)
		print([utils.array_to_str(el) for el in lst])
		exps_path=exp_path+'/'+sla['name']
		#next_exp=_find_next_exp(lst,adaptive_scaler.workers,[],lst[0],base,window)
		d[sla['name']]={}
		#tenant_nb=1
		retry_attempt=0
		#start=0
		#next_conf=[]
		#ScaledDown=False
		#FailedScalings=[]
		#ScaledWorkerIndex=-1
		startTenant = sla['startTenant']
		tenant_nb = startTenant
		slo=float(sla['slos']['completionTime'])
		next_conf=get_conf_for_start_tenant(slo,tenant_nb,adaptive_scaler,lst,window)
		start=lst.index(next_conf)
		next_exp=_find_next_exp(lst,adaptive_scaler.workers,[],next_conf,base,window)
		while tenant_nb <= sla['maxTenants']:
			results=[]
			nr_of_experiments=len(next_exp)
			print("Running " + str(nr_of_experiments) + " experiments") 
			for i,ws in enumerate(next_exp):
				#samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws[0]])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws[0],sla['slos'])
				samples=int(ws[4]*SAMPLING_RATE)
				if samples == 0:
					samples=1
				for res in _generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i+retry_attempt),ws[1],ws[2],ws[3]):
					results.append(res)
			result=find_optimal_result(adaptive_scaler.workers,results)
			#slo=float(sla['slos']['completionTime'])
			print("SLO is " + str(slo))
			if result:
				print("RESULT FOUND")
				metric=float(result['CompletionTime'])
				print("Measured completion time is " + str(metric))
				conf=get_conf(adaptive_scaler.workers,result)
				print(conf)
			print("New cycle")
			for w in adaptive_scaler.workers:
				print(w.resources)
			states=adaptive_scaler.validate_result(result, get_conf(adaptive_scaler.workers,result), slo)
			print(states)
			state=states.pop(0)
			print("State of adaptive_scaler")
			adaptive_scaler.status()
			if adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
				adaptive_scaler.failed_results = return_failed_confs(workers, results, lambda r: float(r['score']) < THRESHOLD and r['Successfull'] == 'true' and float(r['CompletionTime']) <= slo * SCALING_UP_THRESHOLD)
			if state == NO_COST_EFFECTIVE_RESULT:
				print("NO COST EFFECTIVE RESULT")
				if states and states.pop(0) == UNDO_SCALE_ACTION:
					print("Previous scale down undone")
					lst=sort_configs(adaptive_scaler.workers,lst)
				else: 
					remove_failed_confs(lst, adaptive_scaler.workers, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),False,[], tenant_nb == startTenant)
				start_and_window=get_start_and_window_for_next_experiments()
				print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
				start=start_and_window[0]
				new_window=start_and_window[1]
				next_conf=lst[start]
			elif state == COST_EFFECTIVE_RESULT:
				print("COST-EFFECTIVE-RESULT")
				if adaptive_scaler.ScalingUpPhase:
					lst=sort_configs(adaptive_scaler.workers,lst)
				remove_failed_confs(lst, adaptive_scaler.workers, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),True,adaptive_scaler.failed_results,tenant_nb == startTenant)
				if adaptive_scaler.ScalingUpPhase:
					adaptive_scaler.reset()
				d[sla['name']][str(tenant_nb)]=result
				tenant_nb+=1
				retry_attempt=0
				next_conf=get_conf(adaptive_scaler.workers, result)
				flag_workers(adaptive_scaler.workers,next_conf)
				new_window=window
				start=lst.index(next_conf)
			elif state == NO_RESULT:
				print("NO RESULT")
				if states and states.pop(0) == UNDO_SCALE_ACTION:
					print("Previous scale action undone")
					lst=sort_configs(adaptive_scaler.workers,lst)
					start_and_window=get_start_and_window_for_next_experiments(opt_conf=lst[0])
					print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
					start=start_and_window[0]
					new_window=start_and_window[1]
					next_conf=lst[start]
					result={}
					retry_attempt+=nr_of_experiments
				else:
					remove_failed_confs(lst, adaptive_scaler.workers, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),False,[],tenant_nb == startTenant)
					new_window=window
					lst=sort_configs(adaptive_scaler.workers,lst)
					next_conf=lst[0]
					start=0
					if adaptive_scaler.ScalingDownPhase and adaptive_scaler.failed_results:
						adaptive_scaler.reset()
						start_and_window=get_start_and_window_for_next_experiments()
						print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
						start=start_and_window[0]
						new_window=start_and_window[1]
						next_conf=lst[start]
					else: 
						previous_tenant_results={}
						if tenant_nb > startTenant:
							previous_tenant_results=d[sla['name']]
						print("Moving filtered samples in sorted combinations after the window")
						print([utils.array_to_str(el) for el in lst])
						start_and_window=filter_samples(lst, adaptive_scaler.workers, 0, window, previous_tenant_results, startTenant, tenant_nb-1)
						print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
						print([utils.array_to_str(el) for el in lst])
						next_conf=lst[start_and_window[0]]
						start=start_and_window[0]
						new_window=start_and_window[1]
						result={}
						retry_attempt+=nr_of_experiments

			for w in adaptive_scaler.workers:
				adaptive_scaler.untest(w)
			next_exp=_find_next_exp(lst,adaptive_scaler.workers,result,next_conf,base,adaptive_window.adapt_search_window(result,new_window,False))
	print("Saving results into matrix")
	utils.saveToYaml(d,'Results/matrix.yaml')


#def get_conf_for_start_tenant(slo, tenant_nb, adaptive_scaler, combinations):
#       target=adaptive_scaler.ScalingFunction.target(slo, tenant_nb)
#       total_cost=target['cpu']+target['memory']
#       print("total_cost = " + str(total_cost))
#       for conf in combinations:
#           if resource_cost(adaptive_scaler.workers, conf) > total_cost:
#               return conf
#       return []

def get_conf_for_start_tenant(slo, tenant_nb, adaptive_scaler, combinations, window):
       if len(combinations) == 0:
           return []
       target=adaptive_scaler.ScalingFunction.target(slo, tenant_nb)
       total_cost=0
       for i in target.keys():
           total_cost+=target[i]
       print("total_cost = " + str(total_cost))
       index=0
       conf=combinations[index]
       while index < len(combinations)-1 and resource_cost(adaptive_scaler.workers, conf) <  total_cost:
           index+=1
           conf=combinations[index]
       if resource_cost(adaptive_scaler.workers, conf) >=  total_cost:
           solution_index=max(0,combinations.index(conf)+int(window*SCALINGFUNCTION_TARGET_OFFSET_OF_WINDOW))
           return combinations[solution_index]
       else:
           return []




def involves_worker(workers, conf, worker_index):
	print("SCALING INDEX = " +  str(worker_index))
	if worker_index < 0 or worker_index >= len(workers):
		return True
	if conf[worker_index] > 0:
		return True
	else:
		return False


def all_flagged_conf(workers, conf):
	if not (workers and conf):
		return False
	for w,c in zip(workers, conf):
		if not w.isFlagged() and c > 0:
			return False
	result=True
	for w,c in zip(workers, conf):
		if w.isFlagged() and c == 0:
			result=False
	return  result

def flag_workers(workers, conf):
	for k,v in enumerate(conf):
		if v > 0:
			workers[k].flag()

#def tag_tested_workers(workers, conf):
#	 for k,v in enumerate(conf):
#                if v > 0:
#                        workers[k].tested()



def remove_failed_confs(sorted_combinations, workers, results, slo, optimal_conf, start, window, optimal_conf_is_cost_effective, tipped_over_results,startingTenant=False):
		if optimal_conf and optimal_conf_is_cost_effective:
			if tipped_over_results and optimal_conf in tipped_over_results:
				tipped_over_results.remove(optimal_conf)
			tmp_combinations=sort_configs(workers,sorted_combinations, cost_aware=False)
			failed_range=tmp_combinations.index(optimal_conf)
			for i in range(0, failed_range):
				possible_removal=tmp_combinations[i]
				if resource_cost(workers, possible_removal,cost_aware=False) < (resource_cost(workers, optimal_conf, cost_aware=False) ):
					print("Removing config because it has a lower resource cost than the optimal result and we assume it will therefore fail for the next tenant")
					print(possible_removal)
					sorted_combinations.remove(possible_removal)
		elif not optimal_conf and SAMPLING_RATE < 1.0 and SAMPLING_RATE >= 0.5:
			failed_range=start+window
			print("Removing all configs in window going over the scaling_up_threshold because no optimal config has been found at all")
			index=0 if startingTenant else start
			possible_tipped_over_confs=return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) <= slo * SCALING_UP_THRESHOLD and r['Successfull'] == 'true')
			for i in range(start,failed_range,1):
				print("???")
				print(sorted_combinations[index])
				if not sorted_combinations[index] in possible_tipped_over_confs:
					print(sorted_combinations[index])
					sorted_combinations.remove(sorted_combinations[index])
				else:
					index+=1
		#for failed_conf in return_failed_confs(workers,results, lambda result: float(result['score']) <= THRESHOLD):
		for failed_conf in return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) > slo * SCALING_UP_THRESHOLD):
			if failed_conf in sorted_combinations:
				print("Removing failed conf")
				print(failed_conf)
				sorted_combinations.remove(failed_conf)
		if tipped_over_results:
			for failed_conf in tipped_over_results:
				if failed_conf in sorted_combinations:
					print("Removing tipped over conf")
					print(failed_conf)
					sorted_combinations.remove(failed_conf)


def filter_samples(sorted_combinations, workers, start, window, previous_results, start_tenant, tenant_nb, check_workers=False, ScaledDownWorkerIndex=-1):
        i=start_tenant
        new_window=window
        start_window=window
        if previous_results:
                while i <= tenant_nb:
                        previous_tenant_conf=get_conf(workers, previous_results[str(i)])
                        for el in range(start, start+window):
                                result_conf=sorted_combinations[el-(window-new_window)]
                                print(result_conf)
                                qualitiesOfSample=_pairwise_transition_cost(previous_tenant_conf,result_conf)
                                cost=qualitiesOfSample['cost']
                                nb_shrd_replicas=qualitiesOfSample['nb_shrd_repls']
                                if isinstance(MINIMUM_SHARED_REPLICAS,int):
                                        minimum_shared_replicas = min([MINIMUM_SHARED_REPLICAS,reduce(lambda x, y: x + y, previous_tenant_conf)])
                                else:
                                        minimum_shared_replicas = max([1,int(MINIMUM_SHARED_REPLICAS*reduce(lambda x, y: x + y, previous_tenant_conf))])
                                if (check_workers and all_flagged_conf(workers, result_conf)) or cost > MAXIMUM_TRANSITION_COST or nb_shrd_replicas < minimum_shared_replicas or not (not check_workers or involves_worker(workers, result_conf, ScaledDownWorkerIndex)):
                                        print("removed")
                                        sorted_combinations.remove(result_conf)
                                        sorted_combinations.insert(new_window+el-1,result_conf)
                                        new_window-=1

                                else:
                                        print("not removed")
                        if new_window == 0:
                                return filter_samples(sorted_combinations, workers, start+start_window, start_window, previous_results, start_tenant, tenant_nb, check_workers, ScaledDownWorkerIndex)
                        else:
                                i+=1
                                window=new_window
                                while i <= tenant_nb and equal_conf(previous_tenant_conf,get_conf(workers, previous_results[str(i)])):
                                        i+=1
        else:
                for el in range(start, start+window):
                        result_conf=sorted_combinations[el-(window-new_window)]
                        print(result_conf)
                        if not (not check_workers or involves_worker(workers, result_conf, ScaledDownWorkerIndex)):
                                print("removed")
                                sorted_combinations.remove(result_conf)
                                sorted_combinations.insert(start+new_window+el-1,result_conf)
                                new_window-=-1
                        else:
                                print("not removed")
                if new_window == 0:
                        return filter_samples(sorted_combinations, workers, start+window, window, previous_results, start_tenant, tenant_nb, check_workers, ScaledDownWorkerIndex)
        return [start, new_window]

def equal_conf(conf1, conf2):
        for x, y in zip(conf1, conf2):
                if x != y:
                        return False
        return True


def get_conf(workers, result):
	if result:
		return [int(result['worker'+str(worker.worker_id)+'.replicaCount']) for worker in workers]
	else:
		return []


#def return_cost_optimal_conf(workers,results):
#        optimal_results=sort([result for result in results if float(result['score']) > THRESHOLD])
#        if optimal_results:
#    	        return get_conf(workers,optimal_results[0])
#        else:
#                return []
# 


def return_failed_confs(workers,results, f):
#	if DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT:
	failed_results=[result for result in results if f(result)]
	return sort_configs(workers,[get_conf(workers,failed_result) for failed_result in failed_results])
#	else:
#		return []


#def tag_tested_workers(workers, results):
#	for r in results:
#		for k,v in enumerate(get_conf(workers, r)):
#			if v > 0:
#				workers[k].tested()


def find_optimal_result(workers,results):
	print("Results")
	print(results)
	filtered_results=[result for result in results if float(result['score']) > THRESHOLD]
	print("Filtered results")
	if filtered_results:
		filtered_results=sort_results(filtered_results)
		print(filtered_results)
		return filtered_results[0]
	else:
		return {}


#def find_maximum(workers,experiments):
#	configs=[]
#	for exp in experiments:
#		conf=[c.max_replicas for c in exp]
#		configs.append(conf)
#	configs.reverse()
#	resource_costs=[_resource_cost(workers, c) for c in configs]
#	index=resource_costs.index(max(resource_costs))
#	return configs[index]


def generate_matrix2(initial_conf):
        bin_path=initial_conf['bin']['path']
        chart_dir=initial_conf['charts']['chartdir']
        exp_path=initial_conf['output']
        util_func=initial_conf['utilFunc']
        slas=initial_conf['slas']

        d={}

        for sla in slas:
                alphabet=sla['alphabet']
                window=alphabet['searchWindow']
                adaptive_window=AdaptiveWindow(window)
                base=alphabet['base']
                scalingFunction=ScalingFunction(667.1840993,-0.8232555,136.4046126, {"cpu": 2, "memory": 2}, alphabet['costs'], ["cpu"],NODES)
                workers=create_workers(alphabet['elements'], alphabet['costs'], base)
                for w in workers:
                        print(w.resources)
                # HARDCODED => make more generic by putting workers into an array
                workers[0].setReplicas(min_replicas=0,max_replicas=0)
                workers[1].setReplicas(min_replicas=0,max_replicas=0)
                workers[2].setReplicas(min_replicas=0,max_replicas=0)
                workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
                #print(smallest_worker_of_conf(workers, [1,0,0,0]).worker_id)
                w2=workers[3].clone()
                print(w2.equals(workers[3]))
                for w in workers:
                        print(w.resources)
                        print(w.costs)
                print(workers[0].str())
                print("scalingFunction.scale_worker_down(workers,0,1)")
                scalingFunction.scale_worker_down(workers,0,1)
                print(scalingFunction.workersScaledDown)
                for w in workers:
                        print(w.resources)
                print("scalingFunction.scale_worker_down(workers,0,1)")
                scalingFunction.scale_worker_down(workers,0,1)
                print(scalingFunction.workersScaledDown)
                for w in workers:
                        print(w.resources)
                print("scalingFunction.undo_scaled_down(workers)")
                scalingFunction.undo_scaled_down(workers)
                print(scalingFunction.workersScaledDown)
                for w in workers:
                        print(w.resources)
                print("scalingFunction.scale_worker_down(workers,0,1)")
                scalingFunction.scale_worker_down(workers,0,1)
                for w in workers:
                        print(w.resources)
                print(scalingFunction.workersScaledDown)
                print("scalingFunction.undo_scaled_down(workers)")
                scalingFunction.undo_scaled_down(workers)
                for w in workers:
                        print(w.resources)

def sort_results(results):
	def score_for_sort(result):
		return  -1*float(result['score']) 

	return sorted(results,key=score_for_sort)


def sort_configs(workers,combinations,cost_aware=True):
	def cost_for_sort(elem):
                return resource_cost(workers,elem,cost_aware)

	sorted_list=sorted(combinations, key=cost_for_sort)
	return sorted_list



def _sort(workers,base):
	def cost_for_sort(elem):
		return resource_cost(workers,elem)

	initial_conf=int(utils.array_to_str([worker.min_replicas for worker in workers]),base)
	max_conf=int(utils.array_to_str([base-1 for worker in workers]),base)
	print(initial_conf)
	print(max_conf)
	index=range(initial_conf,max_conf+1)
	comb=[utils.number_to_base(c,base) for c in index]
        #comb=[utils.array_to_str(utils.number_to_base(combination,base)) for combination in range(min_conf_dec,max_conf_dec+1)]
	for c1 in comb:
		while len(c1) < len(workers):
			c1.insert(0,0)
	sorted_list=sorted(comb,key=cost_for_sort)
	return sorted_list




def resource_cost(workers, conf, cost_aware=True):
        cost=0
        for w,c in zip(workers,conf):
            worker_cost=0
            for resource_name in w.resources.keys():
                 weight=w.costs[resource_name] if cost_aware else 1
                 worker_cost+=w.resources[resource_name]*weight*c
            cost+=worker_cost
        return cost


def _pairwise_transition_cost(previous_conf,conf):
        if not previous_conf:
               return {'cost': 0, 'nb_shrd_repls': MINIMUM_SHARED_REPLICAS}
        cost=0
        shared_replicas=0
        for c1,c2 in zip(conf,previous_conf):
               if  c1 > c2:
                       cost+=c1-c2
               if c2 >= 1  and c1 >= 1:
                       shared_replicas+=min(c1,c2)
        return {'cost': cost, 'nb_shrd_repls': shared_replicas}




def _find_next_exp(sorted_combinations, workers, results, next_conf, base, window):
	workers_exp=[]
	min_conf=next_conf
	print("min_conf: " + utils.array_to_delimited_str(min_conf, " "))
	intervals=_split_exp_intervals(sorted_combinations, min_conf, window, base)
	print("Next possible experiments for next nb of tenants")
	print(intervals["exp"])
	tmp_workers=leftShift(workers, intervals["nbOfshiftsToLeft"])
	length=len(sorted_combinations[0])
	nb_of_variable_workers=length-NB_OF_CONSTANT_WORKER_REPLICAS
	for k, v in intervals["exp"].items():
		const_workers=k.split(" ")
		constant_ws_replicas=map(lambda a: int(a),const_workers)  
		max_replica_count_index=0
		min_replica_count_index=99999999
		nb_of_samples=len(v)
		elementstr="["
		for variable_workers in v:
			back_shifted_conf=rightShift([int(el) for el in const_workers]+variable_workers,intervals["nbOfshiftsToLeft"])
			elementstr=elementstr+"[" + utils.array_to_delimited_str(back_shifted_conf,",") + "];"
			index=sorted_combinations.index(back_shifted_conf)
			if index > max_replica_count_index:
				max_replica_count_index=index 
			if index < min_replica_count_index:
				min_replica_count_index=index
		last_char_index=elementstr.rfind(";")
		elementstr = elementstr[:last_char_index] + "]"
		print("Elementstr: " + elementstr)
		max_replica_count=utils.array_to_delimited_str(sorted_combinations[max_replica_count_index], " ")
		min_replica_count=utils.array_to_delimited_str(sorted_combinations[min_replica_count_index], " ")
		experiment=[]
		for replicas,worker in zip(constant_ws_replicas,tmp_workers[:-nb_of_variable_workers]):
			new_worker=WorkerConf(worker.worker_id,worker.resources,worker.costs,replicas,replicas)
			experiment.append(new_worker)
		for i in reversed(range(0,nb_of_variable_workers)):
			l=i+1
			worker_min=min(map(lambda a: int(a[-l]),v))
			worker_max=max(map(lambda a: int(a[-l]),v))
			new_worker=WorkerConf(tmp_workers[-l].worker_id,tmp_workers[-l].resources,tmp_workers[-l].costs,worker_min,worker_max)
			experiment.append(new_worker)
		workers_exp.append([experiment, elementstr, min_replica_count,max_replica_count,nb_of_samples])
		print("Min replicacount:" + min_replica_count)
		print("Max replicacount:" + max_replica_count)

	return workers_exp


def leftShift(text,n):
        return text[n:] + text[:n]

def rightShift(text,n):
	return text[-n:] + text[:-n]



def _split_exp_intervals(sorted_combinations, min_conf, window, base):
	min_conf_dec=sorted_combinations.index(min_conf)
	print("min_conf_dec: " + str(min_conf_dec))
	max_conf_dec=min_conf_dec+window
	combinations=[sorted_combinations[c][:] for c in range(min_conf_dec,max_conf_dec)]
	for c in range(min_conf_dec,max_conf_dec):
		print(c)
		print(sorted_combinations[c])
	list=[]
	length=len(combinations[0])
	rotated_combinations=[[leftShift(comb,i) for i in range(0,length)] for comb in combinations]
	expMin=dict(zip(range(0,window+1), range(0,window+1)))
	max=-1
	nb_of_variable_workers=length-NB_OF_CONSTANT_WORKER_REPLICAS
	for i in range(0, length):
		exp={}
		for c in rotated_combinations:
			exp[utils.array_to_delimited_str(c[i][:-nb_of_variable_workers]," ")]=[]

		for c in rotated_combinations:
			tmp_lst=[]
			for j in range(0,nb_of_variable_workers):
				l=j+1
				tmp_lst.insert(0,c[i][-l])
			exp[utils.array_to_delimited_str(c[i][:-nb_of_variable_workers]," ")].append(tmp_lst)
		print(exp)
		if len(exp.keys()) < len(expMin.keys()):
			expMin=exp
			max=i

	return {"exp":expMin, "nbOfshiftsToLeft": max}



def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path, conf, minimum_repl, maximum_repl):
	# conf_ex=ConfigParser(
	# 	optimizer='exhaustive',
	# 	chart_dir=chart_dir,
	# 	util_func= util_func,
	# 	samples= samples,
	# 	output= exp_path+'/exh',
	# 	slas=slas)
		
	conf_op=ConfigParser(
		optimizer='bestconfig',
		chart_dir=chart_dir,
		util_func= util_func,
		samples= samples,
		sampling_rate=SAMPLING_RATE,
		output= exp_path+'/op/',
		# prev_results=exp_path+'/exh/results.json',
		slas=slas,
		maximum_replicas='"'+maximum_repl+'"',
		minimum_replicas='"'+minimum_repl+'"',
		configs='"'+conf+'"')

	# exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op/')

	# exp_ex.runExperiment()
	exp_op.runExperiment()

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()

	return results


