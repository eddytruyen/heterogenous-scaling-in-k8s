import logging
import requests
import os
import threading
from stress import StressCPU
import json
import http.client

try:
	import Queue as queue
except ImportError:
	# Python 3
	import queue

DNS_NAMESPACE = os.getenv('DNS_NAMESPACE')
# STRESS_SIZE = os.getenv('STRESS_SIZE')
STRESS_SIZE = 1

QUEUE_HOST= 'http://127.0.0.1:8080'
# QUEUE_HOST = "demo." + DNS_NAMESPACE + ".svc.cluster.local:80"

# print("Establishing connection with queue at: "+QUEUE_HOST)
# conn = http.client.HTTPConnection(QUEUE_HOST,30699)

class TaskQueue():
	def __init__(self):
		self.task_queue = queue.Queue()
		self.threads = []

		threads = []
		for i in range(10):
			t = threading.Thread(target=_worker,  args=[self.task_queue])
			t.start()
			self.threads.append(t)

	def pullTask(self):
		task=_pull_task()
		if(task != None):
			# print("Pulled task with id:"+task)
			self.task_queue.put(task)

	def endQueue(self):
		for i in self.threads:
			self.task_queue.put(None)
		for t in self.threads:
			t.join()	

def _worker(task_queue):
	while True:
		task_id = task_queue.get()
		if task_id is None:
			break
		_complete_task(task_id)
		task_queue.task_done()

def _pull_task():
	r=requests.get(QUEUE_HOST+"/pull")
	response = r.text
	task = json.loads(response)

	return task['id']

def _complete_task(task_id):
	stress=StressCPU(STRESS_SIZE)
	stress.runTest()
	print("Completed task with id:"+task_id)
	_ack_task(task_id)	

def _ack_task(task_id):
	ack_url=QUEUE_HOST+"/pull"
	r=requests.get(ack_url,params={'ack':str(task_id)})
	print(r.text)


