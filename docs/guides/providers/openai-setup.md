# OpenAI Setup Guide

## Overview

OpenAI provides the most mature and widely-used LLM APIs. This guide walks you through setting up OpenAI with Convoscope, from account creation to advanced configuration.

## Quick Setup

### 1. Get Your API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Give it a descriptive name (e.g., "Convoscope Chat App")
6. Copy the key (starts with `sk-`)

!!! warning "Keep Your Key Safe"
    API keys are sensitive credentials. Store them securely and never commit them to version control.

### 2. Set Environment Variable

=== "Linux/macOS"
    ```bash
    # Temporary (current session only)
    export OPENAI_API_KEY="sk-your-actual-key-here"
    
    # Permanent (add to ~/.bashrc or ~/.zshrc)
    echo 'export OPENAI_API_KEY="sk-your-actual-key-here"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Windows"
    ```powershell
    # PowerShell (temporary)
    $env:OPENAI_API_KEY="sk-your-actual-key-here"
    
    # Permanent (Windows 10/11)
    setx OPENAI_API_KEY "sk-your-actual-key-here"
    ```

=== ".env File"
    ```bash
    # Create/edit .env file in project root
    echo "OPENAI_API_KEY=sk-your-actual-key-here" >> .env
    ```

### 3. Verify Setup

Test your API key:

```bash
# Quick API test
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models | grep -o '"gpt-[^"]*"'

# Test with Convoscope
python -c "
from src.services.llm_service import LLMService
service = LLMService()
print('OpenAI available:', 'openai' in service.get_available_providers())
print('Models:', service.get_available_models('openai'))
"
```

## Available Models

### GPT-4o Mini (Recommended Default)
- **Model ID**: `gpt-4o-mini` 
- **Best For**: General use, development, cost-conscious applications
- **Context**: 128K tokens
- **Cost**: $0.15/1M input, $0.60/1M output tokens
- **Speed**: Very fast

### GPT-4o  
- **Model ID**: `gpt-4o`
- **Best For**: Complex reasoning, multimodal tasks
- **Context**: 128K tokens  
- **Cost**: $2.50/1M input, $10/1M output tokens
- **Features**: Vision, advanced reasoning

### GPT-3.5 Turbo
- **Model ID**: `gpt-3.5-turbo`
- **Best For**: Fast responses, simple tasks
- **Context**: 16K tokens
- **Cost**: $0.50/1M input, $1.50/1M output tokens
- **Speed**: Fastest

### GPT-4 Turbo
- **Model ID**: `gpt-4-turbo`  
- **Best For**: High-quality responses, complex analysis
- **Context**: 128K tokens
- **Cost**: $10/1M input, $30/1M output tokens
- **Quality**: Highest

## Configuration Options

### Basic Configuration

```python
# Default configuration in Convoscope
OPENAI_CONFIG = {
    "default_model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
}
```

### Advanced Configuration

=== "Custom Organization"
    ```bash
    # If you're part of an OpenAI organization
    export OPENAI_ORG_ID="org-your-org-id"
    ```

=== "Custom Base URL"
    ```bash
    # For Azure OpenAI or compatible endpoints
    export OPENAI_BASE_URL="https://your-azure-endpoint.openai.azure.com/"
    ```

=== "Custom Parameters"
    ```python
    # Modify in your local configuration
    OPENAI_CUSTOM_CONFIG = {
        "model": "gpt-4o-mini",
        "temperature": 0.9,        # More creative
        "max_tokens": 4000,        # Longer responses
        "presence_penalty": 0.1,   # Reduce repetition
        "frequency_penalty": 0.1   # Encourage variety
    }
    ```

## Usage Guidelines

### Token Management

```python
# Understanding token usage
def estimate_tokens(text):
    """Rough estimation: ~4 chars = 1 token"""
    return len(text) // 4

# Example
user_message = "Write a summary of machine learning"
estimated_tokens = estimate_tokens(user_message)
print(f"Estimated tokens: {estimated_tokens}")
```

### Cost Optimization

| Strategy | Description | Savings |
|----------|-------------|---------|
| **Use gpt-4o-mini** | Default to most cost-effective model | 75% vs GPT-4 |
| **Shorter prompts** | Be concise in system messages | 20-30% |
| **Lower max_tokens** | Set appropriate response limits | 10-50% |
| **Temperature tuning** | Use lower values for deterministic tasks | N/A |

### Rate Limits

| Tier | RPM (Requests/min) | TPM (Tokens/min) | Requirements |
|------|-------------------|------------------|---------------|
| Free | 3 | 200K | New accounts |
| Tier 1 | 500 | 10M | $5+ spent |
| Tier 2 | 5,000 | 30M | $50+ spent |
| Tier 3 | 10,000 | 60M | $100+ spent |

## Testing Your Setup

### 1. Basic Functionality Test

```python
# Test basic completion
from src.services.llm_service import LLMService

service = LLMService()
messages = [
    {"role": "user", "content": "Say hello in one sentence."}
]

