from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .searchwindow import AdaptiveWindow, ScalingFunction, AdaptiveScaler, COST_EFFECTIVE_RESULT, NO_RESULT, NO_COST_EFFECTIVE_RESULT, UNDO_SCALE_ACTION, REDO_SCALE_ACTION, RETRY_WITH_ANOTHER_WORKER_CONFIGURATION,NO_COST_EFFECTIVE_ALTERNATIVE
from . import runtimemanager
from functools import reduce
import yaml
import sys
import os
import random
from operator import add,mul


NB_OF_CONSTANT_WORKER_REPLICAS = 1
SORT_SAMPLES=False
LOG_FILTERING=True
TEST_CONFIG_CODE=7898.89695959
USE_PERFORMANCE_MODEL=True

def create_workers(elements, costs, base):
    resources=[v['size'] for v in elements]
    workers=[]
    for i in range(0,len(resources)):
        worker_conf=WorkerConf(worker_id=i+1, resources=resources[i], costs=costs[i], min_replicas=0,max_replicas=base-1)
        workers.append(worker_conf)
    return workers


def print_results(adaptive_scaler,results):
    print("SAMPLE_LIST")
    for r in results:
        print("[" + utils.array_to_delimited_str(get_conf(adaptive_scaler.workers, r), ", ") + "] -> " + str(r["CompletionTime"]))

