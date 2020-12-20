kubectl create -f storageclass-nfs.yaml
count=`kubectl get nodes | wc -l`
nodes=`expr $count - 2`
for i in `seq 20`; do sed "s/nfs-volume/nfs-volume-$i/g" persistentvolume.yaml > pv.yaml; kubectl create -f pv.yaml; done
