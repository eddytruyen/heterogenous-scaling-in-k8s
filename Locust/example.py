from locust import HttpLocust, TaskSet, task
import locust.events
import uuid


class TasksetT1(TaskSet):

    @task
    def pushJob(self):
        with self.client.get("/",name="gold", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure("Got wrong response")

    
class Tenant1(HttpLocust):
    weight = 1
  
    # host = "http://demo.gold.svc.cluster.local:80
    host = "http://example.org"

    min_wait = 0
    max_wait = 0
    task_set = TasksetT1
# 
    def __init__(self):
        super(Tenant1, self).__init__()
        self.id_user=uuid.uuid4()
        self.filepath='Results/'+str(self.id_user)+'.csv'       
        
        locust.events.request_success += self.hook_save_requests

    def hook_save_requests(self, request_type, name, response_time, response_length):
        try:
            with open(self.filepath, "a") as report:
                report.write(str(response_time)+",")
        except:
            print("Can't save results")

