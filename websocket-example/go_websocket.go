package main

import (
	"golang.org/x/net/websocket"
	"fmt"
	"log"
	"net/http"
)

func Echo(ws *websocket.Conn){
	var err error

	for {
		var reply string
		if err = websocket.Message.Receive(ws, &reply); err != nil{
			fmt.Println("Can't receive!")
			break
		}

		fmt.Println("Received back from cilent: " + reply)
		msg := "Received: " + reply
		fmt.Println("Sending to client: " + msg)

		if err = websocket.Message.Send(ws, msg); err!= nil{
			fmt.Println("Can't send")
			break
		}
	}
}

func main(){
	http.Handle("/", websocket.Handle(Echo))

	if err := http.ListenAndServe(":8000", nil); err != nil{
		log.Fatal("ListenAndServe:", err)
	}
}