#!/bin/bash
COMPONENT=$1
DOCKERACCOUNT="decomads"
mvn clean package
./mvnw dockerfile:build
echo $DOCKERACCOUNT"/"$COMPONENT":latest"   
docker push $DOCKERACCOUNT"/"$COMPONENT":latest"     
