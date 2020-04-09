from locust import HttpLocust, TaskSet, task, events, web
from locust.wait_time import between
import locust.events
import time
import socket
import atexit

class TasksetT1(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]

    def on_start(self):
        self.sock = socket.socket()
        self.client.get("/login")
        try:
            self.sock.connect(('172.17.13.106', 30688))
        except (socket.error):
            print("Couldnt connect with the socket-server: terminating program...")
        
    def on_stop(self):
        self.client.get("/logout")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    

    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/10",name="gold", catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class MyLocust(HttpLocust):
    weight = 1
  
    # host = "http://demo.gold.svc.cluster.local:80
    host = "http://172.17.13.106:30698"

    wait_time = between(0,0)  
    
    task_set = TasksetT1

    def __init__(self):
        super(MyLocust, self).__init__()
        self.sock = socket.socket()
        try:
            self.sock.connect(('172.17.13.106', 30689))
        except (socket.error):
            print("Couldnt connect with the socket-server: terminating program...")
        
        locust.events.request_success += self.hook_request_success
        # locust.events.request_failure += self.atexit.register(self.exit_handler)

    def hook_request_success(self, request_type, name, response_time, response_length):
        data_latency="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.latency', response_time,  time.time())
        # data_request="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.requests', 1,  time.time())
        self.sock.send(data_latency.encode())
        # self.sock.send(data_request.encode())

    def hook_request_fail(self, request_type, name, response_time, exception):
        self.request_fail_stats.append([name, request_type, response_time, exception])

    def exit_handler(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

