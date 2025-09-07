"""Mock LLM responses for testing purposes."""

MOCK_TOPIC_EXTRACTION_RESPONSE = """
## Main Topics Discussed

### Python Programming Language
- Definition and characteristics of Python
- High-level programming language
- Known for simplicity and readability

### General Conversation
- Greeting and pleasantries
- Information seeking behavior
- Polite conversation ending

### Technical Support
- Question and answer format
- Helpful assistant behavior
- Offering additional assistance
"""

MOCK_CHAT_RESPONSES = [
    "This is a mock response from the AI assistant.",
    "I understand your question. Here's a helpful response for testing.",
    "Thank you for using our chat application. This is a test response.",
    "I'm here to help! This is a simulated AI response."
]

MOCK_ERROR_RESPONSES = {
    "api_error": "API service temporarily unavailable. Please try again later.",
    "rate_limit": "Rate limit exceeded. Please wait before making another request.",
    "invalid_key": "Invalid API key. Please check your configuration.",
    "network_error": "Network connection error. Please check your internet connection."
}

# Mock streaming response chunks for testing
MOCK_STREAMING_CHUNKS = [
    "This ",
    "is ",
    "a ",
    "mock ",
    "streaming ",
    "response ",
    "for ",
    "testing ",
    "purposes."
]