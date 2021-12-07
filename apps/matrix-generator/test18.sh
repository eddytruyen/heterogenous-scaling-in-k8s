# Remove tipped_over_intermediate_results"
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=231&previoustenants=9&previousconf=0_2_0_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=160&previoustenants=9&previousconf=0_2_1_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=159&previoustenants=9&previousconf=0_3_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=154&previoustenants=9&previousconf=0_2_1_0" | jq '.'
