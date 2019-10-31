package main
import (
	"fmt"
	"log"
	"os"
	"encoding/json"
	"net/url"
	"net/http"
	"strconv"

)

type ConsumerPod struct{
	id int
	namespace string
	replicas int32
}



type OptimalConfMatrix struct{
	optimalConfMatrix   	map[TenantCount][]ConsumerPod
	nbOfElements	int	
}


func queryMatrix(sla string, tenantNum int) []ConsumerPod {
	base, err := url.Parse("http://"+ResourcePlannerHost+"/conf")
	if err != nil {
		return nil
	}

	var result map[string]interface{}

	// Query params
	params := url.Values{}
	params.Add("namespace", sla)
	params.Add("tenants", strconv.Itoa(tenantNum))
	base.RawQuery = params.Encode() 

	fmt.Println("Querying planner for optimal alloc...")
	fmt.Println(base.String())


	resp, err := http.Get(base.String())
	if err != nil {
		log.Fatal(err)
		os.Exit(1)

		return nil

	}
	defer resp.Body.Close()

	json.NewDecoder(resp.Body).Decode(&result)

	var slas []string
	slas = append(slas,"gold") 
	getDeploymentState(slas)

	replica1, _ := strconv.Atoi(result["worker1Replicas"].(string))
	replica2, _ := strconv.Atoi(result["worker2Replicas"].(string))
	replica3, _ := strconv.Atoi(result["worker3Replicas"].(string))

	consumer1 := ConsumerPod{id:1,namespace: sla, replicas: int32(replica1)}
	consumer2 := ConsumerPod{id:2,namespace: sla, replicas: int32(replica2)}
	consumer3 := ConsumerPod{id:3,namespace: sla, replicas: int32(replica3)}

	var pods []ConsumerPod
	pods = append(pods,consumer1,consumer2,consumer3) 

	return pods
}
