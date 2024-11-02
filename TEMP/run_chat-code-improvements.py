# config.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import os

@dataclass
class Config:
    SAVE_PATH: str = 'conversation_history'
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 30
    
    @classmethod
    def setup_logging(cls) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chat_app.log'),
                logging.StreamHandler()
            ]
        )

# llm_handler.py
from typing import List, Dict, Optional, AsyncGenerator
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self, api_key: str, model: str, temperature: float):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def stream_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Stream responses from the LLM with retry logic and error handling.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Yields:
            String chunks of the response
            
        Raises:
            APIError: If the API call fails after retries
            TimeoutError: If the API call times out
        """
        try:
            async with asyncio.timeout(Config.TIMEOUT_SECONDS):
                response = await self._make_api_call(messages)
                async for chunk in response:
                    yield chunk
        except asyncio.TimeoutError:
            logger.error(f"API call timed out after {Config.TIMEOUT_SECONDS} seconds")
            raise TimeoutError("API request timed out")
        except Exception as e:
            logger.error(f"Error streaming LLM response: {str(e)}")
            raise

# conversation_manager.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import logging
from pathlib import Path

@dataclass
class Conversation:
    messages: List[Dict[str, str]]
    metadata: Dict[str, any]
    
    def to_json(self) -> str:
        return json.dumps({
            'messages': self.messages,
            'metadata': self.metadata
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Conversation':
        data = json.loads(json_str)
        return cls(
            messages=data['messages'],
            metadata=data['metadata']
        )

class ConversationManager:
    def __init__(self, save_dir: Path):
        self.save_dir = save_dir
        self.save_dir.mkdir(exist_ok=True)
        
    def save_conversation(self, conversation: Conversation, filename: str) -> None:
        """
        Save a conversation to disk with error handling.
        
        Args:
            conversation: Conversation object to save
            filename: Name of file to save to
            
        Raises:
            IOError: If saving fails
        """
        try:
            save_path = self.save_dir / f"{filename}.json"
            with save_path.open('w') as f:
                f.write(conversation.to_json())
            logging.info(f"Saved conversation to {save_path}")
        except Exception as e:
            logging.error(f"Failed to save conversation: {str(e)}")
            raise IOError(f"Could not save conversation: {str(e)}")

# tests/test_conversation_manager.py
import pytest
from pathlib import Path
from conversation_manager import ConversationManager, Conversation

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path / "test_conversations"

@pytest.fixture
def conversation_manager(temp_dir):
    return ConversationManager(temp_dir)

def test_save_and_load_conversation(conversation_manager):
    # Test data
    test_conversation = Conversation(
        messages=[{"role": "user", "content": "test"}],
        metadata={"timestamp": "2024-01-01"}
    )
    
    # Save conversation
    conversation_manager.save_conversation(test_conversation, "test_convo")
    
    # Load and verify
    loaded = conversation_manager.load_conversation("test_convo")
    assert loaded.messages == test_conversation.messages
    assert loaded.metadata == test_conversation.metadata
