# Remove tipped_over_intermediate_results"
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=229&previoustenants=1&previousconf=0_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=167&previoustenants=2&previousconf=0_0_1_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=145&previoustenants=3&previousconf=0_1_0_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=263&previoustenants=3&previousconf=0_0_0_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=238&previoustenants=2&previousconf=0_0_0_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=143&previoustenants=1&previousconf=0_0_1_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=170&previoustenants=2&previousconf=0_0_0_3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
