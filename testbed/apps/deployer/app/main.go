package main

func main() {

	// initAppState()
	initDeployerConfig()
	channel,queue := initConsumer()

	startConsuming(channel,queue)
}
