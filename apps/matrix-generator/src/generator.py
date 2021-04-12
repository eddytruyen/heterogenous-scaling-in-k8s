from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .searchwindow import ScalingFunction
from functools import reduce

THRESHOLD = -1
DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT = True

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
		workers=[WorkerConf(worker_id=i+1, cpu=v['size']['cpu'], memory=v['size']['memory'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
		# HARDCODED => make more generic by putting workers into an array
		workers[0].setReplicas(min_replicas=0,max_replicas=0)
		workers[1].setReplicas(min_replicas=0,max_replicas=0)
		workers[2].setReplicas(min_replicas=0,max_replicas=0)
		workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
		lst=_sort(workers,base)
		print(lst)
		exps_path=exp_path+'/'+sla['name']
		next_exp=_find_next_exp(lst,workers,[],[],base,window,True)
		d[sla['name']]={}
		tenant_nb=1
		retry_attempt=0
		No_Previous_Result=True
		while tenant_nb <= sla['maxTenants']:
			results=[]
			nr_of_experiments=len(next_exp)
			print("Running " + str(nr_of_experiments) + " experiments") 
			for i,ws in enumerate(next_exp):
				samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws,sla['slos'])
				for res in _generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i+retry_attempt)):
					results.append(res)
			previous_tenant_result={}
			if tenant_nb > 1:
				previous_tenant_result=d[sla['name']][str(tenant_nb-1)]
			result=find_optimal_conf(workers,results,previous_tenant_result)
			if result:
				result_x=result["trans-optimal"]
				d[sla['name']][str(tenant_nb)]=result_x
				tenant_nb+=1
				next_conf=get_conf(workers,result["optimal"])
				retry_attempt=0
				No_Previous_Result=False
			else: 
				print("NO RESULT")
				if No_Previous_Result:
					next_conf=lst[lst.index(utils.array_to_str(find_maximum(workers,next_exp)))+1]
				else:
					No_Previous_Result=True
				retry_attempt+=nr_of_experiments
				result_x={}
			for failed_conf in return_failed_confs(workers,results):
				lst.remove(utils.array_to_str(failed_conf))
			next_exp=_find_next_exp(lst,workers,result_x,next_conf,base,window,False)
	print("Saving results into matrix")
	utils.saveToYaml(d,'Results/matrix.yaml')


def get_conf(workers, result):
	return [result['worker'+str(worker.worker_id)+'.replicaCount'] for worker in workers]


def return_failed_confs(workers,results):
	if DO_NOT_REPEAT_FAILED_CONFS_FOR_NEXT_TENANT:
		failed_results=[result for result in results if float(result['score']) <= THRESHOLD]
		print("Failed results")
		print(failed_results)
		return [get_conf(workers,failed_result) for failed_result in failed_results]
	else:
		return []


def find_optimal_conf(workers,results,previous_result):
	print("Results")
	print(results)
	print("Previous results")
	print(previous_result)
	filtered_results=[result for result in results if float(result['score']) > THRESHOLD]
	print("Filtered results")
	print(filtered_results)
	if filtered_results:
		scores=[float(result['score']) for result in filtered_results]
		max_index=scores.index(max(scores))
		index=-1
		if previous_result:
			previous_conf=[previous_result['worker'+str(worker.worker_id)+'.replicaCount'] for worker in workers]
			transition_costs=[_pairwise_transition_cost(previous_conf,get_conf(workers, result)) for result in filtered_results]
			index=transition_costs.index(min(transition_costs))
		else:
			index=max_index
		return {"trans-optimal": filtered_results[index], "optimal": filtered_results[max_index]}
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


        for sla in slas:
                alphabet=sla['alphabet']
                nodes=[[4,8],[8,32],[8,32],[8,32],[8,16],[8,16],[8,8],[3,6]]
                f=ScalingFunction(172.2835754,-0.4288966,66.9643290,2,2,True,nodes,alphabet)
                slo=sla['slos']['completionTime']
                for i in range(1,10+1,1):
                        print(i)
                        print(f.target(slo,i,4))
                window=alphabet['searchWindow']
                base=alphabet['base']
                workers=[WorkerConf(worker_id=i+1, cpu=v['size']['cpu'], memory=v['size']['memory'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
                # HARDCODED => make more generic by putting workers into an array
                workers[0].setReplicas(min_replicas=0,max_replicas=0)
                workers[1].setReplicas(min_replicas=0,max_replicas=0)
                workers[2].setReplicas(min_replicas=0,max_replicas=0)
                workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
                lst=_sort(workers,base)
                print("=======================================================")
                print(lst)
                next_exp=_find_next_exp(lst,workers,[],[],[],base, window,True)
                for exp in next_exp:
                          for w in exp:
                                print(w.min_replicas, w.max_replicas)
                print(find_previous_maximum(workers,next_exp))



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
	return [utils.array_to_str(c) for c in sorted_list]




def _resource_cost(workers, conf):
        cost=0
        for w,c in zip(workers,conf):
            cost+=c*w.cpu+c*w.memory
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
	min_conf=utils.array_to_str([worker.min_replicas for worker in workers])
	if not first_tenant:
		print("Processing previous worker results")
		if results:
			optimal_conf=get_conf(workers, results)
			print("Optimal conf....")
			print(optimal_conf)
			min_conf=utils.array_to_str(optimal_conf)
			only_min_conf=True
		else:
			min_conf=utils.array_to_str(next_conf)
	print("min_conf: " + min_conf)
	intervals=_split_exp_intervals(sorted_combinations, min_conf, only_min_conf, window, base)
	print("Next possible experiments for next nb of tenants")
	print(intervals)
	for k, v in intervals.items():
		constant_ws_replicas=map(lambda a: int(a),list(k))

		experiment=[]

		for replicas,worker in zip(constant_ws_replicas,workers[:-1]):
			new_worker=WorkerConf(worker.worker_id,worker.cpu,worker.memory,replicas,replicas)
			experiment.append(new_worker)

		new_worker=WorkerConf(workers[-1].worker_id,workers[-1].cpu,workers[-1].memory,min(map(lambda a: int(a),v)),max(map(lambda a: int(a),v)))
		experiment.append(new_worker)

		workers_exp.append(experiment)

	return workers_exp	



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
		print(c)
		print(sorted_combinations[c])
	exp={}

	for c in combinations:
		exp[c[:-1]]=[]

	for c in combinations:
		exp[c[:-1]].append(c[-1])		

	return exp


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


def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path):
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
		slas=slas)

	# exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op/')

	# exp_ex.runExperiment()
	exp_op.runExperiment()

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()

	return results


