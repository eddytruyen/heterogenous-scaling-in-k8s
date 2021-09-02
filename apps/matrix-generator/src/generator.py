from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .searchwindow import AdaptiveWindow, ScalingFunction, AdaptiveScaler, COST_EFFECTIVE_RESULT, NO_RESULT, NO_COST_EFFECTIVE_RESULT, UNDO_SCALE_ACTION, REDO_SCALE_ACTION, RETRY_WITH_ANOTHER_WORKER_CONFIGURATION,NO_COST_EFFECTIVE_ALTERNATIVE,SCALING_DOWN_TRESHOLD,SCALING_UP_THRESHOLD,MINIMUM_RESOURCES
from . import runtimemanager
from functools import reduce
import yaml
import sys
import os

NB_OF_CONSTANT_WORKER_REPLICAS = 1
MAXIMUM_TRANSITION_COST=2
MINIMUM_SHARED_REPLICAS=2
SAMPLING_RATE=0.75
SCALINGFUNCTION_TARGET_OFFSET_OF_WINDOW=0.0

def create_workers(elements, costs, base):
    resources=[v['size'] for v in elements]
    workers=[]
    for i in range(0,len(resources)):
        worker_conf=WorkerConf(worker_id=i+1, resources=resources[i], costs=costs[i], min_replicas=0,max_replicas=base-1)
        workers.append(worker_conf)
    return workers


