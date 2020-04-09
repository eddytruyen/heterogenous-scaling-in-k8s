import matplotlib
matplotlib.use('PS')
import json
from json import JSONEncoder
import GPy
import GPyOpt
from numpy.random import seed
import numpy as np 
import sys


class Parameter:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class K8ResOpt:
    def __init__(self, domain, domainValues, scores, exact_eval):
        self.domain = domain
        
        self.domainValues = np.array(domainValues) #np.array([self.normalize(xi) for xi in ])
        print(self.domainValues)
        self.scores = np.array(scores)
        self.exact_eval = exact_eval
    
    @classmethod
    def fromJsonFile(cls, path):
        with open(path, 'r') as f: 
            dict = json.load(f)
            return cls(**dict)
    
    def nextSampleSuggestion(self, outputLocationPlot):
        bo_step = GPyOpt.methods.BayesianOptimization(f = None, domain = self.domain, X = self.domainValues,normalize_Y=False, Y = self.scores, 
            initial_design_numdata = len(self.domainValues), exact_feval=self.exact_eval)
        next = bo_step.suggest_next_locations()
        bo_step.plot_acquisition(filename=outputLocationPlot)
        return next

    def outputSampleSuggestionAsJson(self, next, outputLocationSuggestions):
        parameters = list()
        next = next.flatten().tolist()
        
        for d in range(len(next)):
            parameters.append(Parameter(self.domain[d]["name"], next[d]))
        
        with open(outputLocationSuggestions, 'w') as outfile:
            json.dump([par.__dict__ for par in parameters], outfile)

        
        return parameters

    def normalize(self, value):
        return value / 1000.0
    
        


seed(1234)
# first cmd line arg is the input file
inputfile = sys.argv[1]
# second cmd line arg is the output location for suggestions
outputLocationSuggestions = sys.argv[2]
# third cmd line arg is the output location for the aquisition function plit
outputLocationPlot = sys.argv[3]
optimizer = K8ResOpt.fromJsonFile(inputfile)
optimizer.outputSampleSuggestionAsJson(optimizer.nextSampleSuggestion(outputLocationPlot),outputLocationSuggestions)








