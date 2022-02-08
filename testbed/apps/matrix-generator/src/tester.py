#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import utils
import sys
import argparse, textwrap
import os


parser = argparse.ArgumentParser(

description='Workload generator using Locust',
        usage='"%(prog)s <command> <arg>". Use  "python %(prog)s --help" o "python %(prog)s -h" for more information',
        formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("file",
help= textwrap.dedent('''\
	start: 		Start generating the workload
	stop:		Stop Locust swarm

'''))

args = parser.parse_args()


configfile = args.file

config_data = yaml.safe_load(open(configfile))


def test():
    directory=config_data['outputDir']


    params=[{param['name']: param['searchspace']['max']} for param in config_data['slas'][0]['parameters']]
    print(params)
    report='Ressdsd \n'

    for param in params:
        for k,v in param.items():
            report+=(k+'\t')
    report+='score \n'

    for param in params:    
        for k,v in param.items():
            report+=(str(v)+'\t')
    report+='1'        

    utils.saveToFile(report,directory+'/report.csv')    


test()