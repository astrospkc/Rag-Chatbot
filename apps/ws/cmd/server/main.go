package main

import (
	"fmt"
	"log"
	"net/http"

	"rag-chatbot/ws/internal/handler"
)

func main() {
	port := ":8080"

	// Register WebSocket endpoint
	http.HandleFunc("/ws", handler.WebSocketHandler)

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status": "ok", "service": "ws-gateway"}`))
	})

	fmt.Printf("🚀 Go WebSocket Gateway listening on ws://localhost%s/ws\n", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v\n", err)
	}
}
