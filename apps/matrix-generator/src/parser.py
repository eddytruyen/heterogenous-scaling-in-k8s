from . import utils

class ConfigParser:
	def __init__(self, optimizer, util_func, slas, chart_dir, samples, output,  maximum_replicas, prev_results=None):
		self.optimizer = optimizer
		self.prev_results = prev_results
		self.util_func = util_func
		self.slas = slas
		self.chart_dir = chart_dir
		self.samples = samples
		self.output = output
		self.maximum_replicas = maximum_replicas


	def parseConfig(self):
		config=	{
			'prev_results': self.prev_results,
			'optimizer': self.optimizer,
			'chart_dir': self.chart_dir,
			'samples': self.samples,
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
						'maximumReplicas': self.maximum_replicas
					},
					'workers': [{
						'id': worker.worker_id,
						'replicas':{
							'min':worker.min_replicas,
							'max':worker.max_replicas
						}
					} for worker in sla.workers]
				} 
				for sla in self.slas]
		}
		return config
