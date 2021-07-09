from flask import Flask
from flask import request
from flask import current_app
import yaml
import json
import matrix
from src.searchwindow import AdaptiveScaler, ScalingFunction
from src.sla import WorkerConf
from src.generator import create_workers as _create_workers

NODES=[{"cpu": 4,"memory": 8},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 32},{"cpu": 8,"memory": 16},{"cpu": 8,"memory": 16},{"cpu": 8,"memory": 16},{"cpu": 3,"memory": 6}]

def create_app():
    app = Flask(__name__)
    #app.config.from_object("settings")

    app.add_url_rule("/conf", view_func=matrix.home)
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
    scalingFunction=ScalingFunction(667.1840993,-0.8232555,136.4046126, {"cpu": 2, "memory": 2}, alphabet['costs'], ["cpu"],NODES)
    workers=_create_workers(alphabet['elements'], alphabet['costs'], alphabet['base'])
    # HARDCODED => make more generic by putting workers into an array
    workers[0].setReplicas(min_replicas=0,max_replicas=0)
    workers[1].setReplicas(min_replicas=0,max_replicas=0)
    workers[2].setReplicas(min_replicas=0,max_replicas=0)
    workers[3].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
    #workers[0].setReplicas(min_replicas=1,max_replicas=workers[-1].max_replicas)
    adaptive_scalers={}
    for w in workers:
        adaptive_scalers[w.worker_id]=AdaptiveScaler(workers, scalingFunction)
    app.config["adaptive_scaler"] = adaptive_scalers
    app.config["initial_config"] = initial_config
    app.config["nodes"] = NODES

    return app

app = create_app()

if __name__ == "__main__":
    port = app.config.get("PORT",80)
    app.run(host= '0.0.0.0',port=port,debug=True)



