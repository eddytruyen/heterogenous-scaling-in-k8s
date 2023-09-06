purge=${1:-0}

if [ -eq $purge 1 ] 
then
	./purge-cri.sh
else
	./pre-cri.sh
fi

./pre-net.sh
./install-containerd.sh
./install-cni-plugins.sh