# update matrix with makespan of the previous sparkbench-run  consisting of #previous_tenants, using configuration previous_conf
# and obtaining performance metric completion_time. The next request is for #tenants. If no entry exists in the matrix, see if there is an entry for a previous
# tenant; otherwise using the curve-fitted scaling function to estimate a target configuration.
def generate_matrix(initial_conf, adaptive_scalers, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf):

        def get_next_exps(adaptive_scaler, rm, lst, conf, sampling_ratio, window,tenants):
                        next_exp=_find_next_exp(lst,adaptive_scaler.workers,conf,base, adaptive_window.adapt_search_window({},window,tenants != 1))
                        rm.set_raw_experiments(next_exp)
                        nr_of_experiments=len(next_exp)
                        for i,ws in enumerate(next_exp):
                                #samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws[0]])
                                sla_conf=SLAConf(sla['name'],tenants,ws[0],sla['slos'])
                                samples=int(ws[4]*sampling_ratio)
                                if samples == 0:
                                        samples=1
                                results=[]
                                sample_list=_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenants)+'_tenants-ex'+str(i),ws[1],ws[2],ws[3],sampling_ratio, initial_conf)
                                if SORT_SAMPLES:
                                    sample_list=sort_results(adaptive_scaler.workers,slo,sample_list)
                                rm.set_experiment_list(i,ws,sample_list)#sort_results(adaptive_scaler.workers,slo,sample_list))
                                print_results(adaptive_scaler,sample_list)
        
        def check_and_get_next_exps(adaptive_scaler, rm, lst,previous_conf, start_index, window, tenants, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function, filter=True, retry=False, retry_window=None, higher_tenants_only=False):
            if adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown and (rm.no_experiments_left() and not rm.last_experiment_in_queue()):
                print("Getting next batch of experiments for " + str(tenants) + " tenants")
                try:
                    if filter:
                        print("Moving filtered samples in sorted combinations after the window")
                        print([utils.array_to_str(el) for el in lst])
                        if d[sla['name']]:
                            previous_tenant_results=d[sla['name']]
                        else:
                            previous_tenant_results={}
                        print("Filtering from index " + str(start_index) +  " with window " + str(window))
                        if previous_tenants:
                            include_current_tenant_nb=not higher_tenants_only and tenants == int(previous_tenants)
                        else:
                            include_current_tenant_nb=False
                        start_and_window=filter_samples(adaptive_scalers, lst,adaptive_scaler,start_index, window, previous_tenant_results, 1, tenants, runtime_manager, scaling_down_threshold, slo, check_workers=False, ScaledDownWorkerIndex=-1, log=LOG_FILTERING, include_current_tenant_nb=include_current_tenant_nb)
                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                        print([utils.array_to_str(el) for el in lst])
                        next_conf=lst[start_and_window[0]]
                        start=start_and_window[0]
                        new_window=start_and_window[1]
                    else:
                        next_conf=lst[start_index]
                        new_window=window
                        start=start_index
                    get_next_exps(adaptive_scaler, rm, lst, next_conf, sampling_ratio, new_window, tenants)
                except IndexError:
                    if retry and retry_window:
                        get_next_exps(adaptive_scaler, rm, lst, get_conf_for_closest_tenant_nb(tenants, window_offset_for_scaling_function), sampling_ratio, retry_window, tenants)
                    else:
                        lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers, lst))
                        start=0
                        tmp_window=min(window, lst.index(previous_conf))
                        get_next_exps(adaptive_scaler, rm, lst, lst[0], sampling_ratio, tmp_window, tenants)

        def resource_cost_for_scale_up_is_too_high(original_adaptive_scaler, opt_conf):
            if not original_adaptive_scaler.careful_scaling:
                return False
            tmp_combinations=sort_configs(original_adaptive_scaler.workers, lst)
            tmp_index_conf=tmp_combinations.index(opt_conf)
            original_resource_cost=resource_cost(original_adaptive_scaler.workers,opt_conf)
            new_tmp_index=tmp_index_conf+1
            while new_tmp_index < len(tmp_combinations) and (original_resource_cost == resource_cost(original_adaptive_scaler.workers, tmp_combinations[new_tmp_index])):
                new_tmp_index+=1
            if original_resource_cost < resource_cost(original_adaptive_scaler.workers, tmp_combinations[new_tmp_index]):
                if resource_cost(adaptive_scaler.workers, opt_conf, cost_aware=True) > resource_cost(original_adaptive_scaler.workers, tmp_combinations[new_tmp_index]):
                    return True
                else:
                    return False
            else:
                return False


        def process_results(result,results, rm, adaptive_scaler, lst, start, adaptive_window, tenant_nb, previous_conf):

            def get_start_and_window_for_next_experiments(adaptive_scaler,opt_conf=None):

                                    only_failed_results=False if result else True

                                    def copy_state_of_adaptive_scaler():
                                        original_adaptive_scaler=adaptive_scaler.clone()
                                        tmp_result={}
                                        if adaptive_scaler.initial_confs[0][0]:
                                            for i,w in enumerate(original_adaptive_scaler.workers):
                                                w=adaptive_scaler.initial_confs[0][2][i].clone()
                                        elif result:
                                            tmp_result=result
                                        elif str(tenant_nb) in d[sla['name']].keys():
                                            tmp_result=d[sla['name']][str(tenant_nb)]
                                        if tmp_result:
                                            for w in original_adaptive_scaler.workers:
                                                w.resources=extract_resources_from_result(tmp_result,w.worker_id,w.resources.keys())
                                        return original_adaptive_scaler

                                    def process_states(adaptive_scaler,conf_and_states,original_adaptive_scaler=None):
                                        nonlocal result
                                        nonlocal slo
                                        #nonlocal tenant_nb
                                        nonlocal lst
                                        #nonlocal adaptive_scaler
                                        nonlocal startTenants
                                        #nonlocal previous_tenants
                                        #nonlocal previous_conf
                                        nonlocal maxTenants
                                        nonlocal opt_conf
                                        nonlocal start
                                        nonlocal only_failed_results
                                        nonlocal d
                                        nonlocal sla
                                        nonlocal window

                                        conf=conf_and_states[0]
                                        states=conf_and_states[1]
                                        state=states.pop(0)

                                        if state == RETRY_WITH_ANOTHER_WORKER_CONFIGURATION:
                                            lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                                            if opt_conf != None:
                                                    start=lst.index(opt_conf)
                                            result={}
                                            if adaptive_scaler.ScalingDownPhase:
                                                    if d[sla['name']]:
                                                        previous_tenant_results=d[sla['name']]
                                                    else:
                                                        previous_tenant_results={}
                                                    print("Moving filtered samples in sorted combinations after the window")
                                                    print([utils.array_to_str(el) for el in lst])
                                                    try:
                                                        print("Filtering from index " + str(start) +  " with window " + str(window))
                                                        start_and_window=filter_samples(adaptive_scalers,lst,adaptive_scaler,start, window, previous_tenant_results, 1, tenant_nb, runtime_manager, scaling_down_threshold, slo, True, adaptive_scaler.ScaledWorkerIndex, log=LOG_FILTERING, original_adaptive_scaler=original_adaptive_scaler, initial_conf=adaptive_scaler.initial_confs[0][1], include_current_tenant_nb=tenant_nb == startTenants)
                                                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                        print([utils.array_to_str(el) for el in lst])
                                                        scaled_conf=lst[start_and_window[0]]
                                                        adaptive_scaler=add_incremental_result(adaptive_scalers, tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, previous_conf=previous_conf,next_conf=scaled_conf)
                                                        print("RETRYING WITH ANOTHER WORKER CONFIGURATION")
                                                        return start_and_window
                                                    except IndexError as e:
                                                        print("No config exists that meets all filtering constraints")
                                                        for w in adaptive_scaler.workers:
                                                            adaptive_scaler.untest(w)
                                                        adaptive_scaler.validate_result({},opt_conf,slo)
                                                        if str(e) == "recursive_scaling_may_help":
                                                            recursive_scale_down=True
                                                        else:
                                                            recursive_scale_down=False
                                                            print("Recursive down scaling disabled")
                                                        return process_states(adaptive_scaler,[[],adaptive_scaler.find_cost_effective_config(opt_conf, slo, tenant_nb, scale_down=True, only_failed_results=only_failed_results,recursive_scale_down=recursive_scale_down)], original_adaptive_scaler=original_adaptive_scaler)
                                            else:
                                                    scaled_conf=adaptive_scaler.current_tipped_over_conf
                                                    #adaptive_scaler=add_incremental_result(adaptive_scalers,tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, previous_conf=previous_conf, next_conf=scaled_conf)
                                                    if d[sla['name']]:
                                                        previous_tenant_results=d[sla['name']]
                                                    else:
                                                        previous_tenant_results={}
                                                    print("Moving filtered samples in sorted combinations after the window")
                                                    print([utils.array_to_str(el) for el in lst])
                                                    try:
                                                        if resource_cost_for_scale_up_is_too_high(original_adaptive_scaler, scaled_conf):
                                                            raise IndexError
                                                        print("Filtering from index " + str(lst.index(scaled_conf)) +  " with window 1")
                                                        start_and_window=filter_samples(adaptive_scalers,lst,adaptive_scaler, lst.index(scaled_conf), 1, previous_tenant_results, 1, tenant_nb, runtime_manager, scaling_down_threshold, slo, True, adaptive_scaler.ScaledWorkerIndex, log=LOG_FILTERING, original_adaptive_scaler=original_adaptive_scaler, initial_conf=scaled_conf, include_current_tenant_nb=tenant_nb == startTenants)
                                                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                        print([utils.array_to_str(el) for el in lst])
                                                        scaled_conf=lst[start_and_window[0]]
                                                        adaptive_scaler=add_incremental_result(adaptive_scalers, tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, previous_conf=previous_conf,next_conf=scaled_conf)
                                                        print("RETRYING WITH ANOTHER WORKER CONFIGURATION")
                                                        return start_and_window
                                                    except IndexError:
                                                        print("No config exists that meets all filtering constraints")
                                                        for w in adaptive_scaler.workers:
                                                            adaptive_scaler.untest(w)
                                                        adaptive_scaler.validate_result({},scaled_conf,slo)
                                                        return process_states(adaptive_scaler,adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb),original_adaptive_scaler=original_adaptive_scaler)  
                                                    #return [lst.index(scaled_conf), 1]
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
                                                    if not adaptive_scaler.tipped_over_confs:
                                                        if only_failed_results:
                                                            start=remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(),results[0], adaptive_scaler.failed_results, scaling_up_threshold, sampling_ratio)
                                                        #else:
                                                         #   start=remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(), d[sla['name']][str(tenant_nb)],[],scaling_up_threshold, sampling_ratio)
                                                        adaptive_scaler.reset()
                                                        rm.reset()
                                                            #window=adaptive_window.get_current_window()
                                                    elif do_remove:
                                                        start=remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, [], start, adaptive_window.get_current_window(),results[0], [], scaling_up_threshold, sampling_ratio)
                                                    if  opt_conf and previous_conf != opt_conf:
                                                            adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,opt_conf)
                                                    if not only_failed_results:
                                                            add_incremental_result(adaptive_scalers,tenant_nb,d,sla,adaptive_scaler,slo,lambda x, slo: float(x['CompletionTime']) > slo or float(x['CompletionTime']) <= 1.0,result=result)
                                                            next_conf=opt_conf
                                                            start=lst.index(opt_conf)
                                                            window=1
                                                    print("Moving filtered samples in sorted combinations after the window")
                                                    print([utils.array_to_str(el) for el in lst])
                                                    if d[sla['name']]:
                                                            previous_tenant_results=d[sla['name']]
                                                    else:
                                                            previous_tenant_results={}
                                                    try:
                                                            print("Filtering from index " + str(start) +  " with window " + str(window))
                                                            start_and_window=filter_samples(adaptive_scalers,lst,adaptive_scaler, start, window, previous_tenant_results, 1, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers=False, ScaledDownWorkerIndex=-1, log=LOG_FILTERING, include_current_tenant_nb=tenant_nb == startTenants)
                                                            print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                                                            print([utils.array_to_str(el) for el in lst])
                                                            return start_and_window
                                                    except IndexError:
                                                            print("No config exists that meets all filtering constraints")
                                                            print("Returning first config")
                                                            return [0, window] 

                                            else:
                                                    #changePhase=False if adaptive_scaler.workers_are_scaleable() else True
                                                    #if changePhase:
                                                    tors=rm.get_tipped_over_results(nullify=False)
                                                    adaptive_scaler.failed_results=tors["results"]
                                                    if adaptive_scaler.failed_results:
                                                        adaptive_scaler.workers=tors["workers"][0]
                                                    adaptive_scaler.reset()
                                                    adaptive_scaler.set_tipped_over_failed_confs()
                                                    conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                                    return process_states(adaptive_scaler,conf_and_states, original_adaptive_scaler=original_adaptive_scaler)
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
                                    original_adaptive_scaler=copy_state_of_adaptive_scaler()
                                    if adaptive_scaler.ScalingDownPhase:
                                            print(adaptive_scaler.ScalingFunction.workersScaledDown)
                                            states=adaptive_scaler.find_cost_effective_config(opt_conf, slo, tenant_nb, scale_down=True, only_failed_results=only_failed_results)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states(adaptive_scaler,[[],states],original_adaptive_scaler=original_adaptive_scaler)
                                    elif adaptive_scaler.ScalingUpPhase:
                                            adaptive_scaler.set_tipped_over_failed_confs()
                                            conf_and_states=adaptive_scaler.find_cost_effective_tipped_over_conf(slo, tenant_nb)
                                            for w in adaptive_scaler.workers:
                                                    print(w.resources['cpu'])
                                            return process_states(adaptive_scaler,conf_and_states,original_adaptive_scaler=original_adaptive_scaler) 
                                    for w in adaptive_scaler.workers:
                                            print(w.resources['cpu'])
            if result:
                print("RESULT FOUND")
                metric=float(result['CompletionTime'])
                print(get_conf(adaptive_scaler.workers,result))
                print("Measured completion time is " + str(metric))
            print("New adaptive scaling cycle...Current resources of workers are:")
            for w in adaptive_scaler.workers:
                print(w.resources)
            #validate the found optimal result (could be no one found) to classify the result
            states=adaptive_scaler.validate_result(result, get_conf(adaptive_scaler.workers,result), slo)
            print(states)
            state=states.pop(0)
            if adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
                tipped_over_results=return_failed_confs(adaptive_scaler.workers, results, lambda r: float(r['CompletionTime']) > slo and r['Successfull'] == 'true' and float(r['CompletionTime']) <= slo * scaling_up_threshold)
                if tipped_over_results:
                    rm.add_tipped_over_result({"workers": [w.clone() for w in adaptive_scaler.workers], "results": tipped_over_results})
            if state == NO_COST_EFFECTIVE_RESULT:
                print("NO COST EFFECTIVE RESULT")
                if states and states.pop(0) == UNDO_SCALE_ACTION:
                    print("Previous scale down undone")
                    lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                # ??else branch is deleted in at-runtime version
                else:
                    remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),results[0],[], scaling_up_threshold, sampling_ratio, careful_scaling=adaptive_scaler.careful_scaling)#, tenant_nb == startTenant)
                next_conf=get_conf(adaptive_scaler.workers, result)
                start=lst.index(next_conf)
                start_and_window=get_start_and_window_for_next_experiments(adaptive_scaler)
                print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                start=start_and_window[0]
                new_window=start_and_window[1]
                next_conf=lst[start]
                print(next_conf)
                #if next_conf != previous_conf:
                #    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],tenant_nb,next_conf,slo, clone_scaling_function=True)
                #adaptive_scaler=add_incremental_result(adaptive_scalers,tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: float(x['CompletionTime']) > slo,previous_conf=previous_conf,next_conf=next_conf,result=result)
            elif state == COST_EFFECTIVE_RESULT:
                print("COST-EFFECTIVE-RESULT")
                if adaptive_scaler.ScalingUpPhase:
                    adaptive_scaler.reset()#lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                    remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),results[0],[],scaling_up_threshold, sampling_ratio, careful_scaling=adaptive_scaler.careful_scaling)
                else:
                    remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),results[0],(rm.get_tipped_over_results())["results"],scaling_up_threshold, sampling_ratio, careful_scaling=adaptive_scaler.careful_scaling)#, tenant_nb == startTenant)
                #if adaptive_scaler.ScalingUpPhase:
                #    adaptive_scaler.reset()
                adaptive_scaler.failed_results=[]
                add_incremental_result(adaptive_scalers,tenant_nb,d,sla,adaptive_scaler,slo,lambda x, slo: float(x['CompletionTime']) > slo or float(x['CompletionTime'])*scaling_down_threshold < slo or float(x['CompletionTime']) <= 1.0, result=result)
                #d[sla['name']][str(tenant_nb)]=result
                #tenant_nb+=1
                #retry_attempt=0
                next_conf=get_conf(adaptive_scaler.workers, result)
                #flag_workers(adaptive_scaler.workers,next_conf)
                new_window=window
                if not next_conf in lst:
                    print("!!!!!!!!!!!!!!!!!!!!!!It seems the alphabet does not scale monotonically anymore: ADJUSTING minimum_shared_replicas!!!!!!!!!!!!!!!!!!!!!!:" + str(rm.minimum_shared_replicas) + " -> " + str(rm.minimum_shared_replicas+1))
                    rm.minimum_shared_replicas=rm.minimum_shared_replicas+1
                    #raise RuntimeError('It seems the alphabet does not scale monotonically anymore. Adjust your transition constraints or opt out for restart!!!')
                    lst.append(next_conf)
                    lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                    #raise RuntimeError('It seems the alphabet does not scale monotonically anymore. Adjust your transition constraints or opt out for restart!!!')
                start=lst.index(next_conf)
                rm.reset()
                #if not (evaluate_previous or evaluate_current):
                #    result={}
            elif state == NO_RESULT:
                print("NO RESULT")
                if states and states.pop(0) == UNDO_SCALE_ACTION:
                    try:
                        print("Previous scale action undone")
                        lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                        if adaptive_scaler.ScalingDownPhase:
                            start_and_window=get_start_and_window_for_next_experiments(adaptive_scaler,opt_conf=adaptive_scaler.initial_confs[0][1])
                        else:
                            start_and_window=get_start_and_window_for_next_experiments(adaptive_scaler,opt_conf=adaptive_scaler.current_tipped_over_conf)
                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                        start=start_and_window[0]
                        new_window=start_and_window[1]
                        next_conf=lst[start]
                        #if previous_conf != next_conf:
                        #    adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,next_conf)
                        #adaptive_scaler=add_incremental_result(adaptive_scalers,tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, previous_conf=previous_conf,next_conf=next_conf)
                        result={}
                        #retry_attempt+=nr_of_experiments
                        filter=False
                    except:
                        rm.reset()
                        start=0
                        new_window=window
                        filter=True
                else:
                    if adaptive_scaler.ScalingDownPhase and rm.tipped_over_results:
                        remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),results[0],[],scaling_up_threshold, sampling_ratio)#,tenant_nb == startTenant)
                        tors=rm.get_tipped_over_results(nullify=False)
                        adaptive_scaler.failed_results=tors["results"]
                        adaptive_scaler.reset()
                        start_and_window=get_start_and_window_for_next_experiments(adaptive_scaler)
                        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                        start=start_and_window[0]
                        new_window=start_and_window[1]
                        next_conf=lst[start]
                        filter=False
                        #adaptive_scaler=add_incremental_result(adaptive_scalers, tenant_nb,d,sla,adaptive_scaler,slo, lambda x, slo: True, previous_conf=previous_conf,next_conf=next_conf)
                    else:
                        lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))    
                        start=remove_failed_confs(runtime_manager, tenant_nb, lst, adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, result), start, adaptive_window.get_current_window(),results[0],adaptive_scaler.failed_results,scaling_up_threshold, sampling_ratio)#,tenant_nb == startTenant)
                        if d[sla['name']]:
                            previous_tenant_results=d[sla['name']]
                        else:
                            previous_tenant_results={}
                        print("Moving filtered samples in sorted combinations after the window")
                        print([utils.array_to_str(el) for el in lst])
                        try:
                            print("Filtering from index " + str(start) +  " with window " + str(window))
                            start_and_window=filter_samples(adaptive_scalers,lst, adaptive_scaler, start, window, previous_tenant_results, 1, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers=False, ScaledDownWorkerIndex=-1, log=LOG_FILTERING, include_current_tenant_nb=tenant_nb == startTenants)
                            print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                            print([utils.array_to_str(el) for el in lst])
                            next_conf=lst[start_and_window[0]]
                            start=start_and_window[0]
                            new_window=start_and_window[1]
                            result={}
                            rm.reset()
                            if adaptive_scaler.ScalingUpPhase:
                                adaptive_scaler.reset()
                            filter=False
                        except IndexError:
                                print("No config found that meets all constraints")
                                rm.reset()
                                start=0
                                new_window=window
                                if adaptive_scaler.ScalingUpPhase:
                                    adaptive_scaler.reset()
                                #TIJDELIJKE DEBUG -> HANGT AF VAN RESOLUTIE debug-kladblok
                                #if adaptive_scaler.ScalingDownPhase:
                                #    adaptive_scaler.StartScalingDown=True
                                #Eunde tihdelijhke debug
                                print("Starting at index " + str(start) + " with window " +  str(window))
                                print([utils.array_to_str(el) for el in lst])
                                filter=True
                                #opt_conf=get_conf(adaptive_scaler.workers, d[sla['name']][str(tenant_nb)])
                                #if not opt_conf in lst:
                                #    lst.append(opt_conf)
                                #    lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers,lst))
                                #start=lst.index(opt_conf)
                                #new_window=1
                        #retry_attempt+=nr_of_experiments
            for w in adaptive_scaler.workers:
                adaptive_scaler.untest(w)
            #if not (evaluate_current or evaluate_previous) and not no_exps:i
            if state == NO_RESULT and adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
                check_and_get_next_exps(adaptive_scaler,rm,lst,previous_conf,start,new_window,tenant_nb, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function, filter=filter)
                d[sla['name']][str(tenant_nb)]=rm.get_next_sample()
                update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,get_conf(adaptive_scaler.workers,d[sla['name']][str(tenant_nb)]))
            print("Saving optimal results into matrix for previous results")
            utils.saveToYaml(d,'Results/matrix.yaml')


        def get_adaptive_scaler_for_closest_tenant_nb(tenants):
                        as_predictedConf=None
                        k=tenants
                        while k >= 1:
                                if str(k) in d[sla['name']].keys():
                                        as_predictedConf=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, adaptive_scaler, d[sla['name']], k, get_conf(adaptive_scaler.workers,d[sla['name']][str(k)]),slo, include_current_tenant_nb=True)
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
                                        rm_tenants=runtimemanager.instance(runtime_manager, k, window).copy_to_tenant_nb(tenants)
                                        k=0
                                else:
                                        k-=1
                        if rm_tenants:
                                runtime_manager[tenants]=rm_tenants
                                return rm_tenants
                        else:
                                return runtimemanager.instance(runtime_manager, tenants, window)

        def get_conf_for_closest_tenant_nb(tenants, window_offset_for_scaling_function):
                        closest_conf=None
                        k=tenants-1
                        while k >= 1:
                                if str(k) in d[sla['name']].keys():
                                        closest_conf=get_conf(adaptive_scaler.workers,d[sla['name']][str(k)])
                                        k=0
                                else:
                                        k-=1
                        if closest_conf:
                                return closest_conf
                        else:
                                return get_conf_for_start_tenant(slo,tenants,adaptive_scaler,lst,window, window_offset_for_scaling_function)


        def update_conf_array(rm,lst,adaptive_scaler,tenant_nb):
                    nonlocal start
                    nonlocal next_conf
                    conf_array=rm.get_left_over_configs()
                    if SORT_SAMPLES:
                        tmp_lst=sort_configs(adaptive_scaler.workers,lst)
                    else:
                        tmp_lst=lst
                    print("Left over configs in runtime manager: ")
                    print(conf_array)
                    if conf_array: # if still configs remain to be tested
                        last_experiment=False
                        #Remove confs that violate constraints about transition cost and number of shared replicas from the set of experiment samples still to run
                        print("Moving filtered samples in sorted combinations after the window")
                        print([utils.array_to_str(el) for el in tmp_lst])
                        if d[sla['name']]:
                            previous_tenant_results=d[sla['name']]
                        else:
                            previous_tenant_results={}
                        try:
                            #tmp_array0=sort_configs(adaptive_scaler.workers, conf_array[:])
                            #print("Filtering from index " + str(tmp_lst.index(tmp_array0[0])) +  " with window " + str(window))
                            print("Filtering from index " + str(start) +  " with window " + str(window))
                            start_and_window=filter_samples(adaptive_scalers,tmp_lst,adaptive_scaler,start, window, previous_tenant_results, 1, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers=False, ScaledDownWorkerIndex=-1, log=LOG_FILTERING, include_current_tenant_nb=tenant_nb == startTenants)
                            print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
                            print([utils.array_to_str(el) for el in tmp_lst])
                            next_conf=tmp_lst[start_and_window[0]]
                            start=start_and_window[0]
                            tmp_window=start_and_window[1]
                            tmp_array=tmp_lst[start:start+tmp_window]
                            #removing filtered out configs
                            for conf in conf_array:
                                if not conf in tmp_array:
                                    print("Removing conf " + utils.array_to_str(conf) + " from left experiments in runtime manager because of this conf violates transition constraints")
                                    rm.remove_sample_for_conf(conf)
                        except IndexError:
                            last_experiment=True
                        # there is no better experiment sample than the inputted previous result, therefore end this set of samples.
                        if not rm.get_left_over_configs():
                            last_experiment=True
                    else:
                        # there is no experiment sample left, therefore end this set of samples.
                        last_experiment=True
                    return last_experiment

        def process_samples(rm,tenant_nb,ws):
                        next_exp=rm.get_raw_experiments()
                        results=[]
                        nr_of_experiments=len(next_exp)
                        print("Running " + str(nr_of_experiments) + " experiments")
                        for i,ws in enumerate(next_exp):
                            sla_conf=SLAConf(sla['name'],tenant_nb,ws[0],sla['slos'])
                            samples=int(ws[4]*sampling_ratio)
                            if samples == 0:
                                samples=1
                            for res in _generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i),ws[1],ws[2],ws[3], sampling_ratio, initial_conf):
                                results.append(res)
                        # if we evaluate a result for a conf that is not part of the configs selected by k8-resource-optimizer, than make sure this result is part of the results
                        #if not (get_conf(adaptive_scaler.workers, tmp_result) in [get_conf(adaptive_scaler.workers, r) for r in results]):
                            #results.append(tmp_result)i
                        print_results(adaptive_scaler, results)
                        return results
        

        def process_request_for_next_tenant_nb():
            nonlocal adaptive_scaler
            nonlocal lst
            nonlocal start
            nonlocal d
            nonlocal rm
            nonlocal adaptive_window

            predictedConf=[]
            currentResult={}
            maximum_transition_cost=rm.maximum_transition_cost
            minimum_shared_replicas=rm.minimum_shared_replicas
            if str(startTenants) in d[sla['name']]:
                currentResult=d[sla['name']][str(startTenants)]
            elif startTenants > 1 and str(startTenants-1) in d[sla['name']]:
                #copy result for startTenants-1 but set an artificial high  completion time
                #so that a later actual result will always outperform this completion time.
                if float(d[sla['name']][str(startTenants-1)]['CompletionTime']) > 1.0 and float(d[sla['name']][str(startTenants-1)]['CompletionTime']) < slo and d[sla['name']][str(startTenants-1)]['Successfull'] == 'true':
                    currentResult=d[sla['name']][str(startTenants-1)]
                    transfer_result(d, sla, adaptive_scalers, int(tenants)-1,int(tenants),slo,scaling_down_threshold) #previous_conf, previous_tenants)
                    adaptive_window.adapt_search_window(d[sla['name']][str(startTenants-1)], 1, False)
            #rm=get_rm_for_closest_tenant_nb(startTenants)
            #adaptive_window=rm.get_adaptive_window()
            if currentResult:
                found_conf=get_conf(adaptive_scalers['init'].workers, d[sla['name']][str(startTenants)])
                if len(previous_conf)==len(alphabet['elements']):
                    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,get_adaptive_scaler_for_closest_tenant_nb(startTenants),d[sla['name']],startTenants,found_conf,slo, include_current_tenant_nb=int(previous_tenants) == startTenants)
                else:
                    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,get_adaptive_scaler_for_closest_tenant_nb(startTenants),d[sla['name']],startTenants,found_conf,slo)
                lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
                start=lst.index(found_conf)
                if adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown and rm.no_experiments_left() and not rm.last_experiment_in_queue() and (1 in [random.choice(range(1,int(100/(100*(adaptive_scaler.exploration_rate+0.00000000001)))+1))]): #i#(previous_tenants and startTenants != int(previous_tenants)):
                    if can_be_improved_by_another_config(d[sla['name']], lst, adaptive_scaler, startTenants, slo, scaling_up_threshold):
                #if can_be_improved_by_larger_config(d[sla['name']], startTenants, slo, scaling_up_threshold):
                        if can_be_improved_by_smaller_config(d[sla['name']], lst, adaptive_scaler, startTenants):
                            lst=rm.update_sorted_combinations(sort_configs(adaptive_scaler.workers, lst))
                            start=0
                            tmp_window=min(window, lst.index(found_conf))
                        check_and_get_next_exps(adaptive_scaler,rm,lst,found_conf, start, tmp_window, startTenants, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function)
                        if (found_conf == lst[start]) and found_conf in rm.get_left_over_configs():
                            rm.remove_sample_for_conf(lst[start])
                        else:
                            d[sla['name']][str(startTenants)]=rm.get_next_sample()
            elif USE_PERFORMANCE_MODEL:
                print("using curve-fitted scaling function to estimate configuration for tenants " + str(startTenants))
                adaptive_scaler_closest_tenant=get_adaptive_scaler_for_closest_tenant_nb(startTenants)
                lst=rm.set_sorted_combinations(_sort(adaptive_scaler_closest_tenant.workers,base))
                predictedConf=get_conf_for_start_tenant(slo,startTenants,adaptive_scaler_closest_tenant,lst,window,window_offset_for_scaling_function)
                adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler_closest_tenant,startTenants,predictedConf, start_fresh=True)
                if len(previous_conf)==len(alphabet['elements']):
                    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scalers['init'],d[sla['name']],startTenants,predictedConf,slo, include_current_tenant_nb=int(previous_tenants) == startTenants)
                else:
                    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scalers['init'],d[sla['name']],startTenants,predictedConf,slo)
                lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
                start=lst.index(predictedConf)
                if start >= window:
                    conf_in_case_of_IndexError=lst[start-window]
                    retry_wdw=window
                else:
                    conf_in_case_of_IndexError=lst[0]
                    retry_wdw=window-start+1

                next_conf=predictedConf
                check_and_get_next_exps(adaptive_scaler,rm,lst,conf_in_case_of_IndexError, start, window, startTenants, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function, retry=True, retry_window=retry_wdw)
                d[sla['name']][str(startTenants)]=rm.get_next_sample()
            else:
                lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
                next_conf=lst[0]
                start=0
                tmp_adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scalers['init'],d[sla['name']],startTenants,next_conf,slo)
                check_and_get_next_exps(adaptive_scaler,rm,lst,next_conf, start, window, startTenants, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function, retry=True, retry_window=window)
                d[sla['name']][str(startTenants)]=rm.get_next_sample()

        def check_mononoticity(workers, r, rm):
                    mono_constraint_violated=False
                    if "last_tenant_nb" in runtime_manager.keys(): 
                        last_tenant_nb=runtime_manager["last_tenant_nb"]
                        previous_rm=runtime_manager[last_tenant_nb]
                        tmp_result=previous_rm.list_of_results[-1]
                        qualities_of_sample=_pairwise_transition_cost(tmp_result["workers"], tmp_result["conf"], workers, get_conf(workers, r), rm.minimum_shared_replicas, rm.minimum_shared_resources, log=False)
                        shrd_replicas=qualities_of_sample['nb_shrd_repls']
                        shrd_resources=qualities_of_sample['shrd_resources']
                        #if shrd_replicas < rm.minimum_shared_replicas:
                        #    raise RuntimeError("Error in Filtering: the number of shrd_replicas is lower than the mimimum_shared_replicas")
                        #for key in rm.minimum_shared_resources.keys():
                        #    if shrd_resources[key] < rm.minimum_shared_resources[key]:
                        #        raise RuntimeError("Error in Filtering: the amount of shrd_resources is lower than the minimum_shared_resources for resource type " + key)
                        mono_constraint_violated=False
                        history=runtime_manager[tenant_nb].get_results()
                        #We start from tenants+2 due prevent non-linear scaling effects
                        for k in range(tenant_nb+2, max([int(t) for t in d[sla['name']].keys()])+1):
                            history+=runtime_manager[k].get_results()
                        for h in history:
                                if resource_cost(workers, get_conf(workers,r), False) >= resource_cost(h["workers"], h["conf"], False):
                                        print("Conf " + str(h["conf"]) + " with completion time " + str(h['result']['CompletionTime']) + "s has smaller resource amount") 
                                        if  float(r['CompletionTime']) > (float(h['result']['CompletionTime']) + initial_conf['monotonicity_threshold']):
                                                print("!!!!!!!!!!!!!!!!!!!!!!It seems the alphabet does not scale monotonically anymore: ADJUSTING transition constraints for TENANT NB from " + str(tenant_nb) + "concurrent jobs and higher number of concurrent jobs!!!!!!!!!!!!!!!!!!!!!!!!:")
                                                resources_incremented=False
                                                for key in shrd_resources.keys():
                                                    if key in initial_conf["dominant_resources"]:
                                                        if shrd_resources[key] < rm.current_min_shrd_resources[key]:
                                                            print("!!!!!! ADJUSTING shared_resources for resource type " + key +  ": "  + str(rm.minimum_shared_resources[key]) +  " -> " + str(shrd_resources[key]+initial_conf['increments'][key])) 
                                                            rm.minimum_shared_resources[key]=shrd_resources[key]+initial_conf['increments'][key]
                                                            resources_incremented=True
                                                if not resources_incremented:
                                                    print("!!!!ADJUSTUNG shared_replicas: "  + str(rm.minimum_shared_replicas) +  " -> " + str(shrd_replicas+1))
                                                    rm.minimum_shared_replicas=shrd_replicas+1
                                                mono_constraint_violated=True
                                                for t in range(tenant_nb, max([int(t) for t in d[sla['name']].keys()])+1):
                                                    if runtime_manager[t].minimum_shared_replicas < rm.minimum_shared_replicas:
                                                        runtime_manager[t].minimum_shared_replicas=rm.minimum_shared_replicas
                                                    for key in rm.minimum_shared_resources.keys():
                                                        if runtime_manager[t].minimum_shared_resources[key] < rm.minimum_shared_resources[key]:
                                                            runtime_manager[t].minimum_shared_resources[key]=rm.minimum_shared_resources[key]
                                                break
                    if not mono_constraint_violated:
                            print("ADDING CORRECT RESULT TO HISTORY:")
                            print(r)
                            if "last_tenant_nb" in runtime_manager.keys():
                                print("shared_replicas: " + str(shrd_replicas))
                                for key in shrd_resources.keys():
                                    print("shared_resources for resource type " + key + ": " + str(shrd_resources[key]))
                                rm.add_result(r,tenant_nb,shrd_replicas,shrd_resources)
                            else:
                                rm.add_result(r,tenant_nb)
                    return mono_constraint_violated


        def debug():
            if '3' in d[sla['name']].keys():
                conf56 = get_conf(adaptive_scaler.workers,  d[sla['name']]['3'])
                as2 = get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],3,conf56,slo)
                print(as2.ScalingFunction.workersScaledDown)
                print(as2.ScalingFunction.LastScaledDownWorker)
                if len(as2.ScalingFunction.LastScaledDownWorker) >= 2:
                    raise RuntimeError("ERRORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")


        bin_path=initial_conf['bin']['path']
        chart_dir=initial_conf['charts']['chartdir']
        exp_path=initial_conf['output']
        util_func=initial_conf['utilFunc']
        slas=initial_conf['slas']
        sampling_ratio=initial_conf['sampling_ratio']
        window_offset_for_scaling_function=initial_conf['window_offset_for_scaling_function']
        scaling_up_threshold=initial_conf['scaling_up_threshold']
        scaling_down_threshold=initial_conf['scaling_down_threshold'] 
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
        check_consistency_adaptive_scalers_and_results(d, sla, adaptive_scalers, adaptive_scaler, slo, initial_conf)
        startTenants = int(tenants)
        tenant_nb=startTenants
        maxTenants = -1
        result={}
        next_conf=[]
        evaluate=False
        if not str(startTenants) in d[sla['name']]:
            rm=get_rm_for_closest_tenant_nb(startTenants)
            lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
            start=0
            adaptive_window=rm.get_adaptive_window()
            process_request_for_next_tenant_nb()
            next_tenant_nb_processed=True
        else:
            next_tenant_nb_processed=False
        mono_constraint_violated=False
        if len(previous_conf)==len(alphabet['elements']) and int(previous_tenants) > 0 and float(completion_time) > 0:
            #if there is a performance metric for the lastly completed set of jobs, we will evaluate it and update the matrix accordingly
            evaluate=True
            tenant_nb=int(previous_tenants)
            maxTenants=int(previous_tenants)
            adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, get_adaptive_scaler_for_closest_tenant_nb(tenant_nb), d[sla['name']], tenant_nb, previous_conf,slo,include_current_tenant_nb=int(previous_tenants) == startTenants)
            rm=get_rm_for_closest_tenant_nb(tenant_nb)
            maximum_transition_cost=rm.maximum_transition_cost
            minimum_shared_replicas=rm.minimum_shared_replicas
            adaptive_window=rm.get_adaptive_window()
            lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
            print([utils.array_to_str(el) for el in lst])
            no_exps=False
            if rm.no_experiments_left() and not rm.last_experiment_in_queue():
                #if not can_be_improved_by_another_config(d[sla['name']], lst, adaptive_scaler, tenant_nb, slo, scaling_up_threshold):
                no_exps=True
            tmp_result=create_result(adaptive_scaler, completion_time, previous_conf, sla['name'])
            mono_constraint_violated=check_mononoticity(adaptive_scaler.workers, tmp_result, rm)
            next_conf=get_conf(adaptive_scaler.workers, tmp_result)
            results=[tmp_result]

        start=0
        if next_conf:
            start=lst.index(next_conf)
        print("Starting at: " + str(start))
        nr_of_experiments=1
        while tenant_nb <= maxTenants and evaluate:
            print("Tenant_nb: " + str(tenant_nb)  + ", maxTenants: " + str(maxTenants))
            #slo=float(sla['slos']['completionTime'])
            print("SLO is " + str(slo))
            #if not no_exps and adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
            print("Removing all configs that are useless to actually test as a result of the current result")
            tmp_adaptive_scaler=adaptive_scaler.clone()
            intermediate_result=find_optimal_result(tmp_adaptive_scaler.workers,results,slo)
            tipped_over_intermediate_confs=return_failed_confs(tmp_adaptive_scaler.workers, results, lambda r: float(r['CompletionTime']) > slo and r['Successfull'] == 'true' and float(r['CompletionTime']) <= slo * scaling_up_threshold)
            intermediate_states=tmp_adaptive_scaler.validate_result(intermediate_result, get_conf(tmp_adaptive_scaler.workers,intermediate_result), slo)
            intermediate_state=intermediate_states.pop(0)
            print("State of adaptive_scaler")
            adaptive_scaler.status()
            #if (intermediate_state==NO_RESULT or intermediate_state==NO_COST_EFFECTIVE_RESULT) and not (intermediate_states and intermediate_states.pop(0) == UNDO_SCALE_ACTION):
            #        remove_failed_confs(runtime_manager, tenant_nb, lst, tmp_adaptive_scaler.workers, rm, results, slo, get_conf(tmp_adaptive_scaler.workers, intermediate_result), start, adaptive_window.get_current_window(),False,[], scaling_up_threshold, sampling_ratio, intermediate_remove=True, careful_scaling=adaptive_scaler.careful_scaling)
            for i in range(1, max([int(t) for t in d[sla['name']].keys()])+1):
                            if i != tenant_nb and str(i) in d[sla['name']].keys():
                                    print("UPDATING RUNTIME MANAGER FOR NB OF TENANTS: " + str(i))
                                    tmp_adaptive_scaler2=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, get_adaptive_scaler_for_closest_tenant_nb(i), d[sla['name']], i, get_conf(adaptive_scaler.workers, d[sla['name']][str(i)]),slo)   
                                    tmp_rm=get_rm_for_closest_tenant_nb(i)
                                    tmp_adaptive_window=tmp_rm.get_adaptive_window()
                                    tmp_lst=tmp_rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
                                    #if intermediate result is tipped_over_result, then remove conf of intermediate_result, if tmp_adaptive_scaler2 has all workers of conf flagged
                                    if tipped_over_intermediate_confs and not adaptive_scaler.careful_scaling:
                                        #if all_flagged_tipped_over_conf_for_all_worker_indices_of_conf(tmp_adaptive_scaler2, tipped_over_intermediate_confs[0]):
                                        #    do_higher_tenant_remove=True
                                        #else:
                                        do_higher_tenant_remove=False
                                    else:
                                        do_higher_tenant_remove=True
                                    if tmp_adaptive_scaler2.ScalingDownPhase and tmp_adaptive_scaler2.StartScalingDown and not (intermediate_states and intermediate_states.pop(0) == UNDO_SCALE_ACTION):
                                        if i > tenant_nb and intermediate_state==NO_RESULT:
                                            print("Current result is NO RESULT, therefore, we remove all configs with lower resource_cost than current result for higher number of tenants: " + str(tenant_nb+1) + ".." + str(max([int(t) for t in d[sla['name']].keys()])))
                                            print("REMOVING CONFS FOR NB OF TENANTS: " + str(i))
                                            remove_failed_confs(runtime_manager, tenant_nb, tmp_lst, tmp_adaptive_scaler2.workers, tmp_rm, results, slo, [], 0, tmp_adaptive_window.get_current_window(),results[0],[], scaling_up_threshold, sampling_ratio, intermediate_remove=True,higher_tenant_remove=do_higher_tenant_remove)
                                        elif i < tenant_nb and (intermediate_state==COST_EFFECTIVE_RESULT or intermediate_state==NO_COST_EFFECTIVE_RESULT):
                                            print("RESULT FOUND,  we remove all configs with higher resource_cost than current result for lower number of tenants: 1 .. " + str(tenant_nb-1))
                                            remove_failed_confs(runtime_manager, tenant_nb, tmp_lst, tmp_adaptive_scaler2.workers, tmp_rm, results, slo, get_conf(adaptive_scaler.workers, intermediate_result), 0, tmp_adaptive_window.get_current_window(),results[0],[], scaling_up_threshold, sampling_ratio, intermediate_remove=True, careful_scaling=adaptive_scaler.careful_scaling)
                                        if not get_conf(adaptive_scaler.workers, d[sla['name']][str(i)]) in tmp_lst:
                                            print("SHIFTING TO NEXT SAMPLE FOR HIGHER NB OF TENANTS: " + str(i))
                                            last_experiment=update_conf_array(tmp_rm,tmp_lst,tmp_adaptive_scaler2,i)
                                            if not last_experiment:
                                                d[sla['name']][str(i)]=tmp_rm.get_next_sample()
                                            elif tmp_rm.last_experiment:
                                                ws=tmp_rm.get_current_experiment_specification()
                                                print(ws)
                                                results_tmp1=process_samples(tmp_rm,i,ws)
                                                result_tmp1=find_optimal_result(tmp_adaptive_scaler2.workers,results_tmp1,slo, just_return_best=True)
                                                if result_tmp1:
                                                    if not result_tmp1 in tmp_lst:
                                                        tmp_lst.append(get_conf(adaptive_scaler.workers, result_tmp1))
                                                        tmp_rm.sorted_combinations=sort_configs(adaptive_scaler.workers, tmp_lst)                                                       
                                                    print("NO SAMPLES LEFT, BUT THERE IS AN EVALUATED SAMPLE THAT NEEDS TO BE PROCESSED")
                                                    start_tmp=tmp_rm.sorted_combinations.index(get_conf(adaptive_scaler.workers, result_tmp1))
                                                    adaptive_window_tmp=tmp_rm.get_adaptive_window()
                                                    result_tmp2=find_optimal_result(tmp_adaptive_scaler2.workers,results_tmp1,slo)
                                                    process_results(result_tmp2,results_tmp1, tmp_rm, tmp_adaptive_scaler2, tmp_rm.sorted_combinations, start_tmp, adaptive_window_tmp, i, get_conf(adaptive_scaler.workers, d[sla['name']][str(i)]) )
                                                else:
                                                    print("NO SAMPLES LEFT, ASKING K8-RESOURCE-OPTIMIZER FOR OTHER SAMPLES")
                                                    tmp_rm.reset()
                                                    check_and_get_next_exps(tmp_adaptive_scaler2, tmp_rm, tmp_lst,tmp_lst[0],0,window,i, sampling_ratio, minimum_shared_replicas, maximum_transition_cost, window_offset_for_scaling_function, filter=True, retry=True, retry_window=tmp_rm.get_adaptive_window(), higher_tenants_only=True)
                                                    d[sla['name']][str(i)]=tmp_rm.get_next_sample()
                                                    update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,tmp_adaptive_scaler2,i,get_conf(adaptive_scaler.workers,d[sla['name']][str(i)]))
                                            print("NEXT SAMPLE FOR HIGHER NUMBER OF TENANTS " + str(i) + " :")
                                            print(get_conf(adaptive_scaler.workers,d[sla['name']][str(i)]))
                #elif intermediate_state == COST_EFFECTIVE_RESULT:
                #    remove_failed_confs(runtime_manager, tenant_nb, lst, tmp_adaptive_scaler.workers, rm, results, slo, get_conf(tmp_adaptive_scaler.workers, intermediate_result), start, adaptive_window.get_current_window(),True,[],scaling_up_threshold, sampling_ratio, intermediate_remove=True)
            if not no_exps and adaptive_scaler.ScalingDownPhase and adaptive_scaler.StartScalingDown:
                tmp_adaptive_scaler=adaptive_scaler.clone()
                intermediate_result=find_optimal_result(tmp_adaptive_scaler.workers,results,slo)
                tipped_over_intermediate_confs=return_failed_confs(tmp_adaptive_scaler.workers, results, lambda r: float(r['CompletionTime']) > slo and r['Successfull'] == 'true' and float(r['CompletionTime']) <= slo * scaling_up_threshold)
                intermediate_states=tmp_adaptive_scaler.validate_result(intermediate_result, get_conf(tmp_adaptive_scaler.workers,intermediate_result), slo)
                intermediate_state=intermediate_states.pop(0)
                #Remembering current experiment_nb and experiment_spec:
                if rm.experiments:
                    i=rm.get_nb_of_experiment_for_conf(previous_conf)
                    ws=rm.get_experiment_specification_for_experiment_nb(i)
                elif rm.last_experiment:
                    ws=rm.last_experiment["experiment_spec"]
                    i=rm.last_experiment["experiment_nb"]
                else:
                    raise RuntimeError("No experiments left in runtime manager")
                #removing failed_conf
                if not (intermediate_states and intermediate_states.pop(0) == UNDO_SCALE_ACTION):
                    start=remove_failed_confs(runtime_manager, tenant_nb, lst, tmp_adaptive_scaler.workers, rm, results, slo, get_conf(adaptive_scaler.workers, intermediate_result), start, adaptive_window.get_current_window(),results[0],[],scaling_up_threshold, sampling_ratio, intermediate_remove=True, careful_scaling=adaptive_scaler.careful_scaling)
                # if still configs remain to be tested
                last_experiment=update_conf_array(rm,lst,adaptive_scaler,tenant_nb)
                sla_conf=SLAConf(sla['name'],tenant_nb,ws[0],sla['slos'])
                samples=int(ws[4]*sampling_ratio)
                if samples == 0:
                    samples=1
                results=[]
                previous_result=float(completion_time)
                previous_replicas="[" + utils.array_to_delimited_str(previous_conf,",") + "]"
                sample_list=_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i),ws[1],ws[2],ws[3], sampling_ratio, initial_conf, previous_result=previous_result, previous_replicas=previous_replicas)
                print_results(adaptive_scaler, sample_list)
                if SORT_SAMPLES:
                    sample_list=sort_results(adaptive_scaler.workers,slo,sample_list)
                if not last_experiment:
                    print("There still remains configs to be tested in the current k8-resource-optimizer experiment batch")
                    rm.update_experiment_list(i,ws,sample_list)
                    d[sla['name']][str(tenant_nb)]=rm.get_next_sample()
                    update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,get_conf(adaptive_scaler.workers,d[sla['name']][str(tenant_nb)]))
                    #we have still samples left for k8-resource-optimizer, yield further processing and exit while loop
                    tenant_nb+=1
                    break
                else:
                    print("All useful experiment samples have been tested. We let k8-resource-optimizer return all the samples and we calculate the most optimal result from the set of samples that meet the slo")
                    results=process_samples(rm,tenant_nb,ws)
            result=find_optimal_result(adaptive_scaler.workers,results,slo)
            process_results(result, results, rm, adaptive_scaler, lst, start, adaptive_window, tenant_nb, previous_conf)
            tenant_nb+=1
        if not next_tenant_nb_processed or mono_constraint_violated:
            rm=get_rm_for_closest_tenant_nb(startTenants)
            lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
            start=0
            adaptive_window=rm.get_adaptive_window()
            process_request_for_next_tenant_nb()
        print("Saving optimal results into matrix")
        utils.saveToYaml(d,'Results/matrix.yaml')
        #When scaling to a number of jobs that is different from the previous number of jobs or the previous number of jobs +1
        #we search from the known optimal for the requested nr of jobs until a configuration is found that meets
        #the different constraints of transition cost and shared number of replicas. 
        #However this config should not be stored in the matrix because we need to remember the current found optimimum
        #therefore we store it in a different yaml file
        #Note: transition cost only applies when scaling up to a higher number of tenants.
        #if previous_conf and not (evaluate_current or evaluate_previous) and int(tenants) >= int(previous_tenants): #and not adaptive_scaler.hasScaled():
        #    adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(tenants),get_conf(adaptive_scaler.workers,d[sla['name']][tenants]),slo, include_current_tenant_nb= int(tenants) == int(previous_tenants))
        #    print("Moving filtered samples in sorted combinations after the window")
        #    rm=get_rm_for_closest_tenant_nb(int(tenants))
        #    lst=rm.set_sorted_combinations(_sort(adaptive_scaler.workers,base))
        #    print([utils.array_to_str(el) for el in lst])
        #    next_conf=get_conf(adaptive_scaler.workers,d[sla['name']][tenants])
        #    try:
        #        start_and_window=filter_samples_previous_tenant_conf(lst,adaptive_scaler,previous_conf, int(tenants) > int(previous_tenants), lst.index(next_conf), window, minimum_shared_replicas, maximum_transition_cost)
        #        print("Starting at index " + str(start_and_window[0]) + " with window " +  str(start_and_window[1]))
        #        print([utils.array_to_str(el) for el in lst])
        #        next_conf=lst[start_and_window[0]]
        #    except IndexError:
        #        print("No result that meets the transition costs and shared replicas constraints, returning to stored result")
        #    if currentResult and next_conf != get_conf(adaptive_scaler.workers, currentResult):
        #        current_conf=get_conf(adaptive_scaler.workers, currentResult)
        #        adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(tenants),current_conf,slo,include_current_tenant_nb= int(tenants) == int(previous_tenants))
        #        d[sla['name']][tenants]=create_result(adaptive_scaler, str(float(slo)+999999.000), next_conf, sla['name'])
        #print("Saving filtered results into matrix")
        utils.saveToYaml(d,'Results/result-matrix.yaml')


