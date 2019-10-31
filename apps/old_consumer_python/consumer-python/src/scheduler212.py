import asyncio
import os
import logging
import concurrent.futures
from concurrent.futures import ALL_COMPLETED
from stress import StressCPU
import json
import sys
import aiohttp

# Based on:
# http://numberoverzero.com/posts/2017/07/17/periodic-execution-with-asyncio

DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
# STRESS_SIZE = os.getenv('STRESS_SIZE')
STRESS_SIZE = 1

# QUEUE_HOST = "http://demo." + DNS_NAMESPACE + ".svc.cluster.local:80"
QUEUE_HOST= 'http://172.19.42.15:30699'
QUEUE_URL = QUEUE_HOST+'/pull'

loop = asyncio.get_event_loop()


class Scheduler:
	def __init__(self, loop):
		self.loop = loop
		self.session = aiohttp.ClientSession(loop=loop)

	async def _fetch(self, url):
		async with self.session.get(url) as response:
			status = response.status
			assert status == 200
			data = await response.text()
			return data

	async def __call__(self):
		logging.info("Checking "+ QUEUE_URL+" for new tasks")
		tasks = [self._fetch(QUEUE_URL) for i in range(101)]
		done, pending = await asyncio.wait(
			tasks,
			loop=self.loop,
			return_when=ALL_COMPLETED
		)

		tasks_compute=[ 
			_compute_task(json.loads(task.result())['id'],self) 
			for task in done 
			if json.loads(task.result())['id'] != None 
			]

		if (tasks_compute):
			logging.info("Computing new tasks")
			completed_task , _ = await asyncio.wait(
				tasks_compute,
				loop=self.loop,
				return_when=ALL_COMPLETED
			)
			for t in completed_task:
				logging.info("Completed task")
	
	def __del__(self):
		self.session.close()

async def constant_pooling():
	while True:
		try:
			await queue_pooling()
		except:
			logging.info("There was an error when executing the loop. Retrying in 10 seconds...")
			await asyncio.sleep(1, loop=loop)
			pass
			# self.loop.close()
			# sys.exit()	

		# await asyncio.sleep(1, loop=loop)

queue_pooling=Scheduler(loop=loop)

async def _compute_task(task_id,scheduler):
	if(STRESS_SIZE):
		stress=StressCPU(int(STRESS_SIZE))
	else:
		stress=StressCPU()	
	stress.runTest()
	await scheduler._fetch(QUEUE_URL+'?ack='+str(task_id))

def main():
	logging.basicConfig(level=logging.DEBUG)
	logging.info("Starting application")
	task = loop.create_task(constant_pooling())
	loop.run_forever()

if __name__ == '__main__':
	main()