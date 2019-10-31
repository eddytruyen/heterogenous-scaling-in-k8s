package main

import(
	"fmt"
	"strconv"
)


func failOnError(err error, msg string) {
	if err != nil {
		// Exit the program.
		panic(fmt.Sprintf("%s: %s", msg, err))
	}
}

func int32Ptr(i int32) *int32 { return &i }

func int2str( i int) string{
	return strconv.Itoa(i)
}