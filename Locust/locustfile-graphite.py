from locust import HttpLocust, TaskSet, task, events, web
import locust.events
import time
import uuid
import socket
import atexit

class TasksetT1(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]

    def on_start(self):
        self.locust_id=self.locust.id_user
        self.sock = socket.socket()
        self.client.get("/login")
        try:
            self.sock.connect(('172.19.42.20', 30688))
        except (socket.error):
            print("Couldnt connect with the socket-server: terminating program...")
        
    def on_stop(self):
        self.client.get("/logout")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.locust.exit_handler()
    

    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        data_request="%s %d %d\n" % ("performance.gold.requests", 1,  time.time())
        self.sock.send(data_request.encode())        
        with self.client.get("/pushJob/10",name=str(self.locust_id), catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class MyLocust(HttpLocust):
    weight = 1
  
    # host = "http://demo.gold.svc.cluster.local:80
    host = "http://172.19.42.20:30698"

    min_wait = 0
    max_wait = 0
    task_set = TasksetT1

    def __init__(self):
        super(MyLocust, self).__init__()
        self.sock = socket.socket()
        self.id_user=uuid.uuid4()
        self.filepath_req='Results/report-'+str(self.id_user)+'.csv' 
        self.filepath_th='Results/th-'+str(self.id_user)+'.txt' 
        self.start_time=time.time()
        self.req_num=0

        try:
            self.sock.connect(('172.19.42.20', 30688))
        except (socket.error):
            print("Couldnt connect with the socket-server: terminating program...")
        
        locust.events.request_success += self.hook_request_success
        locust.events.request_success += self.hook_save_requests
        locust.events.request_failure += self.hook_save_failure

    def hook_save_requests(self, request_type, name, response_time, response_length):
        if(name == str(self.id_user)):
            self.req_num+=1
            try:
                with open(self.filepath_req, "a") as report:
                    report.write(str(response_time)+",")
            except:
                print("Can't save results")
        # locust.events.request_failure += self.atexit.register(self.exit_handler)

    def hook_save_failure(self, request_type, name, response_time, response_length):
        if(name == str(self.id_user)):
            try:
                with open(self.filepath_req, "a") as report:
                    report.write(str(response_time)+",")
            except:
                print("Can't save results")

    def hook_request_success(self, request_type, name, response_time, response_length):
        data_latency="%s %d %d\n" % ("performance.gold.latency", response_time,  time.time())
        # data_request="%s %d %d\n" % ("performance." + name.replace('.', '-')+'.requests', 1,  time.time())
        self.sock.send(data_latency.encode())
        # self.sock.send(data_request.encode())

    def hook_request_fail(self, request_type, name, response_time, exception):
        self.request_fail_stats.append([name, request_type, response_time, exception])

    def exit_handler(self):
        duration=time.time()-self.start_time
        t=self.req_num/duration
        try:
            with open(self.filepath_th, "a") as report:
                report.write(str(t))
        except:
            print("Can't save results \n")

        # self.sock.shutdown(socket.SHUT_RDWR)
        # self.sock.close()

