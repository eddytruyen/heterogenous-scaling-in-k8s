import argparse
import textwrap
import yaml
from src.generator import generate_matrix as _generate_matrix


parser = argparse.ArgumentParser(

description='Workload generator using Locust',
        usage='"%(prog)s <command> <arg>". Use  "python %(prog)s --help" o "python %(prog)s -h" for more information',
        formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("config",
help= textwrap.dedent('''\
	start: 		Start generating the workload
	stop:		Stop Locust swarm

'''))



args = parser.parse_args()


CONFIG_FILE = args.config


config_data = yaml.safe_load(open(CONFIG_FILE))


def generate_matrix():
	_generate_matrix(config_data)

generate_matrix()