from . import generator
from . import utils
from .searchwindow import AdaptiveWindow

class RuntimeManager:
    def __init__(self,adaptive_scaler,tenant_nb, runtime_manager, adaptive_window, minimum_shared_replicas, maximum_transition_cost, minimum_shared_resources):
        self.adaptive_scaler=adaptive_scaler
        self.tenant_nb=tenant_nb
        self.raw_experiments=[]
        self.experiments={} #{1..n, [experiment_specification,samples: [conf]]}
        self.current_experiment={"experiment_nb":0,"sample_nb":0}
        self.finished=True
        self.sorted_combinations=[]
        self.runtime_manager=runtime_manager
        self.adaptive_scalers=runtime_manager["adaptive_scalers"]
        self.tipped_over_results=[]
        self.last_experiment={}#{"experiment_spec": experiment_spec, "experiment_nb": experiment_nb, "sample_nb": sample_nb, "sample": next_exp}
        self.previous_returned_experiment={}
        self.initial_window=adaptive_window.get_current_window()
        self.adaptive_window=adaptive_window
        self.minimum_shared_replicas=minimum_shared_replicas
        self.maximum_transition_cost=maximum_transition_cost
        self.minimum_shared_resources=minimum_shared_resources
        self.list_of_results=[]
        self.last_result={}
        self.current_min_shrd_replicas=-1
        self.current_min_shrd_resources={}
        for key in minimum_shared_resources.keys():
            self.current_min_shrd_resources[key]=-1
        self.pushed_back_results=[]
        self.already_retuned=False

    def copy_to_tenant_nb(self, tenant_nb):
        rm=RuntimeManager(self.adaptive_scaler.clone(start_fresh=True),tenant_nb,self.runtime_manager, AdaptiveWindow(self.initial_window),self.minimum_shared_replicas,self.maximum_transition_cost, dict(self.minimum_shared_resources))
        rm.sorted_combinations=self.sorted_combinations[:]
        return rm

    def reset(self):
        self.experiments={}
        self.current_experiment={"experiment_nb":0,"sample_nb":0}
        self.finished=True
        #self.sorted_combinations=[]
        self.tipped_over_results=[]
        self.last_experiment={}
        self.previous_returned_experiment={}
        self.adaptive_window.adapt_search_window({},self.initial_window,self.tenant_nb == 1)

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

    def set_raw_experiments(self, experiments):
        self.raw_experiments=experiments

    def get_raw_experiments(self):
        return self.raw_experiments
    
    def set_experiment_list(self, experiment_nb, experiment_specification, samples):
        self.finished=False
        self.experiments[experiment_nb]=[experiment_specification,samples]

    def conf_in_samples(self, conf, samples):
        return conf in [generator.get_conf(self.adaptive_scaler.workers,r) for r in samples]

    def conf_in_experiments(self,conf):
        for exp in self.experiments.values():
            if  self.conf_in_samples(conf,exp[1]):
                return True
        return False

    def remove_sample_for_conf(self,conf):
        print("Runtime manager:: Removing sample for the following conf: [" + utils.array_to_delimited_str(conf, ",") + "]")  
        found=False
        for exp_nb in self.experiments.keys():
            if exp_nb in self.experiments.keys() and self.conf_in_samples(conf,self.experiments[exp_nb][1]):
                found=True
                print("Runtime manager:: Sample list before remove:")
                for exp_nb_tmp in self.experiments.keys():
                    print([generator.get_conf(self.adaptive_scaler.workers, r) for r in self.experiments[exp_nb_tmp][1]])
                already_next_current_experiment=False
                sample_nb=self.get_nb_of_sample_for_conf(exp_nb,conf)
                experiment_spec=self.experiments[exp_nb][0]
                experiment_nb=exp_nb
                next_exp=self.experiments[exp_nb][1][sample_nb]
                if exp_nb == self.get_current_experiment_nb():
                    if sample_nb < self.get_current_sample_nb():
                        self.previous_current_experiment()
                    elif sample_nb == self.get_current_sample_nb() and sample_nb == self.get_total_nb_of_samples(exp_nb)-1:
                        print("Runtime manager:: Going to next experiment")
                        self.next_current_experiment()
                        already_next_current_experiment=True
                print("Runtime manager:: Sample list after remove:")
                if not self.no_experiments_left():
                    (self.experiments[exp_nb][1]).pop(self.get_nb_of_sample_for_conf(exp_nb,conf))
                for exp_nb_tmp in self.experiments.keys():
                    print([generator.get_conf(self.adaptive_scaler.workers, r) for r in self.experiments[exp_nb_tmp][1]])
                if (exp_nb == self.get_current_experiment_nb()):
                    if (not already_next_current_experiment) and self.get_total_nb_of_samples(exp_nb) == 0:
                        print("Runtime manager:: Going to next experiment")
                        self.next_current_experiment()
                #elif (not already_next_current_experiment) and self.get_total_nb_of_samples(exp_nb) == 0:
                    #remove exp_nb from self.experiments? NO
        if found and self.no_experiments_left() and not self.last_experiment:
            print("Runtime manager:: No experiments left.")
            if self.previous_returned_experiment:
                self.last_experiment=self.previous_returned_experiment
            else:
                self.last_experiment={"experiment_spec": experiment_spec, "experiment_nb": experiment_nb, "sample_nb": sample_nb, "sample": next_exp}
            print("Runtime manager:: last_executed_experiment:")
            print(self.last_experiment)

    def update_experiment_list(self, experiment_nb, experiment_specification, samples):
        experiment=self.experiments[experiment_nb]
        experiment[0]=experiment_specification
        for sample in samples:
            sample_index=self.get_nb_of_sample_for_conf(experiment_nb, generator.get_conf(self.adaptive_scaler.workers,sample))
            if sample_index >= 0:
                experiment[1][sample_index]=sample

    def get_current_experiment_specification(self):
        exp=self.last_experiment_in_queue()
        if exp:
            return exp["experiment_spec"]
        else:
            experiment_nb=self.get_current_experiment_nb()
            return self.experiments[experiment_nb][0]

    def get_current_experiment_nb(self):
        exp=self.last_experiment_in_queue()
        if exp:
            return exp["experiment_nb"]
        else:
            return self.current_experiment["experiment_nb"]

    def get_nb_of_experiment_for_conf(self,conf):
        for exp_nb in self.experiments.keys():
            if self.conf_in_samples(conf,self.experiments[exp_nb][1]):
                return exp_nb
        return -1

    def get_experiment_specification_for_experiment_nb(self, experiment_nb):
        if experiment_nb in self.experiments.keys():
            return self.experiments[experiment_nb][0]
        else:
            return None


    def get_nb_of_sample_for_conf(self,experiment_nb,conf):
        if self.conf_in_experiments(conf):
            for i, elem in enumerate([generator.get_conf(self.adaptive_scaler.workers,r) for r in self.experiments[experiment_nb][1]]):
                if generator.equal_conf(conf, elem):
                    return i
        return -1

    def get_current_sample(self):
        exp=self.last_experiment_in_queue()
        if exp:
            return exp["sample"]
        else:
            return self.experiments[self.get_current_experiment_nb()][1][self.get_current_sample_nb()]

    def get_current_sample_nb(self):
        exp=self.last_experiment_in_queue()
        if exp:
            return exp["sample_nb"]
        else:
            return self.current_experiment["sample_nb"]

    def get_total_nb_of_experiments(self):
        return len(self.experiments.keys())

    def get_total_nb_of_samples(self, experiment_nb):
        if experiment_nb < self.get_total_nb_of_experiments():
            return len(self.experiments[experiment_nb][1])
        else:
            return -1

    def get_next_sample(self):
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        next_exp=self.experiments[experiment_nb][1][sample_nb]
        experiment_spec=self.experiments[experiment_nb][0]
        self.previous_returned_experiment={"experiment_spec": experiment_spec, "experiment_nb": experiment_nb, "sample_nb": sample_nb, "sample": next_exp}
        self.next_current_experiment()
        if self.no_experiments_left():
            self.last_experiment={"experiment_spec": experiment_spec, "experiment_nb": experiment_nb, "sample_nb": sample_nb, "sample": next_exp}
        return next_exp

    def last_experiment_in_queue(self):
        return self.last_experiment

    def get_left_over_configs(self):
        experiment_nb=self.get_current_experiment_nb()
        sample_nb=self.current_experiment["sample_nb"]
        if sample_nb < self.get_total_nb_of_samples(experiment_nb):
            lst=self.experiments[experiment_nb][1][sample_nb:]
        else:
            lst=[]
        while experiment_nb < self.get_total_nb_of_experiments()-1:
            experiment_nb+=1
            lst+=self.experiments[experiment_nb][1]
        return [generator.get_conf(self.adaptive_scaler.workers,s) for s in lst]   


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
        if self.finished and self.last_experiment:
            self.set_experiment_list(self.last_experiment["experiment_nb"],self.last_experiment["experiment_spec"], [self.last_experiment["sample"]])
            self.current_experiment={"experiment_nb": self.last_experiment["experiment_nb"], "sample_nb": 0}
            self.last_experiment={}
        else:
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


    def add_tipped_over_result(self, results):
        self.tipped_over_results+=[results]

    def get_tipped_over_results(self, nullify=True):
        results=[]
        workers=[]
        for tor in self.tipped_over_results:
            results+=tor["results"]
            workers+=[[w.clone() for w in tor["workers"]]]
        if nullify:
            self.tipped_over_results=[]
        return {"workers": workers, "results": results}

    def remove_tipped_over_result(self, conf):
        print("Removing " + str(conf) + " from tipped_over_results in rm")
        found=False
        index=0
        while not found and index < len(self.tipped_over_results):
            tor=self.tipped_over_results[index]
            if conf == tor["results"]:
                found=True
            else:
                index+=1
        if found:
            print("Found and removed")
            del self.tipped_over_results[index]


    def get_adaptive_window(self):
        return self.adaptive_window

    def add_result(self,result,tenant_nb,nb_shrd_replicas=None, shrd_resources=None):
        if not nb_shrd_replicas==None and not shrd_resources==None:
            if self.current_min_shrd_replicas == -1 or  nb_shrd_replicas < self.current_min_shrd_replicas:
                self.current_min_shrd_replicas=nb_shrd_replicas
            for key in shrd_resources.keys():
                if self.current_min_shrd_resources[key] == -1 or shrd_resources[key] < self.current_min_shrd_resources[key]:
                    self.current_min_shrd_resources[key]=shrd_resources[key]
        #workers_result=[w.clone() for w in self.adaptive_scalers["init"].workers]
        #resource_types=self.adaptive_scalers["init"].workers[0].resources.keys()
        #for w in workers_result:
        #     w.resources=generator.extract_resources_from_result(result, w.worker_id, resource_types)
        self.set_last_sampled_result(result, tenant_nb, nb_shrd_replicas, shrd_resources)
        self.list_of_results.append(self.get_last_sampled_result())

    def get_results(self):
        return self.list_of_results

    def set_last_sampled_result(self,result,tenant_nb, nb_shrd_replicas=None, shrd_resources=None):
        self.runtime_manager['last_tenant_nb'] = tenant_nb
        workers_result=[w.clone() for w in self.adaptive_scaler.workers]
        resource_types=self.adaptive_scaler.workers[0].resources.keys()
        for w in workers_result:
             w.resources=generator.extract_resources_from_result(result, w.worker_id, resource_types)
        self.last_result={"conf": generator.get_conf(workers_result, result), "CompletionTime": float(result['CompletionTime']), "workers": workers_result, "nb_shrd_replicas": nb_shrd_replicas, "shrd_resources": shrd_resources}


    def get_last_sampled_result(self):
        return dict(self.last_result)
    
    def equal_workers(self,workersA,workersB):
                if len(workersA) != len(workersB):
                        return False
                for a,b in zip(workersA,workersB):
                        if not a.equals(b):
                              return False
                return True

    def result_is_stored(self, workers, result):
        found=False
        for r in self.list_of_results:
            if  float(result["CompletionTime"]) == r["CompletionTime"] and generator.get_conf(workers,result) == r["conf"] and self.equal_workers(workers, r["workers"]):
                    found=True
                    break
        return found


    def conf_X_workers_has_been_sampled_already(self, conf, workers):
        found=False
        for r in self.list_of_results:
            if  conf == r["conf"] and self.equal_workers(workers, r["workers"]):
                    print(utils.array_to_delimited_str(conf,"_") + " has already been sampled for the following workers:")
                    for w in workers:
                        print(w.resources)
                    found=True
                    break
        return found

    def get_result(self, conf, workers):
         for r in self.list_of_results:
            if  conf == r["conf"] and self.equal_workers(workers, r["workers"]):
                return r
         return None   

    def add_pushed_back_result(self, result, nb_shrd_replicas=None, shrd_resources=None):
        workers_result=[w.clone() for w in self.adaptive_scaler.workers]
        self.pushed_back_results+=[{"conf": generator.get_conf(workers_result, result), "CompletionTime": float(result['CompletionTime']), "workers": workers_result, "nb_shrd_replicas": nb_shrd_replicas, "shrd_resources": shrd_resources}]


    def remove_pushed_back_results_after_retuning(self):
        print("Removing the folloing pushed back results:")
        tmp_pushed_back_results=self.pushed_back_results[:]
        for pbr in tmp_pushed_back_results:
            if pbr["nb_shrd_replicas"] >= self.minimum_shared_replicas:
                self.pushed_back_results.remove(pbr)
                print(pbr)
            else:
                for res in self.minimum_shared_resources.keys():
                    if pbr["shrd_resources"][res] >= self.minimum_shared_resources[res]:
                        self.pushed_back_results.remove(pbr)
                        print(prb)
                        break



    def conf_X_workers_has_been_pushed_back_already(self, conf, workers):
        found=False
        for r in self.pushed_back_results:
            if  conf == r["conf"] and self.equal_workers(workers, r["workers"]):
                    print(utils.array_to_delimited_str(conf,"_") + " has already been pushed back for the following workers:")
                    for w in workers:
                        print(w.resources)
                    found=True
                    break
        return found


    def retune(self):
        tenant_success=False
        if not self.adaptive_scaler.already_adapted_shared_resources_during_scaling_down:
            if self.minimum_shared_replicas > 0:
                print("!!!!!!!!!!Reducing minimum shared replicas from " + str(self.minimum_shared_replicas) + " to " + str(self.minimum_shared_replicas-1))
                self.adaptive_scaler.already_adapted_shared_resources_during_scaling_down=True
                self.minimum_shared_replicas=self.minimum_shared_replicas-1
                tenant_success=True
            for res in self.minimum_shared_resources.keys():
                if self.minimum_shared_resources[res] > 0:
                    print("!!!!!!!!!!Reducing minimum shared resources for " + res + " from " + str(self.minimum_shared_resources[res]) + " to " + str(self.minimum_shared_resources[res]-self.adaptive_scaler.increments[res]))
                    self.adaptive_scaler.already_adapted_shared_resources_during_scaling_down=True
                    self.minimum_shared_resources[res]=self.minimum_shared_resources[res]-self.adaptive_scaler.increments[res]
                    tenant_success=True
            if tenant_success:
                print("!!!!!Removing pushed back results with an equal amount of shared resources as the reduced minimum")
                self.remove_pushed_back_results_after_retuning()
                print("!!!!Setting already_retuned flag")
                self.already_retuned=True
        else:
            print("Already reduced shared resources during scaling down for " + str(tx) + " tenants")
        return tenant_success


def instance(runtime_manager, tenant_nb, window):
    if not tenant_nb in runtime_manager.keys():
        runtime_manager[tenant_nb] = RuntimeManager(runtime_manager["adaptive_scalers"]["init"].clone(start_fresh=True),tenant_nb, runtime_manager, AdaptiveWindow(window), runtime_manager["minimum_shared_replicas"], runtime_manager["maximum_transition_cost"], runtime_manager["minimum_shared_resources"])
    return runtime_manager[tenant_nb]