# update matrix with makespan of the previous sparkbench-run  consisting of #previous_tenants, using configuration previous_conf
# and obtaining performance metric completion_time. The next request is for #tenants. If no entry exists in the matrix, see if there is an entry for a previous
# tenant; otherwise using the curve-fitted scaling function to estimate a target configuration.
def generate_matrix(initial_conf, adaptive_scalers, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf):

	def get_next_exps(conf, window):
                        next_exp=_find_next_exp(lst,adaptive_scaler.workers,conf,base,adaptive_window.adapt_search_window({},window,False))
                        nr_of_experiments=len(next_exp)
                        for i,ws in enumerate(next_exp):
                                #samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws[0]])
                                sla_conf=SLAConf(sla['name'],int(tenants),ws[0],sla['slos'])
                                samples=int(ws[4]*SAMPLING_RATE)
                                if samples == 0:
                                        samples=1
                                results=[]
                                sample_list=_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+tenants+'_tenants-ex'+str(i),ws[1],ws[2],ws[3])
                                rm.set_experiment_list(i,ws,sample_list)#sort_results(adaptive_scaler.workers,slo,sample_list))

	def get_start_and_window_for_next_experiments(opt_conf=None):

                                    only_failed_results=False if result else True

                                    def process_states(conf_and_states):
                                        nonlocal result
                                        nonlocal slo
                                        nonlocal tenant_nb
                                        nonlocal lst
                                        nonlocal adaptive_scaler
                                        nonlocal nr_of_experiments
                                        nonlocal startTenants
                                        nonlocal tenants
                                        nonlocal previous_tenants
                                        nonlocal previous_conf
                                        nonlocal maxTenants
                                        nonlocal opt_conf
                                        nonlocal start
                                        nonlocal only_failed_results

                                        conf=conf_and_states[0]
                                        states=conf_and_states[1]
                                        state=states.pop(0)

                                        if state == RETRY_WITH_ANOTHER_WORKER_CONFIGURATION:
                                            print("RETRYING WITH ANOTHER WORKER CONFIGURATION")
                                            lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                                            if opt_conf != None:
                                                    start=lst.index(opt_conf)
                                            result={}
                                            if adaptive_scaler.ScalingDownPhase:
                                                    previous_tenant_results={}
                                                    if tenant_nb > 1:
                                                            previous_tenant_results=d[sla['name']]
                                                    print("Moving filtered samples in sorted combinations after the window")
                                                    print([utils.array_to_str(el) for el in lst])
                                                    start_and_window=filter_samples(lst,adaptive_scaler.workers,start, window, previous_tenant_results, 1, tenant_nb, True, adaptive_scaler.ScaledWorkerIndex)
                                                    if start_and_window[0] == -1:
                                                            return start_and_window
                                                    print([utils.array_to_str(el) for el in lst])
                                                    scaled_conf=lst[start_and_window[0]]
                                                    add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, next_conf=scaled_conf)
                                                    return start_and_window
                                            else:
                                                    next_conf=adaptive_scaler.current_tipped_over_conf
                                                    if previous_conf != next_conf:
                                                            adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,next_conf)
                                                    #add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, next_conf=next_conf)
                                                    return [lst.index(next_conf), 1]
                                        elif state ==  NO_COST_EFFECTIVE_ALTERNATIVE:
                                            print("NO BETTER COST EFFECTIVE ALTERNATIVE IN SIGHT")
                                            if states and states.pop(0) == REDO_SCALE_ACTION:
                                                    print("REDOING_CHEAPEST_SCALED_DOWN")
                                                    lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                                                    opt_conf=conf[1] 
                                                    result=conf[0]
                                                    start=lst.index(opt_conf)
                                                    only_failed_results=False
                                                    do_remove=False
                                            else:
                                                    do_remove=True
                                            if adaptive_scaler.ScalingUpPhase:
                                                    if do_remove:
                                                            remove_failed_confs(lst, adaptive_scaler.workers, runtimemanager.instance(runtime_manager,tenant_nb), results, slo, [], start, adaptive_window.get_current_window(), False, adaptive_scaler.failed_results)
                                                    if not adaptive_scaler.tipped_over_confs:
                                                            adaptive_scaler.reset()
                                                    if not only_failed_results:
                                                            #add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo,result=result)
                                                            next_conf=opt_conf
                                                            return [lst.index(next_conf),1]
                                                    else:
                                                            print("Moving filtered samples in sorted combinations after the window")
                                                            print([utils.array_to_str(el) for el in lst])
                                                            previous_tenant_results={}
                                                            if tenant_nb > 1:
                                                                  previous_tenant_results=d[sla['name']]
                                                            start_and_window=filter_samples(lst,adaptive_scaler.workers,0, window, previous_tenant_results, 1, tenant_nb)
                                                            print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                            print([utils.array_to_str(el) for el in lst])
                                                            return start_and_window
                                            else:
                                                    #changePhase=False if adaptive_scaler.workers_are_scaleable() else True
                                                    #if changePhase:
                                                    tors=rm.get_tipped_over_results()
                                                    adaptive_scaler.failed_results=tors["results"]
                                                    if adaptive_scaler.failed_results:
                                                        adaptive_scaler.workers=tors["workers"][0]
                                                    adaptive_scaler.reset()
                                                    adaptive_scaler.set_tipped_over_failed_confs()
                                                    conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                                    return process_states(conf_and_states)
                                                    #else:
                                                    #        adaptive_scaler.redo_scale_action()
                                                    #        #adaptive_scaler.reset(changePhase=False)
                                                    #        print("Moving filtered samples in sorted combinations after the window")
                                                    #        print([utils.array_to_str(el) for el in lst])
                                                    #        previous_tenant_conf=[]
                                                    #        previous_nb_of_tenants=maxTenants
                                                    #        if previous_conf:
                                                    #              previous_tenant_conf=previous_conf
                                                    #              previous_nb_of_tenants=int(previous_tenants)
                                                    #        start_and_window=filter_samples(lst,[],previous_tenant_conf, int(tenants) > previous_nb_of_tenants, start, window)
                                                    #        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                    #        print([utils.array_to_str(el) for el in lst])
                                                    #        return start_and_window


                                    if not opt_conf and result:
                                            opt_conf=get_conf(adaptive_scaler.workers, result)
                                            print("Starting with" + utils.array_to_delimited_str(opt_conf,delimiter='_'))
                                    elif not opt_conf and not result:
                                            if not adaptive_scaler.ScalingUpPhase:
                                                    exit("No result during scaling down phase, thus explicit optimal conf needed")
                                    if adaptive_scaler.ScalingDownPhase:
                                            states=adaptive_scaler.find_cost_effective_config(opt_conf, slo, tenant_nb, scale_down=True, only_failed_results=only_failed_results)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states([[],states])
                                    elif adaptive_scaler.ScalingUpPhase:
                                            adaptive_scaler.set_tipped_over_failed_confs()
                                            conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states(conf_and_states) 
                                    for w in adaptive_scaler.workers:
                                            print(w.resources['cpu'])

	def get_adaptive_scaler_for_closest_tenant_nb(tenants):
                        as_predictedConf=None
                        k=tenants-1
                        while k >= 1:
                                if str(k) in d[sla['name']].keys():
                                        as_predictedConf=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, adaptive_scaler, d[sla['name']], k, get_conf(adaptive_scaler.workers,d[sla['name']][str(k)]),slo)
                                        k=0
                                else:
                                        k-=1
                        if as_predictedConf:
                                return as_predictedConf
                        else:
                                return adaptive_scalers['init']

	def get_rm_for_closest_tenant_nb(tenants):
                        if tenants in runtime_manager.keys():
                                return runtime_manager[tenants]
                        rm_tenants=None
                        k=tenants-1
                        while k >= 1:
                                if k in runtime_manager.keys():
                                        rm_tenants=runtimemanager.instance(runtime_manager, k).copy_to_tenant_nb(tenants)
                                        k=0
                                else:
                                        k-=1
                        if rm_tenants:
                                runtime_manager[tenants]=rm_tenants
                                return rm_tenants
                        else:
                                return runtimemanager.instance(runtime_manager, tenants)


	bin_path=initial_conf['bin']['path']
	chart_dir=initial_conf['charts']['chartdir']
	exp_path=initial_conf['output']
	util_func=initial_conf['utilFunc']
	slas=initial_conf['slas']
	adaptive_scaler=adaptive_scalers['init']
	tmp_dict=get_matrix_and_sla(initial_conf, namespace)
	d=tmp_dict["matrix"]
	sla=tmp_dict["sla"]
	alphabet=sla['alphabet']
	supTenants=sla['maxTenants']
	window=alphabet['searchWindow']
	exps_path=exp_path+'/'+sla['name']
	base=alphabet['base']
	slo=float(sla['slos']['completionTime'])

	adaptive_scaler=adaptive_scalers['init']
	adaptive_window=AdaptiveWindow(window)
	startTenants = int(tenants)
	tenant_nb=startTenants
	maxTenants = -1
	result={}
	next_conf=[]
	predictedConf=[]
	evaluate=False
	evaluate_current=False
	evaluate_previous=False
	currentResult={}
	previousResult={}
	if str(startTenants) in d[sla['name']]:
		currentResult=d[sla['name']][str(startTenants)]
	elif startTenants > 1 and str(startTenants-1) in d[sla['name']]:
		#copy result for startTenants-1 but set an artificial high  completion time
		#so that a later actual result will always outperform this completion time.
		previousResult=d[sla['name']][str(startTenants-1)]
		transfer_result(d, sla, adaptive_scalers, int(tenants)-1,int(tenants),slo)
	if not (currentResult or previousResult):
		# using curve-fitted scaling function to estimate configuration for tenants
		adaptive_scaler_closest_tenant=get_adaptive_scaler_for_closest_tenant_nb(startTenants)
		rm=get_rm_for_closest_tenant_nb(startTenants)
		lst=rm.set_sorted_combinations(_sort(adaptive_scaler_closest_tenant.workers,base))
		predictedConf=get_conf_for_start_tenant(slo,startTenants,adaptive_scaler_closest_tenant,lst,window)
		adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler_closest_tenant,startTenants,predictedConf)
	if len(previous_conf)==len(alphabet['elements']) and int(previous_tenants) > 0 and float(completion_time) > 0:
		#if there is a performance metric for the lastly completed set of jobs, we will evaluate it and update the matrix accordingly
		evaluate=True
		if (currentResult or previousResult):
		#a special case is when the lastly completed set of jobs has a cardinality that is the same as the  nr of tenants as queried by the scaler
			if currentResult and int(previous_tenants) == int(startTenants):
				evaluate_current=True
			if previousResult and int(previous_tenants) == int(startTenants-1):
				evaluate_previous=True
		tenant_nb=int(previous_tenants)
		maxTenants=int(previous_tenants)
		adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, adaptive_scalers['init'], d[sla['name']], tenant_nb, previous_conf,slo)
		rm=get_rm_for_closest_tenant_nb(tenant_nb)
		lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
		print([utils.array_to_str(el) for el in lst])
		tmp_result=create_result(adaptive_scaler, completion_time, previous_conf, sla['name'])
		next_conf=get_conf(adaptive_scaler.workers, tmp_result)
		results=[tmp_result]

	#tenant_nb=1
	#start=0
	#next_conf=[]
	#ScaledDown=False
	#FailedScalings=[]
	#ScaledWorkerIndex=-1
	#next_exp=_find_next_exp(lst,adaptive_scaler.workers,next_conf,base,window)
	start=0
	if next_conf:
		start=lst.index(next_conf)
	print("Starting at: " + str(start))
	nr_of_experiments=1
	while tenant_nb <= maxTenants and evaluate:
		print("Tenant_nb: " + str(tenant_nb)  + ", maxTenants: " + str(maxTenants))
		#slo=float(sla['slos']['completionTime'])
		print("SLO is " + str(slo))
		result=find_optimal_result(adaptive_scaler.workers,results,slo)
		if result:
			print("RESULT FOUND")
			metric=float(result['CompletionTime'])
			print(get_conf(adaptive_scaler.workers, result))
			print("Measured completion time is " + str(metric))
		print("New cycle")
		for w in adaptive_scaler.workers:
			print(w.resources)
		states=adaptive_scaler.validate_result(result, get_conf(adaptive_scaler.workers,result), slo)
		print(states)
		state=states.pop(0)
		print("State of adaptive_scaler")
		adaptive_scaler.status()
		if adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
			tipped_over_results=return_failed_confs(adaptive_scaler.workers, results, lambda r: float(r['CompletionTime']) > slo and r['Successfull'] == 'true' and float(r['CompletionTime']) <= slo * SCALING_UP_THRESHOLD)
			if tipped_over_results:
                            rm.add_tipped_over_result({"workers": [w.clone() for w in adaptive_scaler.workers], "results": tipped_over_results})
		scaling=False
		if state == NO_COST_EFFECTIVE_RESULT:
			print("NO COST EFFECTIVE RESULT")
			if states and states.pop(0) == UNDO_SCALE_ACTION:
				print("Previous scale down undone")
				lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
				scaling=True
			#else: 
			#	remove_failed_confs(lst, adaptive_scaler.workers, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),False,[], tenant_nb == startTenants			
			if scaling: 
				start=lst.index(get_conf(adaptive_scaler.workers, result))
				start_and_window=get_start_and_window_for_next_experiments()
				print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
				start=start_and_window[0]
				new_window=start_and_window[1]
				next_conf=lst[start]
				print(next_conf)
				if next_conf != previous_conf:
					adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],tenant_nb,next_conf,slo, clone_scaling_function=True)
				add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: float(x['CompletionTime']) > slo,next_conf=next_conf,result=result)
			else:
                                #rm=runtimemanager.instance(runtime_manager,tenant_nb)
                                rm.add_not_cost_effective_result(result)
                                conf_array=rm.get_left_over_configs()#sort_configs(adaptive_scaler.workers,rm.get_left_over_configs())
                                if conf_array and resource_cost(adaptive_scaler.workers, sort_configs(adaptive_scaler.workers,conf_array)[0]) <= resource_cost(adaptive_scaler.workers, get_conf(adaptive_scaler.workers, result)):
                                        print("Moving filtered samples in sorted combinations after the window")
                                        print([utils.array_to_str(el) for el in lst])
                                        previous_tenant_results={}
                                        if tenant_nb > 1:
                                                 previous_tenant_results=d[sla['name']]
                                        start_and_window=filter_samples(lst,adaptive_scaler.workers,lst.index(conf_array[0]), window, previous_tenant_results, 1, tenant_nb)
                                        #start_and_window=filter_samples(lst,[],previous_conf, True, start, window)
                                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                        print([utils.array_to_str(el) for el in lst])
                                        next_conf=lst[start_and_window[0]]
                                        start=start_and_window[0]
                                        new_window=start_and_window[1]
                                        runtimemanager.instance(runtime_manager,tenant_nb).add_not_cost_effective_result(result)
                                        result={}
                                        state=NO_RESULT
                                        conf_array=lst[start:start+new_window]
                                        rm_list=rm.get_left_over_configs()
                                        for conf in rm_list:
                                            if not conf in conf_array:
                                                print("Removing conf " + utils.array_to_str(conf) + " from left experiments in runtime manager")
                                                rm.remove_sample_for_conf(conf)
                                else:
                                        tmp_results=sort_results(adaptive_scaler.workers, slo, rm.get_not_cost_effective_results())
                                        if len(tmp_results) > 0:
                                                result=tmp_results[0]
                                                start=lst.index(get_conf(adaptive_scaler.workers, result))
                                                start_and_window=get_start_and_window_for_next_experiments()
                                                print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                start=start_and_window[0]
                                                new_window=start_and_window[1]
                                                next_conf=lst[start]
                                                print(next_conf)
                                                if next_conf != previous_conf:
                                                         adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],tenant_nb,next_conf,slo, clone_scaling_function=True)
                                                add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: float(x['CompletionTime']) > slo,next_conf=next_conf,result=result)
		elif state == COST_EFFECTIVE_RESULT:
			print("COST-EFFECTIVE-RESULT")
			if adaptive_scaler.ScalingUpPhase:
				lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
			remove_failed_confs(lst, adaptive_scaler.workers, runtimemanager.instance(runtime_manager,tenant_nb), results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),True,adaptive_scaler.failed_results,startingTenant=True)
			if adaptive_scaler.ScalingUpPhase:
                                adaptive_scaler.reset()
			adaptive_scaler.failed_results=[]
			add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo,lambda x, slo: float(x['CompletionTime']) > slo or float(x['CompletionTime'])*SCALING_DOWN_TRESHOLD < slo, result=result)
			next_conf=get_conf(adaptive_scaler.workers, result)
			new_window=window
			start=lst.index(next_conf)
			rm.reset()
			if not (evaluate_previous or evaluate_current):
				result={}
		elif state == NO_RESULT:
			print("NO RESULT")
			if states and states.pop(0) == UNDO_SCALE_ACTION:
				print("Previous scale action undone")
				lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
				start_and_window=get_start_and_window_for_next_experiments(opt_conf=lst[start])
				print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
				start=start_and_window[0]
				new_window=start_and_window[1]
				next_conf=lst[start]
				add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, next_conf=next_conf)
				result={}
				scaling=True
			else:
				conf_array=rm.get_left_over_configs()#sort_configs(adaptive_scaler.workers,rm.get_left_over_configs())
				if conf_array:
                                        remove_failed_confs(lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(),False,[])
                                        print("Moving filtered samples in sorted combinations after the window")
                                        print([utils.array_to_str(el) for el in lst])
                                        previous_tenant_results={}
                                        if tenant_nb > 1:
                                                 previous_tenant_results=d[sla['name']]
                                        start_and_window=filter_samples(lst,adaptive_scaler.workers,lst.index(conf_array[0]), window, previous_tenant_results, 1, tenant_nb)
                                        #start_and_window=filter_samples(lst,[],previous_conf, True, start, window)
                                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                        print([utils.array_to_str(el) for el in lst])
                                        next_conf=lst[start_and_window[0]]
                                        start=start_and_window[0]
                                        new_window=start_and_window[1]
                                        conf_array=lst[start:start+new_window]
                                        rm_list=rm.get_left_over_configs()
                                        for conf in rm_list:
                                            if not conf in conf_array:
                                                print("Removing conf " + utils.array_to_str(conf) + " from left experiments in runtime manager")
                                                rm.remove_sample_for_conf(conf)
				else:
					if adaptive_scaler.ScalingDownPhase and rm.tipped_over_results:
						remove_failed_confs(lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(),False,[])
						tors=rm.get_tipped_over_results()
						adaptive_scaler.failed_results=tors["results"]
						adaptive_scaler.reset()
						start_and_window=get_start_and_window_for_next_experiments()
						print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
						start=start_and_window[0]
						new_window=start_and_window[1]
						next_conf=lst[start]
						add_incremental_result(tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, next_conf=next_conf)
					else: 
						start=remove_failed_confs(lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(),False,[])
						print("Moving filtered samples in sorted combinations after the window")
						print([utils.array_to_str(el) for el in lst])
						previous_tenant_results={}
						if tenant_nb > 1:
							previous_tenant_results=d[sla['name']]
						start_and_window=filter_samples(lst,adaptive_scaler.workers,start, window, previous_tenant_results, 1, tenant_nb)
						#start_and_window=filter_samples(lst,[],previous_conf, True, start, window)
						print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
						print([utils.array_to_str(el) for el in lst])
						next_conf=lst[start_and_window[0]]
						start=start_and_window[0]
						new_window=start_and_window[1]
						result={}
						rm.reset()
		for w in adaptive_scaler.workers:
			adaptive_scaler.untest(w)
		#if adaptive_scaler.ScalingUpPhase and adaptive_scaler.hasScaled():
		#	adaptive_scaler2=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, adaptive_scaler, d[sla['name']], tenant_nb, next_conf,slo, check_workers=True)
		#if state != NO_RESULT or adaptive_scaler.hasScaled():
		#	if tenant_nb < supTenants:
		#		transfer_result(d, sla, adaptive_scalers, tenant_nb, tenant_nb+1,slo)
		#		if tenant_nb < supTenants -1:
		#			update_all_adaptive_scalers(d, sla, adaptive_scalers, adaptive_scaler, tenant_nb+1, base, window,slo)
			#else:
			#	 update_all_adaptive_scalers(d, sla, adaptive_scalers, adaptive_scaler, tenant_nb, base, window,slo)
		if not scaling and state == NO_RESULT and adaptive_scaler.ScalingDownPhase:
			#rm=runtimemanager.instance(runtime_manager,tenant_nb)
			if rm.no_experiments_left():
				get_next_exps(next_conf, new_window)
			else:
				ws=rm.get_current_experiment_specification()
				i=rm.get_current_experiment_nb()
				sla_conf=SLAConf(sla['name'],tenant_nb,ws[0],sla['slos'])
				samples=int(ws[4]*SAMPLING_RATE)
				if samples == 0:
					samples=1
				results=[]
				previous_result=None
				previous_replicas=None
				if len(previous_conf)==len(alphabet['elements']) and int(previous_tenants) > 0 and float(completion_time) > 0:
					previous_result=float(completion_time)
					previous_replicas="[" + utils.array_to_delimited_str(previous_conf,",") + "]"
				sample_list=_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i),ws[1],ws[2],ws[3], previous_result=previous_result, previous_replicas=previous_replicas)
				rm.update_experiment_list(i,ws,sort_results(adaptive_scaler.workers, slo, sample_list))
			d[sla['name']][str(tenant_nb)]=rm.get_next_sample()
		tenant_nb+=1
	if predictedConf:
		adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(tenants),predictedConf,slo)
		rm=get_rm_for_closest_tenant_nb(int(tenants))
		lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
		if rm.no_experiments_left():
                     start=lst.index(predictedConf)
                     new_window=window
                     next_conf=predictedConf
                     print("Moving filtered samples in sorted combinations after the window")
                     print([utils.array_to_str(el) for el in lst])
                     previous_tenant_results={}
                     if int(tenants) > 1:
                         previous_tenant_results=d[sla['name']]
                         start_and_window=filter_samples(lst,adaptive_scaler.workers,lst.index(predictedConf), window, previous_tenant_results, 1, int(tenants))
                         print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                         print([utils.array_to_str(el) for el in lst])
                         next_conf=lst[start_and_window[0]]
                         start=start_and_window[0]
                         new_window=start_and_window[1]
                     get_next_exps(next_conf, new_window)
		d[sla['name']][tenants]=rm.get_next_sample()
	print("Saving optimal results into matrix")
	utils.saveToYaml(d,'Results/matrix.yaml')
        #When scaling to a number of jobs that is different from the previous number of jobs or the previous number of jobs +1
        #we search from the known optimal for the requested nr of jobs until a configuration is found that meets
        #the different constraints of transition cost and shared number of replicas. 
        #However this config should not be stored in the matrix because we need to remember the current found optimimum
	#therefore we store it in a different yaml file
	#Note: transition cost only applies when scaling up to a higher number of tenants.
	if previous_conf and not (evaluate_current or evaluate_previous) and int(tenants) > tenant_nb-1: #and not adaptive_scaler.hasScaled():
		adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(tenants),get_conf(adaptive_scaler.workers,d[sla['name']][tenants]),slo)
		print("Moving filtered samples in sorted combinations after the window")
		rm=get_rm_for_closest_tenant_nb(int(tenants))
		lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
		print([utils.array_to_str(el) for el in lst])
		next_conf=get_conf(adaptive_scaler.workers,d[sla['name']][tenants])
		start_and_window=filter_samples_previous_tenant_conf(lst,[],previous_conf, int(tenants) > int(previous_tenants), lst.index(next_conf), window)
		print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
		print([utils.array_to_str(el) for el in lst])
		next_conf=lst[start_and_window[0]]
		if currentResult and next_conf != get_conf(adaptive_scaler.workers, currentResult):
			current_conf=get_conf(adaptive_scaler.workers, currentResult)
			adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(tenants),current_conf,slo)
			d[sla['name']][tenants]=create_result(adaptive_scaler, str(float(slo)+999999.000), next_conf, sla['name'])
	print("Saving filtered results into matrix")
	utils.saveToYaml(d,'Results/result-matrix.yaml')


