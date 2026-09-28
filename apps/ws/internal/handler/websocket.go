package handler

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// Upgrader configures WebSocket connection settings
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
	UserQuery string `json:"user_query,omitempty"`
	Query     string `json:"query,omitempty"`
	Message   string `json:"message,omitempty"`
	Text      string `json:"text,omitempty"`
	Prompt    string `json:"prompt,omitempty"`
	SessionID string `json:"session_id,omitempty"`
	UserType  string `json:"user_type,omitempty"`
	UserID    string `json:"user_id,omitempty"`
}

// GetQuery extracts the query string from whichever field the client provided
func (c *ClientMessage) GetQuery() string {
	if c.UserQuery != "" {
		return c.UserQuery
	}
	if c.Query != "" {
		return c.Query
	}
	if c.Message != "" {
		return c.Message
	}
	if c.Text != "" {
		return c.Text
	}
	if c.Prompt != "" {
		return c.Prompt
	}
	return ""
}

// StreamResponse is the outgoing message structure sent back to the frontend chat
type StreamResponse struct {
	Token     string           `json:"token,omitempty"`
	Answer    string           `json:"answer,omitempty"`
	Text      string           `json:"text,omitempty"`
	Message   string           `json:"message,omitempty"`
	Status    string           `json:"status,omitempty"`
	Error     string           `json:"error,omitempty"`
	SessionID string           `json:"session_id,omitempty"`
	Sources   []map[string]any `json:"sources,omitempty"`
	Cached    *bool            `json:"cached,omitempty"`
}

// PythonResponse matches the JSON returned by FastAPI's query_document
type PythonResponse struct {
	Query       string           `json:"query"`
	SearchQuery string           `json:"search_query"`
	Answer      string           `json:"answer"`
	SessionID   string           `json:"session_id"`
	Sources     []map[string]any `json:"sources"`
	Cached      bool             `json:"cached"`
}

// SafeConn wraps websocket.Conn with a mutex for thread-safe writing across goroutines
type SafeConn struct {
	*websocket.Conn
	mu sync.Mutex
}

// WriteSafeJSON thread-safely writes JSON to the WebSocket connection
func (s *SafeConn) WriteSafeJSON(v any) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.WriteJSON(v)
}

// WebSocketHandler handles incoming WebSocket connections
func WebSocketHandler(w http.ResponseWriter, r *http.Request) {
	rawConn, err := Upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Failed to upgrade connection: %v\n", err)
		return
	}
	defer rawConn.Close()

	safeConn := &SafeConn{Conn: rawConn}
	log.Printf("New client connected from %s\n", rawConn.RemoteAddr())

	for {
		// Read message from frontend
		messageType, message, err := rawConn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("Unexpected close error: %v\n", err)
			} else {
				log.Printf("Client disconnected: %v\n", rawConn.RemoteAddr())
			}
			break
		}

		if messageType != websocket.TextMessage {
			continue
		}

		var clientMsg ClientMessage
		if err := json.Unmarshal(message, &clientMsg); err != nil {
			// If not JSON, check if it's a raw text query
			rawText := strings.TrimSpace(string(message))
			if rawText != "" {
				clientMsg = ClientMessage{UserQuery: rawText}
			} else {
				safeConn.WriteSafeJSON(StreamResponse{Error: "Invalid JSON format. Expected: {\"user_query\": \"...\"}"})
				continue
			}
		}

		query := clientMsg.GetQuery()
		if query == "" {
			safeConn.WriteSafeJSON(StreamResponse{Error: "user_query cannot be empty"})
			continue
		}

		userType := clientMsg.UserType
		if userType == "" {
			userType = "guest"
		}
		userID := clientMsg.UserID
		if userID == "" {
			userID = "guest"
		}

		// Notify client that the AI is processing
		safeConn.WriteSafeJSON(StreamResponse{
			Status:    "thinking",
			SessionID: clientMsg.SessionID,
		})

		// Stream from Python FastAPI backend in a separate goroutine
		go StreamFromPython(safeConn, query, clientMsg.SessionID, userType, userID)
	}
}

