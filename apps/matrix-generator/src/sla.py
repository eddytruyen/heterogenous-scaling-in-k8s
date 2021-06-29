class SLAConf:
	def __init__(self, sla_class, tenants, workers,demo_cpu,slos):
		self.sla_class = sla_class
		self.tenants = tenants
		self.workers = workers
		self.demo_cpu = demo_cpu
		self.slos = slos

class WorkerConf:
	def __init__(self, worker_id, cpu, min_replicas,max_replicas):
		self.worker_id = worker_id
		self.cpu = cpu
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