def update_all_adaptive_scalers(d, sla, adaptive_scalers, adaptive_scaler, tenant_nb, base, window, slo):
	for t in d[sla['name']].keys():
		if int(t) > tenant_nb:
			other_conf=get_conf(adaptive_scaler.workers, d[sla['name']][t])
			other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(t),other_conf,slo, clone_scaling_function=True)
			if not adaptive_scaler.equal_workers(other_as.workers):
				changed_scaler=False
				for i,w in enumerate(other_as.workers):
                                                changed=False
                                                if w.isFlagged():
                                                        changed_scaler=True
                                                        changed=True
                                                if changed:
                                                        other_as.workers[i]=adaptive_scaler.workers[i].clone()
				if changed_scaler:
					d[sla['name']][t]=create_result(other_as, float(slo) + 999999.0, get_conf_for_start_tenant(slo,int(t),other_as,_sort(other_as.workers,base),window), sla['name'])
	return d


def get_matrix_and_sla(initial_conf,namespace):
        slas=initial_conf['slas']
        d={}
        sla={}
        for s in slas:
                if s['name'] == namespace:
                        sla=s
        d=yaml.safe_load(open('Results/matrix.yaml'))
        if not sla['name'] in d:
                d[sla['name']]={}
        return {"matrix": d, "sla":sla}


