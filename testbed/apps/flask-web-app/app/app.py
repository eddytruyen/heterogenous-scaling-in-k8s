import os
from flask import Flask
from datetime import datetime
from influxdb import InfluxDBClient

app = Flask(__name__)

app.debug = True

INFLUXDB_HOST = 'monitoring-influxdb.kube-system.svc.cluster.local'
INFLUXDB_PORT = 8086

@app.route('/')
def hello_thesis():
    return "Hello, this is the home page of my thesis! v1"

@app.route('/create-influx')
def create_influx():
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)  # Hard coded, could be improved
    client.create_database('flask-data')
    return "done"

@app.route('/list-influx-dbs')
def list_dbs():
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    print(client.get_list_database())
    return "done"

@app.route('/post-influxdb/<float:current_value>')
def post_new_val(current_value):
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    client.switch_database("flask-data")
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    json_body = [{
        "measurement": "sampleEvents",
        "time": time[0],
        "tags": {
            "podName": os.getenv('CURRENT_POD_NAME', 'Unknown'),
            "nodeName": os.getenv('CURRENT_NODE_NAME', 'Unknown')
        },
        "fields": {
            "value": current_value
        }
    }]
    client.write_points(json_body)
    return json_body[0]

@app.route('/get-vals')
def get_values():
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)    
    client.switch_database("flask-data")
    results = client.query('SELECT * FROM "flask-data"."autogen"."sampleEvents" WHERE time > now() - 4d')
    print(results.raw)
    return results.raw

if __name__ == '__main__':
    app.run(host='0.0.0.0')