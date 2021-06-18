from flask import Flask
from flask import request
from flask import current_app
import yaml
import json
import matrix
from src.searchwindow import AdaptiveScaler, ScalingFunction
from src.sla import WorkerConf

NODES=[[4,8],[8,32],[8,32],[8,32],[8,16],[8,16],[8,16],[3,6]]


def create_app():
    app = Flask(__name__)
    #app.config.from_object("settings")

    #app.add_url_rule("/conf", view_func=home)
    #app.add_url_rule("/movies", view_func=views.movies_page)

    #db = Database()
    #db.add_movie(Movie("Slaughterhouse-Five", year=1972))
    #db.add_movie(Movie("The Shining"))
    initial_config=yaml.safe_load(open("conf/matrix-spark.yaml"))

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == 'silver':
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

    app.config["adaptive_scaler"] = adaptive_scaler
    app.config["initial_config"] = initial_config

    return app

app = create_app()

if __name__ == "__main__":
    port = app.config.get("PORT",80)
    app.run(host= '0.0.0.0',port=port,debug=True)


@app.route("/conf")
def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')
    completion_time = request.args.get('completiontime')
    previous_tenants = request.args.get('previoustenants')
    previous_conf = request.args.get('previousconf')

    adaptive_scaler=current_app.config["adaptive_scaler"]
    initial_config=current_app.config["initial_config"]

    slas=initial_config['slas']
    for s in slas:
        if s['name'] == namespace:
            sla=s

    matrix.generate_matrix(initial_config, adaptive_scaler, namespace, tenants, completion_time, previous_tenants,previous_conf)

    config_data = yaml.safe_load(open('Results/matrix.yaml'))
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)

