#test ("UPDATING RUNTIME MANAGER HIGHER NB OF TENANTS: " + str(i)
# met tmp_adaptive_scaler2.ScalingDownPhase and tmp_adaptive_scaler2.StartScalingDown == True
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=1&previousconf=0_1_0_0" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_0_1_2"| jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_1_1" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=160&previoustenants=3&previousconf=0_0_1_3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=190&previoustenants=3&previousconf=0_1_0_3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3&completiontime=120&previoustenants=3&previousconf=1_0_0_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_0_1_3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_0_3" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=2&completiontime=190&previoustenants=2&previousconf=0_1_1_2" | jq '.'
sleep 3
curl "http://172.17.13.119:80/conf?namespace=silver&tenants=3" | jq '.'

