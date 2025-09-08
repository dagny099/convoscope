# LLM Service API

## Overview

The `LLMService` class provides a unified interface for interacting with multiple Large Language Model providers, featuring automatic fallback, retry logic, and comprehensive error handling.

## Provider Management

### LLMProvider Dataclass

::: src.services.llm_service.LLMProvider

### Supported Providers

The service currently supports three major LLM providers:

=== "OpenAI"
    
    **Models Available:**
    - `gpt-4o` - Latest GPT-4 Omni model
    - `gpt-3.5-turbo` - Fast, cost-effective option
    - `gpt-4-turbo` - Enhanced GPT-4 with larger context
    
    **Environment Variable:** `OPENAI_API_KEY`
    
    ```python
    # Example usage
    service = LLMService()
    response = service.get_completion(
        provider="openai",
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```

=== "Anthropic"
    
    **Models Available:**
    - `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet
    - `claude-3-haiku-20240307` - Fast, lightweight Claude
    
    **Environment Variable:** `ANTHROPIC_API_KEY`
    
    ```python  
    # Example fallback usage
    try:
        response = service.get_completion("openai", "gpt-3.5-turbo", messages)
    except LLMServiceError:
        response = service.get_completion("anthropic", "claude-3-haiku-20240307", messages)
    ```

=== "Google"
    
    **Models Available:**
    - `gemini-pro` - Google's flagship model
    - `gemini-1.5-pro` - Enhanced version with multimodal capabilities
    
    **Environment Variable:** `GEMINI_API_KEY`
    
    ```python
    # Check provider availability
    available = service.get_available_providers()
    if "google" in available:
        models = service.get_available_models("google")
        print(f"Google models: {models}")
    ```

## Core Methods

### get_completion

Primary method for getting LLM completions with comprehensive error handling.

**Parameters:**
- `provider` (str): Provider name ("openai", "anthropic", "google")
- `model` (str): Model identifier from provider's available models
- `messages` (List[Dict[str, str]]): Conversation messages in OpenAI format
- `temperature` (float, optional): Response randomness (0.0-1.0, default: 0.7)
- `max_retries` (int, optional): Maximum retry attempts (default: 3)
- `timeout` (int, optional): Request timeout in seconds (default: 30)

**Returns:**
- `Optional[str]`: Generated response text, or None if all attempts failed

**Raises:**
- `LLMServiceError`: For provider unavailability, invalid models, or configuration issues

**Example:**
```python
service = LLMService()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."}
]

try:
    response = service.get_completion(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        max_retries=3
    )
    print(f"Response: {response}")
except LLMServiceError as e:
    print(f"Error: {e}")
```

### get_completion_with_fallback

Intelligent method that automatically tries multiple providers for maximum reliability.

**Parameters:**
- `messages` (List[Dict[str, str]]): Conversation messages
- `primary_provider` (str, optional): First provider to try (default: "openai") 
- `primary_model` (str, optional): Model for primary provider (default: "gpt-3.5-turbo")
- `fallback_provider` (str, optional): Backup provider (default: "anthropic")
- `fallback_model` (str, optional): Model for fallback provider (default: "claude-3-haiku-20240307")
- `temperature` (float, optional): Response temperature (default: 0.7)

**Returns:**
- `Optional[str]`: Generated response from any available provider, or None if all failed

**Example:**
```python
# Automatic fallback handling
response = service.get_completion_with_fallback(
    messages=messages,
    primary_provider="openai",
    primary_model="gpt-4o",
    fallback_provider="anthropic", 
    fallback_model="claude-3-5-sonnet-20241022",
    temperature=0.7
)

if response:
    print(f"Got response: {response}")
else:
    print("All providers failed")
```

### Provider Discovery Methods

#### get_available_providers

Returns dictionary of providers that have valid API keys configured.

**Returns:**
- `Dict[str, LLMProvider]`: Available providers with their configuration

**Example:**
```python
available = service.get_available_providers()
print(f"Available providers: {list(available.keys())}")

for name, provider in available.items():
    print(f"{name}: {len(provider.models)} models available")
```

#### get_available_models

Get list of models for a specific provider.

**Parameters:**
- `provider_name` (str): Provider to query

**Returns:**
- `List[str]`: Available model names, empty list if provider unavailable

**Example:**
```python
# Check what models are available
openai_models = service.get_available_models("openai")
anthropic_models = service.get_available_models("anthropic")

