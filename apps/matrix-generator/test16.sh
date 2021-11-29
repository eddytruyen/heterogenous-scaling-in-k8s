# test "NO SAMPLES LEFT, ASKING K8-RESOURCE-OPTIMIZER FOR OTHER SAMPLES"
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=0_1_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=0_1_0_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=0_1_1_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=5&previousconf=0_2_1_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=140&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=140&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=160&previoustenants=5&previousconf=0_3_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=7&previousconf=0_3_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=120&previoustenants=7&previousconf=1_2_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=140&previoustenants=5&previousconf=1_2_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=1_1_1_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=1_1_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=190&previoustenants=5&previousconf=1_2_0_0" | jq '.'

