curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=160&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_2_0_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_0_2" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=160&previoustenants=3&previousconf=0_1_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=120&previoustenants=3&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=3&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=4&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=4&previousconf=0_2_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=160&previoustenants=4&previousconf=0_1_2_0" | jq '.' > test.json
sleep 10
echo '{
  "CompletionTime": "120",
  "SLAName": "silver",
  "Successfull": "true",
  "best_score": "-0.24",
  "config": "0",
  "score": "-0.24",
  "worker1.replicaCount": "0",
  "worker1.resources.requests.cpu": "6",
  "worker1.resources.requests.memory": "4",
  "worker2.replicaCount": "2",
  "worker2.resources.requests.cpu": "4",
  "worker2.resources.requests.memory": "2",
  "worker3.replicaCount": "1",
  "worker3.resources.requests.cpu": "4",
  "worker3.resources.requests.memory": "2",
  "worker4.replicaCount": "0",
  "worker4.resources.requests.cpu": "1",
  "worker4.resources.requests.memory": "2"
}' > test2.json
cat test.json
diff test.json test2.json
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=160&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=4&previousconf=0_1_1_1" | jq '.'
sleep 10
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=2&previousconf=0_2_0_0" | jq '.' > test.json
sleep 10
echo '{
  "CompletionTime": "140",
  "SLAName": "silver",
  "Successfull": "true",
  "best_score": "-0.15384615384615385",
  "config": "0",
  "score": "-0.15384615384615385",
  "worker1.replicaCount": "0",
  "worker1.resources.requests.cpu": "6",
  "worker1.resources.requests.memory": "4",
  "worker2.replicaCount": "2",
  "worker2.resources.requests.cpu": "4",
  "worker2.resources.requests.memory": "2",
  "worker3.replicaCount": "0",
  "worker3.resources.requests.cpu": "4",
  "worker3.resources.requests.memory": "2",
  "worker4.replicaCount": "0",
  "worker4.resources.requests.cpu": "2",
  "worker4.resources.requests.memory": "2"
}' > test2.json
cat test.json
diff test.json test2.json