#precondition: d[sla['name'][str(source_tenant_nb)] exists
def transfer_result(d, sla, adaptive_scalers, source_tenant_nb, destination_tenant_nb,slo):
	print("Transferring result from " +  str(source_tenant_nb)+ " to " + str(destination_tenant_nb)) 
	sourceResult=d[sla['name']][str(source_tenant_nb)]
	adaptive_scaler=adaptive_scalers['init']
	source_conf=get_conf(adaptive_scaler.workers, sourceResult)
	source_adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],source_tenant_nb,source_conf,slo)
	destination_adaptive_scaler=None
	if str(destination_tenant_nb) in d[sla['name']].keys():
		destination_conf=get_conf(adaptive_scaler.workers, d[sla['name']][str(destination_tenant_nb)])
		destination_adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],destination_tenant_nb,destination_conf,slo)
	else:
		sourceResult=None
	if source_tenant_nb != destination_tenant_nb:
		sourceResult=None
	return add_incremental_result(destination_tenant_nb, d, sla, source_adaptive_scaler, slo, lambda x, slo: float(x['CompletionTime']) > slo or float(x['CompletionTime'])*SCALING_DOWN_TRESHOLD < slo, destination_adaptive_scaler=destination_adaptive_scaler, next_conf=source_conf, result=sourceResult)

