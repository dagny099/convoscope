"""Tests for session state utility functions."""

import pytest
from unittest.mock import patch, Mock, MagicMock
from src.utils.session_state import (
    update_priming_text,
    initialize_session_state,
    get_session_state_value
)


class MockSessionState:
    """Mock class that behaves like Streamlit session state."""
    def __init__(self):
        self._data = {}
        
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class TestUpdatePrimingText:
    """Tests for update_priming_text function."""
    
    @patch('src.utils.session_state.st')
    def test_update_from_selectbox(self, mock_st):
        """Test updating priming text from selectbox."""
        # Setup mock session state
        mock_session_state = MockSessionState()
        mock_session_state.selectbox_choice = 'python'
        mock_st.session_state = mock_session_state
        
        priming_messages = {
            'default': 'You are a helpful assistant.',
            'python': 'You are a Python expert.'
        }
        
        update_priming_text(priming_messages)
        
        # Check that session state was updated correctly
        assert mock_session_state['priming_key'] == 'python'
        assert mock_session_state['priming_text'] == 'You are a Python expert.'
    
    @patch('src.utils.session_state.st')
    def test_update_from_button(self, mock_st):
        """Test updating priming text from button."""
        mock_session_state = MockSessionState()
        mock_st.session_state = mock_session_state
        
        priming_messages = {
            'default': 'You are a helpful assistant.',
            'data': 'You are a data scientist.'
        }
        
        new_value = ('data', 'You are a data scientist.')
        update_priming_text(priming_messages, source='button', new_value=new_value)
        
        # Check that session state was updated correctly
        assert mock_session_state['priming_key'] == 'data'
        assert mock_session_state['priming_text'] == 'You are a data scientist.'
    
    @patch('src.utils.session_state.st')
    def test_update_from_button_no_value(self, mock_st):
        """Test updating priming text from button with no new value."""
        mock_session_state = MockSessionState()
        mock_st.session_state = mock_session_state
        
        priming_messages = {'default': 'You are a helpful assistant.'}
        
        # Should not crash when new_value is None
        update_priming_text(priming_messages, source='button', new_value=None)
        
        # Session state should not be updated when new_value is None
        assert 'priming_key' not in mock_session_state
        assert 'priming_text' not in mock_session_state


class TestInitializeSessionState:
    """Tests for initialize_session_state function."""
    
    @patch('src.utils.session_state.st')
    def test_initialize_new_key(self, mock_st):
        """Test initializing a new session state key."""
        mock_st.session_state = {}
        
        initialize_session_state('test_key', 'default_value')
        
        assert mock_st.session_state['test_key'] == 'default_value'
    
    @patch('src.utils.session_state.st')
    def test_initialize_existing_key(self, mock_st):
        """Test initializing an existing session state key."""
        mock_st.session_state = {'test_key': 'existing_value'}
        
        initialize_session_state('test_key', 'default_value')
        
        # Should not overwrite existing value
        assert mock_st.session_state['test_key'] == 'existing_value'
    
    @patch('src.utils.session_state.st')
    def test_initialize_different_types(self, mock_st):
        """Test initializing with different data types."""
        mock_st.session_state = {}
        
        initialize_session_state('string_key', 'test')
        initialize_session_state('int_key', 42)
        initialize_session_state('list_key', [1, 2, 3])
        initialize_session_state('dict_key', {'a': 1})
        
        assert mock_st.session_state['string_key'] == 'test'
        assert mock_st.session_state['int_key'] == 42
        assert mock_st.session_state['list_key'] == [1, 2, 3]
        assert mock_st.session_state['dict_key'] == {'a': 1}


class TestGetSessionStateValue:
    """Tests for get_session_state_value function."""
    
    @patch('src.utils.session_state.st')
    def test_get_existing_value(self, mock_st):
        """Test getting an existing session state value."""
        mock_st.session_state = Mock()
        mock_st.session_state.get.return_value = 'existing_value'
        
        result = get_session_state_value('test_key')
        
        mock_st.session_state.get.assert_called_once_with('test_key', None)
        assert result == 'existing_value'
    
    @patch('src.utils.session_state.st')
    def test_get_non_existing_value_with_default(self, mock_st):
        """Test getting a non-existing value with default."""
        mock_st.session_state = Mock()
        mock_st.session_state.get.return_value = 'default_value'
        
        result = get_session_state_value('non_existing_key', 'default_value')
        
        mock_st.session_state.get.assert_called_once_with('non_existing_key', 'default_value')
        assert result == 'default_value'
    
    @patch('src.utils.session_state.st')
    def test_get_non_existing_value_no_default(self, mock_st):
        """Test getting a non-existing value without default."""
        mock_st.session_state = Mock()
        mock_st.session_state.get.return_value = None
        
        result = get_session_state_value('non_existing_key')
        
        mock_st.session_state.get.assert_called_once_with('non_existing_key', None)
        assert result is None