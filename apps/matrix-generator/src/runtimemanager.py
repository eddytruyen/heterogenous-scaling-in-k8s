from . import generator
from . import utils

class RuntimeManager:
    def __init__(self, tenant_nb, adaptive_scalers):
        self.tenant_nb=tenant_nb
        self.experiments={}
        self.current_experiment={"experiment_nb":0,"sample_nb":0}
        self.finished=True
        self.sorted_combinations=[]
        self.adaptive_scalers=adaptive_scalers

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
        import pdb; pdb.set_trace()
        self.finished=False
        self.experiments[experiment_nb]=[experiment_specification,samples]

    def conf_in_results(self, conf, results):
        return conf in [generator.get_conf(self.adaptive_scalers["init"].workers,r) for r in results]

    def conf_in_experiments(self,conf):
        for exp in self.experiments.values():
            if  self.conf_in_results(conf,exp[1]):
                return True
        return False

    def remove_sample_for_conf(self,conf):
        import pdb; pdb.set_trace()
        for exp_nb in self.experiments.keys():
            if self.conf_in_results(conf,self.experiments[exp_nb][1]):
                if exp_nb == self.get_current_experiment_nb():
                    if self.get_nb_of_sample_for_conf(exp_nb,conf) < self.get_current_sample_nb():
                        self.previous_current_experiment()
                (self.experiments[exp_nb][1]).pop(self.get_nb_of_sample_for_conf(exp_nb,conf))

    def update_experiment_list(self, experiment_nb, experiment_specification, samples):
        experiment=self.experiments[experiment_nb]
        experiment[0]=experiment_specification
        for sample in samples:
            sample_index=self.get_nb_of_sample_for_conf(experiment_nb, generator.get_conf(self.adaptive_scalers["init"].workers,sample))
            if sample_index >= 0:
                experiment[1][sample_index]=sample

    def get_current_experiment_specification(self):
        experiment_nb=self.get_current_experiment_nb()
        return self.experiments[experiment_nb][0]

    def get_current_experiment_nb(self):
        return self.current_experiment["experiment_nb"]

    def get_nb_of_sample_for_conf(self,experiment_nb,conf):
        if self.conf_in_experiments(conf):
            for i, elem in enumerate([generator.get_conf(self.adaptive_scalers["init"].workers,r) for r in self.experiments[experiment_nb][1]]):
                if generator.equal_conf(conf, elem):
                    return i
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
        import pdb; pdb.set_trace()
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        next_exp=self.experiments[experiment_nb][1][sample_nb]
        self.next_current_experiment()
        return next_exp

    def next_current_experiment(self):
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        if sample_nb < self.get_total_nb_of_samples(experiment_nb) - 1:
            self.current_experiment["sample_nb"]=sample_nb + 1
        elif experiment_nb < self.get_total_nb_of_experiments() - 1:
            self.current_experiment["experiment_nb"]=experiment_nb + 1
            self.current_experiment["sample_nb"]=0
            if self.get_total_nb_of_samples(experiment_nb+1) == 0:
                self.next_current_experiment()
        else:
            self.finished=True
            self.experiments={}
            self.current_experiment={"experiment_nb":0,"sample_nb":0}

    def previous_current_experiment(self):
        import pdb; pdb.set_trace()
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        if sample_nb > 0:
            self.current_experiment["sample_nb"]=sample_nb-1
        elif experiment_nb > 0:
            self.current_experiment["experiment_nb"]=experiment_nb-1
            self.current_experiment["sample_nb"]=self.get_total_nb_of_samples(experiment_nb-1)-1
            if self.get_total_nb_of_samples(experiment_nb-1) == 0:
                self.previous_current_experiment()
        else:
            total_exp=self.get_total_nb_of_experiments()
            total_samples=self.get_total_nb_of_samples(total_exp-1)
            self.current_experiment={"experiment_nb": total_exp-1,"sample_nb":total_samples-1}

    def no_experiments_left(self):
        return self.finished


def instance(runtime_manager, tenant_nb):
    if not tenant_nb in runtime_manager.keys():
        runtime_manager[tenant_nb] = RuntimeManager(tenant_nb, runtime_manager["adaptive_scalers"])
    return runtime_manager[tenant_nb]


