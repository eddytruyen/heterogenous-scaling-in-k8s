import argparse
import textwrap
import yaml
from src.generator import generate_matrix2 as generate_matrix2
from src.searchwindow import ScalingFunction


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
	generate_matrix2(config_data)
	nodes=[[4,8],[8,32],[8,32],[8,32],[8,16],[8,16],[8,8],[3,6]]
	f=ScalingFunction(667.1840993,-0.8232555,136.4046126,2,2,True,nodes)
	for i in range(1,10,1):
		print(f.eval(i))
	print(f.target(90,1))
#	max=f.maximum(2,3)
#	print(max)
#	min=f.minimum(1,10)
#	range=max-min
	#for x in range(1,10,1):
	#	if  
	#for i in range(100,110,1):
	#	print(f.eval(i))
#	print(f.maximum(1,10))
#	print(f.minimum(1,10))
#	print(f.derivative(1,2))

generate_matrix()
