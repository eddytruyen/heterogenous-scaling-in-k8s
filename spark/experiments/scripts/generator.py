import sys
import argparse, textwrap
import os.path
import yaml
import time
import socket
import atexit
import subprocess

GRAPHITE_HOST = '172.17.13.119'
GRAPHITE_PORT = 30688
SLA='silver'

parser = argparse.ArgumentParser(

description='Workload generator using SparkBench',
        usage='"%(prog)s <command> <arg>". Use  "python %(prog)s --help" o "python %(prog)s -h" for more information',
        formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("command",
help= textwrap.dedent('''\
	start: 		Start generating the workload
	stop:		Stop Locust swarm

'''))

parser.add_argument("-f","--file",action='store', help="File containing a trace")
parser.add_argument("--host",action='store', help="Locust web endpoint")
parser.add_argument("--graphite",action='store_true', help="Push user count to Graphite host")

args = parser.parse_args()


command = args.command
STORE_METRICS = args.graphite
CONFIG_FILE = args.file
LOCUST_HOST=args.host

print(STORE_METRICS)

if(STORE_METRICS):
	sock = socket.socket()
	try:
		sock.connect((GRAPHITE_HOST, GRAPHITE_PORT))
	except (socket.error):
		abort("Couldnt connect with the socket-server, terminating program...")

def stop_load():
	print("Stopping")

def file_exists(n):
	return os.path.isfile(n)

def abort(msg):
	print(msg)
	stop_load()
	sys.exit(1)		

def set_user_count(count, intermediate_first_or_last=0):
        p=set_tenant_nb(count, intermediate_first_or_last)
        print(p.decode())
        if (p and STORE_METRICS):
            sock.send(p)   
	# print(r.status_code)


def set_tenant_nb(count, intermediate_first_or_last=0):
    commands="./scaler-generator.sh " + str(count) + " " + str(count)
    if intermediate_first_or_last == 1:
        commands=commands + " 1"
    elif intermediate_first_or_last == 2:
        commands=commands + " 0"
    print(commands)
    p = subprocess.check_output(commands.split())
    return p

def check_params(segment_type,initial_count,end_count):
	
	try:
		assert initial_count >= 0
		assert end_count >= 0
		#assert duration >= 0
		assert initial_count == int(initial_count)
		assert end_count == int(end_count)
		#assert duration == int(duration)
	except:
		abort("Invalid params in config file, counts and duration need to be positive integers")	
	
	if(segment_type=='stable'):
		try:
			assert initial_count==end_count
		except: 
			abort('Invalid configuration. Stable segments need to have the same initial and end count')

	elif(segment_type=='rising'):		
		try:
			assert initial_count<end_count
		except: 
			abort('Invalid configuration. Rising segments need to have the initial count smaller than the end count')

	elif(segment_type=='decreasing'):		
		try:
			assert initial_count>end_count
		except: 
			abort('Invalid configuration. Decreasing segments need to have the initial count greater than the end count')

	else:
		abort('Invalidad segment type. Options are: stable, rising, decreasing')

def process_segment(trace, intermediate_first_or_last=0):
	segment_type=trace['segment']
	initial_count=trace['initialCount']
	end_count=trace['endCount']
	#duration=trace['duration']

	check_params(segment_type,initial_count,end_count)

	if(segment_type=='stable'):
		set_user_count(initial_count, intermediate_first_or_last)

	elif(segment_type=='rising'):
		times=end_count-initial_count

		for t in range(times+1):
			set_user_count(t+initial_count, intermediate_first_or_last)
		# set_user_count(end_count)

	elif(segment_type=='decreasing'):
		times=initial_count-end_count

		for t in range(times+1):
			set_user_count(initial_count-t, intermediate_first_or_last)
		# set_user_count(end_count)	

def generate_load():
	if(file_exists(CONFIG_FILE)):
		try:
			config_data = yaml.safe_load(open(CONFIG_FILE))
		except:
			print("The file provided was not a correct file. Please try again...")
			sys.exit(1)
	else:
		print("File does not exists. Please try again...")
		sys.exit(1)		

	traces=config_data['load']

	if(STORE_METRICS):
		data_request="%s %d %d\n" % ("performance."+SLA+".users", 0,  time.time())
		sock.send(data_request.encode())


	last=None

	for i, trace in enumerate(traces):
		for k in range(trace['repeat']):
			for j,segment in enumerate(trace['trace']):
				if i==0 and k==0 and j==0:
					intermediate_first_or_last=1
				elif i==len(traces)-1 and k == len(range(trace['repeat']))-1 and j == len(trace['trace'])-1:
 					intermediate_first_or_last=2
                                else:
                                        intermediate_first_or_last=0
				process_segment(segment,intermediate_first_or_last)
				last=segment['endCount']


	if(STORE_METRICS):
		data_request="%s %d %d\n" % ("performance."+SLA+".users", last,  time.time())
		sock.send(data_request.encode())

	stop_load()			


if(command=='start'):
	generate_load()

elif(command=='stop'):
	stop_load()

