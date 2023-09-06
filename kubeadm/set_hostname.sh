hostname=${1:-"master"}
echo setting hostname
if [ -f "worker_count" ];
then
	hostname="worker-"`cat worker_count`
fi
hostnamectl set-hostname $hostname
echo `hostname -i | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"` $hostname >> /etc/hosts
exec bash
