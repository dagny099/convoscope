# Utilities API

## Overview

The utilities modules provide essential helper functions and session state management for the Convoscope application. These functions handle common operations with proper error handling and validation.

## Helper Functions

### get_index

Safe list indexing with bounds checking and type validation.

**Parameters:**
- `lst` (List[Any]): List to search in
- `item` (Any): Item to find
- `default` (Any, optional): Value to return if item not found (default: None)

**Returns:**
- `Union[int, Any]`: Index of item if found, otherwise default value

**Features:**
- **Bounds Safety**: Never raises IndexError
- **Type Flexibility**: Works with any list type and item type
- **Default Handling**: Customizable return value for missing items
- **Performance Optimized**: Uses built-in list.index() when possible

**Example:**
```python
from src.utils.helpers import get_index

# Basic usage
numbers = [10, 20, 30, 40]
index = get_index(numbers, 30)  # Returns: 2
missing = get_index(numbers, 99)  # Returns: None

# With custom default
index_or_zero = get_index(numbers, 99, default=0)  # Returns: 0

# Mixed type lists
mixed = [1, 'hello', 3.14, True, None]
str_index = get_index(mixed, 'hello')  # Returns: 1
bool_index = get_index(mixed, True)    # Returns: 3
none_index = get_index(mixed, None)    # Returns: 4
```

### sanitize_filename

Comprehensive filename sanitization for secure file operations.

**Parameters:**
- `filename` (str): Filename to sanitize
- `replacement` (str, optional): Character to replace invalid chars with (default: '_')
- `max_length` (int, optional): Maximum filename length (default: 255)

**Returns:**
- `str`: Sanitized filename safe for filesystem operations

**Security Features:**
- **Directory Traversal Prevention**: Removes `../`, `./`, and absolute paths
- **Special Character Handling**: Replaces filesystem-unsafe characters
- **Length Limiting**: Enforces maximum filename length
- **Empty Name Protection**: Generates valid name for empty/invalid input
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux

**Example:**
```python
from src.utils.helpers import sanitize_filename

# Basic sanitization
clean = sanitize_filename("My Document.txt")  # Returns: "My Document.txt"

# Remove dangerous characters
dangerous = "file<>|?*name"
safe = sanitize_filename(dangerous)  # Returns: "file_____name"

# Directory traversal prevention  
traversal = "../../../etc/passwd"
blocked = sanitize_filename(traversal)  # Returns: "etc_passwd"

# Custom replacement character
custom = sanitize_filename("file*name", replacement="-")  # Returns: "file-name"

# Length limiting
long_name = "a" * 300
limited = sanitize_filename(long_name, max_length=100)  # Returns: "a" * 100
```

### format_conversation_for_display

Formats conversation messages for user-friendly display with proper styling and metadata.

**Parameters:**
- `conversation` (List[Dict[str, str]]): List of conversation messages
- `include_timestamps` (bool, optional): Whether to include timestamps (default: False)
- `max_content_length` (int, optional): Maximum content length before truncation (default: None)
- `role_colors` (Dict[str, str], optional): Color mapping for different roles

**Returns:**
- `str`: Formatted conversation string ready for display

**Formatting Features:**
- **Role-Based Styling**: Different formatting for system, user, and assistant messages
- **Timestamp Support**: Optional timestamp display with relative formatting
- **Content Truncation**: Smart truncation for long messages with ellipsis
- **Color Support**: Customizable colors for different message roles
- **Markdown Compatible**: Output works with Streamlit markdown rendering

**Example:**
```python
from src.utils.helpers import format_conversation_for_display

conversation = [
    {"role": "system", "content": "You are a helpful assistant.", "timestamp": "2025-01-07T10:00:00Z"},
    {"role": "user", "content": "Hello!", "timestamp": "2025-01-07T10:01:00Z"},
    {"role": "assistant", "content": "Hi there! How can I help you today?", "timestamp": "2025-01-07T10:01:05Z"}
]

# Basic formatting
formatted = format_conversation_for_display(conversation)

# With timestamps and truncation
detailed = format_conversation_for_display(
    conversation,
    include_timestamps=True,
    max_content_length=50
)

# Custom colors
custom_colors = {
    "system": "#888888",
    "user": "#0066cc", 
    "assistant": "#00aa44"
}
styled = format_conversation_for_display(
    conversation,
    role_colors=custom_colors
)
```

