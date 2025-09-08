# Anthropic Claude Setup Guide

## Overview

Anthropic's Claude models are known for their strong reasoning capabilities, safety measures, and helpful responses. This guide walks you through setting up Claude with Convoscope.

## Quick Setup

### 1. Get Your API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://console.anthropic.com/settings/keys)
4. Click "Create Key"
5. Give it a descriptive name (e.g., "Convoscope App")
6. Copy the key (starts with `sk-ant-api03-`)

!!! info "Beta Access"
    Anthropic's API is in beta. You may need to join a waitlist or request access.

### 2. Set Environment Variable

=== "Linux/macOS"
    ```bash
    # Temporary (current session only)
    export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
    
    # Permanent (add to ~/.bashrc or ~/.zshrc)
    echo 'export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Windows"
    ```powershell
    # PowerShell (temporary)
    $env:ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
    
    # Permanent (Windows 10/11)
    setx ANTHROPIC_API_KEY "sk-ant-api03-your-actual-key-here"
    ```

=== ".env File"
    ```bash
    # Create/edit .env file in project root
    echo "ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here" >> .env
    ```

### 3. Verify Setup

Test your API key:

```bash
# Quick API test
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     https://api.anthropic.com/v1/messages \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# Test with Convoscope
python -c "
from src.services.llm_service import LLMService
service = LLMService()
print('Anthropic available:', 'anthropic' in service.get_available_providers())
print('Models:', service.get_available_models('anthropic'))
"
```

## Available Models

### Claude 3.5 Sonnet (Most Capable)
- **Model ID**: `claude-3-5-sonnet-20241022`
- **Best For**: Complex reasoning, analysis, coding, creative writing
- **Context**: 200K tokens
- **Cost**: $3/1M input, $15/1M output tokens
- **Strengths**: Excellent reasoning, long context, multimodal

### Claude 3 Haiku (Fast & Efficient) ⭐ Default
- **Model ID**: `claude-3-haiku-20240307`  
- **Best For**: Quick responses, simple tasks, high-volume use
- **Context**: 200K tokens
- **Cost**: $0.25/1M input, $1.25/1M output tokens
- **Strengths**: Very fast, cost-effective, still high quality

## Key Features

### Safety & Alignment
- **Constitutional AI**: Built-in safety measures
- **Harmlessness**: Refuses harmful requests appropriately  
- **Helpfulness**: Aims to be maximally helpful within safety bounds
- **Honesty**: Acknowledges uncertainty rather than guessing

### Capabilities
- **Long Context**: 200K+ token context window
- **Reasoning**: Strong analytical and logical reasoning
- **Code Understanding**: Excellent at reading and writing code
- **Research**: Great for analysis and summarization
- **Creative Writing**: High-quality creative content

### Limitations
- **Knowledge Cutoff**: Training data cutoff date
- **No Internet**: Cannot browse the web or access real-time data
- **No Function Calling**: Limited tool use compared to other providers
- **Image Input**: Only Claude 3.5 Sonnet supports vision

## Configuration Options

### Basic Configuration

```python
# Default configuration in Convoscope
ANTHROPIC_CONFIG = {
    "default_model": "claude-3-haiku-20240307",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
}
```

### Advanced Configuration

=== "Custom Headers"
    ```python
    # Custom API version
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "messages-2023-12-15"
    }
    ```

=== "Message Format"
    ```python
    # Anthropic uses a specific message format
    messages = [
        {
            "role": "user", 
            "content": "Your question here"
        }
    ]
    
    # System messages are handled separately
    system_message = "You are a helpful assistant."
    ```

=== "Response Configuration"
    ```python
    ANTHROPIC_CUSTOM_CONFIG = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4000,        # Up to 4K output
        "temperature": 0.3,        # More focused
        "top_p": 0.9,             # Nucleus sampling
        "stop_sequences": ["\n\n"] # Custom stop sequences
    }
    ```

## Usage Guidelines

### Best Practices

=== "🎯 Optimal Use Cases"
    
    **Excellent For**:
    - Complex analysis and reasoning
    - Long document processing
    - Code review and explanation
    - Research and summarization
    - Creative writing
    - Educational content
    
    **Less Optimal For**:
    - Simple keyword responses
    - Real-time data queries
    - Function calling/tool use
    - High-frequency, simple tasks

=== "💡 Prompt Engineering"
    
    **Effective Techniques**:
    ```python
    # Be specific and clear
    prompt = "Analyze this code for security vulnerabilities. Provide specific line numbers and explain the risks."
    
    # Use structured requests  
    prompt = """
    Please review this document and provide:
    1. A summary of key points
    2. Any logical inconsistencies
    3. Recommendations for improvement
    """
    
    # Leverage long context
    prompt = "Here's a 50-page research paper: [content]. What are the main conclusions and how do they relate to [specific topic]?"
    ```

=== "⚡ Performance Tips"
    
    - **Use Haiku for simple tasks**: 10x faster, much cheaper
    - **Use Sonnet for complex work**: Better reasoning, worth the cost
    - **Leverage long context**: Don't split documents unnecessarily
    - **Be specific**: Clear requests get better responses
    - **Use system messages**: Guide overall behavior

### Cost Optimization

| Strategy | Model | Savings |
|----------|-------|---------|
| **Use Haiku by default** | claude-3-haiku-20240307 | 80% vs Sonnet |
| **Batch simple queries** | Both | 20-30% |
| **Optimize max_tokens** | Both | 10-50% |
| **Use for strengths** | Both | Quality/$ improvement |

## Testing Your Setup

### 1. Basic Functionality Test

```python
# Test basic completion
from src.services.llm_service import LLMService

