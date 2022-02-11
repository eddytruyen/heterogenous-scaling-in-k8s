curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=181&previoustenants=1&previousconf=0_0_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=127&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=127&previoustenants=2&previousconf=0_1_2_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=120&previoustenants=3&previousconf=0_1_2_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=4&previousconf=0_0_2_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=154&previoustenants=5&previousconf=0_1_1_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=149&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=144&previoustenants=5&previousconf=1_1_0_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=155&previoustenants=4&previousconf=0_1_1_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=123&previoustenants=3&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=119&previoustenants=2&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=129&previoustenants=1&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=120&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=156&previoustenants=2&previousconf=0_1_2_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=156&previoustenants=3&previousconf=0_1_2_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=130&previoustenants=4&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=127&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=6&completiontime=121&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=132&previoustenants=6&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=8&completiontime=157&previoustenants=7&previousconf=0_2_1_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=132&previoustenants=8&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=158&previoustenants=9&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=181&previoustenants=10&previousconf=1_1_1_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=166&previoustenants=10&previousconf=1_1_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=161&previoustenants=10&previousconf=1_1_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=8&completiontime=172&previoustenants=9&previousconf=1_1_1_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=158&previoustenants=8&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=6&completiontime=174&previoustenants=7&previousconf=1_0_1_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=136&previoustenants=6&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=129&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=142&previoustenants=4&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=211&previoustenants=3&previousconf=0_0_3_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=169&previoustenants=2&previousconf=0_1_2_0" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=180&previoustenants=1&previousconf=0_0_2_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=121&previoustenants=1&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1&completiontime=119&previoustenants=1&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=118&previoustenants=1&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=121&previoustenants=2&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=234&previoustenants=3&previousconf=0_0_3_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=117&previoustenants=4&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=124&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=122&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=123&previoustenants=5&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=116&previoustenants=4&previousconf=0_2_0_1" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=237&previoustenants=3&previousconf=0_0_3_1" | jq '.'
sleep 1

