#!/bin/bash
for i in 103 105 106 119 120 121 122; do ssh 172.17.13.$i "rm -r /mnt/fast-disks/spark-bench-test"; done
for i in 103 105 106 119 120 121 122; do scp -r /mnt/fast-disks/spark-bench-test/ 172.17.13.$i:; done
for i in 103 105 106 119 120 121 122; do ssh 172.17.13.$i "mv spark-bench-test /mnt/fast-disks/"; done


