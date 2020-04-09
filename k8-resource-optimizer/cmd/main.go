package main

import (
	"log"
	"os"

	"k8-resource-optimizer/pkg/decomposer"
)

func main() {

	if len(os.Args) < 2 {
		log.Printf("Need config path as argument!")
		os.Exit(0)
	}
	configPath := os.Args[1]
	decomposerInstance, err := decomposer.NewDecomposerFromFile(configPath)
	if err != nil {
		panic("failed")
	}

	offline := false
	decomposerInstance.Execute(offline)

}
