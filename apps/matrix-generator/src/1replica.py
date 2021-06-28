from . import utils
from .parser import ConfigParser
from .experiment import SLAConfigExperiment
from .analyzer import ExperimentAnalizer
from .sla import SLAConf,WorkerConf
from .functools import reduce

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
		workers=[WorkerConf(worker_id=i+1,cpu=v['size'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
                workers[0].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas) 
		exps_path=exp_path+'/'+sla['name']
		next_exp=[workers]
		d[sla['name']]={}
		
		for tenant_nb in range(1,sla['maxTenants']+1):
			results=[]
			for i,ws in enumerate(next_exp):
				samples=reduce(lambda a, b: a * b, [worker.max_replicas-worker.min_replicas+1 for worker in ws])
				sla_conf=SLAConf(sla['name'],tenant_nb,ws,sla['demoCPU'],sla['slos'])
				results.append(_generate_experiment(chart_dir,util_func,[sla_conf],samples,bin_path,exps_path+'/'+str(tenant_nb)+'_tenants-ex'+str(i)))
			result=find_optimal_conf(results)
			d[sla['name']][str(tenant_nb)]=result
			next_exp=_find_next_exp(workers,result, base, window)
	utils.saveToYaml(d,'Results/matrix.yaml')		

def find_optimal_conf(results):
	scores=[result['score'] for result in results]
	index=scores.index(max(scores))

	return results[index]

def _find_next_exp(workers, results, base, window):
	workers_exp=[]
	
	optimal_conf=[results['worker'+str(worker.worker_id)+'Replicas'] for worker in workers]
	
	min_conf=utils.array_to_str(optimal_conf)
	
	intervals=_split_exp_intervals(min_conf, window, base)

	for k, v in intervals.items():
		constant_ws_replicas=map(lambda a: int(a),list(k))

		experiment=[]

		for replicas,worker in zip(constant_ws_replicas,workers[:-1]):
			new_worker=WorkerConf(worker.worker_id,worker.cpu,replicas,replicas)
			experiment.append(new_worker)

		new_worker=WorkerConf(workers[-1].worker_id,workers[-1].cpu,min(map(lambda a: int(a),v)),max(map(lambda a: int(a),v)))
		experiment.append(new_worker)

		print([w.max_replicas for w in experiment])
		workers_exp.append(experiment)

	return workers_exp	



def _split_exp_intervals(min_conf, window, base):
	min_conf_dec=int(min_conf,base)	
	max_conf_dec=min_conf_dec+window

	combinations=[utils.array_to_str(utils.number_to_base(combination,base)) for combination in range(min_conf_dec,max_conf_dec+1)]

	exp={}

	for c in combinations:
		exp[c[:-1]]=[]

	for c in combinations:
		exp[c[:-1]].append(c[-1])		

	return exp


def _generate_experiment(chart_dir, util_func, slas, samples, bin_path, exp_path):
	conf_ex=ConfigParser(
		optimizer='exhaustive',
		chart_dir=chart_dir,
		util_func= util_func,
		samples= samples,
		output= exp_path+'/exh',
		slas=slas)
		
	conf_op=ConfigParser(
		optimizer='exhaustive',
		chart_dir=chart_dir,
		util_func= util_func,
		samples= samples,
		output= exp_path+'/op',
		prev_results=exp_path+'/exh',
		slas=slas)

	exp_ex=SLAConfigExperiment(conf_ex,bin_path,exp_path+'/exh')
	exp_op=SLAConfigExperiment(conf_op,bin_path,exp_path+'/op')

	exp_ex.runExperiment()
	exp_op.runExperiment()

	results=ExperimentAnalizer(exp_path+'/op').analyzeExperiment()

	return results