def add_incremental_result(destination_tenant_nb, d, sla, source_adaptive_scaler, slo, isExistingResultNotCostEffective, destination_adaptive_scaler=None, next_conf=None, result=None):
	if result:
		result_conf=get_conf(source_adaptive_scaler.workers, result)
		if next_conf:
			if next_conf != result_conf:
				result={}
		else:
			next_conf=result_conf
	if not destination_adaptive_scaler:
		destination_adaptive_scaler=source_adaptive_scaler
	if str(destination_tenant_nb) in d[sla['name']]:
		x=d[sla['name']][str(destination_tenant_nb)]
		if resource_cost(destination_adaptive_scaler.workers, get_conf(destination_adaptive_scaler.workers, x)) >= resource_cost(source_adaptive_scaler.workers, next_conf) or isExistingResultNotCostEffective(x,slo):
			print("Adding stronger incremental result")
			d[sla['name']][str(destination_tenant_nb)]=result.copy() if result else create_result(source_adaptive_scaler, float(slo) + 999999.0 , next_conf, sla['name'])
	else:
		print("Adding stronger incremental result")
		d[sla['name']][str(destination_tenant_nb)]=result.copy() if result else create_result(source_adaptive_scaler, float(slo) + 999999.0 , next_conf, sla['name'])
	return d


