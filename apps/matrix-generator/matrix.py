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

    adaptive_scalers=current_app.config["adaptive_scalers"]
    initial_config=current_app.config["initial_config"]

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == namespace:
            sla=s
    if previous_conf:
        previous_conf_array=list(map(lambda x: int(x),previous_conf.split('_',-1)))
    else:
        previous_conf_array=[]
    generate_matrix(initial_config, adaptive_scalers, namespace, tenants, completion_time, previous_tenants,previous_conf_array)

    config_data = yaml.safe_load(open('Results/result-matrix.yaml'))
    print(config_data)
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)


def generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants, previous_conf):

	_generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants, previous_conf)

#generate_matrix()
