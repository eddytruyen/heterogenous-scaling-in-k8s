# How to run an experiment

Running an experiment takes a number of steps. 

## Prerequisites:

Know the ips of the applications (either gold, locust).
Know the pod name of the resource planner

`kubectl get pods -n scaler`

## Steps

1. Set the resource matrix to your desired configuration. See also files under /matrices. 
   1. Copy the file to the pod
   
      `kubectl cp <path-to-yaml> scaler/resource-planner-***:/data/2-all-750.yaml`

   2. Change the server.py path via
    
      `kubectl exec -it resource-planner-*** -n scaler -- sh`
      `vi server.py`

2. Start locust with the correct file

   `locust -f ~/heterogenous-scaling-in-k8s/Locust/locustfile-exp1.py`

3. Start up the locust workload generator

   `python3 apps/workload-generator-v2/workload-generator.py start -f apps/workload-generator-v2/traces/seasonal.yaml -l http://172.19.133.29:8089 -i 172.19.133.29 -p 30421`

4. Start collecting metrics from the locust server

   `python3 apps/locust-influx-metrics/collector.py -l http://172.19.133.29:8089 -i 172.19.133.29 -p 30421 -s 5 -d gold-app-data`

5. To calculate the ideal throughput, use following command:
   
   `python3 ideal-throughput.py`

6. You can monitor the data using influxdb/grafana

# Experiments run with Ideal Throughput

## Experiment 1:

Calculating the ideal throughput of a pod in a isolated environment.

Meaning:

- The only pod serving the application
- Start with
  - 1000m CPU
  - 1 Gb Mem