"""Conversation management service with improved error handling and validation."""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path


class ConversationError(Exception):
    """Custom exception for conversation management errors."""
    pass


class ConversationManager:
    """Manages conversation loading, saving, and validation with robust error handling."""
    
    def __init__(self, conversation_dir: str = "conversation_history"):
        """
        Initialize the conversation manager.
        
        Args:
            conversation_dir: Directory where conversations are stored
        """
        self.conversation_dir = Path(conversation_dir)
        self._ensure_directory_exists()
        
    def _ensure_directory_exists(self) -> None:
        """Ensure the conversation directory exists."""
        try:
            self.conversation_dir.mkdir(exist_ok=True)
        except OSError as e:
            raise ConversationError(f"Failed to create conversation directory: {e}")
    
    def validate_conversation(self, conversation: Any) -> bool:
        """
        Validate conversation data structure.
        
        Args:
            conversation: Conversation data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(conversation, list):
            return False
        
        for item in conversation:
            if not isinstance(item, dict):
                return False
            if 'user' not in item or 'ai' not in item:
                return False
            if not isinstance(item['user'], str) or not isinstance(item['ai'], str):
                return False
                
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove path components to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename = filename + '.json'
            
        # Prevent empty filenames
        if filename == '.json':
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        return filename
    
    def get_conversation_path(self, filename: str) -> Path:
        """
        Get full path for conversation file.
        
        Args:
            filename: Conversation filename
            
        Returns:
            Full path to conversation file
        """
        sanitized = self.sanitize_filename(filename)
        return self.conversation_dir / sanitized
    
    def save_conversation(
        self,
        conversation: List[Dict[str, str]],
        filename: str,
        create_backup: bool = True
    ) -> Tuple[bool, str]:
        """
        Save conversation to file with backup and validation.
        
        Args:
            conversation: List of conversation messages
            filename: Name of file to save to
            create_backup: Whether to create backup of existing file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate conversation data
            if not self.validate_conversation(conversation):
                return False, "Invalid conversation data format"
            
            file_path = self.get_conversation_path(filename)
            backup_path = file_path.with_suffix('.backup')
            
            # Create backup if file exists and backup is requested
            if create_backup and file_path.exists():
                try:
                    shutil.copy2(file_path, backup_path)
                except OSError as e:
                    return False, f"Failed to create backup: {e}"
            
            # Save conversation
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(conversation, f, indent=2, ensure_ascii=False)
            except (OSError, TypeError) as e:
                # Restore from backup if save failed
                if create_backup and backup_path.exists():
                    try:
                        shutil.copy2(backup_path, file_path)
                    except OSError:
                        pass  # Backup restore failed, but we still need to report original error
                return False, f"Failed to save conversation: {e}"
            
            # Remove backup on successful save
            if create_backup and backup_path.exists():
                try:
                    backup_path.unlink()
                except OSError:
                    pass  # Backup removal failed, but save was successful
            
            timestamp = datetime.now().strftime("%b %d, %Y %H:%M")
            message_count = len(conversation)
            return True, f"Saved to '{filename}' ({message_count} messages, {timestamp})"
            
        except Exception as e:
            return False, f"Unexpected error saving conversation: {e}"
    
    def load_conversation(self, filename: str) -> Tuple[bool, str, Optional[List[Dict[str, str]]]]:
        """
        Load conversation from file with validation.
        
        Args:
            filename: Name of file to load from
            
        Returns:
            Tuple of (success, message, conversation_data)
        """
        try:
            file_path = self.get_conversation_path(filename)
            
            if not file_path.exists():
                return False, f"Conversation file '{filename}' not found", None
            
            # Load and parse JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in '{filename}': {e}", None
            except OSError as e:
                return False, f"Failed to read '{filename}': {e}", None
            
            # Validate conversation structure
            if not self.validate_conversation(conversation):
                return False, f"Invalid conversation format in '{filename}'", None
            
            return True, f"Loaded '{filename}' ({len(conversation)} messages)", conversation
            
        except Exception as e:
            return False, f"Unexpected error loading conversation: {e}", None
    
    def list_conversations(self, exclude_auto_save: bool = True) -> List[str]:
        """
        List all available conversation files.
        
        Args:
            exclude_auto_save: Whether to exclude auto-save files
            
        Returns:
            List of conversation filenames (without .json extension)
        """
        try:
            conversations = []
            for file_path in self.conversation_dir.glob("*.json"):
                filename = file_path.stem  # Filename without extension
                
                # Skip auto-save files if requested
                if exclude_auto_save and filename == 'restore_last_convo':
                    continue
                    
                # Skip backup files
                if filename.endswith('.backup'):
                    continue
                    
                conversations.append(filename)
            
            return sorted(conversations)
            
        except OSError:
            return []
    
    def delete_conversation(self, filename: str) -> Tuple[bool, str]:
        """
        Delete a conversation file.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            file_path = self.get_conversation_path(filename)
            
            if not file_path.exists():
                return False, f"Conversation '{filename}' not found"
            
            file_path.unlink()
            return True, f"Deleted conversation '{filename}'"
            
        except OSError as e:
            return False, f"Failed to delete '{filename}': {e}"
        except Exception as e:
            return False, f"Unexpected error deleting conversation: {e}"
    
    def auto_save_conversation(self, conversation: List[Dict[str, str]]) -> Tuple[bool, str]:
        """
        Auto-save conversation for recovery purposes.
        
        Args:
            conversation: Conversation to save
            
        Returns:
            Tuple of (success, message)
        """
        return self.save_conversation(
            conversation, 
            "restore_last_convo.json", 
            create_backup=False
        )
    
    def get_conversation_stats(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics about a conversation file.
        
        Args:
            filename: Conversation filename
            
        Returns:
            Dictionary with stats or None if file doesn't exist
        """
        try:
            file_path = self.get_conversation_path(filename)
            
            if not file_path.exists():
                return None
            
            # Get file stats
            stat = file_path.stat()
            
            # Load conversation for content stats
            success, _, conversation = self.load_conversation(filename)
            if not success or conversation is None:
                return None
            
            # Calculate content statistics
            total_user_chars = sum(len(msg['user']) for msg in conversation)
            total_ai_chars = sum(len(msg['ai']) for msg in conversation)
            
            return {
                'filename': filename,
                'message_count': len(conversation),
                'file_size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'total_user_characters': total_user_chars,
                'total_ai_characters': total_ai_chars,
                'total_characters': total_user_chars + total_ai_chars
            }
            
        except Exception:
            return None