import argparse
import textwrap
import yaml
from src.generator import generate_matrix as _generate_matrix




def generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants):

	_generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants)

#generate_matrix()
