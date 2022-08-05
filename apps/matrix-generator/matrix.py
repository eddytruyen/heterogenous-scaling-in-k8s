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

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == namespace:
            sla=s
    if previous_conf:
        previous_conf_array=list(map(lambda x: int(x),previous_conf.split('_',-1)))
    else:
        previous_conf_array=[]
    generate_matrix(initial_config, adaptive_scalers, runtime_manager, namespace, tenants, completion_time, previous_tenants,previous_conf_array, total_cpu, total_memory, ignore_auto_scaler)

    config_data = yaml.safe_load(open('Results/result-matrix.yaml'))
    print(config_data)
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)


def generate_matrix(initial_config, adaptive_scaler, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf, total_cpu, total_memory, ignore_auto_scaler):

	_generate_matrix(initial_config, adaptive_scaler, runtime_manager, namespace, tenants, completion_time, previous_tenants, previous_conf, total_cpu, total_memory, ignore_auto_scaler)

#generate_matrix()
