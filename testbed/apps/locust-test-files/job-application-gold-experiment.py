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
    
    @task
    def pushJob(self):
        with self.client.get("/pushJob/10",name="gold", catch_response=True) as resp:
            print(resp)
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class MyUser(HttpUser):
    weight = 1

    host = "http://172.19.133.29:30698" # URL of the job application

    wait_time = between(0,0)  
    
    tasks = [TasksetT1]

    #For graphite!
    #sock = socket.socket()
    #try:
    #    sock.connect(('172.19.133.24', 30689))
    #except (socket.error):
    #    print("Couldnt connect with the socket-server: terminating program...")

    @events.request_success.add_listener
    def hook_request_success(request_type, name, response_time, response_length, **kw):
        print("DONE# type=" + str(request_type) + ", name=" + str(name) \
                            + ", response_time=" + str(response_time) + ", response_length=" + str(response_length))
        # If Grapĥite is used
        # data_latency="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.latency', response_time,  time.time())
        #MyUser.sock.send(data_latency.encode())

    def hook_request_fail(self, request_type, name, response_time, exception):
        self.request_fail_stats.append([name, request_type, response_time, exception])
    
    @events.test_stop.add_listener
    def exit_handler(**kw):
        MyUser.sock.shutdown(socket.SHUT_RDWR)
        MyUser.sock.close()