### extract_conversation_metadata

Extracts useful metadata from conversation data for analysis and display.

**Parameters:**
- `conversation` (List[Dict[str, str]]): Conversation messages

**Returns:**
- `Dict[str, Any]`: Dictionary containing conversation metadata

**Metadata Fields:**
- `total_messages`: Total number of messages
- `user_messages`: Count of user messages  
- `assistant_messages`: Count of assistant responses
- `system_messages`: Count of system messages
- `total_characters`: Total character count across all messages
- `average_message_length`: Average message length in characters
- `conversation_duration`: Time span from first to last message (if timestamps available)
- `message_frequency`: Average time between messages
- `longest_message`: Length and content of longest message
- `shortest_message`: Length and content of shortest message

**Example:**
```python
from src.utils.helpers import extract_conversation_metadata

conversation = [
    {"role": "user", "content": "Hello!", "timestamp": "2025-01-07T10:00:00Z"},
    {"role": "assistant", "content": "Hi! How can I help?", "timestamp": "2025-01-07T10:00:05Z"},
    {"role": "user", "content": "What's the weather like?", "timestamp": "2025-01-07T10:01:00Z"}
]

metadata = extract_conversation_metadata(conversation)

print(f"Total messages: {metadata['total_messages']}")
print(f"User messages: {metadata['user_messages']}")  
print(f"Duration: {metadata['conversation_duration']} seconds")
print(f"Avg message length: {metadata['average_message_length']:.1f} chars")
```

## Session State Management

::: src.utils.session_state

### initialize_session_state

Initializes Streamlit session state with application defaults and validates existing state.

**Parameters:**
- `defaults` (Dict[str, Any], optional): Default values for session state variables
- `reset_existing` (bool, optional): Whether to reset existing values (default: False)

**Returns:**
- `bool`: True if initialization successful

**Default State Variables:**
- `conversation`: Empty conversation list
- `current_provider`: Default LLM provider
- `temperature`: Response temperature setting
- `max_tokens`: Maximum response length
- `conversation_history`: List of saved conversation names
- `priming_messages`: System prompt templates
- `error_messages`: Error display queue

**Example:**
```python
import streamlit as st
from src.utils.session_state import initialize_session_state

# Initialize with defaults
initialize_session_state()

# Custom defaults
custom_defaults = {
    "conversation": [],
    "theme": "dark",
    "auto_save": True,
    "provider_preference": ["openai", "anthropic", "google"]
}
initialize_session_state(custom_defaults)

# Reset existing state (use carefully)
initialize_session_state(reset_existing=True)
```

### update_priming_text

Updates system prompt/priming text with validation and formatting.

**Parameters:**
- `priming_messages` (Dict[str, str]): Available priming message templates
- `source` (str): Source of update ('selectbox', 'text_area', 'file_upload')
- `new_value` (str): New priming text content

**Returns:**
- `Tuple[bool, str]`: Success status and validation message

**Validation Features:**
- **Length Validation**: Ensures priming text is reasonable length
- **Content Filtering**: Removes potentially harmful content
- **Format Checking**: Validates system message format
- **Source Tracking**: Records how priming text was updated
- **History Preservation**: Maintains history of priming text changes

**Example:**
```python
import streamlit as st
from src.utils.session_state import update_priming_text

# Priming message templates
priming_templates = {
    "helpful": "You are a helpful assistant.",
    "creative": "You are a creative writing assistant.",
    "technical": "You are a technical expert assistant."
}

# Update from selectbox
success, message = update_priming_text(
    priming_templates,
    source="selectbox", 
    new_value="helpful"
)

# Update from text area
custom_prompt = "You are an expert in Python programming."
success, message = update_priming_text(
    priming_templates,
    source="text_area",
    new_value=custom_prompt
)

if success:
    st.success(f"Priming text updated: {message}")
else:
    st.error(f"Update failed: {message}")
```

