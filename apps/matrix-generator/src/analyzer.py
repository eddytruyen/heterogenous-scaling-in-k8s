from . import utils

class ExperimentAnalizer:
	def __init__(self, exp_path):
		self.exp_path = exp_path

	def setConfig(self,config):
		self.exp_config=config

	def analyzeExperiment(self):
		content=utils.readFile(self.exp_path+ '/report.csv')
		results=[line.replace('#','') for line in content.split('\n') if line.strip() != '']
		header=results[0].replace("best score", "best_score")
		runs=results[1:]
		values=[]
		score_index=header.index('score')

		for run in runs:
			d={}
			for h,v in zip(header.split(),run.split()):
				d[h]=v
			values.append(d)  

		#scores=[float(val['score']) for val in values]
		#opt_configuration=values[scores.index(max(scores))]
		#return opt_configuration
		return values

