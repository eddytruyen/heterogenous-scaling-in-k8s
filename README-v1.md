# Prerequisites

Given the following cluster setup note the workerNode and monitoringNode labels
```
$ kubectl get nodes --show-labels
k8-test-1   Ready    master   56d   v1.14.1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8-test-1,kubernetes.io/os=linux,node-role.kubernetes.io/master=
k8-test-2   Ready    <none>   56d   v1.14.1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8-test-2,kubernetes.io/os=linux,monitoringNode=yes
k8-test-3   Ready    <none>   56d   v1.14.1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8-test-3,kubernetes.io/os=linux,workerNode=yes
```

On the monitoringNode heapster, grafana, influxdb and graphite are deployed
On the workerNode the scaler-controller chart is deployed

# Install locust on the master using pip3

pip3 requires python3

```
$ pip3 install locust
```

Add locust to your PATH by adding the following line to your .bashrc or .bash_profile file

```
export PATH=$PATH:$HOME/.local/bin
```

# Install helm

```bash
# Install Helm client, 
$ curl -LO https://kubernetes-helm.storage.googleapis.com/helm-v2.8.0-linux-amd64.tar.gz && tar xvzf helm-v2.8.0-linux-amd64.tar.gz && chmod +x ./linux-amd64/helm && sudo mv ./linux-amd64/helm /usr/local/bin/helm
```

To install helm in distributed cluster, you'll first need to first create a [service-account for Helm](http://jayunit100.blogspot.be/2017/07/helm-on.html) and initiate helm with this service account. Short, you have to execute the following commands


```
$ kubectl create -f helm.yaml
$ helm init --service-account helm
``` 

# Install the python-based application

```
#install golden SLA-class
$ helm install charts/exp2app

#install bronzen SLA-class
$ helm install charts/bronze
```

Resources and additional params can be modified in values.yaml.

# Install the scaler

```
helm install charts/scaler-controller

```
Set the appropriate matrix in the resource planner pod

```
$ kubectl get pods -n scaler
NAME                              READY   STATUS    RESTARTS   AGE
go-deployer-58bb7c4c49-tg5c9      1/1     Running   6          61m
rabbitmq-7b944bfdf4-wsltc         1/1     Running   0          61m
resource-planner-589d79bf-sh6pp   1/1     Running   0          61m
$ kubectl exec -it resource-planner-589d79bf-sh6pp -n scaler -- sh
/ # vi server.py
```

Edit in server.py the following line
```
config_data = yaml.safe_load(open('data/matrix.yaml'))
```
`/data/matrix.yaml` is the matrix for heterogeneous scaling, while `/data/single-replica.yaml` is for homogeneous scaling. The values in the matrix have been determined for the workload sent out in the workload-generator app.


# Install graphite

```
$ helm install charts/graphite --name graphite
```
It logs the results off the experiments. To push metrics, two different endpoints are available, one for discrete data and the other for aggregated data.

# Install Heapster, Grafana and InfluxDB

```
$ helm install charts/heapster-grafana-influxdb --name heapster
```

To display graphite metrics on Grafana dashboard, log into the dashboard and [add graphite as data source](https://grafana.com/docs/grafana/latest/features/datasources/graphite/). This deployment does not implement any persistance mechanism, so all data is going to be lost on cluster failure. [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
can be used to avoid this (see charts/graphite/templates/volume.yaml)


# Start the locust server

Edit `Locust/locustfile-exp.py' to replace the IP of the queue host on the HttpLocust class for your queue endpoint. For generating local files with throughput and turnaround time, Locust/locustfile-graphite.py can be used instead. In both cases, the socket connection (self.sock.connect(IP, port)) needs to match the graphite aggregator service (running by default on nodePort 30688).

```
$cd Locust
$locust -f locustfile-exp.py
[2020-03-19 17:58:18,258] k8-test-1/INFO/locust.main: Starting web monitor at http://*:8089
[2020-03-19 17:58:18,259] k8-test-1/INFO/locust.main: Starting Locust 0.14.5
```
Open browser at `http://ip of master node:8089` and check Locust is up. To get metrics from the runs, in a separate terminal run:

```
cd ../apps/workload-generator
python3 metrics.py 
```

This script is going to fetch metrics from the current run using the Locust API and push them to the graphite host. Modify the SLA class and graphite endpoint if needed.

# Start the workload generator

```
cd ../apps/workload-generator
python3 generator.py start -f thesis/seasonal.yaml --host=http://172.17.13.106:8089
```
The above tests a seasonal workload. 