def get_adaptive_scaler_for_closest_tenant_nb(adaptive_scalers, adaptive_scaler, previous_results, tenants, slo):
                        as_predictedConf=None
                        k=tenants
                        while k >= 1:
                                if str(k) in  previous_results.keys():
                                        as_predictedConf=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers, adaptive_scaler,  previous_results, k, get_conf(adaptive_scaler.workers, previous_results[str(k)]),slo, include_current_tenant_nb=True)
                                        k=0
                                else:
                                        k-=1
                        if as_predictedConf:
                                return as_predictedConf
                        else:
                                return adaptive_scalers['init']


def extract_resources_from_result(result, worker_id, resource_types):
    resources={}
    for key in resource_types:
        resources[key]=int(result["worker"+str(worker_id)+".resources.requests." + key])
    return resources

def update_all_adaptive_scalers(d, sla, adaptive_scalers, adaptive_scaler, tenant_nb, base, window, slo, window_offset_for_scaling_function):
	for t in d[sla['name']].keys():
		if int(t) > tenant_nb:
			other_conf=get_conf(adaptive_scaler.workers, d[sla['name']][t])
			other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(t),other_conf,slo, clone_scaling_function=True)
			if not adaptive_scaler.equal_workers(other_as.workers) and other_as.ScalingDownPhase and other_as.StartScalingDown:
			#if not adaptive_scaler.equal_workers(other_as.workers):
				changed_scaler=False
				for i,w in enumerate(other_as.workers):
                                                changed=False
                                                if w.isFlagged():
                                                        changed_scaler=True
                                                        changed=True
                                                if changed:
                                                        other_as.workers[i]=adaptive_scaler.workers[i].clone()
				if changed_scaler:
					d[sla['name']][t]=create_result(other_as, float(slo) + 999999.0, get_conf_for_start_tenant(slo,int(t),other_as,_sort(other_as.workers,base),window), sla['name'], window_offset_for_scaling_function)
	return d


