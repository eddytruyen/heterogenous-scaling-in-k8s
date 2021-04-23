from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .searchwindow import AdaptiveWindow
from functools import reduce

THRESHOLD = -1
#DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT = True
NB_OF_CONSTANT_WORKER_REPLICAS = 1
MAXIMUM_TRANSITION_COST=2

def generate_matrix(initial_conf):
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
		workers=[WorkerConf(worker_id=i+1, cpu=v['size']['cpu'], memory=v['size']['memory'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
		# HARDCODED => make more generic by putting workers into an array
		workers[0].setReplicas(min_replicas=0,max_replicas=0)
		workers[1].setReplicas(min_replicas=0,max_replicas=0)
		workers[2].setReplicas(min_replicas=0,max_replicas=0)
		workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
		lst=_sort(workers,base)
		print([utils.array_to_str(el) for el in lst])
		exps_path=exp_path+'/'+sla['name']
		next_exp=_find_next_exp(lst,workers,[],lst[0],base,window)
		d[sla['name']]={}
		tenant_nb=1
		retry_attempt=0
		while tenant_nb <= sla['maxTenants']:
			results=[]
			nr_of_experiments=len(next_exp)
			print("Running " + str(nr_of_experiments) + " experiments") 
			for i,ws in enumerate(next_exp):
				#samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws[0]])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws[0],sla['slos'])
				for res in _generate_experiment(chart_dir,util_func,[sla_conf],int(ws[4]/2),bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i+retry_attempt),ws[1],ws[2],ws[3]):
					results.append(res)

			previous_tenant_result={}
			if tenant_nb > 1:
				previous_tenant_result=d[sla['name']][str(tenant_nb-1)]
			result=find_optimal_result(workers,results,previous_tenant_result)
			#for failed_conf in return_failed_confs(workers,results):
			#	print(failed_conf)
			#	if failed_conf in lst:
			#		print("Removing failed conf!")
			#		lst.remove(failed_conf)
			optimal_conf=return_cost_optimal_conf(workers,results)
			if optimal_conf:
				print("Optimal Result")
				print(optimal_conf)
				failed_range=lst.index(optimal_conf)
			else:
				failed_range=adaptive_window.get_current_window()
			for i in range(0,failed_range):
				print("Removing failed conf")
				print(lst[0])
				lst.remove(lst[0])
			if _pairwise_transition_cost(get_conf(workers,previous_tenant_result),get_conf(workers,result)) > MAXIMUM_TRANSITION_COST:
				lst.remove(lst[lst.index(get_conf(workers,result))])
			for failed_conf in return_failed_confs(workers,results):
				if failed_conf in lst:
					print("Removing failed conf!")
					print(failed_conf)
					lst.remove(failed_conf)
			if result and (_pairwise_transition_cost(get_conf(workers,previous_tenant_result),get_conf(workers,result)) <= MAXIMUM_TRANSITION_COST):
				d[sla['name']][str(tenant_nb)]=result
				tenant_nb+=1
				retry_attempt=0
				next_conf=get_conf(workers, result)
			else:
				print("NO RESULT")
				result={}
				retry_attempt+=nr_of_experiments
				next_conf=lst[0]
			next_exp=_find_next_exp(lst,workers,result,next_conf,base,adaptive_window.adapt_search_window(result,window,False))
	print("Saving results into matrix")
	utils.saveToYaml(d,'Results/matrix.yaml')


def get_conf(workers, result):
	if result:
		return [int(result['worker'+str(worker.worker_id)+'.replicaCount']) for worker in workers]
	else:
		return []


def return_cost_optimal_conf(workers,results):
        optimal_results=sort([result for result in results if float(result['score']) > THRESHOLD])
        if optimal_results:
    	        return get_conf(workers,optimal_results[0])
        else:
                return []
 


def return_failed_confs(workers,results):
#	if DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT:
	failed_results=[result for result in results if float(result['score']) <= THRESHOLD]
	print("Failed results")
	print(failed_results)
	return [get_conf(workers,failed_result) for failed_result in failed_results]
#	else:
#		return []


def find_optimal_result(workers,results,previous_result):
	print("Results")
	print(results)
	print("Previous result")
	print(previous_result)
	filtered_results=[result for result in results if float(result['score']) > THRESHOLD]
	print("Filtered results")
	filtered_results=sort(filtered_results)
	print(filtered_results)
	if filtered_results:
		index=-1
		if previous_result:
			previous_conf=get_conf(workers,previous_result)
			transition_costs=[_pairwise_transition_cost(previous_conf,get_conf(workers, result)) for result in filtered_results]
			index=transition_costs.index(min(transition_costs))
		else:
			scores=[float(result['score']) for result in filtered_results]
			index=scores.index(max(scores))
		return filtered_results[index]
	else:
		return {}


def find_maximum(workers,experiments):
	configs=[]
	for exp in experiments:
		conf=[c.max_replicas for c in exp]
		configs.append(conf)
	configs.reverse()
	resource_costs=[_resource_cost(workers, c) for c in configs]
	index=resource_costs.index(max(resource_costs))
	return configs[index]


def generate_matrix2(initial_conf):
        bin_path=initial_conf['bin']['path']
        chart_dir=initial_conf['charts']['chartdir']
        exp_path=initial_conf['output']
        util_func=initial_conf['utilFunc']
        slas=initial_conf['slas']
        conf_op=ConfigParser(
                optimizer='bestconfig',
                chart_dir=chart_dir,
                util_func=util_func,
                samples=9,
                output= '/op/',
                # prev_results=exp_path+'/exh/results.json',
                slas=slas,
                maximum_replicas='"1 2 2 1"',
                minimum_replicas='"0 0 0 0"',
                configs=[])
        print(conf_op.iterations)



def sort(results):
	def score_for_sort(result):
		return  -1*float(result['score']) 

	return sorted(results,key=score_for_sort)



def _sort(workers,base):
	def cost_for_sort(elem):
		return _resource_cost(workers,elem)

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




def _resource_cost(workers, conf):
        cost=0
        for w,c in zip(workers,conf):
            cost+=c*w.cpu+c*w.memory
        return cost



def _pairwise_transition_cost(previous_conf,conf):
        if not previous_conf:
               return 0
        cost=0
        for c1,c2 in zip(conf,previous_conf):
               if  c1 > c2:
                       cost+=c1-c2
        return cost




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
			new_worker=WorkerConf(worker.worker_id,worker.cpu,worker.memory,replicas,replicas)
			experiment.append(new_worker)
		for i in reversed(range(0,nb_of_variable_workers)):
			l=i+1
			worker_min=min(map(lambda a: int(a[-l]),v))
			worker_max=max(map(lambda a: int(a[-l]),v))
			new_worker=WorkerConf(tmp_workers[-l].worker_id,tmp_workers[-l].cpu,tmp_workers[-l].memory,worker_min,worker_max)
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


#def _split_exp_intervals_with_metadata(sorted_combinations, include_min_conf, min_conf, window, base):#
	#min_conf_dec=sorted_combinations.index([int(min_conf,base),min_conf,_resource_cost(workers,min_conf))
#	min_conf=sorted_combinations.index(min_conf)
	#min_conf_dec=int(min_conf_index,base)
#	print("min_conf_dec: " + str(min_conf_dec))
#	if not include_min_conf :
		#rollover maximum conf of previous experiments
#		min_conf=utils.array_to_str(utils.number_to_base(min_conf_dec[1],base))
#	max_conf_dec=min_conf_dec[1]+window
#	for c in range(min_conf_dec[1],max_conf_dec):
#		print(c)
#		print(sorted_combinations[c])
#	combinations=[utils.array_to_str(sorted_combinations[c]) for c in range(min_conf_dec[1],max_conf_dec)]
#	for c in comb:
#		while len(c) < len(min_conf):
#			c='0'+c
#		combinations.append(c)	
#	exp={}
#
#	for c in combinations:
#		exp[c[:-1]]=[]
#
#	for c in combinations:
#		exp[c[:-1]].append(c[-1])		
#
#	return exp


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


