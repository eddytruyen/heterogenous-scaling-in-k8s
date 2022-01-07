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