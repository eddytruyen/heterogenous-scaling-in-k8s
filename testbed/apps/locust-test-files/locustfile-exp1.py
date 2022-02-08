from locust import HttpUser, TaskSet, task, between, events, web
import time
import socket
import atexit
from influxdb import InfluxDBClient
from datetime import datetime

DEBUG = True
APPLICATION_HOST = "http://172.19.133.29:30698"
INFLUXDB_HOST = '172.19.133.29'
INFLUXDB_PORT = 30421
DATABASE = "gold-app-data"

class TasksetT1(TaskSet):
    def on_start(self):
        self.client.get("/login")
        
    def on_stop(self):
        self.client.get("/logout")

    @task
    def pushJob(self):
        with self.client.get("/pushJob/10",name="gold", catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class MyUser(HttpUser):
    weight = 1
    host = APPLICATION_HOST
    wait_time = between(0,0)  
    tasks = [TasksetT1]
    sock = socket.socket() # -> graphite

    idb = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, timeout=5)
    idb.switch_database(DATABASE)

    if DEBUG:
        print("Checking connection to influxdb... wait max 15 seconds")
    try:
        v = idb.ping()
        if DEBUG:
            print('Succesfully pinged InfluxDB')
    except:
        exit("Problem with connection to Influxdb, check ip and port, aborting")

    @events.request_success.add_listener
    def hook_request_success(request_type, name, response_time, response_length, **kw):
        ti = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        if DEBUG:
            print(str(ti) + " - reqType: " + str(request_type) + ", name: " + str(name) + ", respTime: " + str(response_time) + ", respLength: " + str(response_length))
        if str(name) == 'gold':
            ti = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            json_body = [{
                "measurement": "response_time",
                "time": ti,
                "fields": {
                    "response_time": float(response_time)
                }
            }]
            MyUser.idb.write_points(json_body)

    def hook_request_fail(self, request_type, name, response_time, exception):
        if DEBUG:
            print(str(time.time()) + " - FAILED - reqType: " + str(request_type) + ", name: " + str(name) + ", respTime: " + str(response_time) + ", EXCEPTION: " + str(exception))
        self.request_fail_stats.append([name, request_type, response_time, exception])
    
    @events.test_stop.add_listener
    def exit_handler(**kw):
        MyUser.idb.close()