service = LLMService()
messages = [
    {"role": "user", "content": "Explain quantum computing in simple terms."}
]

try:
    response = service.get_completion("anthropic", "claude-3-haiku-20240307", messages)
    print(f"✅ Anthropic working: {response[:100]}...")
except Exception as e:
    print(f"❌ Anthropic error: {e}")
```

### 2. Model Comparison Test

```python
# Test different models
models = ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"]
test_prompt = "Write a Python function to calculate the Fibonacci sequence."

for model in models:
    try:
        response = service.get_completion("anthropic", model, [
            {"role": "user", "content": test_prompt}
        ])
        print(f"✅ {model}: {len(response)} characters")
    except Exception as e:
        print(f"❌ {model} failed: {e}")
```

### 3. Long Context Test

```python
# Test long context capability
long_text = "Lorem ipsum..." * 1000  # Long document
prompt = f"Summarize this document in 3 bullet points:\n\n{long_text}"

try:
    response = service.get_completion("anthropic", "claude-3-haiku-20240307", [
        {"role": "user", "content": prompt}
    ])
    print(f"✅ Long context test passed: {len(response)} chars")
except Exception as e:
    print(f"❌ Long context test failed: {e}")
```

## Troubleshooting

### Common Issues

=== "❌ Invalid API Key"
    
    **Error**: `authentication_error: invalid x-api-key`
    
    **Solutions**:
    1. **Check key format**: Must start with `sk-ant-api03-`
    2. **Verify key is active**: Check Anthropic Console
    3. **Check environment variable**:
       ```bash
       echo $ANTHROPIC_API_KEY
       ```
    4. **Request access**: API may be in beta/waitlist

=== "💳 Credit Issues"
    
    **Error**: `rate_limit_error` or billing errors
    
    **Solutions**:
    1. **Check credits**: Visit [Anthropic Console](https://console.anthropic.com/)
    2. **Add payment method**: Required for continued usage
    3. **Monitor usage**: Track token consumption
    4. **Request increase**: Contact support for higher limits

=== "🚫 Rate Limited"
    
    **Error**: `rate_limit_error: Number of requests per minute exceeded`
    
    **Solutions**:
    1. **Check rate limits**: [Anthropic limits documentation](https://docs.anthropic.com/claude/reference/rate-limits)
    2. **Reduce frequency**: Add delays between requests
    3. **Use exponential backoff**: Built into Convoscope
    4. **Request increase**: For production usage

=== "📏 Context Length"
    
    **Error**: `invalid_request_error: messages: array too long`
    
    **Solutions**:
    1. **Check total tokens**: Input + output must be < 200K
    2. **Truncate input**: Remove older messages
    3. **Reduce max_tokens**: Leave room for response
    4. **Split requests**: Break large documents into chunks

### Advanced Troubleshooting

=== "🔍 Debug API Calls"
    
    Enable detailed logging:
    ```python
    import logging
    logging.getLogger('anthropic').setLevel(logging.DEBUG)
    ```

=== "🧪 Direct API Testing"
    
    Test without Convoscope:
    ```bash
    curl https://api.anthropic.com/v1/messages \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{
        "model": "claude-3-haiku-20240307",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

