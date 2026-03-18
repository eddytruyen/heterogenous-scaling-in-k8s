from flask import request
from flask import current_app
import argparse
import textwrap
import yaml
import json
from src.generator import generate_matrix as _generate_matrix


def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')
    completion_time = request.args.get('completiontime')
    previous_tenants = request.args.get('previoustenants')
    previous_conf = request.args.get('previousconf')
    try:
        total_cpu = int(request.args.get('totalcpu'))
        total_memory=int(request.args.get('totalmemory'))
    except:
        total_cpu=-1
        total_memory=-1
    if total_cpu >= 0 and total_memory >= 0:
        try:
            ignore_auto_scaler = int(request.args.get('ignoreautoscaler'))
        except:
            ignore_auto_scaler = 0
    else:
        ignore_auto_scaler = 0
     
    

    adaptive_scalers=current_app.config["adaptive_scalers"]
    initial_config=current_app.config["initial_config"]
    runtime_manager=current_app.config["runtime_manager"]
    rl_autoscaler=current_app.config["rl_autoscaler"]

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == namespace:
            sla=s
    if previous_conf:
        previous_conf_array=list(map(lambda x: int(x),previous_conf.split('_',-1)))
    else:
        previous_conf_array=[]

    # Extract ground truth for each worker
    prev_actual_resources = []
    for i in range(1, len(rl_autoscaler.workers) + 1):
        cpu = request.args.get(f'prev_res_worker{i}_cpu')
        mem = request.args.get(f'prev_res_worker{i}_mem')
        inplace = request.args.get(f'inplace_worker{i}')
        if cpu and mem:
            prev_actual_resources.append({'cpu': cpu, 'memory': mem})
        else:
            prev_actual_resources.append(None)
        
        # Ground truth for in-place resize policy
        if inplace == 'true':
            rl_autoscaler.worker_inplace_support[i-1] = True
        elif inplace == 'false':
            rl_autoscaler.worker_inplace_support[i-1] = False

    generate_matrix(initial_config, adaptive_scalers, runtime_manager, namespace, tenants, completion_time, previous_tenants,previous_conf_array, total_cpu, total_memory, ignore_auto_scaler, rl_autoscaler, prev_actual_resources)

    config_data = yaml.safe_load(open('Results/result-matrix.yaml'))
    print(config_data)
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)


def generate_matrix(initial_config, adaptive_scaler, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf, total_cpu, total_memory, ignore_auto_scaler, rl_autoscaler, prev_actual_resources=None):

	_generate_matrix(initial_config, adaptive_scaler, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf, total_cpu, total_memory, ignore_auto_scaler, rl_autoscaler, prev_actual_resources)

#generate_matrix()
