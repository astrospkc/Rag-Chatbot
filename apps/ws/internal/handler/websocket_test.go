package handler

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
)

func TestWebSocketFlow(t *testing.T) {
	// 1. Mock Python FastAPI backend
	mockPython := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/query/stream" {
			http.NotFound(w, r)
			return
		}
		var req map[string]any
		json.NewDecoder(r.Body).Decode(&req)

		resp := PythonResponse{
			Query:       req["user_query"].(string),
			SearchQuery: req["user_query"].(string),
			Answer:      "This is a test answer from AI backend.",
			SessionID:   "test-session-123",
			Sources: []map[string]any{
				{"title": "Doc1.pdf"},
			},
			Cached: false,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))
	defer mockPython.Close()

	os.Setenv("PYTHON_API_URL", mockPython.URL+"/query/stream")

	// 2. Mock Go WebSocket Server
	wsServer := httptest.NewServer(http.HandlerFunc(WebSocketHandler))
	defer wsServer.Close()

	// 3. Connect client
	wsURL := "ws" + strings.TrimPrefix(wsServer.URL, "http")
	client, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatalf("Failed to connect to WS: %v", err)
	}
	defer client.Close()

	// 4. Send message
	msg := ClientMessage{
		UserQuery: "What is AI?",
		SessionID: "sess-1",
	}
	if err := client.WriteJSON(msg); err != nil {
		t.Fatalf("Failed to write to WS: %v", err)
	}

	// 5. Read responses
	var tokens []string
	var finalAnswer string
	var doneReceived bool

	client.SetReadDeadline(time.Now().Add(3 * time.Second))
	for {
		var streamResp StreamResponse
		err := client.ReadJSON(&streamResp)
		if err != nil {
			break
		}

		if streamResp.Token != "" {
			tokens = append(tokens, streamResp.Token)
		}
		if streamResp.Answer != "" {
			finalAnswer = streamResp.Answer
		}
		if streamResp.Status == "done" {
			doneReceived = true
			break
		}
	}

	if !doneReceived {
		t.Errorf("Expected status: done, but didn't receive it")
	}
	if len(tokens) == 0 {
		t.Errorf("Expected streamed tokens, got none")
	}
	combinedTokens := strings.TrimSpace(strings.Join(tokens, ""))
	if combinedTokens != "This is a test answer from AI backend." {
		t.Errorf("Tokens mismatch: got %q", combinedTokens)
	}
	if finalAnswer != "This is a test answer from AI backend." {
		t.Errorf("Final answer mismatch: got %q", finalAnswer)
	}
}
