from . import generator
from . import utils

class RuntimeManager:
    def __init__(self, tenant_nb):
        self.tenant_nb=tenant_nb
        self.experiments={}
        self.current_experiment={"experiment_nb":0,"sample_nb":0}
        self.finished=True
    
    def set_experiment_list(self, experiment_nr, samples):
        self.finished=False
        import pdb; pdb.set_trace()
        self.experiments[experiment_nr]=samples

    def get_next_sample(self):
        experiment_nb=self.current_experiment["experiment_nb"]
        sample_nb=self.current_experiment["sample_nb"]
        next_exp=self.experiments[experiment_nb][sample_nb]
        if sample_nb < len(self.experiments[experiment_nb]):
            self.current_experiment["sample_nb"]=sample_nb + 1
        elif experiment_nb < len(self.experiments.keys()):
            self.current_experiment["experiment_nb"]=experiment_nb + 1
            self.current_experiment["sample_nb"]=0
        else:
            self.experiments={}
            self.finished=True
            self.current_experiment={"experiment_nb":0,"sample_nb":0}
        return next_exp


    def no_experiments_left(self):
        return self.finished


def instance(runtime_manager, tenant_nb):
    if not tenant_nb in runtime_manager.keys():
        runtime_manager[tenant_nb] = RuntimeManager(tenant_nb)
    return runtime_manager[tenant_nb]


