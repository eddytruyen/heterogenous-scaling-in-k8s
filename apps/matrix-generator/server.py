from flask import Flask
from flask import request
import yaml
import json
import matrix
from src.searchwindow import AdaptiveScaler, ScalingFunction
from src.sla import WorkerConf

NODES=[[4,8],[8,32],[8,32],[8,32],[8,16],[8,16],[8,16],[3,6]]


app = Flask(__name__)

@app.route("/conf")
def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')
    completion_time = request.args.get('completiontime')
    previous_tenants = request.args.get('previoustenants')

    initial_config=yaml.safe_load(open("conf/matrix-spark.yaml"))

    slas=initial_config['slas']

    for s in slas:
        if s['name'] == namespace:
            sla=s
    alphabet=sla['alphabet']
    scalingFunction=ScalingFunction(667.1840993,-0.8232555,136.4046126,2,2,True,NODES)
    workers=[WorkerConf(worker_id=i+1, cpu=v['size']['cpu'], memory=v['size']['memory'], min_replicas=0,max_replicas=alphabet['base']-1) for i,v in enumerate(alphabet['elements'])]
    # HARDCODED => make more generic by putting workers into an array
    workers[0].setReplicas(min_replicas=0,max_replicas=0)
    workers[1].setReplicas(min_replicas=0,max_replicas=0)
    workers[2].setReplicas(min_replicas=0,max_replicas=0)
    workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
    #workers[0].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
    adaptive_scaler=AdaptiveScaler(workers, scalingFunction)

    matrix.generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants)
    
    config_data = yaml.safe_load(open('Results/matrix.yaml'))
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=80,debug=True)