print(f"OpenAI models: {openai_models}")
print(f"Anthropic models: {anthropic_models}")
```

## Validation & Error Handling

### validate_messages

Validates message format before sending to LLM providers.

**Parameters:**
- `messages` (List[Dict[str, str]]): Messages to validate

**Returns:**
- `bool`: True if messages are valid, False otherwise

**Validation Rules:**
- Messages must be a non-empty list
- Each message must be a dictionary with 'role' and 'content' keys
- Role must be 'system', 'user', or 'assistant'
- Content must be non-empty string

**Example:**
```python
# Valid messages
valid_messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"}
]

# Invalid messages  
invalid_messages = [
    {"role": "invalid_role", "content": "test"},  # Invalid role
    {"role": "user", "content": ""},              # Empty content
    {"missing_role": "content"}                   # Missing role key
]

assert service.validate_messages(valid_messages) == True
assert service.validate_messages(invalid_messages) == False
```

## Error Types

### LLMServiceError

Base exception class for all LLM service errors.

**Common Error Scenarios:**
- **Provider Unavailable**: API key not set or invalid
- **Model Not Available**: Requested model not supported by provider
- **Rate Limited**: Too many requests to provider API
- **Authentication Failed**: Invalid or expired API key
- **Network Timeout**: Request exceeded timeout limit
- **Unknown Provider**: Requested provider not configured

**Error Handling Patterns:**
```python
try:
    response = service.get_completion(provider, model, messages)
except LLMServiceError as e:
    error_message = str(e)
    
    if "not available" in error_message:
        # Handle provider/model availability
        print(f"Service issue: {error_message}")
    elif "Rate limit" in error_message:
        # Handle rate limiting
        print("Please wait before making another request")
    elif "Invalid API key" in error_message:
        # Handle authentication
        print("Please check your API key configuration")
    else:
        # Handle other errors
        print(f"Service error: {error_message}")
```

## Configuration Examples

### Environment Setup

```bash
# Required environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export GEMINI_API_KEY="AIza..."

# Optional configuration
export DEFAULT_LLM_PROVIDER="openai"
export DEFAULT_TEMPERATURE="0.7"
```

### Advanced Usage Patterns

#### Custom Provider Priority

```python
class CustomLLMService(LLMService):
    """Extended service with custom provider priority."""
    
    def __init__(self):
        super().__init__()
        # Custom provider priority based on cost/performance
        self.provider_priority = ["anthropic", "openai", "google"]
    
    def get_best_available_provider(self):
        """Get highest priority available provider."""
        available = self.get_available_providers()
        
        for provider in self.provider_priority:
            if provider in available:
                return provider
        return None
```

#### Batch Processing

```python
def process_multiple_requests(service, requests):
    """Process multiple requests with consistent error handling."""
    results = []
    
    for i, request in enumerate(requests):
        try:
            response = service.get_completion_with_fallback(
                messages=request["messages"],
                temperature=request.get("temperature", 0.7)
            )
            results.append({"index": i, "response": response, "error": None})
        except Exception as e:
            results.append({"index": i, "response": None, "error": str(e)})
    
    return results
```

#### Performance Monitoring

```python
import time
from functools import wraps

def monitor_llm_calls(func):
    """Decorator to monitor LLM service performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"LLM call succeeded in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"LLM call failed after {duration:.2f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_llm_calls
def get_completion_monitored(service, provider, model, messages):
    return service.get_completion(provider, model, messages)
```

## Integration Examples

### Streamlit Integration

```python
import streamlit as st
from src.services.llm_service import LLMService, LLMServiceError

@st.cache_resource
def get_llm_service():
    """Cached LLM service instance."""
    return LLMService()

def chat_with_llm(user_input):
    """Streamlit chat integration with error handling."""
    service = get_llm_service()
    
    messages = [
        {"role": "system", "content": st.session_state.get("system_prompt", "You are helpful.")},
        {"role": "user", "content": user_input}
    ]
    
    try:
        with st.spinner("Getting response..."):
            response = service.get_completion_with_fallback(messages)
            
        if response:
            st.chat_message("assistant").write(response)
            return response
        else:
            st.error("All LLM providers are currently unavailable.")
            return None
            
    except LLMServiceError as e:
        st.error(f"Service error: {e}")
        return None
```

This API provides a robust foundation for multi-provider LLM integration with comprehensive error handling and flexible configuration options.

---

*Next: [Conversation Manager API](conversation-manager.md) - File persistence and conversation management*