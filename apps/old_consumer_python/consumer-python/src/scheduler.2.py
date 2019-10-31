import asyncio
import os
import logging
import concurrent.futures
from concurrent.futures import ALL_COMPLETED
from stress import StressCPU
import json
import threading
import sys
import aiohttp

try:
	import Queue as queue
except ImportError:
	# Python 3
	import queue

# Based on:
# http://numberoverzero.com/posts/2017/07/17/periodic-execution-with-asyncio

DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
# STRESS_SIZE = os.getenv('STRESS_SIZE')
STRESS_SIZE = 1

# QUEUE_HOST = "http://demo." + DNS_NAMESPACE + ".svc.cluster.local:80"
QUEUE_HOST= 'http://172.19.42.15:30699'
QUEUE_URL = QUEUE_HOST+'/pull'

class Tasker:
	def __init__(self, loop, session, queue):
		self.loop = loop
		self.session = session
		self.queue = queue

	async def _fetch(self, url):
		async with self.session.get(url) as response:
			status = response.status
			assert status == 200
			data = await response.text()
			return data

	def __del__(self):
		self.session.close()

class Consumer(Tasker):
	async def __call__(self):
		logging.debug("Checking tasks in queue")
		with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
			futures = [
				executor.submit(_compute_new_task, self.queue)
				for i in range(10)
			]
		# if True:	
			# asr=[_compute_new_task(self.queue,self.loop) for i in range(11)]
			# results = await asyncio.gather(*asr,loop=self.loop,return_exceptions=True)
			results=[future.result() for future in futures]
			print(results)
			# done, pending = await asyncio.wait(futures,Loop=self.loop,return_when=ALL_COMPLETED)

			# for d in done:
			# 	print("lsda")
			# req = [self._fetch(QUEUE_URL+'?ack='+str(result)) for result in results]
			# done, pending = await asyncio.wait(
			# 	req,
			# 	loop=self.loop,
			# 	return_when=ALL_COMPLETED
			# 	)



class Scheduler(Tasker):
	async def __call__(self):
		logging.debug("Checking "+ QUEUE_URL+" for new tasks")
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


async def _add_to_queue(item,queue,loop):
	logging.debug("Added new item to the queue with id "+str(item))
	queue.put_nowait(item)
	return(item)
	

# async def periodic_producer(queue):
# 	x=0
# 	while True:
# 		await asyncio.sleep(1)
# 		item = f"periodic producer {x}"
# 		logger.info(f"{item} ")
# 		queue.put_nowait(item)
# 		x+=1

def _compute_new_task(queue):
	item = queue.get()
	if (item != None):
		return item
	# if(STRESS_SIZE):
	# 	stress=StressCPU(int(STRESS_SIZE))
	# else:
	# 	stress=StressCPU()	
	# stress.runTest()
	queue.task_done()
	return item
	# logging.debug("hello")
	# return("item")

# async def consumer(queue):
# 	while True:
# 		item = await queue.get()
# 		logger.info(f"{item}")
# 		queue.task_done()
# 		await asyncio.sleep(1)


async def _constant_pooling(loop,session,queue):
	s = Scheduler(queue=queue,loop=loop,session=session)
	while True:
		# try:
		if True:
			await s()
		# except:
		# 	logging.info("There was an error when executing the loop. Retrying in 10 seconds...")
		# 	await asyncio.sleep(10, loop=loop)
		# 	pass
		# 	# self.loop.close()
		# 	# sys.exit()	
		await asyncio.sleep(1, loop=loop)

async def _compute_task(loop,session,queue):
	c = Consumer(loop,session,queue)
	while True:
		empty_queue = c.queue.empty()
		if(empty_queue):
			logging.info("Waiting for elements in the queue")
			await asyncio.sleep(0.1, loop=loop)
		else:
			await c()
		# await asyncio.sleep(1, loop=loop)

def _init_producer(queue,session,loop):
	logging.debug("Creating producer")
	# loop.set_debug(True)
	producer = loop.create_task(_constant_pooling(queue=queue,loop=loop,session=session))
	loop.run_forever()


def _init_consumer(queue,session,loop):
	asyncio.set_event_loop(loop)
	logging.debug("Creating consumer")
	consumer = loop.create_task(_compute_task(queue=queue,loop=loop,session=session))
	loop.run_forever()

def main():
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger("asyncio").setLevel(logging.DEBUG)

	logging.info("Starting application")

	q = queue.Queue()
	loop = asyncio.get_event_loop()
	session = aiohttp.ClientSession(loop=loop)

	threading.Thread(target=lambda: _init_consumer(q,session,loop)).start()
	threading.Thread(target=lambda: _init_producer(q,session,loop)).start()


if __name__ == '__main__':
	main()