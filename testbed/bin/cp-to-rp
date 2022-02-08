
echo "Copying file: $1"

rp_pod=$(kubectl get pods -n scaler | awk '{if ($1 ~ /resource/) print $1}')

kubectl cp $1 scaler/$rp_pod:/data/$1
