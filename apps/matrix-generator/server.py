from flask import Flask
from flask import request
import yaml
import json



config_data = yaml.safe_load(open('data/single-replica.yaml'))


app = Flask(__name__)

@app.route("/conf")
def home():
    namespace = request.args.get('namespace')
    tenants = request.args.get('tenants')

    conf=config_data[str(namespace)][str(tenants)]
    return json.dumps(conf)
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=80,debug=True)