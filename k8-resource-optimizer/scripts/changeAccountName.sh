account=$1
echo $account
sed -i.bak  's/matthijskaminski/'"$account"'/' "conf/helm/mychart/templates/demo-deployment.yaml"
sed -i.bak  's/matthijskaminski/'"$account"'/' "conf/helm/mychart/templates/consumer-deployment.yaml"
sed -i.bak  's/matthijskaminski/'"$account"'/' "tool-deployment.yaml"