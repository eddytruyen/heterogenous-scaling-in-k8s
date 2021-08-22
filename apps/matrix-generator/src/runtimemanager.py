from . import generator
from . import utils

class RuntimeManager:
    def __init__(self, tenant_nb):
        self.tenant_nb=tenant_nb
        self.experiments={}
        self.current_experiment={"experiment_nb":0,"sample_nb":0}
        self.finished=True
        self.sorted_combinations=[]

    def set_sorted_combinations(self, combinations):
        if not self.sorted_combinations:
            self.sorted_combinations=combinations
            return self.sorted_combinations
        else:
            return self.sorted_combinations

    def get_sorted_combinations(self):
        return self.sorted_combinations

    def update_sorted_combinations(self, combinations):
        self.sorted_combinations=combinations
        return self.sorted_combinations
    
    def set_experiment_list(self, experiment_nb, experiment_specification, samples):
        self.finished=False
        self.experiments[experiment_nb]=[experiment_specification,samples]

    def sample_in_experiments(self,sample):
        for exp in self.experiments.items():
            if sample in exp[1]:
                return True
        return False

    def remove_sample(self,sample):
        for exp_nb in self.experiments.keys():
            if sample in self.experiments[nb][1]:
                if nb == self.get_current_experiment_nb():
                    if self.get_nb_of_sample(nb,sample) < self.get_current_sample_nb():
                        self.next_current_experiment()
                exp[1].remove(sample)   

    def update_experiment_list(self, experiment_nb, experiment_specification, samples):
        self.experiments[experiment_nb]=[experiment_specification,samples]

    def get_current_experiment_specification(self):
        experiment_nb=self.get_current_experiment_nb()
        return self.experiments[experiment_nb][0]

    def get_current_experiment_nb(self):
        return self.current_experiment["experiment_nb"]

    def get_nb_of_sample(self,experiment_nb,sample):
        if self.sample_in_experiments(sample):
            return self.experiments[experiment_nb][1].index(sample)
        else:
            return -1

    def get_current_sample(self):
        return self.experiments[self.get_current_experiment_nb()][1][self.get_current_sample_nb()]

    def get_current_sample_nb(self):
        return self.current_experiment["sample_nb"]

    def get_total_nb_of_experiments(self):
        return len(self.experiments.keys())

    def get_total_nb_of_samples(self, experiment_nb):
        return len(self.experiments[experiment_nb][1])

    def get_next_sample(self):
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        next_exp=self.experiments[experiment_nb][1][sample_nb]
        self.next_current_experiment()
        return next_exp

    def next_current_experiment(self):
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        if sample_nb < self.get_total_nb_of_samples(experiment_nb)-1:
            self.current_experiment["sample_nb"]=sample_nb + 1
        elif experiment_nb < self.get_total_nb_of_experiments()-1:
            self.current_experiment["experiment_nb"]=experiment_nb + 1
            self.current_experiment["sample_nb"]=0
        else:
            self.finished=True
            self.current_experiment={"experiment_nb":0,"sample_nb":0}
    

    def no_experiments_left(self):
        return self.finished


def instance(runtime_manager, tenant_nb):
    if not tenant_nb in runtime_manager.keys():
        runtime_manager[tenant_nb] = RuntimeManager(tenant_nb)
    return runtime_manager[tenant_nb]


