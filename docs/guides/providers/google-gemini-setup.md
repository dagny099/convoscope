# Google Gemini Setup Guide

## Overview

Google's Gemini models provide cost-effective, high-quality AI with generous free tiers and multimodal capabilities. This guide walks you through setting up Gemini with Convoscope.

!!! warning "Important: Environment Variable Name"
    Use `GEMINI_API_KEY` (not `GOOGLE_API_KEY`) - this is the most common setup error!

## Quick Setup

### 1. Get Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the top navigation
4. Click "Create API key in new project" (or select existing project)
5. Copy the API key (starts with `AIzaSy`)

!!! info "Free Tier Available"
    Google AI Studio offers generous free quotas perfect for development and testing.

### 2. Set Environment Variable

=== "Linux/macOS"
    ```bash
    # Temporary (current session only)
    export GEMINI_API_KEY="AIzaSy-your-actual-key-here"
    
    # Permanent (add to ~/.bashrc or ~/.zshrc)
    echo 'export GEMINI_API_KEY="AIzaSy-your-actual-key-here"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Windows"
    ```powershell
    # PowerShell (temporary)
    $env:GEMINI_API_KEY="AIzaSy-your-actual-key-here"
    
    # Permanent (Windows 10/11)
    setx GEMINI_API_KEY "AIzaSy-your-actual-key-here"
    ```

=== ".env File"
    ```bash
    # Create/edit .env file in project root
    echo "GEMINI_API_KEY=AIzaSy-your-actual-key-here" >> .env
    ```

### 3. Verify Setup

Test your API key:

```bash
# Quick API test
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY"

# Test with Convoscope
python -c "
from src.services.llm_service import LLMService
service = LLMService()
print('Google available:', 'google' in service.get_available_providers())
print('Models:', service.get_available_models('google'))
"
```

## Available Models

### Gemini 1.5 Pro (Recommended) ⭐ Default
- **Model ID**: `gemini-1.5-pro`
- **Best For**: Complex reasoning, long documents, multimodal tasks
- **Context**: 1M+ tokens (longest available)
- **Cost**: Free tier → $3.50/1M input, $10.50/1M output tokens
- **Features**: Text, images, audio, video understanding

### Gemini Pro (Fast)
- **Model ID**: `gemini-pro`  
- **Best For**: Quick responses, simple tasks, high-volume usage
- **Context**: 30K tokens
- **Cost**: Free tier → $0.35/1M input, $1.05/1M output tokens
- **Speed**: Fastest response times

## Key Features

### Cost Benefits
- **Free Tier**: 15 requests/minute, 1 million tokens/minute
- **Low Cost**: Most affordable among major providers
- **High Quotas**: Generous rate limits even on free tier

### Technical Capabilities
- **Long Context**: Up to 1M+ tokens (industry leading)
- **Multimodal**: Native support for text, images, audio, video
- **Code Understanding**: Strong programming capabilities
- **Multiple Languages**: Supports 100+ languages

### Integration Benefits
- **Google Ecosystem**: Seamless integration with Google services
- **Latest Technology**: Cutting-edge AI from Google DeepMind
- **Rapid Updates**: Frequent model improvements and new features

## Configuration Options

### Basic Configuration

```python
# Default configuration in Convoscope
GEMINI_CONFIG = {
    "default_model": "gemini-1.5-pro",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
}
```

### Advanced Configuration

=== "Safety Settings"
    ```python
    # Configure safety filters
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
    ```

=== "Generation Config"
    ```python
    # Custom generation parameters
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 4000,
        "candidate_count": 1,
        "stop_sequences": ["END"]
    }
    ```

=== "Multimodal Setup"
    ```python
    # For image/video inputs (future feature)
    multimodal_config = {
        "enable_images": True,
        "enable_audio": True,
        "max_file_size_mb": 20
    }
    ```

## Free Tier Details

### Quotas & Limits

| Metric | Free Tier | Paid Tier |
|--------|-----------|-----------|
| **Requests/minute** | 15 | 360 |
| **Tokens/minute** | 1,000,000 | 4,000,000 |
| **Requests/day** | 1,500 | No limit |
| **Context length** | Full (1M+) | Full (1M+) |

### Cost After Free Tier

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| **gemini-1.5-pro** | $3.50 | $10.50 |
| **gemini-pro** | $0.35 | $1.05 |

## Testing Your Setup

### 1. Basic Functionality Test

```python
# Test basic completion
from src.services.llm_service import LLMService

