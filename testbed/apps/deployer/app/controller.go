package main

import (
	"log"
	"time"
)

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
	sla := message.namespace
	addTenant(sla)
	debounced(updateDeployment)
}
func processJobCompleted(message Message){
	sla:=message.namespace
	removeTenant(sla)
	debounced(updateDeployment)
}

