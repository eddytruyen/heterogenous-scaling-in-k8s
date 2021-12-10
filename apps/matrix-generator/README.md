
This is the run-time planner branch to be experimented with by Udit Sareen

1)in case directory githubrepos is empty execute the following command

```
`./mount_githubrepos.sh
```
Then 

```
cd githubrepos
```

2) Then clone heterogeneous scaling  project and change directory into it


3) Then install helm chart:

```
kubectl create ns gold
helm install gold-spark /home/ubuntu/go/src/k8-resource-optimizer/examples/charts/bitnami-heterogeneous/spark/ -n gold
```
4) Then edit conf/matrix-spark.yaml  (in subdirectory apps/matrix-generator of github project on heterogeneous scaling)
change 'silver'  into 'gold'

5) Then start server (in subdirectory apps/matrix-generator):

```
sudo rm -r Results/matrix.yaml
sudo rm -r Results/exp3/gold
sudo python server.py conf/matrix-spark.yaml
```

6) Then start workload-generator (in subdirectory spark/experiments/script):

First however change the value of SLA in generator.py to 'gold'.

Then start it with e.g. a seasonal workload:

```
python generator.py start -f thesis/seasonal.yaml
```

