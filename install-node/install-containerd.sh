wget https://github.com/containerd/containerd/releases/download/v1.6.22/containerd-1.6.22-linux-amd64.tar.gz
sudo tar Czxvf /usr/local containerd-1.6.22-linux-amd64.tar.gz
wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
sudo cp containerd.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now containerd
sudo systemctl status containerd
wget https://github.com/opencontainers/runc/releases/download/v1.1.8/runc.amd64
sudo install -m 755 runc.amd64 /usr/local/sbin/runc
sudo mkdir -p /etc/containerd/
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml
sudo systemctl restart containerd
wget https://github.com/containerd/nerdctl/releases/download/v1.5.0/nerdctl-1.5.0-linux-amd64.tar.gz
sudo tar Cxzvf /usr/local/bin nerdctl-1.5.0-linux-amd64.tar.gz

