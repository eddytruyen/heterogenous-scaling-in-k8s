curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.' 
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=51&previoustenants=1&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=68&previoustenants=1&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=35&previoustenants=2&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=37&previoustenants=3&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=38&previoustenants=4&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=39&previoustenants=5&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=66&previoustenants=5&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=67&previoustenants=5&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=63&previoustenants=4&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=41&previoustenants=3&previousconf=0_0_0_1" | jq '.'
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=39&previoustenants=2&previousconf=0_0_0_1" | jq '.'