### manage_conversation_state

Comprehensive conversation state management with validation and cleanup.

**Parameters:**
- `action` (str): Action to perform ('add_message', 'clear', 'load', 'trim')
- `data` (Any, optional): Data for the action (message dict, conversation list, etc.)
- `options` (Dict, optional): Additional options for the action

**Returns:**
- `Tuple[bool, str]`: Success status and result message

**Supported Actions:**

=== "add_message"
    Add new message to current conversation
    ```python
    # Add user message
    success, msg = manage_conversation_state(
        action="add_message",
        data={"role": "user", "content": "Hello!"}
    )
    
    # Add assistant response
    success, msg = manage_conversation_state(
        action="add_message", 
        data={"role": "assistant", "content": "Hi there!"}
    )
    ```

=== "clear"
    Clear current conversation with optional backup
    ```python
    # Clear conversation
    success, msg = manage_conversation_state(action="clear")
    
    # Clear with backup
    success, msg = manage_conversation_state(
        action="clear",
        options={"create_backup": True, "backup_name": "cleared_conversation"}
    )
    ```

=== "load"
    Load conversation from data
    ```python
    # Load conversation
    conversation_data = [...] # List of messages
    success, msg = manage_conversation_state(
        action="load",
        data=conversation_data
    )
    ```

=== "trim"
    Trim conversation to manage memory usage
    ```python
    # Trim to last 50 messages
    success, msg = manage_conversation_state(
        action="trim",
        options={"max_messages": 50, "preserve_system": True}
    )
    ```

### get_session_summary

Generates comprehensive summary of current session state for debugging and monitoring.

**Returns:**
- `Dict[str, Any]`: Session state summary with sanitized sensitive data

**Summary Contents:**
- **Basic Stats**: Message counts, conversation length, active features
- **Configuration**: Current settings and preferences (API keys sanitized)
- **Performance**: Memory usage, response times, error counts
- **History**: Recent actions and state changes
- **Health**: System health indicators and warnings

**Example:**
```python
from src.utils.session_state import get_session_summary

# Get session summary
summary = get_session_summary()

print(f"Messages in conversation: {summary['conversation']['total_messages']}")
print(f"Current provider: {summary['configuration']['active_provider']}")
print(f"Session duration: {summary['performance']['session_duration_minutes']:.1f} min")
print(f"Errors encountered: {summary['health']['error_count']}")

# Check for warnings
if summary['health']['warnings']:
    print("⚠️  Warnings:")
    for warning in summary['health']['warnings']:
        print(f"  - {warning}")
```

## Validation Utilities

### validate_conversation_message

Validates individual conversation messages for structure and content.

**Parameters:**
- `message` (Dict[str, Any]): Message to validate
- `strict_mode` (bool, optional): Whether to apply strict validation (default: True)

**Returns:**
- `Tuple[bool, List[str]]`: Validation status and list of error messages

**Validation Rules:**
- **Required Fields**: Must have 'role' and 'content' keys
- **Valid Roles**: Role must be 'system', 'user', or 'assistant' 
- **Content Requirements**: Content must be non-empty string
- **Optional Fields**: Timestamp and metadata validation
- **Security Checks**: Content filtering for malicious patterns

**Example:**
```python
from src.utils.helpers import validate_conversation_message

# Valid message
valid_msg = {
    "role": "user",
    "content": "What is machine learning?",
    "timestamp": "2025-01-07T10:00:00Z"
}
is_valid, errors = validate_conversation_message(valid_msg)
# Returns: (True, [])

# Invalid message
invalid_msg = {
    "role": "invalid_role",  # Invalid role
    "content": ""  # Empty content
}
is_valid, errors = validate_conversation_message(invalid_msg)
# Returns: (False, ["Invalid role: invalid_role", "Content cannot be empty"])
```

### sanitize_user_input

Comprehensive user input sanitization for security and safety.

**Parameters:**
- `user_input` (str): Raw user input to sanitize
- `max_length` (int, optional): Maximum allowed length (default: 10000)
- `allow_html` (bool, optional): Whether to allow HTML tags (default: False)