=== "📊 Monitor Usage"
    
    Check your usage programmatically:
    ```python
    # Anthropic doesn't provide usage API yet
    # Monitor through console or implement token counting
    def count_tokens_estimate(text):
        return len(text) // 4  # Rough estimate
    ```

## Best Practices

### Security
- ✅ Store API keys securely
- ✅ Use separate keys for different environments
- ✅ Monitor usage regularly
- ❌ Never expose keys in client-side code
- ❌ Never share keys publicly

### Performance
- ✅ Use Haiku for simple, frequent tasks
- ✅ Use Sonnet for complex reasoning
- ✅ Leverage long context when beneficial
- ✅ Implement proper retry logic
- ❌ Don't use Sonnet for trivial tasks

### Prompt Design
- ✅ Be specific about desired output format
- ✅ Use examples when helpful
- ✅ Leverage Claude's strengths (analysis, reasoning)
- ✅ Break complex tasks into steps
- ❌ Don't assume real-time knowledge

## Integration with Convoscope

### Default Configuration

Convoscope uses these Anthropic defaults:

```python
ANTHROPIC_DEFAULTS = {
    "model": "claude-3-haiku-20240307",  # Fast and cost-effective
    "temperature": 0.7,                  # Balanced creativity
    "max_tokens": 2000,                  # Reasonable responses
    "timeout": 30,                       # 30-second timeout
    "max_retries": 3,                    # Retry failed requests
}
```

### Model Selection

Choose based on your needs:
- **Haiku**: Quick responses, high-volume, cost-sensitive
- **Sonnet**: Complex analysis, reasoning, creative work

### Fallback Behavior

If Anthropic fails, Convoscope:
1. Retries with exponential backoff
2. Falls back to other configured providers
3. Maintains conversation context
4. Logs detailed error information

## Comparison with Other Providers

### vs OpenAI
- **Strengths**: Longer context, better reasoning, safety focus
- **Weaknesses**: Slower, no function calling, newer ecosystem
- **Use when**: Need deep analysis, safety-critical applications

### vs Google Gemini  
- **Strengths**: Higher quality, better reasoning, proven safety
- **Weaknesses**: More expensive, smaller free tier
- **Use when**: Quality matters more than cost

## Getting Help

### Resources
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/)
- [Anthropic Discord](https://discord.gg/anthropic) 
- [Anthropic Blog](https://www.anthropic.com/news)

### Support
- **API Issues**: Check troubleshooting above
- **Account Questions**: [Anthropic Support](mailto:support@anthropic.com)
- **Access Requests**: May need to request beta access
- **Integration Help**: See [Multi-Provider Setup](../multi-provider-setup.md)

---

**Next Steps**:
- [Add Google Gemini for cost optimization →](google-gemini-setup.md)
- [Configure advanced settings →](../configuration.md) 
- [Test all providers together →](../multi-provider-setup.md#testing-your-setup)