import os
import sys
import yaml
import subprocess
from functools import reduce

def file_exists(n):
	return os.path.isfile(n)

# Extracted from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-in-any-base-to-a-string
def number_to_base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def array_to_str(arr):
    if len(arr)>1:
        return reduce(lambda a, b: str(a)+str(b), arr)
    else:
        return str(arr[0])

def array_to_delimited_str(arr, delimiter=';'):
    if len(arr)>1:
        return reduce(lambda a, b: str(a)+ delimiter + str(b), arr)
    else:
        return str(arr[0])


def abort(msg):
	print(msg)
	sys.exit(1)		

def call_cmd(commands):
	p = subprocess.check_output(commands.split())
	return 0

def saveToFile(obj,path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(path, "w") as text_file:
        text_file.write(obj)

def saveToYaml(obj,path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(path, 'w') as outfile:
        yaml.dump(obj, outfile, default_flow_style=False)

def readFile(path):
    with open(path,'r') as f:
        content = f.read()
    return content           
