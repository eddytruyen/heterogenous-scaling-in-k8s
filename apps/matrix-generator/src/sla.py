class SLAConf:
	def __init__(self, sla_class, tenants, workers,slos):
		self.sla_class = sla_class
		self.tenants = tenants
		self.workers = workers
		self.slos = slos


class WorkerConf:
	def __init__(self, worker_id, resources, weights, min_replicas,max_replicas):
		self.worker_id = worker_id
		self.resources = resources
		self.weights = weights
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas
		self._flag = False
		self._tested = False

	def clone(self):
		w2=WorkerConf(self.worker_id, self.resources.copy(), self.weights.copy(), self.min_replicas, self.max_replicas)
		if self.isFlagged():
			w2.flag()
		if self.isTested():
			w2.tested()
		return w2

	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def scale(self, resource, amount):
		self.resources[resource] = amount

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
		if self.worker_id == other.worker_id and self.min_replicas == other.min_replicas and self.max_replicas == other.max_replicas:
			if len(self.resources) != len(other.resources) or len(self.weights) != len(other.weights):
				return False
			for i in self.resources.keys():
				if not (i in other.resources.keys()) or not (i in other.weights.keys()):
					return False
				if self.resources[i] != other.resources[i]:
					return False
				if self.weights[i] !=  other.weights[i]:
					return False
			return True
		else:
			return False
	def str(self):
		return_str =  "{workerId=" + str(self.worker_id)
		for i in self.resources:
			return_str+= ", " + i + "=" + str(self.resources[i]) 
		return_str+= ", min_replicas=" + str(self.min_replicas) + ", max_replicas" + str(self.max_replicas) + ", flagged=" + str(self.isFlagged()) + ", tested=" + str(self.isTested()) + "}" 
		return return_str
