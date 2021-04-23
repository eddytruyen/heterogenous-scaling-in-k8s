from bayes_opt import BayesianOptimization
import json
import sys
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt import UtilityFunction




# the acquistion fuction ucb,..EI 
utility = UtilityFunction(kind='ei', kappa=2.5, xi=0.0)

#json string input argument 
# dict = json.loads(sys.argv[1])
path = sys.argv[1]
with open(path, 'r') as f: 
    dict = json.load(f)
    optimizer = BayesianOptimization(
        f=None,
        pbounds=dict['bounds'], #set max min for parameters
        verbose=2,
        random_state=dict['seed'], #set random seed 
    )

    # register previous samples
    for log in dict['logs']:
        optimizer.register(params=log['params'], target=log['target'])

    # get next suggestion
    next_point_to_probe = optimizer.suggest(utility)
    # suggestion as json to standard output
    print(json.dumps(next_point_to_probe))







