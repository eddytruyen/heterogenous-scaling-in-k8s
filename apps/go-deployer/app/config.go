package main

import(
	"os"
)

const ExchangeName = "non_linear_scaler"
const BindingKey = "job.*"
var RabbitMQHost string = os.Getenv("RABBIT_MQ_HOST")
var RabbitMQPort string = os.Getenv("RABBIT_MQ_PORT") 
var RabbitMQUser string = os.Getenv("RABBIT_MQ_USER") 
var RabbitMQPass string = os.Getenv("RABBIT_MQ_PASS") 
var ResourcePlannerHost string = os.Getenv("RESOURCE_PLANNER_HOST") 


