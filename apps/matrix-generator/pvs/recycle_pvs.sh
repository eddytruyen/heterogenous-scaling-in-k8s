kubectl get pv > l
for i in `cat l | sed 's/|/ /' | awk '{print $1, $8}'`; do kubectl patch pv $i -p '{"spec":{"claimRef": null}}'; done
rm l
