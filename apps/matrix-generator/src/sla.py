class SLAConf:
	def __init__(self, sla_class, tenants, workers,slos):
		self.sla_class = sla_class
		self.tenants = tenants
		self.workers = workers
		self.slos = slos


class WorkerConf:
	def __init__(self, worker_id, resources, costs, min_replicas,max_replicas):
		self.worker_id = worker_id
		self.resources = resources
		self.costs = costs
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas
