import concurrent.futures
import requests
import json
import random
import pprint
import textwrap


max_tenants=15
tenant_group="g7"
host = "http://172.22.8.106:30898"
headers = {'Content-Type': 'application/json'}

def invoke(command, host, session_id,headers):

    def make_request():
        response = requests.post(f"{host}/sessions/{session_id}/statements", data=json.dumps({'code': command}), headers=headers)
        statement_url = host + response.headers['Location']
        r = requests.get(statement_url, headers=headers)
        status = r.json()['state']
        while status != "available":
            r = requests.get(statement_url, headers=headers)
            status = r.json()['state']
        return r.json()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(make_request)
        result = future.result()
    
    return result


def get_session(host, headers): 
   response = requests.get(f"{host}/sessions", headers=headers)
   sessions = response.json()['sessions']

   session_id=0

   active_sessions=[]
   if len(sessions) > 0:
      # Gebruik de eerste actieve sessie
      active_sessions = list(filter(lambda x: x['kind'] == 'spark' and x['state'] != 'dead',sessions))

      if len(active_sessions) > 0:
         for active_session in active_sessions:
            if active_session['kind']=='spark':
               session_id=active_session['id']
               break
   else:
       data = {'kind': 'spark', 'executorMemory': 6442450944, 'executorCores': 4, 'proxyUser': 'ubuntu', 'conf': {'spark.scheduler.mode': 'FAIR','spark.scheduler.allocation.file': 'file:///opt/bitnami/spark/spark_data/fairscheduler.xml', 'spark.scheduler.pool': 'mypool'}}
      r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
      session_id = r.json()['id']



   # Wacht tot de sessie actief is
   session_url = f"{host}/sessions/{session_id}"
   r = requests.get(session_url, headers=headers)
   status = r.json()['state']
   while status == 'starting':
      r = requests.get(session_url, headers=headers)
      status = r.json()['state']
   return session_id


