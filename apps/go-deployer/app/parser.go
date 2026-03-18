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
	cpu      string
	memory   string
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

	// Fetch ground truth for existing workers and send to planner
	for i := 1; i <= 10; i++ {
		workerName := "consumer" + strconv.Itoa(i)
		labelSelector := "app=" + workerName
		cpu, mem := getPodResources(sla, labelSelector)
		if cpu != "0" {
			params.Add(fmt.Sprintf("prev_res_worker%d_cpu", i), cpu)
			params.Add(fmt.Sprintf("prev_res_worker%d_mem", i), mem)
			
			// Check if this worker type supports in-place resize
			canResize, _ := checkInPlaceSupport(sla, labelSelector)
			if canResize {
				params.Add(fmt.Sprintf("inplace_worker%d", i), "true")
			} else {
				params.Add(fmt.Sprintf("inplace_worker%d", i), "false")
			}
		}
	}

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

	var pods []ConsumerPod
	// We need to loop or manually extract for all possible workers. 
	// The number of workers is dynamic but usually 3 or more.
	// Let's dynamically find worker keys.
	for i := 1; ; i++ {
		replicaKey := fmt.Sprintf("worker%d.replicaCount", i)
		if val, ok := result[replicaKey]; ok {
			replicaCount, _ := strconv.Atoi(val.(string))
			cpu := result[fmt.Sprintf("worker%d.resources.requests.cpu", i)].(string)
			memory := result[fmt.Sprintf("worker%d.resources.requests.memory", i)].(string)
			
			// If memory is just a number, append "Gi" or "Mi" as needed. 
			// Based on rescale.sh, it seems it appends "Gi".
			if !fmt.Sprintf("%v", memory)[len(fmt.Sprintf("%v", memory))-1:] == "i" {
				memory = memory + "Gi"
			}

			pods = append(pods, ConsumerPod{
				id:        i,
				namespace: sla,
				replicas:  int32(replicaCount),
				cpu:       cpu,
				memory:    memory,
			})
		} else {
			break
		}
	}

	return pods
}
