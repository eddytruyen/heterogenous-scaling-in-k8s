curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_0_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=140&previoustenants=3&previousconf=0_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=140&previoustenants=2&previousconf=0_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=140&previoustenants=2&previousconf=0_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=140&previoustenants=3&previousconf=0_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=190&previoustenants=4&previousconf=0_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=190&previoustenants=4&previousconf=0_0_1_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=190&previoustenants=4&previousconf=0_1_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=190&previoustenants=4&previousconf=0_1_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=4&completiontime=140&previoustenants=4&previousconf=0_2_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=140&previoustenants=4&previousconf=0_2_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=5&previousconf=0_2_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=160&previoustenants=5&previousconf=0_1_1_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=5&completiontime=140&previoustenants=5&previousconf=0_1_1_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=6&completiontime=140&previoustenants=5&previousconf=0_1_1_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=6&completiontime=190&previoustenants=6&previousconf=0_1_1_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=6&completiontime=120&previoustenants=6&previousconf=0_2_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=120&previoustenants=6&previousconf=0_2_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=160&previoustenants=7&previousconf=0_2_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=160&previoustenants=7&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=7&completiontime=140&previoustenants=7&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=8&completiontime=140&previoustenants=7&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=8&completiontime=140&previoustenants=8&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=140&previoustenants=8&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=190&previoustenants=10&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=190&previoustenants=10&previousconf=1_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=190&previoustenants=10&previousconf=1_1_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=10&completiontime=140&previoustenants=10&previousconf=2_0_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=140&previoustenants=10&previousconf=2_0_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=190&previoustenants=9&previousconf=1_0_1_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=190&previoustenants=9&previousconf=1_1_0_2" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=9&completiontime=140&previoustenants=9&previousconf=1_1_0_3" | jq '.'
sleep 1
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=14&completiontime=140&previoustenants=9&previousconf=1_1_0_3" | jq '.'
sleep 1

