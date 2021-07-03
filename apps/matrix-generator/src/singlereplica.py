from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from functools import reduce

THRESHOLD = 0
DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT = True
#Single Replica
WORKER_ID=3


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
		base=alphabet['base']
		workers=[WorkerConf(worker_id=WORKER_ID-i, cpu=v['size'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
                # HARDCODED => make more generic by putting workers into an array
		workers[0].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
		exps_path=exp_path+'/'+sla['name']
		lst=_sort(workers,base)
		next_exp=_find_next_exp(lst,workers,[],lst[0],base,window,True)
		d[sla['name']]={}
		tenant_nb=1
		retry_attempt=0
		while tenant_nb <= sla['maxTenants']:
			results=[]
			nr_of_experiments=len(next_exp)
			print("Running " + str(nr_of_experiments) + " experiments") 
			for i,ws in enumerate(next_exp):
				samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws,sla['demoCPU'],sla['slos'])
				for res in _generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i+retry_attempt)):
					results.append(res)
			result=find_optimal_result(workers,results)
			for failed_conf in return_failed_confs(workers,results):
				lst.remove(utils.array_to_str(failed_conf))
			if result:
				d[sla['name']][str(tenant_nb)]=result
				tenant_nb+=1
				retry_attempt=0
				next_conf=utils.array_to_str(get_conf(workers, result))
			else:
				print("NO RESULT")
				retry_attempt+=nr_of_experiments
				next_conf=lst[0]
			next_exp=_find_next_exp(lst,workers,result,next_conf,base,window,False)
	print("Saving results into matrix")
	utils.saveToYaml(d,'Results/matrix.yaml')		



def get_conf(workers, result):
	return [result['worker'+str(worker.worker_id)+'Replicas'] for worker in workers]


def return_failed_confs(workers,results):
	if DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT:
		failed_results=[result for result in results if float(result['score']) <= THRESHOLD]
		print("Failed results")
		print(failed_results)
		return [get_conf(workers,failed_result) for failed_result in failed_results]
	else:
		return []


def find_optimal_result(workers,results):
	print("Results")
	print(results)
	filtered_results=[result for result in results if float(result['score']) > THRESHOLD]
	print("Filtered results")
	filtered_results=sort(filtered_results)
	print(filtered_results)
	if filtered_results:
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



def sort(results):
	def score_for_sort(result):
		return  1.0-float(result['score']) 

	return sorted(results,key=score_for_sort)


def _sort(workers,base):
	def cost_for_sort(elem):
		return _resource_cost(workers,elem)

	initial_conf=int(utils.array_to_str([worker.min_replicas for worker in workers]),base)
	#REMARK: Only single replica allows for base higher than 10. This is because int(string,base) does not work properly for base > 10
	if len(workers) == 1:
		print("SINGLE REPLICA CONFIG!")
		max_conf=int(utils.array_to_str([base-1 for worker in workers]))
	else:
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
	return [utils.array_to_str(c) for c in sorted_list]




def _resource_cost(workers, conf):
        cost=0
        for w,c in zip(workers,conf):
            cost+=c*w.cpu
        return cost



def _pairwise_transition_cost(previous_conf,conf):
        cost=0
        for c1,c2 in zip(conf,previous_conf):
               print(c1)
               print(c2)
               if  int(c1) > int(c2):
                       cost+=int(c1)-int(c2)
        return cost


def _find_next_exp(sorted_combinations, workers, results, next_conf, base, window, first_tenant):
	workers_exp=[]
	only_min_conf=False
	min_conf=next_conf
	if not first_tenant:
		print("Processing previous worker results")
		if results:
			only_min_conf=True
	print("min_conf: " + min_conf)
	intervals=_split_exp_intervals(sorted_combinations, min_conf, only_min_conf, window, base)
	print("Next possible experiments for next nb of tenants")
	print(intervals)
	samples=intervals["exp"]["None"]
	nb_of_samples=len(samples)
	worker_min=samples[0]
	worker_max=samples[nb_of_samples-1]
	new_worker=WorkerConf(workers[0].worker_id,workers[0].cpu,int(worker_min),int(worker_max))
	return [[new_worker]]



def _split_exp_intervals(sorted_combinations, min_conf, only_min_conf, window, base):
	min_conf_dec=sorted_combinations.index(min_conf)
        #min_conf_dec=int(min_conf_index,base)
	print("min_conf_dec: " + str(min_conf_dec))
	if only_min_conf:
		max_conf_dec=min_conf_dec+1
	else:
		max_conf_dec=min_conf_dec+window
	combinations=[sorted_combinations[c] for c in range(min_conf_dec,max_conf_dec)]
	for c in range(min_conf_dec,max_conf_dec):
		print(sorted_combinations[c])
	list=[]
	length=len(combinations[0])
	return {"exp": {"None": [sorted_combinations[c] for c in range(min_conf_dec,max_conf_dec)]}, "nbOfshiftsToLeft": 0}


def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path):
	# conf_ex=ConfigParser(
	# 	optimizer='exhaustive',
	# 	chart_dir=chart_dir,
	# 	util_func= util_func,
	# 	samples= samples,
	# 	output= exp_path+'/exh',
	# 	slas=slas)
		
	conf_op=ConfigParser(
		optimizer='mtbestconfig',
		chart_dir=chart_dir,
		util_func= util_func,
		samples= samples,
		output= exp_path+'/op/',
		# prev_results=exp_path+'/exh/results.json',
		slas=slas)

	# exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op/')

	# exp_ex.runExperiment()
	exp_op.runExperiment()

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()

	return results