try:
    response = service.get_completion("openai", "gpt-4o-mini", messages)
    print(f"✅ OpenAI working: {response}")
except Exception as e:
    print(f"❌ OpenAI error: {e}")
```

### 2. Model Comparison Test

```python
# Test different models
models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]
test_prompt = "Explain quantum computing in 50 words."

for model in models:
    try:
        response = service.get_completion("openai", model, [
            {"role": "user", "content": test_prompt}
        ])
        print(f"✅ {model}: {len(response)} characters")
    except Exception as e:
        print(f"❌ {model} failed: {e}")
```

### 3. Streaming Test

```python
# Test streaming responses (if supported)
def test_streaming():
    # This would test real-time response streaming
    # Implementation depends on your streaming setup
    pass
```

## Troubleshooting

### Common Issues

=== "❌ Invalid API Key"
    
    **Error**: `Incorrect API key provided`
    
    **Solutions**:
    1. **Check key format**: Must start with `sk-`
    2. **Verify key is active**: Visit OpenAI dashboard
    3. **Check environment variable**:
       ```bash
       echo $OPENAI_API_KEY
       ```
    4. **Regenerate key**: Create new key if old one is compromised

=== "💳 Insufficient Credits"
    
    **Error**: `You exceeded your current quota`
    
    **Solutions**:
    1. **Check billing**: Visit [OpenAI Billing](https://platform.openai.com/account/billing)
    2. **Add payment method**: Required after free trial
    3. **Set usage limits**: Prevent surprise charges
    4. **Monitor usage**: Track token consumption

=== "🚫 Rate Limited"
    
    **Error**: `Rate limit exceeded`
    
    **Solutions**:
    1. **Wait and retry**: Limits reset after time window
    2. **Reduce request frequency**: Add delays between calls
    3. **Upgrade tier**: Increase rate limits with higher usage
    4. **Use exponential backoff**: Automatic retry with delays

=== "🌐 Network Issues"
    
    **Error**: Connection timeouts or network errors
    
    **Solutions**:
    1. **Check internet connection**
    2. **Verify OpenAI status**: [status.openai.com](https://status.openai.com/)
    3. **Configure proxy**: If behind corporate firewall
    4. **Increase timeout**: For slow connections

### Advanced Troubleshooting

=== "🔍 Debugging API Calls"
    
    Enable detailed logging:
    ```python
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Your API calls will now show detailed information
    ```

=== "🧪 Testing API Directly"
    
    Test without Convoscope:
    ```bash
    curl -X POST https://api.openai.com/v1/chat/completions \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 50
      }'
    ```

=== "📊 Monitoring Usage"
    
    Track your usage:
    ```python
    # Check current usage
    import requests
    
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    response = requests.get("https://api.openai.com/v1/usage", headers=headers)
    print(response.json())
    ```

## Best Practices

### Security
- ✅ Store API keys in environment variables
- ✅ Use separate keys for development/production
- ✅ Rotate keys regularly
- ❌ Never commit keys to version control
- ❌ Never share keys in plain text

### Performance
- ✅ Use appropriate models for each task
- ✅ Set reasonable max_tokens limits
- ✅ Implement retry logic with exponential backoff
- ✅ Cache responses when appropriate
- ❌ Don't use GPT-4 for simple tasks

### Cost Management
- ✅ Monitor usage regularly
- ✅ Set billing alerts
- ✅ Use gpt-4o-mini for development
- ✅ Optimize prompts for clarity
- ❌ Don't leave unlimited spending enabled

## Integration with Convoscope

### Default Configuration

Convoscope uses these OpenAI defaults:

```python
OPENAI_DEFAULTS = {
    "model": "gpt-4o-mini",      # Cost-effective
    "temperature": 0.7,          # Balanced creativity
    "max_tokens": 2000,          # Reasonable responses
    "timeout": 30,               # 30-second timeout
    "max_retries": 3,            # Retry failed requests
}
```

### Customizing Models

Override defaults in the UI:
1. Select "openai" from provider dropdown
2. Choose your preferred model from the model dropdown
3. Adjust temperature slider if needed
4. Your settings persist in the session

### Fallback Behavior

If OpenAI fails, Convoscope automatically:
1. Retries up to 3 times with exponential backoff
2. Falls back to other configured providers
3. Shows clear error messages to users
4. Logs detailed error information

## Getting Help

### Resources
- [OpenAI Documentation](https://platform.openai.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [OpenAI Community Forum](https://community.openai.com/)
- [OpenAI Status Page](https://status.openai.com/)

### Support
- **Account Issues**: [OpenAI Support](https://help.openai.com/)
- **API Problems**: Check the troubleshooting section above
- **Billing Questions**: Visit OpenAI billing dashboard
- **Technical Integration**: See [Multi-Provider Setup Guide](../multi-provider-setup.md)

---

**Next Steps**: 
- [Add Anthropic as fallback →](anthropic-setup.md)
- [Configure advanced settings →](../configuration.md)
- [Test multi-provider setup →](../multi-provider-setup.md#testing-your-setup)