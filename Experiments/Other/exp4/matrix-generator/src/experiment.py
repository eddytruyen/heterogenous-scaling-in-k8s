import utils
from template import SLAConfigTemplate


class SLAConfigExperiment:
	def __init__(self, exp_config, bin_path, exp_path):
		self.exp_config = exp_config
		self.bin_path = bin_path
		self.exp_path = exp_path

	def setConfig(self,config):
		self.exp_config=config

	def runExperiment(self):
		exp_template=SLAConfigTemplate(self.exp_config)
		exp_template.saveTemplate(self.exp_path+'/conf.yaml')
		utils.call_cmd(self.bin_path+' '+self.exp_path+'/conf.yaml')
		print('Generating new experiment. Saving results on '+self.exp_path)
		