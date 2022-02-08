from locust import HttpUser, between, task
import random

class WebsiteUser(HttpUser):
    wait_time = between(1,5)

    @task
    def new_value(self):
        r = round(random.uniform(1,4),2)
        self.client.get("/post-influxdb/" + str(r)) 