// StreamFromPython calls Python FastAPI endpoint and pipes tokens/response to the WebSocket
func StreamFromPython(conn *SafeConn, query, sessionID, userType, userID string) {
	reqMap := map[string]any{
		"user_query": query,
		"user_type":  userType,
		"user_id":    userID,
	}
	if sessionID != "" {
		reqMap["session_id"] = sessionID
	}

	payload, err := json.Marshal(reqMap)
	if err != nil {
		conn.WriteSafeJSON(StreamResponse{Error: "Failed to encode query payload"})
		return
	}

	// Python FastAPI streaming endpoint
	pythonURL := os.Getenv("PYTHON_API_URL")
	if pythonURL == "" {
		pythonURL = "http://127.0.0.1:8000/query/stream"
	}

	log.Printf("[WS -> Python] Calling %s with query: %q, session: %q\n", pythonURL, query, sessionID)

	resp, err := http.Post(pythonURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		log.Printf("Error reaching Python backend: %v\n", err)
		conn.WriteSafeJSON(StreamResponse{Error: "Could not reach Python AI backend at " + pythonURL})
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		log.Printf("Python backend returned non-200 status %d: %s\n", resp.StatusCode, string(bodyBytes))
		conn.WriteSafeJSON(StreamResponse{
			Error:  fmt.Sprintf("AI backend error (status %d): %s", resp.StatusCode, string(bodyBytes)),
			Status: "error",
		})
		return
	}

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Stream read error: %v\n", err)
		conn.WriteSafeJSON(StreamResponse{Error: "Error reading stream from AI service"})
		return
	}

	// Case 1: Python returned JSON result (from docs_handler.py query_document)
	var pyResp PythonResponse
	if err := json.Unmarshal(bodyBytes, &pyResp); err == nil && pyResp.Answer != "" {
		log.Printf("[Python -> WS] Received response for session %s (cached: %v, answer len: %d)\n",
			pyResp.SessionID, pyResp.Cached, len(pyResp.Answer))

		// 1. Stream the answer tokens to the chat UI for a smooth real-time typewriter effect
		words := strings.Fields(pyResp.Answer)
		for _, word := range words {
			if writeErr := conn.WriteSafeJSON(StreamResponse{
				Token:     word + " ",
				SessionID: pyResp.SessionID,
				Status:    "streaming",
			}); writeErr != nil {
				log.Printf("Client disconnected during stream: %v\n", writeErr)
				return
			}
			time.Sleep(15 * time.Millisecond)
		}

		// 2. Send final completion message with full answer, citations/sources, and status: done
		conn.WriteSafeJSON(StreamResponse{
			Token:     "",
			Answer:    pyResp.Answer,
			Text:      pyResp.Answer,
			Message:   pyResp.Answer,
			Sources:   pyResp.Sources,
			SessionID: pyResp.SessionID,
			Cached:    &pyResp.Cached,
			Status:    "done",
		})
		return
	}

	// Case 2: Fallback if the response was a plain text stream with newlines
	reader := bufio.NewReader(bytes.NewReader(bodyBytes))
	for {
		line, readErr := reader.ReadString('\n')
		if len(line) > 0 {
			if writeErr := conn.WriteSafeJSON(StreamResponse{
				Token:     line,
				SessionID: sessionID,
				Status:    "streaming",
			}); writeErr != nil {
				log.Printf("Error writing to client WebSocket: %v\n", writeErr)
				return
			}
		}

		if readErr == io.EOF {
			conn.WriteSafeJSON(StreamResponse{Status: "done", SessionID: sessionID})
			break
		}
		if readErr != nil {
			log.Printf("Stream read error: %v\n", readErr)
			conn.WriteSafeJSON(StreamResponse{Error: "Error reading stream from AI service"})
			break
		}
	}
}
