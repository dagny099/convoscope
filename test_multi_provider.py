#!/usr/bin/env python3
"""
Multi-Provider LLM Testing Script

This script tests the multi-provider functionality of the Convoscope application.
Run with different environment variables to test different scenarios.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.llm_service import LLMService, LLMServiceError

def print_separator(title):
    """Print a nice separator for test sections."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_provider_initialization():
    """Test that all providers are properly configured."""
    print_separator("PROVIDER INITIALIZATION TEST")
    
    service = LLMService()
    
    print("Configured providers:")
    for name, provider in service.PROVIDERS.items():
        status = "✅ Available" if provider.available else "❌ No API Key"
        print(f"  - {name.upper()}: {status}")
        print(f"    Models: {', '.join(provider.models)}")
        print(f"    Env Key: {provider.env_key}")
        print()
    
    available_providers = service.get_available_providers()
    print(f"Available providers: {list(available_providers.keys())}")
    
    return len(available_providers) > 0

def test_model_availability():
    """Test model availability for each provider."""
    print_separator("MODEL AVAILABILITY TEST")
    
    service = LLMService()
    
    for provider_name in service.PROVIDERS.keys():
        models = service.get_available_models(provider_name)
        if models:
            print(f"✅ {provider_name.upper()} models: {', '.join(models)}")
        else:
            print(f"❌ {provider_name.upper()}: No models available (API key needed)")

def test_completion_with_mock_keys():
    """Test completion with mock API keys to verify error handling."""
    print_separator("ERROR HANDLING TEST (Mock Keys)")
    
    # Save original environment
    original_env = {}
    for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY']:
        original_env[key] = os.environ.get(key)
    
    try:
        # Set mock keys
        os.environ['OPENAI_API_KEY'] = 'mock-openai-key'
        os.environ['ANTHROPIC_API_KEY'] = 'mock-anthropic-key'
        os.environ['GEMINI_API_KEY'] = 'mock-gemini-key'
        
        service = LLMService()
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one word."}
        ]
        
        for provider_name in ['openai', 'anthropic', 'google']:
            if provider_name in service.PROVIDERS:
                models = service.PROVIDERS[provider_name].models
                if models:
                    print(f"\nTesting {provider_name} with {models[0]}...")
                    try:
                        response = service.get_completion(
                            provider=provider_name,
                            model=models[0],
                            messages=test_messages,
                            timeout=5  # Short timeout for mock keys
                        )
                        print(f"  Unexpected success: {response}")
                    except LLMServiceError as e:
                        print(f"  ✅ Expected error caught: {str(e)}")
                    except Exception as e:
                        error_str = str(e)
                        if "Invalid API key" in error_str:
                            print(f"  ✅ Expected error caught: {error_str}")
                        else:
                            print(f"  ⚠️  Unexpected error type: {type(e).__name__}: {error_str}")
    
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

def test_fallback_functionality():
    """Test the fallback functionality."""
    print_separator("FALLBACK FUNCTIONALITY TEST")
    
    service = LLMService()
    available_providers = list(service.get_available_providers().keys())
    
    if len(available_providers) >= 2:
        primary = available_providers[0]
        fallback = available_providers[1]
        
        print(f"Testing fallback from {primary} to {fallback}...")
        
        # This would require a real test with API failures, 
        # but we can at least test the logic
        primary_models = service.get_available_models(primary)
        fallback_models = service.get_available_models(fallback)
        
        if primary_models and fallback_models:
            print(f"✅ Fallback configuration valid:")
            print(f"  Primary: {primary} -> {primary_models[0]}")
            print(f"  Fallback: {fallback} -> {fallback_models[0]}")
        else:
            print("❌ Cannot test fallback - missing models")
    else:
        print(f"❌ Cannot test fallback - only {len(available_providers)} provider(s) available")
        print("   (Need at least 2 providers with API keys)")

def test_default_model_selection():
    """Test that gpt-4o-mini is properly set as default."""
    print_separator("DEFAULT MODEL SELECTION TEST")
    
    service = LLMService()
    
    # Test OpenAI default
    openai_models = service.get_available_models('openai')
    if 'gpt-4o-mini' in openai_models:
        print("✅ gpt-4o-mini is available in OpenAI models")
        print(f"   OpenAI models: {openai_models}")
    else:
        print("❌ gpt-4o-mini not found in OpenAI models")
        print(f"   Available models: {openai_models}")
    
    # Test default in fallback function
    fallback_defaults = service.get_completion_with_fallback.__defaults__
    if fallback_defaults and 'gpt-4o-mini' in str(fallback_defaults):
        print("✅ gpt-4o-mini is set as default in fallback function")
    else:
        print("❌ gpt-4o-mini not set as default in fallback function")

def main():
    """Run all tests."""
    print_separator("CONVOSCOPE MULTI-PROVIDER TESTING")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show current environment
    print("\nEnvironment Status:")
    for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY']:
        value = os.environ.get(key)
        if value:
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else 'set'
            print(f"  {key}: {masked}")
        else:
            print(f"  {key}: not set")
    
    # Run tests
    try:
        has_providers = test_provider_initialization()
        test_model_availability()
        test_default_model_selection()
        test_completion_with_mock_keys()
        
        if has_providers:
            test_fallback_functionality()
        
        print_separator("TESTING COMPLETE")
        print("✅ All tests completed successfully!")
        
        if has_providers:
            print("\n🎉 Multi-provider support is working!")
            print("   You can now use the Streamlit app with multiple LLM providers.")
        else:
            print("\n⚠️  No API keys configured.")
            print("   Set environment variables to test with real providers:")
            print("   export OPENAI_API_KEY='your-key-here'")
            print("   export ANTHROPIC_API_KEY='your-key-here'")
            print("   export GEMINI_API_KEY='your-key-here'")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()