def check_consistency_adaptive_scalers_and_results(d, sla, adaptive_scalers, adaptive_scaler, slo, init_conf):
        print("Checking consistency of adaptive_scalers with stored results in matrix")
        for t in d[sla['name']].keys():
                        tmp_result=d[sla['name']][t]
                        other_conf=get_conf(adaptive_scaler.workers, tmp_result)
                        as_key=get_adaptive_scaler_key(t, other_conf)
                        if not as_key in adaptive_scalers.keys():
                            tmp_adaptive_scaler=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,d[sla['name']],int(t),other_conf,slo, clone_scaling_function=True)
                            resources_keys=adaptive_scaler.workers[0].resources.keys()
                            for i, w in enumerate(tmp_adaptive_scaler.workers):
                                for res in resources_keys:
                                    tmp_res=int(tmp_result["worker"+str(i+1)+".resources.requests." + res])
                                    if tmp_res != w.resources[res]:
                                        prefix=str(init_conf['prefix'][res]) if init_conf['prefix'][res] != None else ""
                                        suffix=str(init_conf['suffix'][res]) if init_conf['suffix'][res] != None else ""
                                        print("!!!Resource " + res +  " for worker " + str(w.worker_id) + " differs from the current alphabet setting: " + prefix + str(w.resources[res]) + suffix + " -> " + prefix + str(tmp_res) + suffix)
                                        raise RuntimeError("!!!Resource " + res +  " for worker " + str(w.worker_id) + " differs from the current alphabet setting: " + prefix + str(w.resources[res]) + suffix + " -> " + prefix + str(tmp_res) + suffix)
                        