def get_adaptive_scaler_key(tenant_nb, conf):
	return str(tenant_nb)+ "X" + utils.array_to_delimited_str(conf,delimiter='_')

def get_tenant_nb_of_adaptive_scaler_key(adaptive_scaler_key):
	return  int(adaptive_scaler_key.split('X')[0])

def get_conf_of_adaptive_scaler_key(adaptive_scaler_key):
	str_conf=adaptive_scaler_key.split('X')[1]
	return list(map(lambda x: int(x),str_conf.split('_',-1)))

def get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,results,tenant_nb,conf,slo, clone_scaling_function=False):
       tested_configuration=get_adaptive_scaler_key(tenant_nb, conf)
       if not (tested_configuration in adaptive_scalers.keys()):
                adaptive_scaler=AdaptiveScaler([w.clone() for w in adaptive_scaler.workers], adaptive_scaler.ScalingFunction.clone())
                adaptive_scalers[tested_configuration]=update_adaptive_scaler_with_results(adaptive_scaler, results, tenant_nb, conf)
       else:
                adaptive_scaler2=adaptive_scalers[tested_configuration]
                if clone_scaling_function:
                        adaptive_scaler2.ScalingFunction=adaptive_scaler.ScalingFunction.clone(clone_scaling_records=True)
                unflag_all_workers(adaptive_scaler2.workers)
                adaptive_scaler=adaptive_scaler2
       flag_all_workers_for_tenants_up_to_nb_tenants(results, tenant_nb, adaptive_scaler, slo)
       print("Returning adaptive scaler for  " + str(tenant_nb) + " tenants and " + utils.array_to_delimited_str(conf)+ ":")
       adaptive_scaler.status()
       return adaptive_scaler

def update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,conf):
	tested_configuration=get_adaptive_scaler_key(tenant_nb, conf)
	adaptive_scalers[tested_configuration]=adaptive_scaler.clone()
	print("Setting adaptive scaler for  " + str(tenant_nb) + " tenants and " + utils.array_to_delimited_str(conf)+ ":")
	adaptive_scalers[tested_configuration].status()
	return adaptive_scalers[tested_configuration]


#def get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,results,tenant_nb,conf,slo, clone_scaling_function=False, check_workers=False):
#       tested_configuration=get_adaptive_scaler_key(tenant_nb, conf)
#       if not (tested_configuration in adaptive_scalers.keys()):
#                adaptive_scaler2=AdaptiveScaler([w.clone() for w in adaptive_scaler.workers], adaptive_scaler.ScalingFunction.clone())
#                adaptive_scalers[tested_configuration]=update_adaptive_scaler_with_results(adaptive_scaler, results, tenant_nb, conf)
#       else:
#                adaptive_scaler2=adaptive_scalers[tested_configuration]
#                if clone_scaling_function:
#                        adaptive_scaler2.ScalingFunction=adaptive_scaler.ScalingFunction.clone()
#       if check_workers:
#                adaptive_scaler2.workers=[w.clone() for w in adaptive_scaler.workers]
#       unflag_all_workers(adaptive_scaler2.workers)
#       flag_all_workers_for_tenants_up_to_nb_tenants(results, tenant_nb, adaptive_scaler2, slo)
#       print("Returning adaptive scaler for  " + str(tenant_nb) + " tenants and " + utils.array_to_delimited_str(conf)+ ":")
#       adaptive_scaler2.status()
#       return adaptive_scaler2


def update_adaptive_scaler_with_results(adaptive_scaler, results, tenant_nb, conf):
      if str(tenant_nb) in results.keys():
                tmp_result=results[str(tenant_nb)]
                if conf == get_conf(adaptive_scaler.workers, tmp_result):
                         resources_keys=adaptive_scaler.workers[0].resources.keys()
                         for i, w in enumerate(adaptive_scaler.workers):
                                for res in resources_keys:
                                    w.resources[res]=int(tmp_result["worker"+str(i+1)+".resources.requests." + res])
      return adaptive_scaler

def flag_all_workers_for_tenants_up_to_nb_tenants(results, nb_tenants,adaptive_scaler,slo):
    for t in results.keys():
        if int(t) < nb_tenants: # and float(results[t]['CompletionTime']) <= slo and float(results[t]['CompletionTime'])*SCALING_DOWN_TRESHOLD > slo:
            conf=get_conf(adaptive_scaler.workers, results[t])
            flag_workers(adaptive_scaler.workers, conf)


def create_result(adaptive_scaler, completion_time, conf, sla_name):
	result={'config': '0'}
	for i,w in enumerate(adaptive_scaler.workers):
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
       while index < len(combinations)-1 and resource_cost(adaptive_scaler.workers, conf, cost_aware=False) <  total_cost:
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

