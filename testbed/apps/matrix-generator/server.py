from flask import Flask
from flask import request
import math
import yaml
import json

app = Flask(__name__)

@app.route("/conf")
def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')

    config_data = yaml.safe_load(open('data/single-replica.yaml'))

    if (int(tenants) > 10):
        ten = int(tenants)
        resp_time = -24.17472*ten+2484.84
        cpu_perc = (0.5615677*ten)/(ten-0.3465281)
        cpu_usage = 229.67486 * ten - 10.92843
        cpu_req = 397.79336 * ten - 86.78253

        req = cpu_usage * resp_time / 2500
        lim = min(req/cpu_perc, cpu_req)

        pods = math.ceil(lim / 250)

        t = {
            "config": "0",
            "demoCPU": "800",
            "score": "0.65",
            "worker1CPU": "2200",
            "worker1Replicas": "0", 
            "worker2CPU": "750", 
            "worker2Replicas": "0", 
            "worker3CPU": "250", 
            "worker3Replicas": pods
        }

        print(json.dumps(t))

        return json.dumps(t)
    else:
        conf=config_data[str(namespace)][str(tenants)]
        return json.dumps(conf)
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=80,debug=True)