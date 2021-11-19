curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=1&previousconf=0_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_0_1_2"| jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3" | jq '.'
