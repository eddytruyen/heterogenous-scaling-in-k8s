import asyncio
import socket
import time
from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

class ReplicaCount:
	def __init__(self, loop):
		self.loop = loop
		self.kube = client.AppsV1Api()
		self.sock = socket.socket()

		try:
			self.sock.connect(('172.19.42.20', 30688))
		except (socket.error):
			print("Couldnt connect with the socket-server: terminating program...")

	def _push_metrics(self,namespace,deployment,count):
		data="%s %s %d\n" % ("system."+str(namespace)+"."+str(deployment), str(count), time.time())
		# print("data")	
		self.sock.send(data.encode())

	async def __call__(self):
		namespaces=['gold','bronze']
		for namespace in namespaces:
			ret = self.kube.list_namespaced_deployment(namespace)
			for i in ret.items:
				name= i.metadata.name
				replicas= i.status.available_replicas
				self._push_metrics(namespace,name,replicas)

async def _constant_pooling(loop):
	a = ReplicaCount(loop=loop)
	while True:
		try:
			await a()
		except:
			await asyncio.sleep(2, loop=loop)
		await asyncio.sleep(8, loop=loop)

def main():
	loop = asyncio.get_event_loop()

	loop.create_task(_constant_pooling(loop=loop))
	loop.run_forever()

if __name__ == '__main__':
	main()