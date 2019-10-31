import asyncio
import os
import logging
from concurrent.futures import ALL_COMPLETED
from stress import StressCPU
import json
import sys
import aiohttp

# DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
# STRESS_SIZE = os.getenv('STRESS_SIZE')
STRESS_SIZE = 1

# QUEUE_HOST = "http://demo." + DNS_NAMESPACE + ".svc.cluster.local:80"
QUEUE_HOST= 'http://127.0.0.1:8080'
QUEUE_URL = QUEUE_HOST+'/pull'

class Tasker:
	def __init__(self, loop, session, queue):
		self.loop = loop
		self.session = session
		self.queue = queue

	async def _fetch(self, url, **kwargs):
		# logging.debug("Calling "+url)
		async with self.session.get(url,**kwargs) as response:
			status = response.status
			assert status == 200
			data = await response.text()
			return data

	def __del__(self):
		self.session.close()

class Consumer(Tasker):
	async def __call__(self):
		logging.debug("Checking tasks in queue")
		tasks_computed=[_compute_new_task(self.queue,self.loop) for i in range(self.queue.qsize())]
		done, pending = await asyncio.wait(tasks_computed,loop=self.loop,return_when=ALL_COMPLETED)
		
		completed_tasks=[completed.result() for completed in done]
		pending_acks=[
			self.loop.create_task(self._fetch(QUEUE_URL,params={'ack':str(id)} )) 
			for id 
			in completed_tasks]

		# done, pending = await asyncio.wait(
		# 	pending_acks,
		# 	loop=self.loop,
		# 	return_when=ALL_COMPLETED
		# )

		# acks=[d.result() for d in done]
		# logging.info("Tasks ackd: "+str(len(acks)))

class Scheduler(Tasker):
	async def __call__(self):
		logging.info("Checking "+ QUEUE_URL+" for new tasks")
		tasks = [self._fetch(QUEUE_URL) for i in range(101)]
		done, pending = await asyncio.wait(
			tasks,
			loop=self.loop,
			return_when=ALL_COMPLETED
		)
		tasks_compute=[ 
			await _add_to_queue(json.loads(task.result())['id'],self.queue,self.loop) 
			for task in done 
			if json.loads(task.result())['id'] != None 
			]


def _add_to_queue(item,queue,loop):
	logging.info("Added new item to the queue with id "+str(item))
	queue.put_nowait(item)
	return(item)
	
async def _compute_new_task(queue,loop):
	item = await queue.get()
	if (item != None):
		if(STRESS_SIZE):
			stress=StressCPU(stress_size=int(STRESS_SIZE))
		else:
			stress=StressCPU()	
		stress.runTest()
		queue.task_done()
		return item
	return

async def _constant_pooling(loop,session,queue):
	s = Scheduler(queue=queue,loop=loop,session=session)
	while True:
		try:
			await s()
		except:
			logging.info("There was an error when executing the loop. Retrying in 2 seconds...")
			await asyncio.sleep(1, loop=loop)
			pass
			# self.loop.close()
			# sys.exit()	
		await asyncio.sleep(1, loop=loop)

async def _compute_task(loop,session,queue):
	c = Consumer(loop,session,queue)
	while True:
		empty_queue = c.queue.empty()
		if(empty_queue):
			logging.info("Waiting for elements in the queue")
			# await asyncio.sleep(0.1, loop=loop)
		else:
			await c()
		# await asyncio.sleep(1, loop=loop)

def _init_producer(queue,session,loop):
	logging.info("Creating producer")
	producer = loop.create_task(_constant_pooling(queue=queue,loop=loop,session=session))


def _init_consumer(queue,session,loop):
	logging.info("Creating consumer")
	consumer = loop.create_task(_compute_task(queue=queue,loop=loop,session=session))

def main():
	logging.basicConfig(level=logging.INFO)
	logging.getLogger("asyncio").setLevel(logging.DEBUG)

	logging.info("Starting application")
	# loop.set_debug(True)

	queue = asyncio.Queue()
	loop = asyncio.get_event_loop()
	session = aiohttp.ClientSession(loop=loop)

	_init_producer(queue=queue,loop=loop,session=session)
	_init_consumer(queue=queue,loop=loop,session=session)

	loop.run_forever()


if __name__ == '__main__':
	main()