service = LLMService()
messages = [
    {"role": "user", "content": "Write a haiku about coding."}
]

try:
    response = service.get_completion("google", "gemini-1.5-pro", messages)
    print(f"✅ Google Gemini working: {response}")
except Exception as e:
    print(f"❌ Google Gemini error: {e}")
```

### 2. Model Comparison Test

```python
# Test different models
models = ["gemini-1.5-pro", "gemini-pro"]
test_prompt = "Explain machine learning in 100 words."

for model in models:
    try:
        response = service.get_completion("google", model, [
            {"role": "user", "content": test_prompt}
        ])
        print(f"✅ {model}: {len(response)} characters")
    except Exception as e:
        print(f"❌ {model} failed: {e}")
```

### 3. Long Context Test

```python
# Test long context capability (unique to Gemini 1.5 Pro)
long_document = "Lorem ipsum dolor sit amet..." * 10000  # Very long text
prompt = f"Summarize this document:\n\n{long_document}"

try:
    response = service.get_completion("google", "gemini-1.5-pro", [
        {"role": "user", "content": prompt}
    ])
    print(f"✅ Long context test passed: {len(response)} chars")
except Exception as e:
    print(f"❌ Long context test failed: {e}")
```

## Troubleshooting

### Common Issues

=== "❌ Wrong Environment Variable"
    
    **Error**: `Invalid API key for google`
    **Most Common Cause**: Using `GOOGLE_API_KEY` instead of `GEMINI_API_KEY`
    
    **Solutions**:
    1. **Check variable name**:
       ```bash
       # Wrong - will not work
       export GOOGLE_API_KEY="AIzaSy..."
       
       # Correct - will work  
       export GEMINI_API_KEY="AIzaSy..."
       ```
    2. **Verify it's set**:
       ```bash
       echo $GEMINI_API_KEY
       ```
    3. **Restart application** after changing environment variables

=== "🔑 API Key Issues"
    
    **Error**: Authentication or permission errors
    
    **Solutions**:
    1. **Check key format**: Must start with `AIzaSy`
    2. **Verify in Google AI Studio**: Ensure key is active
    3. **Check API access**: Ensure Generative Language API is enabled
    4. **Test directly**:
       ```bash
       curl -X POST \
         -H "Content-Type: application/json" \
         -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
         "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY"
       ```

=== "📦 Missing Dependencies"
    
    **Error**: `No module named 'google.generativeai'` or similar
    
    **Solutions**:
    1. **Install required packages**:
       ```bash
       pip install google-generativeai
       ```
    2. **Update requirements**:
       ```bash
       pip install -r requirements.txt
       ```
    3. **Check Python environment**: Ensure you're using the correct venv

=== "🚫 Rate Limiting"
    
    **Error**: `Resource exhausted` or quota exceeded
    
    **Solutions**:
    1. **Check quotas**: Visit [Google AI Studio quotas](https://aistudio.google.com/app/quota)
    2. **Monitor usage**: Track requests per minute/day
    3. **Implement delays**: Add pauses between requests
    4. **Upgrade plan**: Move to paid tier for higher limits

### Advanced Troubleshooting

=== "🔍 Debug Mode"
    
    Enable detailed logging:
    ```python
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Also enable LiteLLM debug mode
    import litellm
    litellm.set_verbose = True
    ```

=== "🧪 Direct API Testing"
    
    Test bypassing Convoscope:
    ```python
    import google.generativeai as genai
    import os
    
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, world!")
    print(response.text)
    ```

=== "📊 Quota Monitoring"
    
    Check your current usage:
    ```python
    # Monitor through Google AI Studio
    # No programmatic API for usage yet
    # Visit: https://aistudio.google.com/app/quota
    ```

## Best Practices

### Cost Optimization
- ✅ Start with free tier for development
- ✅ Use `gemini-pro` for simple tasks
- ✅ Use `gemini-1.5-pro` for complex reasoning
- ✅ Monitor usage in Google AI Studio
- ❌ Don't exceed free tier unnecessarily

### Performance
- ✅ Use appropriate model for task complexity
- ✅ Leverage long context when beneficial
- ✅ Implement proper retry logic
- ✅ Cache responses when possible
- ❌ Don't use 1.5 Pro for trivial tasks

### Security
- ✅ Store API keys securely
- ✅ Use separate keys for dev/prod
- ✅ Monitor usage for anomalies
- ❌ Never commit keys to repositories
- ❌ Don't share keys in plain text

## Integration with Convoscope

### Default Configuration

Convoscope uses these Gemini defaults:

```python
GEMINI_DEFAULTS = {
    "model": "gemini-1.5-pro",       # Most capable with long context
    "temperature": 0.7,              # Balanced creativity
    "max_tokens": 2000,              # Reasonable responses
    "timeout": 30,                   # 30-second timeout
    "max_retries": 3,                # Retry failed requests
}
```

### Model Selection Strategy

The app automatically selects models based on:
- **Default**: `gemini-1.5-pro` for best capabilities
- **Fallback**: `gemini-pro` for faster responses
- **User choice**: Override via UI dropdown

### Fallback Behavior

If Gemini fails, Convoscope:
1. Retries up to 3 times with exponential backoff
2. Falls back to OpenAI or Anthropic if configured
3. Shows informative error messages
4. Preserves conversation context

## Comparison with Other Providers

### vs OpenAI
- **Advantages**: Free tier, longer context, lower cost, multimodal
- **Disadvantages**: Newer ecosystem, fewer integrations
- **Use when**: Cost is important, need long context

### vs Anthropic
- **Advantages**: Free tier, longer context, much lower cost  
- **Disadvantages**: May have lower quality for complex reasoning
- **Use when**: Budget-conscious, experimental projects

### Unique Features
- **1M+ token context**: Process entire books/codebases
- **Multimodal native**: Built-in image/audio understanding
- **Free tier**: Generous quotas for development
- **Google integration**: Seamless with Google ecosystem

## Getting Help

### Resources
- [Google AI Studio](https://aistudio.google.com/) - API key management
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Google AI Developer Discord](https://discord.gg/google-dev)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs) - Enterprise features

### Support Channels
- **API Issues**: Check troubleshooting above  
- **Quota Issues**: Visit Google AI Studio quota page
- **Technical Problems**: Google AI Developer Discord
- **Integration Help**: See [Multi-Provider Setup](../multi-provider-setup.md)

### Common Resources
- **Status Page**: [Google Cloud Status](https://status.cloud.google.com/)
- **Changelog**: [AI Studio Updates](https://ai.google.dev/gemini-api/docs/changelog)
- **Pricing**: [Current pricing page](https://ai.google.dev/pricing)

## Next Steps

### Immediate Actions
1. ✅ Verify `GEMINI_API_KEY` is set correctly
2. ✅ Test basic functionality with provided examples
3. ✅ Check quota usage in Google AI Studio
4. ✅ Integrate with your application workflow

### Advanced Setup
- [Configure other providers for redundancy →](../multi-provider-setup.md)
- [Set up advanced configuration →](../configuration.md)
- [Implement cost monitoring →](../advanced-usage.md)

---

**⚠️ Remember**: The most common issue is using `GOOGLE_API_KEY` instead of `GEMINI_API_KEY`. Always double-check your environment variable name!