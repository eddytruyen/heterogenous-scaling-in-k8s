GOLD=$(helm list | grep -o "gold-my-app-....")
helm delete --purge $GOLD
SILVER=$(helm list | grep -o "silver-my-app-....")
helm delete --purge $SILVER

BRONZE=$(helm list | grep -o "bronze-my-app-....")
helm delete --purge $BRONZE