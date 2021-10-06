curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=190&previoustenants=10&previousconf=1_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=120&previoustenants=10&previousconf=1_1_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=12&previoustenants=10&previousconf=1_1_0_1" | jq '.'
sleep 1000
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=90&previoustenants=2&previousconf=1_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=90&previoustenants=3&previousconf=1_1_0_0" | jq '.'

