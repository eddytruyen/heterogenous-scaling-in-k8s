package locustwrap

import (
	"k8-resource-optimizer/pkg/utils"
)

func createNecessaryFiles(dir string) {
	err := utils.WriteStringToFile(dir+"/parser.py", parseScript)
	check(err)
	err = utils.WriteStringToFile(dir+"/runAndParse.sh", bashrunScript)
	check(err)
}

const userTemplate = `
class Taskset#TENANTID(TaskSet):
	@task
	def pushJob(self):
		with self.client.get("/",name="#NAME", catch_response=True) as resp:
			if resp.content.decode('UTF-8') != "completed all tasks":
				resp.failure("Got wrong response")

class Tenant#TENANTID(HttpLocust):
	weight = #WEIGHT
	host = "#URL"
	min_wait = #MIN
	max_wait = #MAX
	task_set = Taskset#TENANTID

`

const parseScript = `#based on :http://www.andymboyle.com/2011/11/02/quick-csv-to-json-parser-in-python/ 

import csv  
import json
import sys
  
# Open the CSV  
filename = sys.argv[1]
f = open(  sys.argv[1], 'rU' )

if "requests" in filename :
    names = ( "Method","Name","# requests","# failures","Median response time","Average response time","Min response time","Max response time","Average Content Size","Requests/s" )
else: 
    names = ("Name","# requests","50%","66%","75%","80%","90%","95%","98%","99%","100%")
reader = csv.DictReader( f, fieldnames = names)  
next(reader,None) #skip headers
# Parse the CSV into JSON  
out = json.dumps( [ row for row in reader ] )  
# Save the JSON  
f = open( filename + '.json', 'w')  
f.write(out)  
`

const bashrunScript = `#!/bin/sh
LOCUSTSCRIPT=$1
NAME=$2
USERS=$3
HATCH=$4
REQUESTS=$5
PARSESCRIPT=$6
# run locust warmup 
locust -f $LOCUSTSCRIPT --csv=$NAME --no-web -c $USERS -r  $HATCH -t 60 
# run locust script
locust -f $LOCUSTSCRIPT --csv=$NAME --no-web -c $USERS -r  $HATCH -t $REQUESTS 
# Parse CSV to JSON files
python $PARSESCRIPT "${NAME}_distribution.csv"
python $PARSESCRIPT "${NAME}_requests.csv"`
