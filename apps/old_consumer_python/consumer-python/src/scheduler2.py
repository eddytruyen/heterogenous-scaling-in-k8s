import asyncio
import os
import functools
import logging
import concurrent.futures
from concurrent.futures import ALL_COMPLETED
from stress import StressCPU
import json
import requests
import aiohttp


DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
# STRESS_SIZE = os.getenv('STRESS_SIZE')
STRESS_SIZE = 1

QUEUE_HOST= 'http://127.0.0.1:8080'
QUEUE_URL = QUEUE_HOST+'/pull'
# QUEUE_HOST = "demo." + DNS_NAMESPACE + ".svc.cluster.local:80"

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
		tasks = [self._fetch(QUEUE_URL) for i in range(11)]
		done, pending = await asyncio.wait(
			tasks,
			loop=self.loop,
			return_when=ALL_COMPLETED
		)

		tasks_aux=[ _compute_task(json.loads(task.result())['id'],self) for task in done if json.loads(task.result())['id'] != None ]

		if (tasks_aux):
			
			print(tasks_aux)

			doness, _ = await asyncio.wait(
				tasks_aux,
				loop=self.loop,
				return_when=ALL_COMPLETED
			)

			for d in doness:
				print("dasdasdasd")

		# for task in done:
		# 	data = task.result()
		# 	task_id = json.loads(data)['id']
		# 	if(task_id != None):
		# 		print("lasdadddd")
				# f = await 
				# await loop.run_in_executor(None,stress.runTest)
				# f = await loop.run_in_executor(None, functools.partial(self._fetch, QUEUE_URL+'ack?='+str(task_id)))
					# future = loop.run_in_executor(None,lambda : print(QUEUE_URL))
				# response = await f

		# TODO placeholder

		# with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
		# 	loop = self.loop
		# 	futures = [
		# 		loop.run_in_executor(
		# 			executor, 
		# 			self._fetch, 
		# 			QUEUE_URL
		# 		)
		# 		for i in range(10)
		# 	]
		# 	for response in await asyncio.wait(*futures):
		# 		task_id = json.loads(response.text)['id']
		# 		if(task_id != None):
		# 			await loop.run_in_executor(None,stress.runTest)
		# 			f= loop.run_in_executor(executor, functools.partial(requests.get, QUEUE_URL, params={'ack':str(task_id)}))
		# 			# future = loop.run_in_executor(None,lambda : print(QUEUE_URL))
		# 			response = await f
	
	def __del__(self):
		self.session.close()


# async def queue_pooling():
# 	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
# 		loop = asyncio.get_running_loop()
# 		futures = [
# 			loop.run_in_executor(
# 				executor, 
# 				requests.get, 
# 				QUEUE_URL
# 			)
# 			for i in range(10)
# 		]
# 		for response in await asyncio.gather(*futures):
# 			task_id = json.loads(response.text)['id']
# 			if(task_id != None):
# 				stress=StressCPU(STRESS_SIZE)
# 				await loop.run_in_executor(None,stress.runTest)
# 				f= loop.run_in_executor(executor, functools.partial(requests.get, QUEUE_URL, params={'ack':str(task_id)}))
# 				# future = loop.run_in_executor(None,lambda : print(QUEUE_URL))
# 				response = await f

async def constant_pooling():
	while True:
		await queue_pooling()
		await asyncio.sleep(2, loop=loop)

queue_pooling=Scheduler(loop=loop)

async def _compute_task(task_id,scheduler):
	stress=StressCPU(STRESS_SIZE)
	stress.runTest()
	await scheduler._fetch(QUEUE_URL+'?ack='+str(task_id))
	# resp = loop.run_in_executor(None, functools.partial(scheduler._fetch, QUEUE_URL+'?ack='+str(task_id)))
	# future = loop.run_in_executor(None,lambda : print(QUEUE_URL))
# loop = asyncio.get_running_loop()


# logging.basicConfig(level=logging.DEBUG)
task = loop.create_task(constant_pooling())
loop.run_forever()

