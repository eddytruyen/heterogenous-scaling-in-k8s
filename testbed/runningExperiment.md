# Tutorial: Running a experiment on a pod

## Step 1: Enable the application

Follow the instructions from Abel to get the application in the cluster.
But at the step to get heapster/grafana/influx in the cluster use the helm charts from this repository.

## Step 2: Change the scaling matrix to the one you want to use for the application

Use the 

## Step 3: Start locust to monitor the application

### Running locust with a experiment -> You can design your own
locust -f ./heterogenous-scaling-in-k8s/Locust/locustfile-exp1.py

### Running the generator -> Generates a workload to run.
python3 apps/workload-generator-v2/workload-generator.py start -f apps/workload-generator-v2/traces/seasonal.yaml -l http://172.19.133.29:8089 -i 172.19.133.29 -p 30421

### Running the collector that collects the data from the RUNNING locust environment
python3 apps/locust-influx-metrics/collector.py -l http://172.19.133.29:8089 -i 172.19.133.29 -p 30421 -s 5 -d gold-app-data