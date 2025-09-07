"""Tests for LLM service with multi-provider support."""

import pytest
from unittest.mock import patch, Mock
from src.services.llm_service import LLMService, LLMServiceError, LLMProvider


class TestLLMService:
    """Tests for LLMService class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.llm_service = LLMService()
    
    def test_provider_initialization(self):
        """Test that providers are properly initialized."""
        providers = self.llm_service.PROVIDERS
        
        assert 'openai' in providers
        assert 'anthropic' in providers
        assert 'google' in providers
        
        # Check provider structure
        openai_provider = providers['openai']
        assert isinstance(openai_provider, LLMProvider)
        assert openai_provider.name == 'openai'
        assert len(openai_provider.models) > 0
        assert openai_provider.env_key == 'OPENAI_API_KEY'
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_check_provider_availability_with_key(self):
        """Test provider availability check when API key is present."""
        service = LLMService()
        assert service.PROVIDERS['openai'].available == True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_check_provider_availability_without_key(self):
        """Test provider availability check when API key is missing."""
        service = LLMService()
        assert service.PROVIDERS['openai'].available == False
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_available_providers(self):
        """Test getting available providers."""
        service = LLMService()
        available = service.get_available_providers()
        
        assert 'openai' in available
        assert 'anthropic' in available
        assert 'google' not in available  # No API key set
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_get_available_models(self):
        """Test getting available models for a provider."""
        service = LLMService()
        models = service.get_available_models('openai')
        
        assert len(models) > 0
        assert 'gpt-3.5-turbo' in models
    
    def test_get_available_models_invalid_provider(self):
        """Test getting models for invalid provider."""
        models = self.llm_service.get_available_models('invalid')
        assert models == []
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_available_models_unavailable_provider(self):
        """Test getting models for unavailable provider."""
        service = LLMService()
        models = service.get_available_models('openai')
        assert models == []
    
    def test_validate_messages_valid(self):
        """Test message validation with valid messages."""
        valid_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        assert self.llm_service.validate_messages(valid_messages) == True
    
    def test_validate_messages_invalid_format(self):
        """Test message validation with invalid formats."""
        # Not a list
        assert self.llm_service.validate_messages("invalid") == False
        
        # Empty list
        assert self.llm_service.validate_messages([]) == False
        
        # Invalid message structure
        invalid_messages = [{"invalid": "message"}]
        assert self.llm_service.validate_messages(invalid_messages) == False
        
        # Invalid role
        invalid_role_messages = [{"role": "invalid", "content": "test"}]
        assert self.llm_service.validate_messages(invalid_role_messages) == False
        
        # Empty content
        empty_content_messages = [{"role": "user", "content": ""}]
        assert self.llm_service.validate_messages(empty_content_messages) == False
    
    def test_get_completion_unknown_provider(self):
        """Test completion with unknown provider."""
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMServiceError, match="Unknown provider"):
            self.llm_service.get_completion("unknown", "model", messages)
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_completion_unavailable_provider(self):
        """Test completion with unavailable provider."""
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMServiceError, match="not available"):
            service.get_completion("openai", "gpt-3.5-turbo", messages)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_get_completion_invalid_model(self):
        """Test completion with invalid model."""
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMServiceError, match="not available for provider"):
            service.get_completion("openai", "invalid-model", messages)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('src.services.llm_service.completion')
    def test_get_completion_success(self, mock_completion):
        """Test successful completion."""
        # Setup mock response
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response
        
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        result = service.get_completion("openai", "gpt-3.5-turbo", messages)
        
        assert result == "Test response"
        mock_completion.assert_called_once()
        
        # Check call arguments
        call_args = mock_completion.call_args
        assert call_args[1]['model'] == 'openai/gpt-3.5-turbo'
        assert call_args[1]['messages'] == messages
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('src.services.llm_service.completion')
    def test_get_completion_rate_limit_error(self, mock_completion):
        """Test handling of rate limit error."""
        mock_completion.side_effect = Exception("rate limit exceeded")
        
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMServiceError, match="Rate limit exceeded"):
            service.get_completion("openai", "gpt-3.5-turbo", messages, max_retries=1)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('src.services.llm_service.completion')
    def test_get_completion_api_key_error(self, mock_completion):
        """Test handling of API key error."""
        mock_completion.side_effect = Exception("invalid api key")
        
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMServiceError, match="Invalid API key"):
            service.get_completion("openai", "gpt-3.5-turbo", messages)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.services.llm_service.completion')
    def test_get_completion_with_fallback_primary_success(self, mock_completion):
        """Test fallback completion when primary succeeds."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Primary response"
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response
        
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        result = service.get_completion_with_fallback(messages)
        
        assert result == "Primary response"
        # Should only call primary
        assert mock_completion.call_count == 1
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.services.llm_service.completion')
    def test_get_completion_with_fallback_primary_fails(self, mock_completion):
        """Test fallback completion when primary fails."""
        # Primary fails, fallback succeeds
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Fallback response"
        mock_response.choices = [mock_choice]
        
        def side_effect(*args, **kwargs):
            if kwargs['model'] == 'openai/gpt-3.5-turbo':
                raise Exception("Primary failed")
            return mock_response
        
        mock_completion.side_effect = side_effect
        
        service = LLMService()
        messages = [{"role": "user", "content": "Hello"}]
        
        result = service.get_completion_with_fallback(messages)
        
        assert result == "Fallback response"
        # Should call primary (with retries) plus fallback - actual count depends on retry logic
        assert mock_completion.call_count >= 2