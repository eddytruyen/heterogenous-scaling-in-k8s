from . import utils

class ConfigParser:
	def __init__(self, optimizer, util_func, slas, chart_dir, samples, sampling_rate, output,  configs, minimum_replicas, maximum_replicas, previous_result=None, previous_replicas=None, prev_results=None):
		self.optimizer = optimizer
		self.prev_results = prev_results
		self.util_func = util_func
		self.slas = slas
		self.chart_dir = chart_dir
		if sampling_rate == 1.0:
			self.samples=samples
			self.iterations=1
		elif samples%2 == 0:
			self.samples=2
			self.iterations=int(samples/2)
		elif samples%3 == 0:
			self.samples=3
			self.iterations=int(samples/3)
		else:
			self.samples=samples
			self.iterations=1
		self.output = output
		self.maximum_replicas = maximum_replicas
		self.minimum_replicas = minimum_replicas
		self.configs = configs
		self.previous_result=previous_result
		self.previous_replicas=previous_replicas


	def parseConfig(self):
		config=	{
			'prev_results': self.prev_results,
			'optimizer': self.optimizer,
			'chart_dir': self.chart_dir,
			'samples': self.samples,
                        'iterations': self.iterations,
			'util_func': self.util_func,
			'output': self.output,
			'slas': [
				{
					'tenants': sla.tenants,
					'class': sla.sla_class,
					'slos': {
						'workload': sla.slos['workload'],
						'benchPath': sla.slos['benchPath'],
                                                'tenantGroup': sla.slos['tenantGroup'],
                                                'completionTime': sla.slos['completionTime'],
						'maximumReplicas': self.maximum_replicas,
						'minimumReplicas': self.minimum_replicas,
						'previousResult': self.previous_result,
 						'previousReplicas': self.previous_replicas,
						'configs': self.configs
					},
					'workers': [{
						'id': worker.worker_id,
						'replicas':{
							'min':worker.min_replicas,
							'max':worker.max_replicas
						},
						'resources': worker.resources,
						'costs': worker.costs
					} for worker in sla.workers]
				} 
				for sla in self.slas]
		}
		return config
