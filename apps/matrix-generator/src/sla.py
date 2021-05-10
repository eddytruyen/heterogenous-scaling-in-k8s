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
		self._flag = False
		self._tested = False

	def clone(self):
		w2=WorkerConf(self.worker_id, self.cpu, self.memory, self.min_replicas, self.max_replicas)
		if self.isFlagged():
			w2.flag()
		if self.isTested():
			w2.tested()
		return w2

	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def scale(self, cpu, memory):
		self.cpu = cpu
		self.memory = memory

	def isTested(self):
		return self._tested

	def tested(self):
		self._tested=True

	def untest(self):
		self._tested=False

	def isFlagged(self):
		return self._flag

	def flag(self):
		self._flag = True

	def unflag(self):
		self._flag = False

	def equals(self, other):
		if self.worker_id == other.worker_id and self.cpu == other.cpu and self.memory == other.memory and self.min_replicas == other.min_replicas and self.max_replicas == other.max_replicas:
			return True
		else:
			return False
