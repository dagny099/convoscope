"""Multi-provider LLM service with error handling and retry logic."""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import litellm
from litellm import completion

# Configure logging for LiteLLM
logging.getLogger('litellm').setLevel(logging.WARNING)


@dataclass 
class LLMProvider:
    """Configuration for an LLM provider."""
    name: str
    models: List[str]
    env_key: str
    available: bool = False


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass


class LLMService:
    """Multi-provider LLM service with comprehensive error handling."""
    
    PROVIDERS = {
        'openai': LLMProvider(
            name='openai',
            models=['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo', 'gpt-4-turbo'],
            env_key='OPENAI_API_KEY'
        ),
        'anthropic': LLMProvider(
            name='anthropic', 
            models=['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
            env_key='ANTHROPIC_API_KEY'
        ),
        'google': LLMProvider(
            name='google',
            models=['gemini-2.5-flash', 'gemini-2.5-pro'],
            env_key='GEMINI_API_KEY'
        )
    }
    
    def __init__(self):
        """Initialize the LLM service."""
        self._check_provider_availability()
        
    def _check_provider_availability(self) -> None:
        """Check which providers have valid API keys."""
        for provider_key, provider in self.PROVIDERS.items():
            api_key = os.getenv(provider.env_key)
            provider.available = bool(api_key and api_key.strip())
    
    def get_available_providers(self) -> Dict[str, LLMProvider]:
        """Get all available providers (those with API keys)."""
        return {key: provider for key, provider in self.PROVIDERS.items() 
                if provider.available}
    
    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a specific provider."""
        if provider_name not in self.PROVIDERS:
            return []
        
        provider = self.PROVIDERS[provider_name]
        return provider.models if provider.available else []
    
    def get_completion(
        self,
        provider: str,
        model: str, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_retries: int = 3,
        timeout: int = 30
    ) -> Optional[str]:
        """
        Get completion from specified provider with error handling and retries.
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            model: Model name
            messages: List of message dictionaries
            temperature: Response temperature (0.0-1.0)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            Generated text response or None if failed
            
        Raises:
            LLMServiceError: If provider is not available or configured
        """
        # Validate provider
        if provider not in self.PROVIDERS:
            raise LLMServiceError(f"Unknown provider: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        if not provider_config.available:
            raise LLMServiceError(
                f"Provider '{provider}' is not available. "
                f"Please set the {provider_config.env_key} environment variable."
            )
        
        # Validate model
        if model not in provider_config.models:
            available_models = ", ".join(provider_config.models)
            raise LLMServiceError(
                f"Model '{model}' not available for provider '{provider}'. "
                f"Available models: {available_models}"
            )
        
        # Handle different provider model naming conventions
        if provider == 'google':
            # Google AI Studio uses 'gemini/' prefix (not 'google/')
            model_name = f"gemini/{model}"
        else:
            # Other providers use provider/model format
            model_name = f"{provider}/{model}"
        
        for attempt in range(max_retries):
            try:
                response = completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    timeout=timeout
                )
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle specific error types
                if "rate limit" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    raise LLMServiceError(f"Rate limit exceeded for {provider}")
                
                elif "api key" in error_msg or "unauthorized" in error_msg:
                    raise LLMServiceError(f"Invalid API key for {provider}")
                
                elif "timeout" in error_msg:
                    if attempt < max_retries - 1:
                        continue
                    raise LLMServiceError(f"Request timeout for {provider}")
                
                elif attempt == max_retries - 1:
                    # Final attempt failed
                    raise LLMServiceError(f"Failed after {max_retries} attempts: {str(e)}")
                
                # Wait before retrying for other errors
                time.sleep(1)
        
        return None
    
    def get_completion_with_fallback(
        self,
        messages: List[Dict[str, str]],
        primary_provider: str = "openai",
        primary_model: str = "gpt-4o-mini",
        fallback_provider: str = "anthropic", 
        fallback_model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Get completion with automatic fallback to secondary provider.
        
        Args:
            messages: List of message dictionaries
            primary_provider: First provider to try
            primary_model: Model for primary provider
            fallback_provider: Fallback provider if primary fails
            fallback_model: Model for fallback provider
            temperature: Response temperature
            
        Returns:
            Generated text response or None if all providers failed
        """
        # Try primary provider first
        try:
            return self.get_completion(
                primary_provider, primary_model, messages, temperature
            )
        except LLMServiceError:
            pass  # Try fallback
        
        # Try fallback provider
        try:
            return self.get_completion(
                fallback_provider, fallback_model, messages, temperature
            )
        except LLMServiceError:
            return None
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        Validate message format.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            True if messages are valid, False otherwise
        """
        if not isinstance(messages, list) or len(messages) == 0:
            return False
            
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if 'role' not in msg or 'content' not in msg:
                return False
            if msg['role'] not in ['system', 'user', 'assistant']:
                return False
            if not isinstance(msg['content'], str) or len(msg['content'].strip()) == 0:
                return False
                
        return True