def get_matrix_and_sla(initial_conf,namespace):
        slas=initial_conf['slas']
        d={}
        sla={}
        for s in slas:
                if s['name'] == namespace:
                        sla=s
        if os.path.isfile('Results/matrix.yaml'):
            d=yaml.safe_load(open('Results/matrix.yaml'))
        else:
            d={}
        if not sla['name'] in d:
                d[sla['name']]={}
        return {"matrix": d, "sla":sla}


def deep_copy_results(d):
	new_d = {}
	for sla_name in d.keys():
		new_d[sla_name]={}
		for tenant_nb in d[sla_name].keys():
			new_d[sla_name][tenant_nb]=dict(d[sla_name][tenant_nb])
	return new_d

#precondition: d[sla['name'][str(source_tenant_nb)] exists
def transfer_result(d, sla, adaptive_scalers, source_tenant_nb, destination_tenant_nb,slo, scaling_down_threshold):# previous_conf=[], previous_tenants = None):
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
	#if previous_conf and previous_tenants and source_tenant_nb != destination_tenant_nb  and int(previous_tenants) < destination_tenant_nb:
		#new_d  =  deep_copy_results(d)
	#else:
 		#new_d = d
	add_incremental_result(adaptive_scalers, destination_tenant_nb, d, sla, source_adaptive_scaler, slo, lambda x, slo: float(x['CompletionTime']) >= 1.0 and (float(x['CompletionTime']) > slo or float(x['CompletionTime'])*scaling_down_threshold < slo), destination_adaptive_scaler=destination_adaptive_scaler, next_conf=source_conf, result=sourceResult)
	return d

def add_incremental_result(adaptive_scalers,destination_tenant_nb, d, sla, source_adaptive_scaler, slo, isExistingResultNotCostEffective, destination_adaptive_scaler=None, previous_conf=None, next_conf=None, result=None):
	for w in source_adaptive_scaler.workers:
		print(w.resources)
	if result:
		result_conf=get_conf(source_adaptive_scaler.workers, result)
		if next_conf:
			if next_conf != result_conf:
				result={}
		else:
			next_conf=result_conf
	if previous_conf and next_conf and previous_conf != next_conf:
		source_adaptive_scaler=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,source_adaptive_scaler,destination_tenant_nb,next_conf)
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
	return source_adaptive_scaler


def get_adaptive_scaler_key(tenant_nb, conf):
	return str(tenant_nb)+ "X" + utils.array_to_delimited_str(conf,delimiter='_')

def get_tenant_nb_of_adaptive_scaler_key(adaptive_scaler_key):
	return  int(adaptive_scaler_key.split('X')[0])

def get_conf_of_adaptive_scaler_key(adaptive_scaler_key):
	str_conf=adaptive_scaler_key.split('X')[1]
	return list(map(lambda x: int(x),str_conf.split('_',-1)))

def get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,results,tenant_nb,conf,slo, clone_scaling_function=False, log=LOG_FILTERING, include_current_tenant_nb=False):
       tested_configuration=get_adaptive_scaler_key(tenant_nb, conf)
       if not (tested_configuration in adaptive_scalers.keys()):
                adaptive_scaler=adaptive_scaler.clone(start_fresh=True)
                adaptive_scalers[tested_configuration]=update_adaptive_scaler_with_results(adaptive_scaler, results, tenant_nb, conf)
       else:
                adaptive_scaler2=adaptive_scalers[tested_configuration]
                if str(tenant_nb) in results.keys() and conf != get_conf(adaptive_scaler.workers,results[str(tenant_nb)]):
                        adaptive_scaler2=update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,results,tenant_nb,get_conf(adaptive_scaler.workers,results[str(tenant_nb)]),slo, clone_scaling_function, log),tenant_nb,conf)
                elif clone_scaling_function:
                        adaptive_scaler2.ScalingFunction=adaptive_scaler.ScalingFunction.clone(clone_scaling_records=True)
                #unflag_all_workers(adaptive_scaler2.workers)
                adaptive_scaler=adaptive_scaler2
       #flag_all_workers_for_tenants_up_to_nb_tenants(results, tenant_nb, adaptive_scaler, slo, include_current_tenant_nb)
       if log:
                print("Returning adaptive scaler for  " + str(tenant_nb) + " tenants and " + utils.array_to_delimited_str(conf)+ ":")
                #adaptive_scaler.status()
       return adaptive_scaler

def update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,tenant_nb,conf, start_fresh=False):
        tested_configuration=get_adaptive_scaler_key(tenant_nb, conf)
        adaptive_scalers[tested_configuration]=adaptive_scaler.clone(start_fresh=start_fresh)
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

def flag_all_workers_for_tenants_up_to_nb_tenants(results, nb_tenants,adaptive_scaler,slo, include_current_tenant_nb=False):
    for t in results.keys():
        if int(t) < nb_tenants or (include_current_tenant_nb and int(t) == nb_tenants): # and float(results[t]['CompletionTime']) <= slo and float(results[t]['CompletionTime'])*SCALING_DOWN_TRESHOLD > slo:
            conf=get_conf(adaptive_scaler.workers, results[t])
            flag_workers(adaptive_scaler.workers, conf)


