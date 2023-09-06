nodes=${3:-"182 65"}
subnet=${2:-"172.22.8"}
k8s_version=${1:-"1.27.5-00"}
worker_count=${4:-1}
for i in `echo $nodes`; do 
	echo $worker_count > worker_count
	echo $k8s_version > k8s_version
	echo Installing kube_worker software for worker `cat worker_count`
	scp -i ~/.ssh/756245.pem preinstall_kubenode.sh set_hostname.sh install_kubeadm_worker.sh preinstall_weave.sh worker_count k8s_version ${subnet}.$i:
	ssh -i ~/.ssh/756245.pem ${subnet}.$i 'chmod 755 *.sh'
	echo Root action required: execute "sudo su; ./set_host_name.sh; exit; exit"; ssh -i  ~/.ssh/756245.pem ${subnet}.$i; 
	ssh -i ~/.ssh/756245.pem ${subnet}.$i 'sudo kubeadm reset -f; ./install_kubeadm_worker.sh `cat ./k8s_version`; ./preinstall_weave.sh'; 
	worker_count=$((worker_count + 1))
done
sudo  kubeadm init --config kubeadm-config.yaml
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f weave-daemonset-k8s.yaml
#for i in `echo $nodes`; do
#       ssh -i ~/.ssh/756245.pem ${subnet}.$i 'sudo kubeadm join 172.22.8.106:6443 --token tnpehh.rru6r40ku522mlbz \
#        --discovery-token-ca-cert-hash sha256:5e71f078e4bc79de4390ea3ac8105765f778137edac5aa0ba2c57246a171e5fe'
#done
rm worker_count
rm k8s_version
