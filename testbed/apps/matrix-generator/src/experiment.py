from . import utils
from .template import SLAConfigTemplate


class SLAConfigExperiment:
	def __init__(self, exp_config, bin_path, exp_path):
		self.exp_config = exp_config
		self.bin_path = bin_path
		self.exp_path = exp_path

	def setConfig(self,config):
		self.exp_config=config

	def runExperiment(self):
		exp_template=SLAConfigTemplate(self.exp_config)
		exp_template.saveTemplate(self.exp_path+'conf.yaml')
		exit_code=utils.call_cmd(self.bin_path+ ' -e locustbatch' + ' -p mtbestconfig' + ' -c '+self.exp_path+'conf.yaml')
		print('Generating new experiment. Saving results on '+self.exp_path)
		try:
			assert exit_code==0
		except:
			utils.abort("Error executing the experiment. The process returned with error code: "+str(exit_code))


