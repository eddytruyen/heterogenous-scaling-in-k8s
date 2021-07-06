#!/bin/bash
COMPONENT=$1
DOCKERACCOUNT="matthijskaminski"
mvn clean package
./mvnw dockerfile:build
echo $DOCKERACCOUNT"/"$COMPONENT":latest"   
docker push $DOCKERACCOUNT"/"$COMPONENT":latest"     