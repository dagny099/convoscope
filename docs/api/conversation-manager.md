# Conversation Manager API

## Overview

The `ConversationManager` class provides robust conversation persistence with atomic operations, validation, backup mechanisms, and comprehensive error handling for the Convoscope application.

## Core Functionality

### save_conversation

Primary method for persisting conversations with comprehensive data integrity protection.

**Parameters:**
- `conversation` (List[Dict[str, str]]): List of conversation messages in standard format
- `filename` (str): Target filename for conversation storage
- `create_backup` (bool, optional): Whether to create backup before writing (default: True)

**Returns:**
- `Tuple[bool, str]`: Success status and descriptive message

**Features:**
- **Atomic Operations**: Uses temporary files and atomic moves to prevent corruption
- **Backup Protection**: Automatically creates backup before modifying existing conversations
- **Input Validation**: Comprehensive validation of conversation structure and content
- **Error Recovery**: Automatic rollback to backup on write failures
- **Filename Sanitization**: Prevents directory traversal and ensures valid filenames

**Example:**
```python
manager = ConversationManager()

conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you!"}
]

success, message = manager.save_conversation(
    conversation=conversation,
    filename="my_chat_session",
    create_backup=True
)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ Save failed: {message}")
```

### load_conversation

Safely loads and validates conversation files with error handling.

**Parameters:**
- `filename` (str): Name of conversation file to load (without .json extension)

**Returns:**
- `Tuple[bool, Union[List[Dict], str]]`: Success status and either conversation data or error message

**Validation Features:**
- File existence checking
- JSON format validation
- Conversation structure verification
- Message format validation
- Encoding error handling

**Example:**
```python
# Load existing conversation
success, result = manager.load_conversation("my_chat_session")

if success:
    conversation = result
    print(f"Loaded {len(conversation)} messages")
    for message in conversation:
        print(f"{message['role']}: {message['content'][:50]}...")
else:
    error_message = result
    print(f"Load failed: {error_message}")
```

### get_conversation_list

Retrieves list of available conversation files with metadata.

**Parameters:**
- `include_metadata` (bool, optional): Whether to include file metadata (default: False)

**Returns:**
- `List[Union[str, Dict]]`: List of filenames or metadata dictionaries

**Metadata Fields** (when `include_metadata=True`):
- `filename`: Base filename without extension
- `full_path`: Complete file path
- `size_bytes`: File size in bytes
- `modified_time`: Last modification timestamp
- `message_count`: Number of messages (if parseable)

**Example:**
```python
# Simple filename list
conversations = manager.get_conversation_list()
print(f"Available conversations: {conversations}")

# Detailed metadata
detailed_list = manager.get_conversation_list(include_metadata=True)
for conv in detailed_list:
    print(f"{conv['filename']}: {conv['message_count']} messages, "
          f"modified {conv['modified_time']}")
```

### delete_conversation

Safely removes conversation files with backup option.

**Parameters:**
- `filename` (str): Name of conversation to delete
- `create_backup` (bool, optional): Create backup before deletion (default: True)

**Returns:**
- `Tuple[bool, str]`: Success status and descriptive message

**Safety Features:**
- Backup creation before deletion
- File existence verification
- Permission checking
- Recovery instructions on failure

**Example:**
```python
# Delete with backup (recommended)
success, message = manager.delete_conversation("old_session", create_backup=True)

# Force delete without backup (use carefully)
success, message = manager.delete_conversation("temp_session", create_backup=False)
```

## Validation Methods

### validate_conversation

Comprehensive conversation structure and content validation.

**Parameters:**
- `conversation` (List[Dict]): Conversation data to validate

**Returns:**
- `bool`: True if valid, False otherwise

**Validation Rules:**
- Must be a non-empty list
- Each message must be a dictionary
- Required keys: 'role' and 'content'
- Role must be: 'system', 'user', or 'assistant'
- Content must be non-empty string
- No malicious content patterns

**Example:**
```python
# Valid conversation
valid_conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"}
]

# Invalid examples
invalid_examples = [
    [],  # Empty list
    [{"role": "invalid", "content": "test"}],  # Invalid role
    [{"role": "user", "content": ""}],  # Empty content
    [{"missing_role": "content"}],  # Missing required keys
]

assert manager.validate_conversation(valid_conversation) == True
for invalid in invalid_examples:
    assert manager.validate_conversation(invalid) == False
```

### validate_filename

Ensures filename safety and prevents security issues.

**Parameters:**
- `filename` (str): Filename to validate and sanitize

**Returns:**
- `str`: Sanitized filename safe for filesystem use

**Sanitization Rules:**
- Removes directory traversal patterns (`../`, `./`)
- Strips dangerous characters (`<`, `>`, `|`, etc.)
- Limits length to reasonable bounds
- Ensures non-empty result
- Adds fallback names for invalid inputs

**Example:**
```python
# Safe filename remains unchanged
safe_name = manager.validate_filename("my_conversation")
assert safe_name == "my_conversation"

# Dangerous filename gets sanitized
dangerous = "../../../etc/passwd"
sanitized = manager.validate_filename(dangerous)
assert sanitized == "etc_passwd"  # Directory traversal removed

# Special characters handled
special = "conv<>|?*eration"
clean = manager.validate_filename(special)
assert clean == "conv_eration"  # Special chars replaced with underscores
```

## Error Handling

### ConversationManagerError

Base exception class for conversation management errors.

**Common Error Types:**
- **FileNotFoundError**: Conversation file doesn't exist
- **PermissionError**: Insufficient filesystem permissions
- **ValidationError**: Invalid conversation data format
- **CorruptionError**: File corruption detected
- **BackupError**: Backup operation failed

