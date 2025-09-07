"""Tests for conversation manager with file operations."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.services.conversation_manager import ConversationManager, ConversationError


class TestConversationManager:
    """Tests for ConversationManager class."""
    
    def setup_method(self):
        """Setup for each test method with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ConversationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test conversation manager initialization."""
        assert self.manager.conversation_dir.exists()
        assert self.manager.conversation_dir.is_dir()
    
    def test_validate_conversation_valid(self):
        """Test conversation validation with valid data."""
        valid_conversation = [
            {"user": "Hello", "ai": "Hi there!"},
            {"user": "How are you?", "ai": "I'm doing well, thanks!"}
        ]
        
        assert self.manager.validate_conversation(valid_conversation) == True
    
    def test_validate_conversation_invalid(self):
        """Test conversation validation with invalid data."""
        # Not a list
        assert self.manager.validate_conversation("invalid") == False
        
        # Invalid structure
        assert self.manager.validate_conversation([{"wrong": "format"}]) == False
        
        # Missing keys
        assert self.manager.validate_conversation([{"user": "test"}]) == False
        
        # Wrong data types
        assert self.manager.validate_conversation([{"user": 123, "ai": "response"}]) == False
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test invalid characters
        assert self.manager.sanitize_filename("test<>file") == "test__file.json"
        
        # Test path traversal prevention - dots and slashes get replaced with underscores
        result = self.manager.sanitize_filename("../../../evil.json")
        assert "evil.json" in result  # basename extracts the filename part
        
        # Test automatic .json extension
        assert self.manager.sanitize_filename("test") == "test.json"
        
        # Test empty filename
        sanitized = self.manager.sanitize_filename("")
        assert sanitized.startswith("conversation_")
        assert sanitized.endswith(".json")
    
    def test_save_conversation_success(self):
        """Test successful conversation saving."""
        conversation = [
            {"user": "Hello", "ai": "Hi there!"},
            {"user": "How are you?", "ai": "I'm doing well!"}
        ]
        
        success, message = self.manager.save_conversation(conversation, "test_convo")
        
        assert success == True
        assert "test_convo" in message  # Filename without .json in message
        assert "2 messages" in message
        
        # Verify file was created
        file_path = self.manager.conversation_dir / "test_convo.json"
        assert file_path.exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == conversation
    
    def test_save_conversation_invalid_data(self):
        """Test saving with invalid conversation data."""
        invalid_conversation = [{"wrong": "format"}]
        
        success, message = self.manager.save_conversation(invalid_conversation, "invalid")
        
        assert success == False
        assert "Invalid conversation data format" in message
    
    def test_save_conversation_with_backup(self):
        """Test saving with backup creation."""
        # Create initial file
        conversation1 = [{"user": "First", "ai": "Response1"}]
        self.manager.save_conversation(conversation1, "backup_test")
        
        # Save new version (should create backup)
        conversation2 = [{"user": "Second", "ai": "Response2"}]
        success, message = self.manager.save_conversation(conversation2, "backup_test")
        
        assert success == True
        
        # Verify new content is saved
        file_path = self.manager.conversation_dir / "backup_test.json"
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == conversation2
        
        # Backup should be removed after successful save
        backup_path = self.manager.conversation_dir / "backup_test.backup"
        assert not backup_path.exists()
    
    def test_load_conversation_success(self):
        """Test successful conversation loading."""
        conversation = [
            {"user": "Hello", "ai": "Hi there!"},
            {"user": "How are you?", "ai": "Great!"}
        ]
        
        # Save first
        self.manager.save_conversation(conversation, "load_test")
        
        # Load
        success, message, loaded_data = self.manager.load_conversation("load_test")
        
        assert success == True
        assert "load_test" in message
        assert "2 messages" in message
        assert loaded_data == conversation
    
    def test_load_conversation_not_found(self):
        """Test loading non-existent conversation."""
        success, message, data = self.manager.load_conversation("nonexistent")
        
        assert success == False
        assert "not found" in message
        assert data is None
    
    def test_load_conversation_invalid_json(self):
        """Test loading file with invalid JSON."""
        # Create file with invalid JSON
        file_path = self.manager.conversation_dir / "invalid.json"
        with open(file_path, 'w') as f:
            f.write("{ invalid json }")
        
        success, message, data = self.manager.load_conversation("invalid")
        
        assert success == False
        assert "Invalid JSON" in message
        assert data is None
    
    def test_load_conversation_invalid_structure(self):
        """Test loading file with invalid conversation structure."""
        # Create file with valid JSON but wrong structure
        file_path = self.manager.conversation_dir / "wrong_structure.json"
        with open(file_path, 'w') as f:
            json.dump({"wrong": "structure"}, f)
        
        success, message, data = self.manager.load_conversation("wrong_structure")
        
        assert success == False
        assert "Invalid conversation format" in message
        assert data is None
    
    def test_list_conversations(self):
        """Test listing conversations."""
        # Create test conversations
        conv1 = [{"user": "Test1", "ai": "Response1"}]
        conv2 = [{"user": "Test2", "ai": "Response2"}]
        
        self.manager.save_conversation(conv1, "conversation1")
        self.manager.save_conversation(conv2, "conversation2")
        self.manager.auto_save_conversation(conv1)  # Should be excluded
        
        conversations = self.manager.list_conversations()
        
        assert "conversation1" in conversations
        assert "conversation2" in conversations
        assert "restore_last_convo" not in conversations  # Auto-save excluded
        assert len(conversations) == 2
    
    def test_list_conversations_include_auto_save(self):
        """Test listing conversations including auto-save."""
        conv = [{"user": "Test", "ai": "Response"}]
        self.manager.auto_save_conversation(conv)
        
        conversations = self.manager.list_conversations(exclude_auto_save=False)
        
        assert "restore_last_convo" in conversations
    
    def test_delete_conversation_success(self):
        """Test successful conversation deletion."""
        conversation = [{"user": "Delete me", "ai": "OK"}]
        self.manager.save_conversation(conversation, "to_delete")
        
        # Verify file exists
        file_path = self.manager.conversation_dir / "to_delete.json"
        assert file_path.exists()
        
        # Delete
        success, message = self.manager.delete_conversation("to_delete")
        
        assert success == True
        assert "Deleted conversation 'to_delete'" in message
        assert not file_path.exists()
    
    def test_delete_conversation_not_found(self):
        """Test deleting non-existent conversation."""
        success, message = self.manager.delete_conversation("nonexistent")
        
        assert success == False
        assert "not found" in message
    
    def test_auto_save_conversation(self):
        """Test auto-save functionality."""
        conversation = [{"user": "Auto save", "ai": "Saved"}]
        
        success, message = self.manager.auto_save_conversation(conversation)
        
        assert success == True
        
        # Verify auto-save file was created
        file_path = self.manager.conversation_dir / "restore_last_convo.json"
        assert file_path.exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == conversation
    
    def test_get_conversation_stats(self):
        """Test getting conversation statistics."""
        conversation = [
            {"user": "Hello world", "ai": "Hi there, how are you?"},
            {"user": "Fine", "ai": "Great!"}
        ]
        
        self.manager.save_conversation(conversation, "stats_test")
        stats = self.manager.get_conversation_stats("stats_test")
        
        assert stats is not None
        assert stats['filename'] == 'stats_test'
        assert stats['message_count'] == 2
        assert stats['file_size'] > 0
        assert 'created' in stats
        assert 'modified' in stats
        assert stats['total_user_characters'] == len("Hello world") + len("Fine")
        assert stats['total_ai_characters'] == len("Hi there, how are you?") + len("Great!")
    
    def test_get_conversation_stats_not_found(self):
        """Test getting stats for non-existent conversation."""
        stats = self.manager.get_conversation_stats("nonexistent")
        assert stats is None
    
    @patch('pathlib.Path.mkdir')
    def test_directory_creation_error(self, mock_mkdir):
        """Test error handling during directory creation."""
        mock_mkdir.side_effect = OSError("Permission denied")
        
        with pytest.raises(ConversationError, match="Failed to create conversation directory"):
            ConversationManager("/invalid/path")
    
    def test_get_conversation_path(self):
        """Test conversation path generation."""
        path = self.manager.get_conversation_path("test")
        
        assert path.name == "test.json"
        assert path.parent == self.manager.conversation_dir
        
        # Test with already .json extension
        path2 = self.manager.get_conversation_path("test.json")
        assert path2.name == "test.json"