package main

import (
	"encoding/json"
)

type Message struct{
	sender string
	namespace string
	messageType string
}

func prepareMessage(messageStr []byte) (error, Message){
    // We need to provide a variable where the JSON
    // package can put the decoded data. This
    // `map[string]interface{}` will hold a map of strings
    // to arbitrary data types.
    var data map[string]interface{}

    // Here's the actual decoding, and a check for
    // associated errors.
    if err := json.Unmarshal(messageStr, &data); err != nil {
        return err, Message{}
    }

	messageType := data["type"].(string)
	sender := data["sender"].(string)
	namespace := data["namespace"].(string)
	// jobID := data["jobID"].(string)
	// jobSize := int(data["jobSize"].(float64))

	// message := Message{sender,namespace,jobID,jobSize,messageType}
	message := Message{sender,namespace,messageType}


	return nil,message

}