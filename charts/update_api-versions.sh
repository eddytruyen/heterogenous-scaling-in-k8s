for i in `find . | grep 'statefulset\|deployment\.yaml'`; do sed -i 's/extensions\/v1beta1/apps\/v1/g' $i; done
for i in `find . | grep 'statefulset\|deployment\.yaml'`; do sed -i 's/apps\/v1beta2/apps\/v1/g' $i; done
for i in `find . | grep '.*riority.*\.yaml'`; do sed -i 's/scheduling.k8s.io\/v1beta1/scheduling.k8s.io\/v1/g' $i; done
for i in `find . | grep '.*service.*yaml'`; do sed -i '/^namespace/d' $i; done
for i in `find . | grep '.*service.*yaml'`; do sed -i '/^  namespace/d' $i; done
for i in `find . | grep '.*svc.*yaml'`; do sed -i '/^namespace/d' $i; done
for i in `find . | grep '.*svc.*yaml'`; do sed -i '/^  namespace/d' $i; done
for i in `find . | grep '.*deployment.*yaml'`; do sed -i '/^namespace/d' $i; done
for i in `find . | grep '.*deployment.*yaml'`; do sed -i '/^  namespace/d' $i; done

