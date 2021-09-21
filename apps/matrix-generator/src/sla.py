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
		self._flag = False

	def clone(self, copy_flag=True):
                w2=WorkerConf(self.worker_id, self.resources.copy(), self.costs.copy(), self.min_replicas, self.max_replicas)
                if copy_flag and self.isFlagged():
                        w2.flag()
                return w2



	def setReplicas(self, min_replicas, max_replicas):
		self.min_replicas = min_replicas
		self.max_replicas = max_replicas

	def scale(self, resource, amount):
		self.resources[resource] = amount

	def isFlagged(self):
		return self._flag

	def flag(self):
		self._flag = True

	def unflag(self):
		self._flag = False

	def equals(self, other):
		if self.worker_id == other.worker_id and self.min_replicas == other.min_replicas and self.max_replicas == other.max_replicas:
			if len(self.resources) != len(other.resources) or len(self.costs) != len(other.costs):
				return False
			for i in self.resources.keys():
				if not (i in other.resources.keys()) or not (i in other.costs.keys()):
					return False
				if self.resources[i] != other.resources[i]:
					return False
				if self.costs[i] !=  other.costs[i]:
					return False
			return True
		else:
			return False

	def str(self):
                return_str =  "{workerId=" + str(self.worker_id) + ", resources: {"
                for i in self.resources.keys():
                        return_str+=i + ": { size: " + str(self.resources[i]) + ", cost: " + str(self.costs[i]) + "}, "
                return_str=return_str[:-2]
                return_str+= "}, min_replicas=" + str(self.min_replicas) + ", max_replicas" + str(self.max_replicas) + ", flagged=" + str(self.isFlagged())  + "}"
                return return_str
