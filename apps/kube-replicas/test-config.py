from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.AppsV1Api()
print("Listing pods with their IPs:")
# ret = v1.list_deployment_for_all_namespaces(watch=False)
ret = v1.list_namespaced_deployment("weave")
for i in ret.items:
    # print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    print(i.metadata.name)
    print(i.status.available_replicas)