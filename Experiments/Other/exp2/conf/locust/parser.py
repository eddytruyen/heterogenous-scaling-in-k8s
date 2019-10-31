#based on : http://www.andymboyle.com/2011/11/02/quick-csv-to-json-parser-in-python/ 

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
