import asyncio
import socket
import argparse
import json
import time
import aiohttp
from influxdb import InfluxDBClient
from datetime import datetime

parser = argparse.ArgumentParser(
    description='Locust collector, collects stats from locust, connected to a INFLUXDB',
    usage='"%(prog)s <command> <arg>". Use  "python %(prog)s --help" o "python %(prog)s -h" for more information',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument("-l", "--lhost",    action='store', help="Locust web endpoint")
parser.add_argument("-i", "--dbip",     action='store', help="IP address of the influx-db")
parser.add_argument("-p", "--dbport",   action='store', help="Port of influx-db")
parser.add_argument("-s", "--speed",    action='store', help="Speed at which to collect the metrics (metrics/sec)")
parser.add_argument("-d", "--influxdb", action='store', help="The database in which to store the metrics")

args = parser.parse_args()

LOCUST_HOST = args.lhost
INFLUXDB_HOST = args.dbip
INFLUXDB_PORT = args.dbport
COLLECT_SPEED = args.speed
DATABASE = args.influxdb

class Collector:
    def __init__(self, loop, session):
        self.loop = loop
        self.session = session
        self.sock = socket.socket()
        self.client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, timeout=5)
        self.client.switch_database(DATABASE)

        print("Checking connection to influxdb... wait max 15 seconds")
        try:
            v = self.client.ping()
            print('Succesfully pinged InfluxDB')
        except:
            exit("Problem with connection to Influxdb, check ip and port, aborting")

    def push_current_metrics(self, userCount, rps, medianRespTime):
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        json_body = [{
            "measurement": "responseData",
            "time": time,
            "fields": {
                "userCount": userCount,
                "rps": float(rps),
                "medianRespTime": float(medianRespTime)
            }
        }]
        print('Pushing: uc: ' + str(userCount) + ' rps: ' + str(rps) + ' rt: ' + str(medianRespTime))
        self.client.write_points(json_body)

    def push_metrics_user_count(self, count):
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        json_body = [{
            "measurement": "userCount",
            "time": time,
            "fields": {
                "userCount": count
            }
        }]
        self.client.write_points(json_body)

    def push_metrics_rps(self, rps):
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        json_body = [{
            "measurement": "rps",
            "time": time,
            "fields": {
                "rps": count
            }
        }]
        self.client.write_points(json_body)

    async def fetch(self, url, **kwargs):
        async with self.session.get(url, **kwargs) as response:
            print('Fetching: ' + url + '  reps: ' + str(response.status))
            status = response.status
            assert status == 200
            data = await response.text()
            return data
    
    async def __call__(self):
        resp = await self.fetch(LOCUST_HOST+'/stats/requests')
        user_count = json.loads(resp)['user_count']
        status = json.loads(resp)['state']

        rps = json.loads(resp)['total_rps']
        
        median = json.loads(resp)['current_response_time_percentile_50']

        if median is None:
            median = 0
        if rps is None:
            rps = 0
        if user_count is None:
            user_count = 0

        # Should only push if rps > 0 ??
        self.push_current_metrics(user_count, rps, median)

async def _constant_pooling(loop):
    session = aiohttp.ClientSession(loop=loop)
    a = Collector(loop=loop,session=session)

    while True:
        try:
            await a()
        except Exception as err:
            print('Error in processing')
            print(type(err))
            print(err)
            await asyncio.sleep(5, loop=loop)
        await asyncio.sleep(int(COLLECT_SPEED), loop=loop)

def main():
    loop = asyncio.get_event_loop()

    loop.create_task(_constant_pooling(loop=loop))

    loop.run_forever()

if __name__ == '__main__':
    main()