def unflag_all_workers(workers):
    for w in workers:
        w.unflag()

def flag_workers(workers, conf):
	for k,v in enumerate(conf):
		if v > 0:
			workers[k].flag()


#def tag_tested_workers(workers, conf):
#	 for k,v in enumerate(conf):
#                if v > 0:
#                        workers[k].tested()

def equal_conf(conf1, conf2):
        for x, y in zip(conf1, conf2):
                if x != y:
                        return False
        return True


def remove_failed_confs(sorted_combinations, workers, rm, results, slo, optimal_conf, start, window, optimal_conf_is_cost_effective, tipped_over_results,startingTenant=False):
		if optimal_conf and optimal_conf_is_cost_effective:
			if tipped_over_results and optimal_conf in tipped_over_results:
				tipped_over_results.remove(optimal_conf)
			tmp_combinations=sort_configs(workers,sorted_combinations, cost_aware=False)
			failed_range=tmp_combinations.index(optimal_conf)
			for i in range(0, failed_range):
				possible_removal=tmp_combinations[i]
				if resource_cost(workers, possible_removal) > resource_cost(workers, optimal_conf):
					print("Removing config because it has a higher resource cost than the optimal result and we assume it will therefore fail for the next tenant")
					print(possible_removal)
					sorted_combinations.remove(possible_removal)
					if rm.conf_in_experiments(possible_removal):
						rm.remove_sample_for_conf(possible_removal)

		#elif not tipped_over_results and not optimal_conf and SAMPLING_RATE < 1.0 and SAMPLING_RATE >= 0.5:
		#	failed_range=start+window
		#	print("Removing  in window going over the scaling_up_threshold because no optimal config has been found at all")
		#	index=0 if startingTenant else start
		#	possible_tipped_over_confs=return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) <= slo * SCALING_UP_THRESHOLD and r['Successfull'] == 'true')
		#	for i in range(start,failed_range,1):
		#		print(sorted_combinations[index])
		#		if not sorted_combinations[index] in possible_tipped_over_confs:
		#			print(utils.array_to_delimited_str(sorted_combinations[index]) + " is removed")
		#			sorted_combinations.remove(sorted_combinations[index])
		#		else:
		#			index+=1
		#for failed_conf in return_failed_confs(workers,results, lambda result: float(result['score']) <= THRESHOLD):
		if tipped_over_results:
                        for failed_conf in tipped_over_results:
                                if failed_conf in sorted_combinations:
                                        print("Removing tipped over conf")
                                        print(failed_conf)
                                        sorted_combinations.remove(failed_conf)
                                rm.reset()
		next_index=0
		for failed_conf in return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) > slo * SCALING_UP_THRESHOLD):
			if failed_conf in sorted_combinations:
				tmp_combinations=sort_configs(workers,sorted_combinations)
				failed_range=tmp_combinations.index(failed_conf)
				for i in range(0, failed_range):
					possible_removal=tmp_combinations[i]
					if not possible_removal in (rm.get_tipped_over_results(nullify=False))["results"] and resource_cost(workers, possible_removal, False) < resource_cost(workers, failed_conf, False):
						print("Removing config because it has a lower resource cost than the failed result and we assume it will therefore fail for this tenant")
						print(possible_removal)
						if possible_removal in sorted_combinations:
							sorted_combinations.remove(possible_removal)
							if rm.conf_in_experiments(possible_removal):
								rm.remove_sample_for_conf(possible_removal)
				print("Removing failed conf")
				print(failed_conf)
				if sorted_combinations.index(failed_conf)-1 > next_index:
					next_index=sorted_combinations.index(failed_conf)-1
				sorted_combinations.remove(failed_conf)
				if rm.conf_in_experiments(failed_conf):
 					rm.remove_sample_for_conf(failed_conf)
		return next_index


def filter_samples(sorted_combinations, workers, start, window, previous_results, start_tenant, tenant_nb, check_workers=False, ScaledDownWorkerIndex=-1):
        i=start_tenant
        new_window=window
        start_window=window
        if previous_results:
                max_tenants=max(map(lambda x: int(x), previous_results.keys()))
                while i <= max_tenants:
                        if i != tenant_nb and str(i) in previous_results.keys():
                                previous_tenant_conf=get_conf(workers, previous_results[str(i)])
                                for el in range(start, start+window):
                                        if el-(window-new_window) >= len(sorted_combinations):
                                                return [-1,-1]
                                        result_conf=sorted_combinations[el-(window-new_window)]
                               	        print(result_conf)
                                        qualitiesOfSample=_pairwise_transition_cost(previous_tenant_conf,result_conf)
                                        cost=qualitiesOfSample['cost']
                                        nb_shrd_replicas=qualitiesOfSample['nb_shrd_repls']
                                        if isinstance(MINIMUM_SHARED_REPLICAS,int):
                                                minimum_shared_replicas = min([MINIMUM_SHARED_REPLICAS,reduce(lambda x, y: x + y, previous_tenant_conf)])
                                        else:
                                                minimum_shared_replicas = max([1,int(MINIMUM_SHARED_REPLICAS*reduce(lambda x, y: x + y, previous_tenant_conf))])
                                        if (check_workers and all_flagged_conf(workers, result_conf)) or (i < tenant_nb and (cost > MAXIMUM_TRANSITION_COST or nb_shrd_replicas < minimum_shared_replicas)) or not (not check_workers or involves_worker(workers, result_conf, ScaledDownWorkerIndex)):
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
                                        stop=False
                                        while i <= max_tenants and not stop:
                                                if str(i) in previous_results.keys():
                                                        if equal_conf(previous_tenant_conf,get_conf(workers, previous_results[str(i)])):
                                                                i+=1
                                                        else:
                                                                stop=True
                                                else:
                                                        i+=1

                        else:
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


