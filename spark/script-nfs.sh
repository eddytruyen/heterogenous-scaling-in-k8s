 #!/bin/bash
for i in 11 109
do 
#	echo $i 
#	scp /etc/apt/sources.list /etc/hosts /etc/fstab 172.17.13.$i:
#	ssh  172.17.13.$i "sudo mv sources.list /etc/apt/sources.list; sudo mv hosts /etc/hosts; sudo mv fstab /etc/fstab; sudo apt-get update; sudo apt-get install nfs-common, sudo mkdir mnt/nfs-disk-2"
	ssh  172.17.13.$i "sudo mount -a"
done


