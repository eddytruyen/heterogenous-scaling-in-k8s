curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=160&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_2_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_0_2" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=120&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=160&previoustenants=2&previousconf=0_1_1_0" | jq '.'
sleep 1
