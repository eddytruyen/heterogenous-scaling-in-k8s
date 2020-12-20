kubectl delete -f storageclass.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq  20`; do kubectl delete pvc spark-data-my-release-spark-worker-$i; done
for i in  `seq 3 20`; do  sed "s/local-pv/local-pv-$i/g" persistentvolume.yaml > pv.yaml; kubectl delete -f pv.yaml; done
