"""
Mock LLM API servers for testing without making real API calls.
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import time

class MockOpenAIHandler(BaseHTTPRequestHandler):
    """Mock OpenAI API handler for testing."""
    
    def do_POST(self):
        """Handle POST requests to OpenAI endpoints."""
        if self.path == "/v1/chat/completions":
            self._handle_chat_completions()
        else:
            self.send_error(404)
    
    def _handle_chat_completions(self):
        """Mock chat completions endpoint."""
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)
        request_data = json.loads(request_body.decode('utf-8'))
        
        # Extract the last user message
        messages = request_data.get('messages', [])
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # Generate a mock response
        mock_response = {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request_data.get('model', 'gpt-3.5-turbo'),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Mock AI response to: {user_message}"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(mock_response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass

class MockLLMServer:
    """Mock LLM server for testing."""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the mock server."""
        self.server = HTTPServer(('localhost', self.port), MockOpenAIHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start
        return f"http://localhost:{self.port}"
    
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)