from locust import HttpUser, TaskSet, task, between, events, web
import time
import socket
import atexit

class TasksetT1(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]

    def on_start(self):
        self.client.get("/login")
        
    def on_stop(self):
        self.client.get("/logout")
    

    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/1",name="silver", catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class MyUser(HttpUser):
    weight = 1
  
    # host = "http://demo.gold.svc.cluster.local:80
    host = "http://172.22.8.106:30698"

    wait_time = between(0,0)  
    
    #task_set = TasksetT1
    tasks = [TasksetT1]

    sock = socket.socket()
    try:
        sock.connect(('172.22.8.106', 30689))
    except (socket.error):
        print("Couldnt connect with the socket-server: terminating program...")

#    def __init__(self, parent):
#        super().__init__(parent)
#        self.sock = socket.socket()
#        try:
#            self.sock.connect(('172.17.13.119', 30689))
#        except (socket.error):
#            print("Couldnt connect with the socket-server: terminating program...")
        #events = self.environment.events
        #events.request_success += self.hook_request_success
        #events.request_failure += self.atexit.register(self.exit_handler)
    @events.request_success.add_listener
    def hook_request_success(request_type, name, response_time, response_length, **kw):
        data_latency="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.latency', response_time,  time.time())
        # data_request="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.requests', 1,  time.time())
        MyUser.sock.send(data_latency.encode())
        # self.sock.send(data_request.encode())

    def hook_request_fail(self, request_type, name, response_time, exception):
        self.request_fail_stats.append([name, request_type, response_time, exception])
    
    @events.test_stop.add_listener
    def exit_handler(**kw):
        MyUser.sock.shutdown(socket.SHUT_RDWR)
        MyUser.sock.close()

