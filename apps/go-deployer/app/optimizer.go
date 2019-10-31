package main
import (
	_	"log"
		"fmt"
)


type TenantCount struct{
	sla string
	number int
}


func getOptimalConf(tenantsCount []TenantCount)  []ConsumerPod{
	var pods []ConsumerPod	

	for _,tenantCount := range tenantsCount{
		optimalConfSLA := tenantCount.sla
		optimalConfNum := tenantCount.number

		optimalConfReplicas := queryMatrix(optimalConfSLA, optimalConfNum)

		for _,pod := range optimalConfReplicas{
			pods = append(pods,pod)
		}
	}
	return pods
}

func getDesiredConf(state map[string]int) []DeploymentScaler{
	var deployments []DeploymentScaler
	var tenants []TenantCount

	for sla,num := range state{
		tenant:=TenantCount{sla,num}
		tenants = append(tenants,tenant)
	}

	pods:=getOptimalConf(tenants)

	for _,pod := range pods{
		consumer:=DeploymentScaler{"consumer"+int2str(pod.id),pod.namespace,pod.replicas}
		deployments = append(deployments,consumer)
	}

	fmt.Printf("%+v\n", deployments)

	return deployments
}