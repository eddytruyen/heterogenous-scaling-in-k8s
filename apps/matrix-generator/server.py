from flask import Flask
from flask import request
import yaml
import json
import matrix




app = Flask(__name__)

@app.route("/conf")
def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')
    completion_time = request.args.get('completiontime')
    previous_tenants = request.args.get('previoustenants')

    matrix.generate_matrix("conf/matrix-spark.yaml", namespace, tenants, completion_time, previous_tenants)

    config_data = yaml.safe_load(open('Results/matrix.yaml'))
    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=80,debug=True)
