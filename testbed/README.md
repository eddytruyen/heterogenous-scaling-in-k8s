# Ideal throughput + Workload complexity

## Structure:
```
apps
├── consumer
|   └── ... -> Abels consumer code
├── flask-web-app
|   └── ... -> A demo flask application, used to test influxdbclient, kube python client, not part of ideal throughput/workload complexity
├── locust-influx-metrics
|   └── collector.py -> Python script to listen to the locust process running, it collects data from locust from its endpoint
├── locust-test-files
|    ├── job-application-gold-experiment.py -> Locust file to push jobs to the queue
|    └── simple-flask-grafana-test.py -> Not important, for myself to test locust
├── matrices
|    ├── ... -> Contains matrices for abels scaler to use. Forces for example only 1 pod for all users
├── workload-complexity
|    ├── ideal-throughput.py -> Calculates the ideal throughput
|    └── workload-complexity.py -> Calculates the workload-complexity
├── workload-generator-v2
     ├── traces
     |      └── ... -> Contains traces for load testing
     └── workload-generator.py -> Adapted workload generator from abel, now pushing metrics to influxdb instead of graphite   

charts
├── flask-web-app
|   └── ... -> To deploy my own test application in the cluster
└── heapster-grafana-influxdb
    └── ... -> Updated deployment from abel, this also exposes influxdb to outside of the cluster, to enable the collector from locust to push to influ

```

## Spark monitoring

### Assume 1 Job is being run

Set the following properties in Sparkbench conf:
```
spark-submit-config = [{
    spark-args = {
      ...
    }
    conf = {
      "spark.eventLog.enabled" = "true"
      "spark.eventLog.dir" = "./spark_data/1"
       ....
    }
```

### During run:
Run at a random node of Kubernetes cluster
```
kubectl port-forward spark-client-0 -n silver --address 0.0.0.0 4040:4040
```

Go to browser and open at `http://IP of random node:4040`

### After run
```
# kubectl exec -it spark-client-0 -n silver -- bash
root@spark-client-0:/opt/bitnami/spark# mkdir /tmp/spark-events
root@spark-client-0:/opt/bitnami/spark# cp spark_data/1/app-20220111181151-0061 /tmp/spark-events/
root@spark-client-0:/opt/bitnami/spark# ./sbin/start-history-server.sh
```
Run at a random node of Kubernetes cluster
```
kubectl port-forward spark-client-0 -n silver --address 0.0.0.0 <choose port>:18080
```

Go to browser and open at `http://IP of random node:<chosen port>`

### Stopping history-server
```
root@spark-client-0:/opt/bitnami/spark# ./sbin/stop-history-server.sh
```

### More information
https://spark.apache.org/docs/2.4.6/monitoring.html