def filter_samples_previous_tenant_conf(sorted_combinations, workers, previous_tenant_conf, costIsRelevant, start, window, ScaledWorkerIndex=-1):
	new_window=window
	for el in range(start, start+window):
		result_conf=sorted_combinations[el-(window-new_window)]
		if previous_tenant_conf:
			qualitiesOfSample=_pairwise_transition_cost(previous_tenant_conf,result_conf)
			cost=qualitiesOfSample['cost']
			nb_shrd_replicas=qualitiesOfSample['nb_shrd_repls']
			if isinstance(MINIMUM_SHARED_REPLICAS,int): 
				minimum_shared_replicas = min([MINIMUM_SHARED_REPLICAS,reduce(lambda x, y: x + y, previous_tenant_conf)])
			else:
				minimum_shared_replicas = max([1,int(MINIMUM_SHARED_REPLICAS*reduce(lambda x, y: x + y, previous_tenant_conf))])
			print(result_conf)
			if all_flagged_conf(workers, result_conf) or (costIsRelevant and cost > MAXIMUM_TRANSITION_COST) or nb_shrd_replicas < minimum_shared_replicas or not involves_worker(workers, result_conf, ScaledWorkerIndex):
				print("Moved")
				sorted_combinations.remove(result_conf)
				#if window > 1:
				sorted_combinations.insert(new_window+el-1,result_conf)
				#elif window == 1:
				#	sorted_combinations.insert(start+new_window+el,result_conf)
				new_window-=1
			else:
				print("Not moved")
		elif not involves_worker(workers, result_conf, ScaledWorkerIndex):
			print("Moved")
			sorted_combinations.remove(result_conf)
			#if window > 1:
			sorted_combinations.insert(start+new_window+el-1,result_conf)
			#elif window == 1:
			#	sorted_combinations.insert(start+new_window+el,result_conf)
			new_window-=1
		else:
			print("Not Moved")
	if new_window == 0:
		return filter_samples_previous_tenant_conf(sorted_combinations, workers, previous_tenant_conf, costIsRelevant, start+window, window, ScaledWorkerIndex)
	else:
		return [start, new_window]


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


def find_optimal_result(workers,results, slo):
	print("Results")
	print(results)
	filtered_results=[result for result in results if float(result['CompletionTime']) <= slo]
	print("Filtered results")
	if filtered_results:
		filtered_results=sort_results(workers,slo,filtered_results)
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
                print("scalingFunction.scale_worker_down(workers,0,2)")
                scalingFunction.scale_worker_down(workers,0,2)
                for w in workers:
                        print(w.resources)

                print("scalingFunction.scale_worker_down(workers,0,1)")
                scalingFunction.scale_worker_down(workers,0,1)
                for w in workers:
                        print(w.resources)

                print("scalingFunction.undo_scaled_down(workers)")
                scalingFunction.undo_scaled_down(workers)
                for w in workers:
                        print(w.resources)

                print("scalingFunction.undo_scaled_down(workers)")
                failed_worker=scalingFunction.undo_scaled_down(workers)
                for w in workers:
                        print(w.resources)
                print(failed_worker.resources)


def sort_results(workers, slo, results):
	def cost_for_sort(elem):
		if float(elem['CompletionTime']) > slo:
			return 999999999*float(float(elem['CompletionTime'])/slo)
		if float(elem['CompletionTime']) == 1:
			return 100*resource_cost(workers,get_conf(workers,elem)) 
		return resource_cost(workers,get_conf(workers,elem))
	return sorted(results,key=cost_for_sort)


def sort_configs(workers,combinations, cost_aware=True):
	def cost_for_sort(elem):
                return resource_cost(workers,elem, cost_aware)

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




def _find_next_exp(sorted_combinations, workers, next_conf, base, window):
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



def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path, conf, minimum_repl, maximum_repl, previous_result=None, previous_replicas=None):
	# conf_ex=ConfigParser(
	# 	optimizer='exhaustive',
	# 	chart_dir=chart_dir,
	# 	util_func= util_func,
	# 	samples= samples,
	# 	output= exp_path+'/exh',
	# 	slas=slas)
	#conf_array=list(map(lambda c: list(map(lambda x: int(x),c.split('[')[1].split(']')[0].split(',',-1))),conf[1:][:-1].split(';',-1)))
	#import random
	#return [random.choice(conf_array)]
	results_json_file=exp_path+'/op/results.json'
	if not os.path.isfile(exp_path+'/op/results.json'):
		results_json_file=None
	if previous_result:	
		conf_op=ConfigParser(
			optimizer='bestconfig',
			chart_dir=chart_dir,
			util_func= util_func,
			samples= samples,
			sampling_rate=SAMPLING_RATE,
			output= exp_path+'/op/',
		        prev_results=results_json_file,
			slas=slas,
			maximum_replicas='"'+maximum_repl+'"',
			minimum_replicas='"'+minimum_repl+'"',
			configs='"'+conf+'"',
			previous_result='"'+str(previous_result)+'"',
			previous_replicas='"'+previous_replicas+'"')
	else:
		conf_op=ConfigParser(
                        optimizer='bestconfig',
                        chart_dir=chart_dir,
                        util_func= util_func,
                        samples= samples,
                        sampling_rate=SAMPLING_RATE,
                        output= exp_path+'/op/',
                        prev_results=results_json_file,
                        slas=slas,
                        maximum_replicas='"'+maximum_repl+'"',
                        minimum_replicas='"'+minimum_repl+'"',
                        configs='"'+conf+'"')

	# exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op/')

	# exp_ex.runExperiment()
	exp_op.runExperiment()
	#conf_array=list(map(lambda c: list(map(lambda x: int(x),c.split('[')[1].split(']')[0].split(',',-1))),conf[1:][:-1].split(';',-1)))
	#import random
	#return [random.choice(conf_array)]

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()
	return results
