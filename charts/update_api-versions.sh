for i in `find . | grep 'statefulset\|deployment\.yaml'`; do sed -i 's/extensions\/v1beta1/apps\/v1/g' $i; done
for i in `find . | grep 'statefulset\|deployment\.yaml'`; do sed -i 's/apps\/v1beta2/apps\/v1/g' $i; done