def create_result(adaptive_scaler, completion_time, conf, sla_name, successfull='true'):
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
		result['Successfull']=successfull
	print(result)
	return result


def get_conf_for_start_tenant(slo, tenant_nb, adaptive_scaler, combinations, window, window_offset_for_scaling_function):
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
           solution_index=max(0,combinations.index(conf)+int(window*window_offset_for_scaling_function))
           return combinations[solution_index]
       else:
           return []


def involves_worker(workers, conf, worker_index):
	if worker_index < 0 or worker_index >= len(workers):
		return True
	if conf[worker_index] > 0:
		return True
	else:
		return False


def all_flagged_tipped_over_conf_for_all_worker_indices_of_conf(adaptive_scaler, conf):
    if adaptive_scaler.opt_in_for_restart:
        return False
    for i,c in enumerate(conf):
        if not adaptive_scaler.workers[i].isFlagged() and c > 0:
            return False
    return True



def all_flagged_conf(adaptive_scaler, conf,ScaledWorkerIndex):
	if adaptive_scaler.opt_in_for_restart:
		return False
	if adaptive_scaler.ScalingDownPhase and not adaptive_scaler.StartScalingDown:
		if not (adaptive_scaler.workers and conf):
			return False
		for w,c in zip(adaptive_scaler.workers, conf):
			if not w.isFlagged() and c > 0:
				return False
		result=True
		for w,c in zip(adaptive_scaler.workers, conf):
			if w.isFlagged() and c == 0:
				result=False
		return  result
	elif adaptive_scaler.ScalingUpPhase:
		return adaptive_scaler.workers[ScaledWorkerIndex].isFlagged()
	else:
		return adaptive_scaler.workers[ScaledWorkerIndex].isFlagged() and conf[ScaledWorkerIndex] > 0

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



def remove_failed_confs(runtime_manager, tenant_nb, sorted_combinations, workers, rm, results, slo, optimal_conf, start, window, previous_result, tipped_over_results, scaling_up_threshold, sampling_ratio, startingTenant=False, intermediate_remove=False, higher_tenant_remove=False, careful_scaling=False):
		if not runtime_manager[tenant_nb].result_is_stored(workers, previous_result):
			return start
		next_index=start
		if optimal_conf and careful_scaling:
		#	if not intermediate_remove:
		#		if tipped_over_results and optimal_conf in tipped_over_results:
		#			tipped_over_results.remove(optimal_conf)
		#		tmp_combinations=sort_configs(workers,sorted_combinations, cost_aware=False)
		#		failed_range=tmp_combinations.index(optimal_conf)
		#		for i in range(0, failed_range):
		#			possible_removal=tmp_combinations[i]
		#			if resource_cost(workers, possible_removal) < resource_cost(workers, optimal_conf):
		#				print("Removing config because it has a lower resource cost than the optimal result and we assume it will therefore fail for the next tenant")
		#				print(possible_removal)
		#				#if not (possible_removal in return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) < slo)):
		#				sorted_combinations.remove(possible_removal)
		#				if rm.conf_in_experiments(possible_removal):
		#					rm.remove_sample_for_conf(possible_removal)
		#	if intermediate_remove:
				tmp_combinations=sort_configs(workers,sorted_combinations)
				failed_range=0
				for i in range(failed_range, len(tmp_combinations)):
					possible_removal=tmp_combinations[i]
					if resource_cost(workers, possible_removal, cost_aware=False) > resource_cost(workers, optimal_conf, cost_aware=False) + 10:
						print(possible_removal)
						if possible_removal in sorted_combinations:
							print("Removing config because it has a higher resource cost than the current optimal result and therefore this config and all higher configs are not cost effective for the currrent or lower number of tenants")
							if sorted_combinations.index(possible_removal) < next_index:
								next_index-=1
							elif sorted_combinations.index(possible_removal) == next_index and next_index > 0:
								next_index-=1
							sorted_combinations.remove(possible_removal)
							if rm.conf_in_experiments(possible_removal):
								rm.remove_sample_for_conf(possible_removal)
	#	elif not intermediate_remove and not tipped_over_results and not optimal_conf and sampling_ratio < 1.0 and sampling_ratio >= 0.5:
	#		failed_configs=sort_configs(workers,return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) > slo), cost_aware=False)
	#		if failed_configs:
	#			tmp_combinations=sort_configs(workers,sorted_combinations, cost_aware=False)
	#			tmp_start=tmp_combinations.index(failed_configs[0])
	#			failed_range=tmp_combinations.index(failed_configs[len(failed_configs)-1])+1
	#			last_failed_conf=failed_configs[len(failed_configs)-1][:]
	#			#failed_range=start+window
	#			print("Removing all confs in window going over the scaling_up_threshold because no optimal config has been found at all")
	#			index=0 #if startingTenant else tmp_start
	#			possible_tipped_over_confs=return_failed_confs(workers, results, lambda r: float(r['CompletionTime']) <= slo * scaling_up_threshold and r['Successfull'] == 'true')
	#			for i in range(index,failed_range,1):
       	#				if i >= tmp_start or resource_cost(workers, tmp_combinations[i]) < resource_cost(workers, last_failed_conf):
	#					print(tmp_combinations[i])
	#					if not tmp_combinations[i] in possible_tipped_over_confs:
	#						print(utils.array_to_delimited_str(tmp_combinations[i], " ") + " is removed")
	#						sorted_combinations.remove(tmp_combinations[i])
# if not intermediate_remove
		#if previous_result and float(previous_result['CompletionTime']) < slo and float(previous_result['CompletionTime']) > 1:
		#	workers_result=[w.clone() for w in workers]
		#	resource_types=workers[0].resources.keys()
		#	for w in workers_result:
		#		w.resources=extract_resources_from_result(previous_result, w.worker_id, resource_types)
		#else:
		#	workers_result=[]
		for failed_conf in return_failed_confs(workers, results, lambda r: (float(r['CompletionTime']) > slo * scaling_up_threshold) or (float(r['CompletionTime']) > slo and (higher_tenant_remove or tipped_over_results))):
			if failed_conf in sorted_combinations:
				tmp_combinations=sort_configs(workers,sorted_combinations)
				failed_range=tmp_combinations.index(failed_conf)
				for i in range(0, failed_range):
					possible_removal=tmp_combinations[i]
					if (higher_tenant_remove or tipped_over_results or not possible_removal in (rm.get_tipped_over_results(nullify=False))["results"]) and resource_cost(workers, possible_removal, False) < resource_cost(workers, failed_conf, False):  
						print(possible_removal)
						if possible_removal in sorted_combinations:
							print("Removing config because it has a lower resource cost than the failed result and we assume it will therefore fail for this tenant")
							sorted_combinations.remove(possible_removal)
							if rm.conf_in_experiments(possible_removal):
								rm.remove_sample_for_conf(possible_removal)
							if possible_removal in (rm.get_tipped_over_results(nullify=False))["results"]:
								rm.remove_tipped_over_result(possible_removal)
				#if (not failed_conf in (rm.get_tipped_over_results(nullify=False))["results"]) or (careful_scaling or higher_tenant_remove or tipped_over_results):
				print("Removing failed conf")
				print(failed_conf)
				i=1
				new_index=sorted_combinations.index(failed_conf)-i
				while new_index >= 0 and resource_cost(workers,failed_conf, False) == resource_cost(workers, sorted_combinations[new_index], False):
					next_index=new_index
					i+=1
					new_index=sorted_combinations.index(failed_conf)-i
				sorted_combinations.remove(failed_conf)
				if rm.conf_in_experiments(failed_conf):
 					rm.remove_sample_for_conf(failed_conf)
				if failed_conf in (rm.get_tipped_over_results(nullify=False))["results"]:
					rm.remove_tipped_over_result(failed_conf)
		if tipped_over_results:
                        for failed_conf in tipped_over_results:
                                if failed_conf in sorted_combinations:
                                        print("Removing tipped over conf")
                                        print(failed_conf)
                                        if sorted_combinations.index(failed_conf) <= next_index and next_index > 0:
                                                next_index=next_index-1
                                        sorted_combinations.remove(failed_conf)
					#rm.remove_tipped_over_result(failed_conf)
                                else:
                                        print("Tipped over conf already removed:")
                                        print(failed_conf)
                                #rm.reset()
		return next_index



def has_different_workers_than(adaptive_scaler_a, conf_a, adaptive_scaler_b, conf_b):
    for worker_index, conf_pair in enumerate(zip(conf_a,conf_b)):
        if conf_pair[0] > 0 and conf_pair[1] > 0:
            if not adaptive_scaler_a.workers[worker_index].equals(adaptive_scaler_b.workers[worker_index]):
                return True
    return False

#def has_different_workers_than(adaptive_scaler_a, conf_a, adaptive_scaler_b, conf_b):
#    return  has_smaller_workers_than(adaptive_scaler_a, conf_a, adaptive_scaler_b, conf_b) or  has_smaller_workers_than(adaptive_scaler_b, conf_b, adaptive_scaler_a, conf_a)

def has_smaller_incremental_workers_than(adaptive_scaler_a, adaptive_scaler_b, conf):
    if len(adaptive_scaler_a.workers) != len(adaptive_scaler_b.workers):
        return False
    if has_smaller_or_equal_workers_than_for_conf(adaptive_scaler_b, adaptive_scaler_a, conf):
        return False
    for worker_index in range(0, len(adaptive_scaler_a.workers)):
            if is_smaller_increment_worker_than(adaptive_scaler_a.workers[worker_index],adaptive_scaler_b.workers[worker_index], adaptive_scaler_a.increments,2):
                return False
    for worker_index in range(0, len(adaptive_scaler_a.workers)):
            if is_smaller_increment_worker_than(adaptive_scaler_a.workers[worker_index],adaptive_scaler_b.workers[worker_index], adaptive_scaler_a.increments,1):
                return True
    return False



def has_smaller_or_equal_workers_than_for_conf(adaptive_scaler_a,adaptive_scaler_b, conf):
    if not has_different_workers_than(adaptive_scaler_a, conf, adaptive_scaler_b, conf):
        return False
    return resource_cost(adaptive_scaler_a.workers,conf, cost_aware=False) <= resource_cost(adaptive_scaler_b.workers,conf,cost_aware=False)


def has_smaller_workers_than(adaptive_scaler_a, conf_a, adaptive_scaler_b, conf_b):
    if not has_different_workers_than(adaptive_scaler_a, conf_a, adaptive_scaler_b, conf_b):
        return False
    test_conf=conf_a[:]
    for worker_index,conf_pair in enumerate(zip(conf_a,conf_b)):
        if conf_pair[0] > 0 and conf_pair[1] > 0:
            test_conf[worker_index]=1
        else:
            test_conf[worker_index]=0
    return resource_cost(adaptive_scaler_a.workers,test_conf, cost_aware=False) <= resource_cost(adaptive_scaler_b.workers,test_conf,cost_aware=False)


def is_smaller_worker_than(worker_a, worker_b):
    if worker_a.equals(worker_b):
        return False
    for res in worker_a.resources.keys():
        if worker_a.resources[res] > worker_b.resources[res]:
            return False
    for res in worker_a.resources.keys():
        if worker_a.resources[res] < worker_b.resources[res]:
            return True
    return False

def is_smaller_increment_worker_than(worker_a, worker_b, increments, nb_of_increments):
    if worker_a.equals(worker_b):
        return False
    for res in worker_a.resources.keys():
        if worker_a.resources[res] > worker_b.resources[res]:
            return False
    for res in worker_a.resources.keys():
        if worker_a.resources[res] + nb_of_increments*increments[res] <= worker_b.resources[res]:
            return True
    return False


def can_be_improved_by_another_config(results, sorted_combinations, adaptive_scaler, tenants, slo, scaling_up_threshold):
    return can_be_improved_by_larger_config(results,tenants,slo, scaling_up_threshold) or can_be_improved_by_smaller_config(results,sorted_combinations,adaptive_scaler,tenants)


def can_be_improved_by_larger_config(results,tenants,slo, scaling_up_threshold):
    if not str(tenants) in results.keys():
        return True
    return (float(results[str(tenants)]['CompletionTime']) >= slo * scaling_up_threshold or results[str(tenants)]['Successfull'] == 'false') and float(results[str(tenants)]['CompletionTime']) != float(TEST_CONFIG_CODE)  

