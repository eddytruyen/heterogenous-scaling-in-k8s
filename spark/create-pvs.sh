kubectl create -f storageclass.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq $nodes`; do sed "s/local-pv/local-pv-$i/g" persistentvolume.yaml > pv.yaml; kubectl create -f pv.yaml; done