**Returns:**
- `Tuple[str, List[str]]`: Sanitized input and list of warnings

**Sanitization Features:**
- **Length Limiting**: Enforces maximum input length
- **HTML Stripping**: Removes potentially dangerous HTML/script tags
- **Special Character Handling**: Escapes or removes special characters
- **Whitespace Normalization**: Cleans up excessive whitespace
- **Encoding Validation**: Ensures proper UTF-8 encoding

**Example:**
```python
from src.utils.helpers import sanitize_user_input

# Basic sanitization
clean_input, warnings = sanitize_user_input("Hello, world!")
# Returns: ("Hello, world!", [])

# HTML removal
html_input = "<script>alert('xss')</script>Safe content"
safe_input, warnings = sanitize_user_input(html_input, allow_html=False)
# Returns: ("Safe content", ["Removed potentially dangerous HTML tags"])

# Length limiting  
long_input = "a" * 15000
limited_input, warnings = sanitize_user_input(long_input, max_length=1000)
# Returns: ("a" * 1000, ["Input truncated from 15000 to 1000 characters"])
```

## Performance Utilities

### measure_performance

Decorator and context manager for measuring function performance.

**Usage as Decorator:**
```python
from src.utils.helpers import measure_performance

@measure_performance
def slow_function():
    time.sleep(1)
    return "result"

result = slow_function()
# Automatically logs: "slow_function completed in 1.00 seconds"
```

**Usage as Context Manager:**
```python
from src.utils.helpers import measure_performance

with measure_performance("expensive_operation"):
    # Perform expensive computation
    result = complex_calculation()
# Logs: "expensive_operation completed in X.XX seconds"
```

### memory_usage_monitor

Context manager for monitoring memory usage during operations.

**Example:**
```python
from src.utils.helpers import memory_usage_monitor

with memory_usage_monitor("conversation_loading"):
    large_conversation = load_large_conversation()
    
# Logs memory usage before, during, and after operation
```

## Integration Examples

### Complete Streamlit Integration

```python
import streamlit as st
from src.utils.session_state import initialize_session_state, manage_conversation_state
from src.utils.helpers import sanitize_user_input, format_conversation_for_display

def main():
    # Initialize session state
    initialize_session_state()
    
    st.title("Convoscope Chat")
    
    # Display conversation
    if st.session_state.conversation:
        formatted = format_conversation_for_display(
            st.session_state.conversation,
            include_timestamps=True
        )
        st.markdown(formatted)
    
    # User input
    user_input = st.chat_input("Ask a question:")
    if user_input:
        # Sanitize input
        clean_input, warnings = sanitize_user_input(user_input)
        
        # Show warnings if any
        for warning in warnings:
            st.warning(warning)
        
        # Add to conversation
        success, message = manage_conversation_state(
            action="add_message",
            data={"role": "user", "content": clean_input}
        )
        
        if success:
            st.rerun()  # Refresh to show new message
        else:
            st.error(f"Failed to add message: {message}")

if __name__ == "__main__":
    main()
```

### Error Handling Integration

```python
from src.utils.helpers import sanitize_filename, get_index
from src.utils.session_state import get_session_summary
import logging

def safe_file_operation(filename, operation_data):
    """Safely perform file operations with comprehensive error handling."""
    
    try:
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # Get session context for logging
        session_info = get_session_summary()
        
        # Log operation attempt
        logging.info(
            f"File operation attempted",
            filename=safe_filename,
            operation="save",
            session_id=session_info.get('session_id'),
            message_count=session_info.get('conversation', {}).get('total_messages', 0)
        )
        
        # Perform operation
        result = perform_file_operation(safe_filename, operation_data)
        
        return True, f"Operation successful: {safe_filename}"
        
    except Exception as e:
        logging.error(f"File operation failed: {e}")
        return False, f"Operation failed: {str(e)}"
```

These utilities provide the foundational building blocks for reliable, secure, and performant application functionality with comprehensive error handling and validation.

---

*Next: [Implementation Guides](../guides/README.md) - Practical usage examples and integration patterns*