def can_be_improved_by_smaller_config(results, sorted_combinations, adaptive_scaler, tenants):
    if not str(tenants) in results.keys():
        return True
    tmp_combinations=sort_configs(adaptive_scaler.workers, sorted_combinations)
    index=tmp_combinations.index(get_conf(adaptive_scaler.workers,results[str(tenants)]))
    return  float(results[str(tenants)]['CompletionTime']) != float(TEST_CONFIG_CODE) and index > 0 and resource_cost(adaptive_scaler.workers, tmp_combinations[0]) < resource_cost(adaptive_scaler.workers, tmp_combinations[index])


def update_other_tenants_from_tenant_nb(runtime_manager, adaptive_scalers,previous_results, adaptive_scaler, tenant_nb, slo, scaling_down_threshold):
        def debug():
            if '1' in previous_results.keys():
                conf56 = get_conf(adaptive_scaler.workers, previous_results['1'])
                as2 = get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,previous_results,1,conf56,slo)
                for w in as2.workers:
                    print(w.resources)
        cloned_other_as={}
        changed_scaler=False
        for t in previous_results.keys():
                stop=True
                if int(t) != tenant_nb:
                        other_conf=get_conf(adaptive_scaler.workers, previous_results[t])
                        other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,get_adaptive_scaler_for_closest_tenant_nb(adaptive_scalers, adaptive_scaler, previous_results, int(t),slo),previous_results,int(t),other_conf,slo, log=True)
                        if not adaptive_scaler.equal_workers(other_as.workers):
                            if other_as.ScalingDownPhase and other_as.StartScalingDown:
                                if float(previous_results[t]['CompletionTime']) == TEST_CONFIG_CODE or not (float(previous_results[t]['CompletionTime']) < 1.0 or float(previous_results[t]['CompletionTime']) > float(slo) * 100):
                                    if float(previous_results[t]['CompletionTime']) == TEST_CONFIG_CODE:
                                        previous_results[t]=runtime_manager[int(t)].list_of_results[-1]['result']
                                        update_adaptive_scaler_with_results(other_as, previous_results, int(t), get_conf(other_as.workers, previous_results[t])) 
                                    if float(previous_results[t]['CompletionTime']) > slo and has_smaller_incremental_workers_than(other_as, adaptive_scaler, other_conf):
                                        stop=False
                                    elif float(previous_results[t]['CompletionTime'])* scaling_down_threshold <= slo and has_smaller_incremental_workers_than(adaptive_scaler, other_as, other_conf):
                                        stop=False
                            #elif not adaptive_scaler.equal_workers(other_as.workers):
                            if not stop:
                                for i,w in enumerate(adaptive_scaler.workers):
                                                changed=False
                                                if not other_as.workers[i].equals(w):
                                                        changed=True
                                                if changed:
                                                        changed_scaler=True
                                                        if not t in cloned_other_as.keys():
                                                            cloned_other_as[t]=other_as.clone(start_fresh=True)
                                                        cloned_other_as[t].workers[i]=adaptive_scaler.workers[i].clone()
        for t in cloned_other_as.keys():
            update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,cloned_other_as[t],t, get_conf(cloned_other_as[t].workers, previous_results[t]))
            previous_results[t]=create_result(cloned_other_as[t], float(TEST_CONFIG_CODE), get_conf(cloned_other_as[t].workers, previous_results[t]),previous_results[t]['SLAName'])
        debug()
        return changed_scaler

#def tenant_nb_X_result_conf_conflict_with_higher_tenants(adaptive_scalers,previous_results, adaptive_scaler, tenant_nb, result_conf, slo):
#        for t in previous_results.keys():
#                if int(t) > tenant_nb:
#                        other_conf=get_conf(adaptive_scaler.workers, previous_results[t])
#                        other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,previous_results,int(t),other_conf,slo, clone_scaling_function=True, log=True)
#                        if float(previous_results[t]['CompletionTime']) <= slo and has_smaller_workers_than(other_as, other_conf, adaptive_scaler, result_conf):
#                            return True
#                        elif  float(previous_results[t]['CompletionTime'])*SCALING_DOWN_TRESHOLD >= slo and has_smaller_workers_than(adaptive_scaler, result_conf, other_as, other_conf):
#                            return True
#        return False

def filter_samples(adaptive_scalers,sorted_combinations, adaptive_scaler, start, window, previous_results, start_tenant, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers=False, ScaledDownWorkerIndex=-1, log=True, original_adaptive_scaler=None, initial_conf=[], include_current_tenant_nb=False, resource_cost_is_too_high=False, update_done=False):        
        def check_resource_cost():
            if original_adaptive_scaler and check_workers:
                if adaptive_scaler.ScalingDownPhase and resource_cost(original_adaptive_scaler.workers, initial_conf, cost_aware=True) <= resource_cost(adaptive_scaler.workers, sorted_combinations[el-(window-new_window)], cost_aware=True):
                    resource_cost_is_too_high=True
                    return True
                elif adaptive_scaler.ScalingUpPhase and not equal_conf(sorted_combinations[el-(window-new_window)], initial_conf):
                    resource_cost_is_too_high=True
                    return True
                else:
                    return False
            else:
                return False
        if log:
            print("Starting at index " + str(start) + " with window " + str(window))
        i=start_tenant
        new_window=window
        start_window=window
        if previous_results:
                if check_workers and ScaledDownWorkerIndex != -1 and not update_done:
                    if 'copy' in adaptive_scalers.keys():
                        del adaptive_scalers['copy']
                    if 'results' in adaptive_scalers.keys():
                        del adaptive_scalers['results']
                    adaptive_scalers['copy']={}
                    for key in adaptive_scalers.keys():
                        if isinstance(adaptive_scalers[key],AdaptiveScaler):
                            adaptive_scalers['copy'][key]=adaptive_scalers[key].clone()
                        elif key != 'copy':
                            adaptive_scalers['copy'][key]=adaptive_scalers[key]
                    adaptive_scalers['results']={}
                    for t in previous_results.keys():
                        adaptive_scalers['results'][t]=dict(previous_results[t])
                    if update_other_tenants_from_tenant_nb(runtime_manager, adaptive_scalers,previous_results, adaptive_scaler, tenant_nb, slo, scaling_down_threshold):
                        print("Updated performed!!!!!!")
                    else:
                        if 'copy' in adaptive_scalers.keys():
                            del adaptive_scalers['copy']
                        if 'results' in adaptive_scalers.keys():
                            del adaptive_scalers['results']
                        
                max_tenants=max(map(lambda x: int(x), previous_results.keys()))
                while i <= max_tenants:
                        #if (include_current_tenant_nb and i == tenant_nb):
                        #    flag_all_workers_for_tenants_up_to_nb_tenants(previous_results, tenant_nb, adaptive_scaler,slo, include_current_tenant_nb=True)
                        if (include_current_tenant_nb or i != tenant_nb) and str(i) in previous_results.keys():
                                if i <= tenant_nb:
                                    previous_tenant_conf=get_conf(adaptive_scaler.workers, previous_results[str(i)])
                                    minimum_shared_replicas=runtime_manager[tenant_nb].minimum_shared_replicas
                                    maximum_transition_cost=runtime_manager[tenant_nb].maximum_transition_cost
                                    minimum_shared_resources=runtime_manager[tenant_nb].minimum_shared_resources
                                else:
                                    minimum_shared_replicas=runtime_manager[i].minimum_shared_replicas
                                    maximum_transition_cost=runtime_manager[i].maximum_transition_cost
                                    minimum_shared_resources=runtime_manager[i].minimum_shared_resources
                                    result_conf=get_conf(adaptive_scaler.workers, previous_results[str(i)])
                                # if scale_action_undo, last failed worker of adapative_scaler should be filtered away for all tenantns (this can be done generally by setting checck_workers to True, ScaledDownWorjerIndex to the index fo the failed worker. Filtering away for all tenants means while i < == max_tannannts; if str(i) in previopus_results.keys(),prevuous_tenantconf
                                #if include_current_tenant_nb and i == tenant_nb  and not check_workers and adaptive_scaler.PreviousFailedScalings:
                                #    check_workers=True
                                #    exceptional_no_check_for_vertical_scaling=True
                                #    ScaledDownWorkerIndex=int(adaptive_scaler.PreviousFailedScalings[-1].worker_id)-1
                                for el in range(start, start+window):
                                        #if el-(window-new_window) >= len(sorted_combinations):
                                        #        return [-1,-1]
                                        try:
                                            if i <= tenant_nb:
                                                result_conf=sorted_combinations[el-(window-new_window)]
                                            else:
                                                previous_tenant_conf=sorted_combinations[el-(window-new_window)]
                                        except IndexError as e:
                                            if 'results' in adaptive_scalers.keys():
                                                previous_results=adaptive_scalers['results']
                                                del adaptive_scalers['results']
                                            if 'copy' in adaptive_scalers.keys():
                                                adaptive_scalers=dict(adaptive_scalers['copy'])
                                            if adaptive_scaler.ScalingDownPhase and resource_cost_is_too_high:
                                                raise IndexError("recursive_scaling_may_help") from e
                                            else:
                                                raise
                                        if log:
                                            if i <= tenant_nb:
                               	                print(result_conf)
                                            else:
                                                print(previous_tenant_conf)
                                        remove=False
                                        #if (not exceptional_no_check_for_vertical_scaling and (not (not check_workers or involves_worker(adaptive_scaler.workers, sorted_combinations[el-(window-new_window)], ScaledDownWorkerIndex))))
                                        if not (not check_workers or involves_worker(adaptive_scaler.workers, sorted_combinations[el-(window-new_window)], ScaledDownWorkerIndex)) or check_resource_cost():
                                            remove=True
                                        else:
                                            if i != tenant_nb:
                                                other_conf=get_conf(adaptive_scaler.workers, previous_results[str(i)])
                                                other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,previous_results,i,other_conf,slo,log=False)
                                                if i < tenant_nb:
                                                    previous_adaptive_scaler=other_as
                                                    current_adaptive_scaler=adaptive_scaler
                                                elif i > tenant_nb:
                                                    previous_adaptive_scaler=adaptive_scaler
                                                    current_adaptive_scaler=other_as
                                            else:
                                                current_adaptive_scaler=adaptive_scaler
                                                previous_adaptive_scaler=update_adaptive_scaler_with_results(adaptive_scaler.clone(), previous_results, tenant_nb, get_conf(adaptive_scaler.workers, previous_results[str(tenant_nb)]))
                                            qualitiesOfSample=_pairwise_transition_cost(previous_adaptive_scaler.workers, previous_tenant_conf, current_adaptive_scaler.workers, result_conf, minimum_shared_replicas, minimum_shared_resources, log=True)
                                        #else:
                                        #    qualitiesOfSample=_pairwise_transition_cost(previous_tenant_conf,result_conf, minimum_shared_replicas, False, -1, log=log)
                                            cost=qualitiesOfSample['cost']
                                            nb_shrd_replicas=qualitiesOfSample['nb_shrd_repls']
                                            shrd_resources=qualitiesOfSample['shrd_resources']
                                            if isinstance(minimum_shared_replicas,int):
                                                min_shared_replicas = min([minimum_shared_replicas,reduce(lambda x, y: x + y, previous_tenant_conf)])
                                            else:
                                                min_shared_replicas = max([1,int(minimum_shared_replicas*reduce(lambda x, y: x + y, previous_tenant_conf))])
                                            min_shared_resources={}
                                            for key in minimum_shared_resources:
                                                minimum_shared_resource_size=minimum_shared_resources[key]
                                                minimum_resources=adaptive_scaler.minimum_resources
                                                if isinstance(minimum_shared_resource_size,int):
                                                    min_shared_resources[key] = min([minimum_shared_resource_size,reduce(add,map(mul,previous_tenant_conf,map(lambda x: x.resources[key],previous_adaptive_scaler.workers)))])
                                                else:
                                                    #1> minimum_resources['cpu']
                                                    min_shared_resources[key] = max([minimum_resources[key],int(minimum_shared_resource_size*reduce(add,map(mul,previous_tenant_conf,map(lambda x: x.resources[key],previous_adaptive_scaler.workers))))])
                                        #if (check_workers and i <= tenant_nb and all_flagged_conf(adaptive_scaler, sorted_combinations[el-(window-new_window)], ScaledDownWorkerIndex))

                                        def check_shared_resources():
                                            reject=False
                                            for key in min_shared_resources.keys():
                                                if shrd_resources[key] < min_shared_resources[key]:
                                                    reject=True
                                                    break
                                            return reject
                                        if remove or cost > maximum_transition_cost or nb_shrd_replicas < min_shared_replicas or check_shared_resources():
                                        #for (i > tenant_nb and tenant_nb_X_result_conf_conflict_with_higher_tenants(adaptive_scalers,previous_results, adaptive_scaler, tenant_nb, sorted_combinations[el-(window-new_window)], slo, scaling_down_threshold)):
                                            if log and ScaledDownWorkerIndex > -1:
                                                print("SCALING INDEX = " + str(ScaledDownWorkerIndex))
                                            if log:
                                                print("removed")
                                            if i <= tenant_nb:
                                                tmp_conf=result_conf
                                            else:
                                                tmp_conf=previous_tenant_conf
                                            sorted_combinations.remove(tmp_conf)
                                            sorted_combinations.insert(new_window+el-1,tmp_conf)
                                            new_window-=1
                                        else:
                                            if log:
                                                print("not removed")
                                if new_window == 0:
                                        #unflag_all_workers(adaptive_scaler.workers)
                                        #flag_all_workers_for_tenants_up_to_nb_tenants(previous_results, tenant_nb, adaptive_scaler,slo, include_current_tenant_nb=False)
                                        return filter_samples(adaptive_scalers, sorted_combinations, adaptive_scaler, start+start_window, start_window, previous_results, start_tenant, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers, ScaledDownWorkerIndex, log, original_adaptive_scaler, initial_conf,include_current_tenant_nb, resource_cost_is_too_high, True)
                                else:
                                        i+=1
                                        if log:
                                            print("Going to " + str(i) + " tenants")
                                        window=new_window
                                        stop=False
                                        while i <= max_tenants and not stop:
                                                if str(i) in previous_results.keys():
                                                        stop=True
                                                else:
                                                        i+=1
                                                        if log:
                                                            print("Going to " + str(i) + " tenants")

                        else:
                                i+=1
                                if log:
                                    print("Going to " + str(i) + " tenants")
        else:
                for el in range(start, start+window):
                        try: 
                            result_conf=sorted_combinations[el-(window-new_window)]
                        except IndexError as e:
                            if resource_cost_is_too_high:
                                raise IndexError("recursive_scaling_may_help") from e
                            else:
                                raise
                        if log:
                            print(result_conf)
                        if not (not check_workers or involves_worker(adaptive_scaler.workers, result_conf, ScaledDownWorkerIndex)) or check_resource_cost():
                                if log and ScaledDownWorkerIndex > -1:
                                    print("SCALING INDEX = " + str(ScaledDownWorkerIndex))
                                if log:
                                    print("removed")
                                sorted_combinations.remove(result_conf)
                                sorted_combinations.insert(start+new_window+el-1,result_conf)
                                new_window-=1
                        else:
                                if log:
                                    print("not removed")
                if new_window == 0:
                        return filter_samples(adaptive_scalers, sorted_combinations, adaptive_scaler, start+window, window, previous_results, start_tenant, tenant_nb, runtime_manager, scaling_down_threshold, slo, check_workers, ScaledDownWorkerIndex, log, original_adaptive_scaler, initial_conf, include_current_tenant_nb, resource_cost_is_too_high, True)
        #When all constraints are satisfied and a worker has been scaled, update all_tenant_confs in previous_results with the appropriate worker "worker_index" if previous_tenant_confs[worker_index]==0
        #for t in previous_results.keys():
        #                if int(t) != tenant_nb:
        #                        for i in get_conf(adaptive_scaler.workers, previous_results[t]):
        #                            if i == 0: 
        #                                adaptive_scalers[get_adaptive_scaler_key(int(t), get_conf(adaptive_scaler.workers, previous_results[t]))].workers[i].resources=dict(adaptive_scaler.workers[i].resources)
        #                            for key in adaptive_scaler.workers[ScaledDownWorkerIndex].resources.keys():
        #                                previous_results[t]["worker"+str(adaptive_scaler.workers[i].worker_id)+".resources.requests." + key]=str(adaptive_scaler.workers[i].resources[key])
        #unflag_all_workers(adaptive_scaler.workers)
        #flag_all_workers_for_tenants_up_to_nb_tenants(previous_results, tenant_nb, adaptive_scaler,slo, include_current_tenant_nb=False)                                               
        return [start, new_window]


