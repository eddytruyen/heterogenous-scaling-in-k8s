import asyncio
import socket
import json
import time
import aiohttp

LOCUST_HOST='http://172.19.140.15:8089'
# LOCUST_HOST='http://localhost:8089'


class Analyzer:
	def __init__(self, loop, session):
		self.loop = loop
		self.session = session
		self.sock = socket.socket()

		try:
			self.sock.connect(('172.19.140.16', 30688))
		except (socket.error):
			print("Couldnt connect with the socket-server: terminating program...")

	def _push_metrics_users(self,count):
		data="%s %s %d\n" % ("performance.gold.users", count, time.time())
		# print("data")	
		self.sock.send(data.encode())

	def _push_metrics_rps(self,rps):
		data="%s %s %d\n" % ("performance.gold.rps", rps, time.time())
		# print("data")	
		self.sock.send(data.encode())

	async def _fetch(self, url, **kwargs):
		async with self.session.get(url,**kwargs) as response:
			status = response.status
			assert status == 200
			data = await response.text()
			return data

	async def __call__(self):
		resp = await self._fetch(LOCUST_HOST+'/stats/requests')
		users=json.loads(resp)['user_count']
		self._push_metrics_users(str(users))

		status = json.loads(resp)['state']
		if(status == "running" and users != 0):
			rps=users=json.loads(resp)['total_rps']
		else:
			rps=0
			data_latency="%s %d %d\n" % ("performance.gold.latency", 0,  time.time())
			self.sock.send(data_latency.encode())
		self._push_metrics_rps(str(rps))
	def __del__(self):
		self.session.close()

async def _constant_pooling(loop):
	session = aiohttp.ClientSession(loop=loop)
	a = Analyzer(loop=loop,session=session)
	while True:
		try:
			await a()
		except:
			await asyncio.sleep(2, loop=loop)
		await asyncio.sleep(1.2, loop=loop)

def main():
	loop = asyncio.get_event_loop()

	loop.create_task(_constant_pooling(loop=loop))
	loop.run_forever()

if __name__ == '__main__':
	main()
