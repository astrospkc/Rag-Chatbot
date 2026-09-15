package handler

import (
	"bufio"
	"bytes"

	"encoding/json"
	"io"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

// Upgrader configures WebSocket connection settings
// Upgrader specifies parameters for upgrading an HTTP connection to a WebSocket connection.
// It is safe to call Upgrader's methods concurrently.
var Upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// Allow any origin for development (adjust for production)
		return true
	},
}

// ClientMessage is the incoming message structure from the frontend
type ClientMessage struct {
	UserQuery string `json:"user_query"`
}

// StreamResponse is the outgoing message structure sent back to the frontend
type StreamResponse struct {
	Token  string `json:"token,omitempty"`
	Status string `json:"status,omitempty"`
	Error  string `json:"error,omitempty"`
}

// {
//   "event": "token | sources | status | done | error",
//   "conversation_id": "conv_8f19b2",
//   "message_id": "msg_90a4bc",
//   "created_at": 1726338471,
//   "data": {}
// }

// WebSocketHandler handles incoming WebSocket connections
func WebSocketHandler(w http.ResponseWriter, r *http.Request) {
	conn, err := Upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Failed to upgrade connection: %v\n", err)
		return
	}
	defer conn.Close()

	log.Printf("New client connected from %s\n", conn.RemoteAddr())

	for {
		// Read message from frontend
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("Unexpected close error: %v\n", err)
			} else {
				log.Printf("Client disconnected: %v\n", conn.RemoteAddr())
			}
			break
		}

		if messageType != websocket.TextMessage {
			continue
		}

		var clientMsg ClientMessage
		if err := json.Unmarshal(message, &clientMsg); err != nil {
			conn.WriteJSON(StreamResponse{Error: "Invalid JSON format. Expected: {\"user_query\": \"...\"}"})
			continue
		}

		if clientMsg.UserQuery == "" {
			conn.WriteJSON(StreamResponse{Error: "user_query cannot be empty"})
			continue
		}

		// Stream from Python FastAPI backend in a separate goroutine
		go StreamFromPython(conn, clientMsg.UserQuery)
	}
}

// StreamFromPython calls the Python FastAPI streaming endpoint and pipes tokens to the WebSocket
func StreamFromPython(conn *websocket.Conn, query string) {
	payload, err := json.Marshal(map[string]string{
		"user_query": query,
	})
	if err != nil {
		conn.WriteJSON(StreamResponse{Error: "Failed to encode query payload"})
		return
	}

	// Python FastAPI streaming endpoint
	pythonURL := "http://localhost:8000/query/stream"

	resp, err := http.Post(pythonURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		log.Printf("Error reaching Python backend: %v\n", err)
		conn.WriteJSON(StreamResponse{Error: "Could not reach Python AI backend at " + pythonURL})
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("Python backend returned non-200 status: %d\n", resp.StatusCode)
		conn.WriteJSON(StreamResponse{Error: "AI backend error during stream"})
		return
	}

	// Read streamed tokens chunk by chunk
	reader := bufio.NewReader(resp.Body)
	for {
		token, err := reader.ReadString('\n')
		if len(token) > 0 {
			if writeErr := conn.WriteJSON(StreamResponse{Token: token}); writeErr != nil {
				log.Printf("Error writing to client WebSocket: %v\n", writeErr)
				return
			}
		}

		if err == io.EOF {
			// Signal to the frontend that streaming is complete
			conn.WriteJSON(StreamResponse{Status: "done"})
			break
		}
		if err != nil {
			log.Printf("Stream read error: %v\n", err)
			conn.WriteJSON(StreamResponse{Error: "Error reading stream from AI service"})
			break
		}
	}
}
