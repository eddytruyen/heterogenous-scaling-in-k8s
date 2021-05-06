class SLAConf:
	def __init__(self, sla_class, tenants, workers,slos):
		self.sla_class = sla_class
		self.tenants = tenants
		self.workers = workers
		self.slos = slos


class WorkerConf:
	def __init__(self, worker_id, cpu, memory, min_replicas,max_replicas):
		self.worker_id = worker_id
		self.cpu = cpu
		self.memory = memory
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas
		self.flag = False

	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def scale(self, cpu, memory):
		self.cpu = cpu
		self.memory = memory

	def isFlagged(self):
		return self.flag

	def flag(self):
		self.flag = True

	def unflag(self):
		self.flag = False

	def equals(self, other):
		if self.worker_id == other.worker_id and self.cpu == other.cpu and self.memory == other.memory and self.min_replicas == other.min_replicas and self.max_replicas == other.max_replicas:
			return True
		else:
			return False