**Error Handling Patterns:**
```python
from src.services.conversation_manager import ConversationManagerError

try:
    success, result = manager.load_conversation("nonexistent")
    if not success:
        print(f"Load failed: {result}")
        
except ConversationManagerError as e:
    error_type = type(e).__name__
    
    if "FileNotFound" in error_type:
        print("File doesn't exist - create new conversation?")
    elif "Permission" in error_type:
        print("Check file permissions or run with appropriate access")
    elif "Validation" in error_type:
        print("Conversation data is corrupted or invalid format")
    else:
        print(f"Unexpected error: {e}")
```

## Configuration & Setup

### Directory Management

**Automatic Directory Creation:**
```python
# Default conversation directory
manager = ConversationManager()  # Uses './conversation_history/'

# Custom directory
manager = ConversationManager(base_dir="/custom/path/conversations")

# Directory created automatically if it doesn't exist
```

**Directory Structure:**
```
conversation_history/
├── conversation_1.json
├── conversation_2.json
├── backups/
│   ├── conversation_1.backup
│   └── conversation_2.backup
└── .gitkeep
```

### File Format Specification

Conversations are stored as JSON files with standardized structure:

```json
[
  {
    "role": "system",
    "content": "You are a helpful assistant.",
    "timestamp": "2025-01-07T10:30:00Z"
  },
  {
    "role": "user", 
    "content": "What is the weather like today?",
    "timestamp": "2025-01-07T10:30:15Z"
  },
  {
    "role": "assistant",
    "content": "I don't have access to current weather data, but I can help you find weather information.",
    "timestamp": "2025-01-07T10:30:18Z"
  }
]
```

## Advanced Usage Patterns

### Batch Operations

```python
def backup_all_conversations(manager):
    """Create backups of all conversations."""
    conversations = manager.get_conversation_list()
    
    for filename in conversations:
        success, conversation = manager.load_conversation(filename)
        if success:
            backup_name = f"{filename}_backup_{datetime.now().strftime('%Y%m%d')}"
            manager.save_conversation(conversation, backup_name, create_backup=False)
```

### Conversation Migration

```python
def migrate_conversation_format(manager, filename):
    """Migrate old format conversations to new format."""
    success, conversation = manager.load_conversation(filename)
    
    if success:
        # Add timestamps to messages missing them
        for message in conversation:
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now().isoformat()
        
        # Save with updated format
        return manager.save_conversation(conversation, filename)
    
    return False, "Failed to load conversation for migration"
```

### Conversation Analysis

```python
def analyze_conversation(manager, filename):
    """Analyze conversation statistics."""
    success, conversation = manager.load_conversation(filename)
    
    if not success:
        return None
        
    stats = {
        'total_messages': len(conversation),
        'user_messages': len([m for m in conversation if m['role'] == 'user']),
        'assistant_messages': len([m for m in conversation if m['role'] == 'assistant']),
        'total_characters': sum(len(m['content']) for m in conversation),
        'average_message_length': sum(len(m['content']) for m in conversation) / len(conversation)
    }
    
    return stats
```

## Integration Examples

### Streamlit Integration

```python
import streamlit as st
from src.services.conversation_manager import ConversationManager

@st.cache_resource
def get_conversation_manager():
    """Cached conversation manager instance."""
    return ConversationManager()

def save_current_conversation():
    """Save current Streamlit session conversation."""
    if 'conversation' in st.session_state:
        manager = get_conversation_manager()
        
        filename = st.text_input("Save as:", value="my_conversation")
        if st.button("Save"):
            success, message = manager.save_conversation(
                st.session_state.conversation,
                filename
            )
            
            if success:
                st.success(message)
            else:
                st.error(f"Save failed: {message}")

def load_conversation_selector():
    """Conversation loading interface."""
    manager = get_conversation_manager()
    conversations = manager.get_conversation_list()
    
    if conversations:
        selected = st.selectbox("Load conversation:", conversations)
        if st.button("Load"):
            success, result = manager.load_conversation(selected)
            
            if success:
                st.session_state.conversation = result
                st.rerun()
            else:
                st.error(f"Load failed: {result}")
    else:
        st.info("No saved conversations found")
```

### Background Auto-Save

```python
import threading
import time
from queue import Queue

class AutoSaveManager:
    """Background auto-save for conversations."""
    
    def __init__(self, conversation_manager, save_interval=30):
        self.manager = conversation_manager
        self.save_queue = Queue()
        self.save_interval = save_interval
        self.running = True
        
        # Start background thread
        self.thread = threading.Thread(target=self._auto_save_worker)
        self.thread.daemon = True
        self.thread.start()
    
    def queue_save(self, conversation, filename):
        """Queue conversation for auto-save."""
        self.save_queue.put((conversation.copy(), filename))
    
    def _auto_save_worker(self):
        """Background worker for auto-saving."""
        while self.running:
            if not self.save_queue.empty():
                conversation, filename = self.save_queue.get()
                
                try:
                    success, message = self.manager.save_conversation(
                        conversation, 
                        f"autosave_{filename}",
                        create_backup=False
                    )
                    if not success:
                        print(f"Auto-save failed: {message}")
                except Exception as e:
                    print(f"Auto-save error: {e}")
            
            time.sleep(self.save_interval)

# Usage
auto_saver = AutoSaveManager(conversation_manager, save_interval=60)
auto_saver.queue_save(current_conversation, "session_1")
```

This API provides comprehensive conversation management capabilities with enterprise-grade reliability and data protection features.

---

*Next: [Utilities API](utilities.md) - Helper functions and session state management*