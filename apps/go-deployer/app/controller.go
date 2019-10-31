package main

import (
	"log"
	"time"
)

// type DeploymentScaler struct {
//     deploymentName string
// 	deploymentNamespace string
// 	desiredReplicas int32
// }

// type Message struct{
// 	sender string
// 	namespace string
// 	jobID string
// 	jobSize int
// 	messageType string
// }

var debounced = New(1000 * time.Millisecond)


func processMessage(messageStr []byte){
	log.Printf("Processing message: %s",messageStr)
	err, message := prepareMessage(messageStr)
	if err != nil {
		panic(err.Error())
	}

	messageType := message.messageType

	switch messageType {
	case "added":
		processJobAdded(message)
	case "completed":
		processJobCompleted(message)
	default:
		log.Printf("Invalid message type")		
	}

}
func updateDeployment(){
	state := getState()
	deployments := getDesiredConf(state)
	scaleDeployments(deployments)
}

func processJobAdded(message Message){

	sla:=message.namespace
	addTenant(sla)
	debounced(updateDeployment)
	// updateDeployment()
}
func processJobCompleted(message Message){
	sla:=message.namespace
	removeTenant(sla)
	debounced(updateDeployment)
	// updateDeployment()
}

