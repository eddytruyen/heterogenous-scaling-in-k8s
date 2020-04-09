from locust import HttpLocust, TaskSet, task
from locust.wait_time import between

class TasksetT1(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]
    
    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/10",name="gold", catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")

class TasksetT2(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]
    
    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/50",name="bronze",catch_response=True) as resp:
            if resp.content.decode('UTF-8') != "completed all tasks":
                resp.failure("Got wrong response")
    
class Tenant1(HttpLocust):
    weight = 1
  
    # host = "http://demo.gold.svc.cluster.local:80
    host = "http://172.17.13.106:30698"

    wait_time = between(0,0)
    
    task_set = TasksetT1
# class Tenant2(HttpLocust):
#     weight = 1
#     # host = "http://demo.gold.svc.cluster.local:80"
#     host = "http://172.19.42.15:30698"

#     min_wait = 0
#     max_wait = 0
#     task_set = TasksetT2

