k8s_version="1.27.5-00"
subnet="172.22.8"
worker_nodes="182 65"
worker_start_index=1
./install_kubeadm_master.sh
./preinstall_weave.sh
./install_cluster.sh $k8s_version $subnet $worker_nodes $worker_start_index
