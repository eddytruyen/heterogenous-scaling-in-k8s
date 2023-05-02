#!/bin/bash
kubectl get pv | grep 'Released' > l
for i in `cat l | sed 's/|/ /' | awk '{print $1, $9}'`; do kubectl patch pv $i -p '{"spec":{"claimRef": null}}'; done
rm l
