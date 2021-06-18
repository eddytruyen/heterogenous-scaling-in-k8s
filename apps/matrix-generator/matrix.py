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

    adaptive_scaler=current_app.config["adaptive_scaler"]
    print(adaptive_scaler.ScalingFunction.CoefA)
    initial_config=current_app.config["initial_config"]

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == namespace:
            sla=s
    previous_conf_array=list(map(lambda x: int(x),previous_conf.split('_',-1)))
    generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants,previous_conf_array)

    config_data = yaml.safe_load(open('Results/matrix.yaml'))
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)


def generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants, previous_conf):

	_generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants, previous_conf)

#generate_matrix()
