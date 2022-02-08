import kubernetes
from datetime import datetime
from influxdb import InfluxDBClient

INFLUXDB_HOST = '172.19.133.29'
INFLUXDB_PORT = 30421

APPLICATION_DATA_DATABASE = "gold-app-date"
HEAPSTER_DATABASE = "k8s"

influxClient = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT) 

kubernetes.config.load_kube_config()

v1 = kubernetes.client.CoreV1Api()

list_cpu_usage_server = []
list_cpu_usage_expected = []

list_cpu_usage_expected_n = []
list_mem_usage_server_n = []
list_mem_usage_expected_n = []

ideal_throughput_list_per_limit = {}

ret = v1.list_namespaced_pod(watch=False, namespace='gold')

consumer_pod_list = [[s.metadata.name, ret.items[0].spec.containers[0].resources.requests['cpu']] for s in ret.items if s.metadata.name.startswith("consumer")]

total_cpu_cores = sum([ int(pod_info[1][:-1]) for pod_info in consumer_pod_list])

def ru_strategy():
    different_configs = set([s[1] for s in consumer_pod_list])
    r = sum([((req_rate*60)/len(different_configs)) * calculate_workload_complexity() * get_latest_ideal_throughput_value(s[1]) for s in consumer_pod_list]) / len(different_configs)
    return r

def normalize_list(list_t):
    return [ (s - min(list_t)) / (max(list_t) - min(list_t)) for s in list_t]

def calculate_workload_complexity():
    return sum(list_cpu_usage_server) / sum(list_cpu_usage_expected)


def get_latest_ideal_throughput_mem_cpu(cpu_limit):
    it_query = 'SELECT "extended-throughput-mem", "extended-throughput-cpu" \
                        FROM "gold-app-data"."autogen"."idealThroughput" \
                        WHERE "cpu" = \''+ cpu_limit + '\' \
                        ORDER BY time DESC LIMIT 3'

    influxClient.switch_database("gold-app-data")
    results = influxClient.query(it_query)
    
    mem = sum([c[1] for c in results.raw['series'][0]['values']]) / len([c[1] for c in results.raw['series'][0]['values']])
    cpu = sum([c[2] for c in results.raw['series'][0]['values']]) / len([c[2] for c in results.raw['series'][0]['values']])

    return [mem, cpu]

def get_latest_ideal_throughput_value(cpu_limit):
    it_query = 'SELECT "basic-throughput" \
                        FROM "gold-app-data"."autogen"."idealThroughput" \
                        WHERE "cpu" = \''+ cpu_limit + '\' \
                        ORDER BY time DESC LIMIT 3'
    influxClient.switch_database("gold-app-data")
    results = influxClient.query(it_query)
    return sum([c[1] for c in results.raw['series'][0]['values']]) / len([c[1] for c in results.raw['series'][0]['values']])

# Pod name is the name of the pod in the kubernetes platform
# Time window is the window of the data you want (i.e. 1m, 10m, 1h, ...)
def get_latest_heapster_data_from_pod(pod_name, metric, namespace_of_pod, time_window):
    influxClient.switch_database(HEAPSTER_DATABASE)
    query = 'SELECT "pod_name", "value" \
                FROM "' + HEAPSTER_DATABASE + '"."default"."' + metric + '"  \
                WHERE "pod_name" = \'' + pod_name + '\' \
                    AND "namespace_name" = \'' + namespace_of_pod + '\' \
                    AND time > now() - ' + time_window
    results = influxClient.query(query)
    return results

def get_latest_cpu_data(pod_name, time_window, namespace):
    results = get_latest_heapster_data_from_pod(pod_name, 'cpu/usage_rate', namespace, time_window)
    return [c[2] for c in results.raw['series'][0]['values']]

def get_latest_mem_data(pod_name, time_window):
    results = get_latest_heapster_data_from_pod(pod_name, 'memory/usage', namespace, time_window)
    return [c[2] for c in results.raw['series'][0]['values']]


req_rate_query = 'SELECT "userCount", "rps", "medianRespTime" \
                    FROM "gold-app-data"."autogen"."responseData" \
                    WHERE time > now() - 1m' 

influxClient.switch_database("gold-app-data")
results = influxClient.query(req_rate_query)
list_req_rate = [c[2] for c in results.raw['series'][0]['values']]

avg_req_rate = sum(list_req_rate) / len(list_req_rate)

influxClient.switch_database("k8s")

for pod_info in consumer_pod_list:
    list_cpu_usage = get_latest_cpu_data(pod_info[0], '1m', 'gold')
    list_mem_usage = get_latest_mem_data(pod_info[0], '1m', 'gold')
    list_mem_usage = normalize_list(list_mem_usage)
    
    avg_cpu_p_usage = (sum(list_cpu_usage) / len(list_cpu_usage)) / int(pod_info[1][:-1])
    avg_mem_usage = sum(list_mem_usage) / len(list_mem_usage)

    ideal_throughput = get_latest_ideal_throughput_value(pod_info[1])
    new_ideal_throughput = get_latest_ideal_throughput_mem_cpu(pod_info[1])
    ideal_throughput_list_per_limit[pod_info[1]] = new_ideal_throughput

    cpu_usage_expected = avg_req_rate*60*(int(pod_info[1][:-1]) / total_cpu_cores) * ideal_throughput

    cpu_usage_expected_n = avg_req_rate*60*(int(pod_info[1][:-1]) / total_cpu_cores) * new_ideal_throughput[1]
    mem_usage_expected_n = avg_req_rate*60*(int(pod_info[1][:-1]) / total_cpu_cores) * new_ideal_throughput[0] # Should be memory restricted value?

    # PAPER
    list_cpu_usage_server.append(avg_cpu_p_usage)
    list_cpu_usage_expected.append(cpu_usage_expected)

    # MEM
    list_cpu_usage_expected_n.append(cpu_usage_expected_n)
    list_mem_usage_server_n.append(avg_mem_usage)
    list_mem_usage_expected_n.append(mem_usage_expected_n)

workload_complex = sum(list_cpu_usage_server) / sum(list_cpu_usage_expected)
print("Workload complexity paper: " + str(workload_complex))

# Actual/Expected from every pod in the current configuration
workload_complex_mem = (sum(list_cpu_usage_server) / sum(list_cpu_usage_expected_n)) + (sum(list_mem_usage_server_n) / sum(list_mem_usage_expected_n))
print("Workload complexity new: " + str(workload_complex_mem))

print("Number of different configs: " + str(len(set([s[1] for s in consumer_pod_list]))))

def ru_strategy():
    different_configs = set([s[1] for s in consumer_pod_list])
    r = sum([((avg_req_rate*60)/len(different_configs)) * calculate_workload_complexity() * get_latest_ideal_throughput_value(s[1]) for s in consumer_pod_list]) / len(different_configs)
    return r

print("RU_Strategy old: " + str(ru_strategy()))

different_configs = set([s[1] for s in consumer_pod_list])

print(ideal_throughput_list_per_limit)

ru_per_cpu_limit = [[(avg_req_rate*ideal_throughput_list_per_limit[s][0])/workload_complex_mem, (avg_req_rate*ideal_throughput_list_per_limit[s][1])/workload_complex_mem] for s in different_configs]
ru_strategy_n = [sum([t[0] for t in ru_per_cpu_limit])/len(ru_per_cpu_limit), sum([t[1] for t in ru_per_cpu_limit])/len(ru_per_cpu_limit)]

print("RU_Strategy new: " + str(ru_strategy_n))
