#!/bin/sh
mkdir "locust_results"
LOCUSTSCRIPT=$1
NAME=$2
USERS=$3
HATCH=$4
REQUESTS=$5
PARSESCRIPT=$6
# run locust warmup 
locust -f $LOCUSTSCRIPT --csv=$NAME --no-web -c $USERS -r  $HATCH -n 15
# run locust script
locust -f $LOCUSTSCRIPT --csv=$NAME --no-web -c $USERS -r  $HATCH -n $REQUESTS
# Parse CSV to JSON files
python $PARSESCRIPT "${NAME}_distribution.csv"
python $PARSESCRIPT "${NAME}_requests.csv"