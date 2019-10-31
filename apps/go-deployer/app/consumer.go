package main

import (
	"fmt"
	"log"
	"github.com/streadway/amqp"
)

type Queue = amqp.Queue
type Channel = amqp.Channel




func initConsumer() (*Channel, Queue){

	//Connect to the broker
	conn, err := amqp.Dial("amqp://"+RabbitMQUser+":"+RabbitMQPass+"@"+RabbitMQHost+":"+RabbitMQPort+"/")
	failOnError(err, "Error connecting to the broker")
	
	// Make sure we close the connection whenever the program is about to exit.
	// defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	// Make sure we close the channel whenever the program is about to exit.
	// defer ch.Close()
	
	// Create the exchange if it doesn't already exist.
	err = ch.ExchangeDeclare(
			ExchangeName, 	// name
			"topic",  		// type
			false,         	// durable
			false,
			false,
			false,
			nil,
	)
	failOnError(err, "Error creating the exchange")
	
	// Create the queue if it doesn't already exist.
	q, err := ch.QueueDeclare(
			"",    // name - empty means a random, unique name will be assigned
			false,  // durable
			false, // delete when unused
			false, 
			false, 
			nil,   
	)
	failOnError(err, "Error creating the queue")

	// Bind the queue to the exchange based on a string pattern (binding key).
	err = ch.QueueBind(
			q.Name,       // queue name
			BindingKey,   // binding key
			ExchangeName, // exchange
			false,
			nil,
	)
	failOnError(err, "Error binding the queue")

	return ch,q

}

func startConsuming(ch *Channel,q Queue){
	// Subscribe to the queue.

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer id - empty means a random, unique id will be assigned
		false,  // auto acknowledgement of message delivery
		false,  
		false,  
		false,  
		nil,
)
failOnError(err, "Failed to register as a consumer")


forever := make(chan bool)

go func() {
	for d := range msgs {
		log.Printf("Received message: %s", d.Body)
		processMessage(d.Body)

		// The 'false' indicates the success of a single delivery, 'true' would mean that
		// this delivery and all prior unacknowledged deliveries on this channel will be
		// acknowledged.
		d.Ack(false)
	}
}()

fmt.Println("Service listening for events...")

// Block until 'forever' receives a value, which will never happen.
<-forever
}
