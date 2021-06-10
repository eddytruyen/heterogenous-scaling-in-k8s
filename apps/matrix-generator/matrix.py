import argparse
import textwrap
import yaml
from src.generator import generate_matrix as _generate_matrix




def generate_matrix(config_file, namespace, tenants, completion_time, previous_tenants):

	config_data = yaml.safe_load(open(config_file))
	_generate_matrix(config_data, namespace, tenants, completion_time, previous_tenants)

#generate_matrix()
