import asyncio
import os
import logging
from stress import StressCPU
import json
import sys
import time
import urllib.request
import aiohttp
import concurrent.futures

DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
POOL_SIZE = os.getenv('POOL_SIZE') or 100
STRESS_SIZE = os.getenv('STRESS_SIZE') or 100


QUEUE_HOST = "http://demo." + DNS_NAMESPACE + ".svc.cluster.local:80"
# QUEUE_HOST= 'http://127.0.0.1:8080'
QUEUE_URL = QUEUE_HOST+'/pull'

class Tasker:
	def __init__(self, loop, session, queue):
		self.loop = loop
		self.session = session
		self.queue = queue

	async def _fetch(self, url, **kwargs):
		logging.debug("Calling "+url)
		async with self.session.get(url,**kwargs) as response:
			status = response.status
			assert status == 200
			data = await response.text()
			return data

	def __del__(self):
		self.session.close()

async def _worker(consumer):
	while True:
		# Get a "work item" out of the queue.
		item = await consumer.queue.get()
		logging.debug("Processing item with id: "+str(item))
		if (item != None):
			if(STRESS_SIZE):
				stress=StressCPU(stress_size=int(STRESS_SIZE))
			else:
				stress=StressCPU()	
			# stress.runTest()
			await consumer.loop.run_in_executor(None, stress.runTest)
			logging.debug("Processed item with id: "+str(item))
			# await consumer.loop.create_task(consumer._fetch(QUEUE_URL,params={'ack':str(item)} ))
			consumer.queue.task_done()

			ack = consumer._fetch(QUEUE_URL,params={'ack':str(item)} )
			resp = await ack
			id=json.loads(resp)['id']
			if(id):
				await _add_to_queue(id,consumer.queue)
		else:
			break	

class Consumer(Tasker):
	async def __call__(self):
		logging.debug("Checking tasks in queue")
		# tasks_computed=[self.loop.create_task(_compute_new_task(self.queue)) for i in range(self.queue.qsize())]
		# ProcessPoolExecutor, otherwise won't use multiple cores
		# executor = concurrent.futures.ProcessPoolExecutor()
		tasks_computed=[self.loop.create_task(_worker(self)) for i in range(int(POOL_SIZE)+1)]
		await self.queue.join()
		# completed_tasks=[await res for res in tasks_computed]
		# pending_acks=[
		# 	self.loop.create_task(self._fetch(QUEUE_URL,params={'ack':str(id)} )) 
		# 	for id 
		# 	in completed_tasks]


class Scheduler(Tasker):
	async def __call__(self):
		logging.debug("Checking "+ QUEUE_URL+" for new tasks")
		tasks = [self.loop.create_task(self._fetch(QUEUE_URL)) for i in range(int(POOL_SIZE)+1)]

		for t in tasks:
			resp = await t
			id=json.loads(resp)['id']
			if(id):
				await _add_to_queue(id,self.queue)
		await asyncio.sleep(0.5, loop=self.loop)

async def _add_to_queue(item,queue):
	logging.debug("Added new item to the queue with id "+str(item))
	await queue.put(item)
	return(item)
	
async def _constant_pooling(loop,session,queue):
	s = Scheduler(queue=queue,loop=loop,session=session)
	c = Consumer(loop,session,queue)

	while True:
		try:
			await s()
			await c()
		except:
			logging.info("There was an error when executing the loop. Retrying in 2 seconds...")
			await asyncio.sleep(1, loop=loop)
			pass
			# self.loop.close()
			# sys.exit()	

def _init_producer(queue,session,loop):
	logging.info("Creating producer")
	producer = loop.create_task(_constant_pooling(queue=queue,loop=loop,session=session))

def _connection_check(url):
	logging.info("Checking connection with "+url)
	status = 0
	while not(status == 200):
		try:
			# con = urllib.request.urlopen(url)
			with urllib.request.urlopen(url,timeout=1) as resp:
				status = resp.getcode()
		except:
			logging.info("Can't connect to "+url+". Retrying in 1s")
			time.sleep(1)
			pass

	logging.info("Connection with "+url+" established...")
	

def main():
	logging.basicConfig(level=logging.DEBUG)
	# logging.getLogger("asyncio").setLevel(logging.DEBUG)

	logging.info("Starting application")
	# loop.set_debug(True)

	queue = asyncio.Queue()
	loop = asyncio.get_event_loop()
	session = aiohttp.ClientSession(loop=loop)

	_connection_check(QUEUE_HOST+"/status")

	loop.create_task(_constant_pooling(queue=queue,loop=loop,session=session))

	loop.run_forever()

if __name__ == '__main__':
	main()