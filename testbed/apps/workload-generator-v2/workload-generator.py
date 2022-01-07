# Author: Arno Van Langendonck
# Inspired by generator.py by Abel
# Generates a workload using locust, sends data to INFLUXDB for further analysis

import sys
import argparse
import textwrap
import os.path
import yaml
import time
import requests
from datetime import datetime
from influxdb import InfluxDBClient
import atexit

parser = argparse.ArgumentParser(
    description='Workload generator using locust, connected to a INFLUXDB',
    usage='"%(prog)s <command> <arg>". Use  "python %(prog)s --help" o "python %(prog)s -h" for more information',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    "command",
    help=textwrap.dedent(
        '''\
        start: 		Start generating the workload
        stop:		Stop Locust swarm
        '''
    )
)
parser.add_argument("-f", "--file",  action='store',
                    help="File containing a trace")
parser.add_argument("-l", "--lhost", action='store',
                    help="Locust web endpoint")
parser.add_argument("-i", "--dbip",  action='store',
                    help="IP address of the influx-db")
parser.add_argument("-p", "--dbport", action='store',
                    help="Port of influx-db")

args = parser.parse_args()

COMMAND = args.command
CONFIG_FILE = args.file
LOCUST_HOST = args.lhost
INFLUXDB_HOST = args.dbip
INFLUXDB_PORT = args.dbport
DEBUG = True

# Test connection to influxdb
client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, timeout=5)
print("Checking connection to influxdb... wait max 15 seconds")
try:
    v = client.ping()
except:
    exit("Problem with connection to Influxdb, check ip and port, aborting")
print("Connection established")
client.switch_database("gold-app-data")


def stop_load():
    r = requests.get(LOCUST_HOST+"/stop")

def abort_experiment(msg):
    stop_load()
    exit("Program aborted: " + msg)

def file_exists(n):
    return os.path.isfile(n)

def set_user_count(count):
    url = LOCUST_HOST + "/swarm"
    r = requests.post(url, data={'user_count': count, 'spawn_rate': count})

    if (r.status_code == 200):
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        json_body = [{
            "measurement": "userCount",
            "time": time,
            "fields": {
                "userCount": count
            }
        }]

        if DEBUG:
            print("writing: t=" + time + " c=" + str(count))
        client.write_points(json_body)

def check_params(segment_type, initial_count, end_count, duration):

    try:
        assert initial_count >= 0
        assert end_count >= 0
        assert duration >= 0
        assert initial_count == int(initial_count)
        assert end_count == int(end_count)
        assert duration == int(duration)
    except:
        abort("Invalid params in config file, counts and duration need to be positive integers")

    if(segment_type == 'stable'):
        try:
            assert initial_count == end_count
        except:
            abort('Invalid configuration. Stable segments need to have the same initial and end count')

    elif(segment_type == 'rising'):
        try:
            assert initial_count < end_count
        except:
            abort('Invalid configuration. Rising segments need to have the initial count smaller than the end count')

    elif(segment_type == 'decreasing'):
        try:
            assert initial_count > end_count
        except:
            abort('Invalid configuration. Decreasing segments need to have the initial count greater than the end count')

    else:
        abort('Invalidad segment type. Options are: stable, rising, decreasing')

def process_segment(trace):
    segment_type = trace['segment']
    initial_count = trace['initialCount']
    end_count = trace['endCount']
    duration = trace['duration']

    check_params(segment_type, initial_count, end_count, duration)

    if(segment_type == 'stable'):
        set_user_count(initial_count)
        time.sleep(duration)

    elif(segment_type == 'rising'):
        times = end_count-initial_count
        delay = duration/times

        for t in range(times+1):
            set_user_count(t+initial_count)
        time.sleep(delay)
        # set_user_count(end_count)

    elif(segment_type == 'decreasing'):
        times = initial_count-end_count
        delay = duration/times

        for t in range(times+1):
            set_user_count(initial_count-t)
            time.sleep(delay)
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

    traces = config_data['load']

    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    json_body = [{
        "measurement": "userCount",
        "time": time,
        "fields": {
            "userCount": 0
        }
    }]
    if DEBUG:
        print("writing: t=" + time + " c=" + str(0))
    client.write_points(json_body)

    last=None

    for trace in traces:
        for _ in range(trace['repeat']):
            for segment in trace['trace']:
                process_segment(segment)
            last=segment['endCount']

    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    json_body = [{
        "measurement": "userCount",
        "time": time,
        "fields": {
            "userCount": 0
        }
    }]
    if DEBUG:
        print("writing: t=" + time + " c=" + str(0))
    client.write_points(json_body)
    
    stop_load()			

if(COMMAND=='start'):
    generate_load()

elif(COMMAND=='stop'):
    stop_load()
