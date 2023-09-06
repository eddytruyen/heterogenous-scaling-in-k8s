k8s_version=${1:-"1.27.5-00"}
echo installing k8s version $k8s_version
sudo apt-get update
./preinstall_kubenode.sh
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://dl.k8s.io/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet=$k8s_version kubeadm=$k8s_version kubectl=$k8s_version
sudo apt-mark hold kubelet kubeadm kubectl
