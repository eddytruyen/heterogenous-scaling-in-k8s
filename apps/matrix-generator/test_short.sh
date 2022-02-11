echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=181&previoustenants=1&previousconf=0_0_0_3" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=181&previoustenants=1&previousconf=0_0_0_3" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=127&previoustenants=1&previousconf=0_0_2_2" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=127&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=127&previoustenants=2&previousconf=0_1_2_0" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=127&previoustenants=2&previousconf=0_1_2_0" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=3&previousconf=0_1_2_0" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=3&previousconf=0_1_2_0" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=4&previousconf=0_0_2_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=4&previousconf=0_0_2_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=154&previoustenants=5&previousconf=0_1_1_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=154&previoustenants=5&previousconf=0_1_1_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=149&previoustenants=5&previousconf=0_2_0_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=149&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=144&previoustenants=5&previousconf=1_1_0_0" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=144&previoustenants=5&previousconf=1_1_0_0" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=155&previoustenants=4&previousconf=0_1_1_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=155&previoustenants=4&previousconf=0_1_1_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=123&previoustenants=3&previousconf=0_2_0_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=123&previoustenants=3&previousconf=0_2_0_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=119&previoustenants=2&previousconf=0_2_0_1" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=119&previoustenants=2&previousconf=0_2_0_1" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=129&previoustenants=1&previousconf=0_1_1_2" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=129&previoustenants=1&previousconf=0_1_1_2" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=120&previoustenants=1&previousconf=0_0_2_2" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=120&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=1&previousconf=0_0_2_2" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
echo 'curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=156&previoustenants=2&previousconf=0_1_2_0" | jq '.''
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=156&previoustenants=2&previousconf=0_1_2_0" | jq '.'
sleep 1
