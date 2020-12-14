kubectl delete -f storageclass.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq $nodes`; do kubectl delete pvc spark-data-my-release-spark-worker-$i; sed "s/local-pv/local-pv-$i/g" persistentvolume.yaml > pv.yaml; kubectl delete -f pv.yaml; done
