from jinja2 import Environment, FileSystemLoader, PackageLoader
from parser import ConfigParser
import utils
import yaml



class SLAConfigTemplate:
  def __init__(self, config):
    self.config = config.parseConfig()
    JINJA_ENV = Environment(loader = PackageLoader('src.template'), trim_blocks=True, lstrip_blocks=True)
    self.template=JINJA_ENV.get_template('template.yaml')

  def renderTemplate(self):
    return self.template.render(self.config)

  def setConfig(self,config):
    self.config=config

  def saveTemplate(self,path):
    utils.saveToFile(self.renderTemplate(),path)



#Load data from YAML into Python dictionary

# c=ConfigParser(
# 	optimizer='exhastive',
# 	prev_results='test/prev',
# 	chart_dir='chartDir',
# 	util_func= 'resourceBased',
# 	samples= 4,
# 	output= 'adasdol',
# 	slas=[{
# 		'tenants': 5,
# 		'class': 'gold',
# 		'demoCPU': 500,
# 		'slos':{
# 			'jobsize': 100,
# 			'throughput': 0.5
# 		},
# 		'workers': [
# 			{'id':1,
# 			'cpu':200,
# 			'replicas':{
# 				'min':0,
# 				'max':2
# 			}},
# 			{'id':2,
# 			'cpu':200,
# 			'replicas':{
# 				'min':0,
# 				'max':2
# 			}}]},
# 			{
# 		'tenants': 5,
# 		'class': 'silver',
# 		'demoCPU': 700,
# 		'slos':{
# 			'jobsize': 100,
# 			'throughput': 0.5
# 		},
# 		'workers': [
# 			{'id':1,
# 			'cpu':200,
# 			'replicas':{
# 				'min':0,
# 				'max':2
# 			}},
# 			{'id':2,
# 			'cpu':200,
# 			'replicas':{
# 				'min':0,
# 				'max':2
# 			}}]
# 	}]	
# )

# t=SLAConfigTemplate(c.parseConfig())

# print(t.renderTemplate())