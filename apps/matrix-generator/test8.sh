curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=190&previoustenants=10&previousconf=1_1_0_0" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=90&previoustenants=3&previousconf=1_1_0_0" | jq '.'

