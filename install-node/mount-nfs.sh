#!/bin/bash

local_nfs_dir=${1:-"/mnt/nfs-disk-2/"}

sudo apt update
sudo apt install nfs-common -y
sudo mkdir -p $local_nfs_dir
sudo mount kronos-dnet-hera.cs.kuleuven.be:/prjeddy $local_nfs_dir
sudo ls $local_nfs_dir/t
