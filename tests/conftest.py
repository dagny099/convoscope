"""Pytest configuration and shared fixtures for Convoscope tests."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime


@pytest.fixture
def mock_conversation():
    """Sample conversation data for testing."""
    return [
        {"user": "Hello, how are you?", "ai": "I'm doing well, thank you! How can I help you today?"},
        {"user": "What is Python?", "ai": "Python is a high-level programming language known for its simplicity and readability."},
        {"user": "Thanks for the info!", "ai": "You're welcome! Feel free to ask if you have any other questions."}
    ]


@pytest.fixture
def temp_conversation_dir():
    """Create a temporary directory for conversation files during testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_choice = Mock()
    mock_choice.message.content = "This is a mock AI response for testing purposes."
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    mock_service = Mock()
    mock_service.get_completion.return_value = "This is a mocked LLM response."
    return mock_service


@pytest.fixture
def sample_session_state():
    """Sample session state data for testing."""
    return {
        'conversation': [],
        'priming_text': 'You are a helpful assistant.',
        'temperature': 0.7,
        'selected_model': 'gpt-3.5-turbo',
        'llm_provider': 'openai',
        'manual_name': 'test_conversation'
    }


@pytest.fixture
def mock_streamlit_session_state():
    """Mock Streamlit session state."""
    with patch('streamlit.session_state') as mock_state:
        mock_state.conversation = []
        mock_state.priming_text = 'You are a helpful assistant.'
        mock_state.temperature = 0.7
        mock_state.selected_model = 'gpt-3.5-turbo'
        mock_state.llm_provider = 'openai'
        mock_state.manual_name = 'test_conversation'
        yield mock_state


# Environment variable fixtures for API keys
@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'GOOGLE_API_KEY': 'test-google-key'
    }):
        yield