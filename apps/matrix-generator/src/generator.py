from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from functools import reduce

THRESHOLD = -1

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
		dict=_sort(workers,base)
		print(dict)
		exps_path=exp_path+'/'+sla['name']
		next_exp=_find_next_exp(dict,workers,[],base,window)
		d[sla['name']]={}
		tenant_nb=1
		while tenant_nb <= sla['maxTenants']+1:
			results=[]
			for i,ws in enumerate(next_exp):
				samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws,sla['slos'])
				results.append(_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i)))
			result=find_optimal_conf(results)
			if float(result["score"]) > THRESHOLD :
				d[sla['name']][str(tenant_nb)]=result
				tenant_nb+=1
			else : 
				print("NO RESULT")
			next_exp=_find_next_exp(dict,workers,result, base, window)
	utils.saveToYaml(d,'Results/matrix.yaml')

def find_optimal_conf(results):
	scores=[float(result['score']) for result in results]
	index=scores.index(max(scores))
	return results[index]


def generate_matrix2(initial_conf):
        bin_path=initial_conf['bin']['path']
        chart_dir=initial_conf['charts']['chartdir']
        exp_path=initial_conf['output']
        util_func=initial_conf['utilFunc']
        slas=initial_conf['slas']


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
                dict=_sort(workers,base)
                print(dict)
                next_exp=_find_next_exp(dict,workers,[], base, window)
                for exp in next_exp:
                          for w in exp:
                                print(w.min_replicas, w.max_replicas)

def _sort(workers,base):
	def cost_for_sort(elem):
		return _cost(workers,elem)

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



def _cost(workers, conf):
        cost=0
        for w,c in zip(workers,conf):
            cost+=c*w.cpu+c*w.memory
        return cost




def _find_next_exp(sorted_combinations, workers, results, base, window):
	workers_exp=[]
	min_conf=utils.array_to_str([worker.min_replicas for worker in workers])
	include_min_conf=True
	if results:
		print("Processing previous worker results")
		optimal_conf=[results['worker'+str(worker.worker_id)+'.replicaCount'] for worker in workers]
		print("Optimal conf....")
		print(optimal_conf)
		min_conf=utils.array_to_str(optimal_conf)
		include_min_conf=bool(float(results["score"]) > THRESHOLD)
	print("min_conf: " + min_conf)
	intervals=_split_exp_intervals(sorted_combinations,include_min_conf, min_conf, window, base)
	print("The following experiments are scheduled:")
	print(intervals)
	for k, v in intervals.items():
		constant_ws_replicas=map(lambda a: int(a),list(k))

		experiment=[]

		for replicas,worker in zip(constant_ws_replicas,workers[:-1]):
			new_worker=WorkerConf(worker.worker_id,worker.cpu,worker.memory,replicas,replicas)
			experiment.append(new_worker)

		new_worker=WorkerConf(workers[-1].worker_id,workers[-1].cpu,workers[-1].memory,min(map(lambda a: int(a),v)),max(map(lambda a: int(a),v)))
		experiment.append(new_worker)

		# print([w.max_replicas for w in experiment])
		workers_exp.append(experiment)

	return workers_exp	



def _split_exp_intervals(sorted_combinations,include_min_conf, min_conf, window, base):
	min_conf_dec=sorted_combinations.index(min_conf)
	#min_conf_dec=int(min_conf_index,base)
	print("min_conf_dec: " + str(min_conf_dec))
	if not include_min_conf :
		min_conf_dec+=1
		min_conf=utils.array_to_str(utils.number_to_base(min_conf_dec,base))
	max_conf_dec=min_conf_dec+window
	for c in range(min_conf_dec,max_conf_dec):
		print(c)
		print(sorted_combinations[c])
	combinations=[utils.array_to_str(sorted_combinations[c]) for c in range(min_conf_dec,max_conf_dec)]
#	for c in comb:
#		while len(c) < len(min_conf):
#			c='0'+c
#		combinations.append(c)	
	exp={}

	for c in combinations:
		exp[c[:-1]]=[]

	for c in combinations:
		exp[c[:-1]].append(c[-1])		

	return exp


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