def filter_samples_previous_tenant_conf(sorted_combinations, adaptive_scaler, previous_tenant_conf, costIsRelevant, start, window, minimum_shared_replicas, maximum_transition_cost, ScaledWorkerIndex=-1):
	new_window=window
	workers=adaptive_scaler.workers
	for el in range(start, start+window):
		result_conf=sorted_combinations[el-(window-new_window)]
		if previous_tenant_conf:
			qualitiesOfSample=_pairwise_transition_cost(previous_tenant_conf,result_conf, minimum_shared_replicas)
			cost=qualitiesOfSample['cost']
			nb_shrd_replicas=qualitiesOfSample['nb_shrd_repls']
			if isinstance(minimum_shared_replicas,int): 
				min_shared_replicas = min([minimum_shared_replicas,reduce(lambda x, y: x + y, previous_tenant_conf)])
			else:
				min_shared_replicas = max([1,int(minimum_shared_replicas*reduce(lambda x, y: x + y, previous_tenant_conf))])
			print(result_conf)
			if all_flagged_conf(adaptive_scaler, result_conf, ScaledWorkerIndex) or (costIsRelevant and cost > maximum_transition_cost) or nb_shrd_replicas < min_shared_replicas or not involves_worker(workers, result_conf, ScaledWorkerIndex):
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
		return filter_samples_previous_tenant_conf(sorted_combinations, adaptive_scaler, previous_tenant_conf, costIsRelevant, start+window, window, minimum_shared_replicas, maximum_transition_cost, ScaledWorkerIndex)
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


def find_optimal_result(workers,results, slo, just_return_best=False):
	print("Results")
	print(results)
	filtered_results=[result for result in results if (just_return_best or float(result['CompletionTime']) <= slo) and float(result['CompletionTime']) > 1.0]
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



def tenant_nb_X_result_conf_conflict_with_other_tenant_nb(adaptive_scalers, previous_results, adaptive_scaler, tenant_nb, result_conf, other_tenant_nb, slo, scaling_down_threshold):
        cloned_other_as={}
        t=str(other_tenant_nb)
        if t in previous_results.keys():
            other_conf=get_conf(adaptive_scaler.workers, previous_results[t])
            other_as=get_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,adaptive_scaler,previous_results,other_tenant_nb,other_conf,slo, clone_scaling_function=True, log=False)
            if other_tenant_nb > tenant_nb:
                        if not adaptive_scaler.equal_workers(other_as.workers):
                            if (float(previous_results[t]['CompletionTime']) < 1.0 or float(previous_results[t]['CompletionTime']) > float(slo) * 100) and has_different_workers_than(other_as, other_conf, adaptive_scaler, result_conf):
                                return True
                            elif float(previous_results[t]['CompletionTime']) <= slo and has_smaller_workers_than(other_as, other_conf, adaptive_scaler, result_conf):
                                return True
                            elif float(previous_results[t]['CompletionTime'])*scaling_down_threshold >= slo and has_smaller_workers_than(adaptive_scaler, result_conf, other_as, other_conf):
                                return True
                            elif not (other_as.ScalingDownPhase and other_as.StartScalingDown):
                                return True
                            #elif not adaptive_scaler.equal_workers(other_as.workers):
                            changed_scaler=False
                            for i,w in enumerate(adaptive_scaler.workers):
                                                changed=False
                                                if involves_worker(adaptive_scaler.workers, result_conf,i) and not other_as.workers[i].equals(w):
                                                        changed=True
                                                if changed:
                                                        if not t in cloned_other_as.keys():
                                                            cloned_other_as[t]=other_as.clone(start_fresh=True)
                                                        cloned_other_as[t].workers[i]=adaptive_scaler.workers[i].clone()
        for t in cloned_other_as.keys():
            update_adaptive_scaler_for_tenantnb_and_conf(adaptive_scalers,cloned_other_as[t],t, get_conf(cloned_other_as[t].workers, previous_results[t]))
            previous_results[t]=create_result(cloned_other_as[t], float(TEST_CONFIG_CODE), get_conf(cloned_other_as[t].workers, previous_results[t]),previous_results[t]['SLAName'])
        return False


def _old_pairwise_transition_cost(worker_previous_conf, workers_conf, previous_conf,conf, minimum_shared_replicas, minimum_shared_resources, check_worker, scaled_worker_index, log=False):
    if not previous_conf:
        return {'cost': 0, 'nb_shrd_repls': minimum_shared_replicas, 'shrd_resources': minimum_shared_resources}
    cost=0
    shared_replicas=0
    shared_resources={}
    for key in minimum_shared_resources.keys():
        shared_resources[key]=0
    index=0
    for worker_index, conf_pair in enumerate(zip(conf,previous_conf)):
        c1=conf_pair[0]
        c2=conf_pair[1]
        if  not (check_worker and index == scaled_worker_index) and c1 > c2:
            cost+=c1-c2
        elif (check_worker and index == scaled_worker_index) and c1 > 0:
            cost+=c1
        if c2 >= 1  and c1 >= 1 and not (check_worker and index == scaled_worker_index):
            shared_replicas+=min(c1,c2)
            for key in minimum_shared_resources.keys():
                shared_resources[key]+=min(workers_conf[worker_index].resources[key], workers_previous_conf[worker_index].resources[key])

        index+=1
    if log:
        print('cost: ' + str(cost) + ', nb_shrd_repls: ' + str(shared_replicas) +  ', shrd_resources: ' + str(shared_resources))
    return {'cost': cost, 'nb_shrd_repls': shared_replicas, 'shrd_resources': shared_resources}

def _pairwise_transition_cost(previous_workers, previous_conf, workers, conf, minimum_shared_replicas, minimum_shared_resources, log=False):
    if not previous_conf or not previous_workers:
        return {'cost': 0, 'nb_shrd_repls': minimum_shared_replicas, 'shrd_resources': minimum_shared_resources}
    cost=0
    shared_replicas=0
    shared_resources={}
    for key in minimum_shared_resources.keys():
        shared_resources[key]=0
    for worker_index, conf_pair in enumerate(zip(conf,previous_conf)):
        if workers[worker_index].equals(previous_workers[worker_index]):
            if conf_pair[0] > conf_pair[1]:
                cost+=conf_pair[0]-conf_pair[1]
            if conf_pair[1] >= 1  and conf_pair[0] >= 1:
                shared_replicas+=min(conf_pair[0],conf_pair[1])
                for key in minimum_shared_resources.keys():
                    shared_resources[key]+=shared_replicas*workers[worker_index].resources[key]
        else:
            cost+=conf_pair[0]
    if log:
        print('cost: ' + str(cost) + ', nb_shrd_repls: ' + str(shared_replicas) +  ', shrd_resources: ' + str(shared_resources))
    return {'cost': cost, 'nb_shrd_repls': shared_replicas, 'shrd_resources': shared_resources}


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



def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path, conf, minimum_repl, maximum_repl, sampling_ratio, initial_conf, previous_result=None, previous_replicas=None):
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
			sampling_rate=sampling_ratio,
			output= exp_path+'/op/',
		        prev_results=results_json_file,
			slas=slas,
			maximum_replicas='"'+maximum_repl+'"',
			minimum_replicas='"'+minimum_repl+'"',
			configs='"'+conf+'"',
			previous_result='"'+str(previous_result)+'"',
			previous_replicas='"'+previous_replicas+'"',
                        suffix=initial_conf['suffix'],
                        prefix=initial_conf['prefix'],
                        increments=initial_conf['increments'])
	else:
		conf_op=ConfigParser(
                        optimizer='bestconfig',
                        chart_dir=chart_dir,
                        util_func= util_func,
                        samples= samples,
                        sampling_rate=sampling_ratio,
                        output= exp_path+'/op/',
                        prev_results=results_json_file,
                        slas=slas,
                        maximum_replicas='"'+maximum_repl+'"',
                        minimum_replicas='"'+minimum_repl+'"',
                        configs='"'+conf+'"',
                        suffix=initial_conf['suffix'],
                        prefix=initial_conf['prefix'],
                        increments=initial_conf['increments'])

	# exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op/')

	# exp_ex.runExperiment()
	exp_op.runExperiment()
	#conf_array=list(map(lambda c: list(map(lambda x: int(x),c.split('[')[1].split(']')[0].split(',',-1))),conf[1:][:-1].split(';',-1)))
	#import random
	#return [random.choice(conf_array)]

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()
	return results
