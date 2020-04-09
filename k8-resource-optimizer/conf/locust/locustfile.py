from locust import HttpLocust, TaskSet, task


class TasksetT1(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]
    
    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/700",name="gold", catch_response=True) as resp:
            if resp.content != "completed all tasks":
                resp.failure("Got wrong response")
class TasksetT2(TaskSet):
    # one can specify tasks like this
    #tasks = [index, stats]
    
    # but it might be convenient to use the @task decorator
    @task
    def pushJob(self):
        with self.client.get("/pushJob/700",name="silver",catch_response=True) as resp:
            if resp.content != "completed all tasks":
                resp.failure("Got wrong response")
    
class Tenant1(HttpLocust):
    weight = 1
  
    host = "http://demo.gold.svc.cluster.local:80"
    min_wait = 100
    max_wait = 100
    task_set = TasksetT1
class Tenant2(HttpLocust):
    weight = 1
    host = "http://demo.gold.svc.cluster.local:80"
    min_wait = 100
    max_wait = 100
    task_set = TasksetT2

