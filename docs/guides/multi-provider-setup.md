# Multi-Provider LLM Setup Guide

## Overview

Convoscope supports multiple AI providers with intelligent fallback - when one provider is down, it automatically switches to another. This guide shows you how to set up OpenAI, Anthropic, and Google Gemini for maximum reliability.

## Why Use Multiple Providers?

Single-provider apps fail when their AI service is unavailable. With Convoscope's multi-provider setup:

```mermaid
flowchart LR
    A[Your Message] --> B{Provider 1}
    B -->|Available| C[✅ Response]
    B -->|Down| D{Provider 2}
    D -->|Available| E[✅ Response]
    D -->|Down| F{Provider 3}
    F -->|Available| G[✅ Response]
    F -->|All Down| H[❌ Clear Error]

    style A fill:#e3f2fd
    style C fill:#e8f5e8
    style E fill:#e8f5e8
    style G fill:#e8f5e8
    style H fill:#ffebee
```

**Benefits:**
- **99.9% uptime**: If one provider is down, others keep working
- **No vendor lock-in**: Switch providers anytime
- **Cost optimization**: Use cheaper providers when possible

## Quick Setup (All Providers)

### 1. Environment Variables

Set up your API keys using environment variables:

```bash
# Required: At least one provider
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key-here"  
export GEMINI_API_KEY="AIzaSy-your-gemini-key-here"
```

### 2. Verify Setup

Test your configuration:

```bash
# Quick test all providers
python test_multi_provider.py

# Run the application
streamlit run run_chat.py
```

**Success looks like this:**

[![Provider Selection Working](../assets/screenshots/02-provider-selector-open.png){: target="_blank"}](../assets/screenshots/02-provider-selector-open.png)
*All three providers available in dropdown - click to enlarge*

## Provider Comparison

| Provider | Environment Variable | Popular Models | Setup Time | Cost Level |
|----------|---------------------|----------------|------------|------------|
| **OpenAI** | `OPENAI_API_KEY` | gpt-4o-mini, gpt-4o, gpt-3.5-turbo | 2 min | $$ |
| **Anthropic** | `ANTHROPIC_API_KEY` | claude-3-5-sonnet, claude-3-haiku | 2 min | $$ |
| **Google** | `GEMINI_API_KEY` | gemini-1.5-pro, gemini-pro | 3 min | $ |

## Provider-Specific Setup

=== "🤖 OpenAI"
    
    **Recommended for**: General use, fastest setup
    
    **Quick Setup**:
    1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
    2. Create new API key
    3. Copy key (starts with `sk-`)
    4. Set environment variable:
       ```bash
       export OPENAI_API_KEY="sk-your-key-here"
       ```
    
    **Models Available**:
    - `gpt-4o-mini` ✅ (Default - Cost-effective)
    - `gpt-4o` (Most capable)
    - `gpt-3.5-turbo` (Fast and affordable)
    - `gpt-4-turbo` (High-quality responses)
    
    [📖 Detailed OpenAI Setup Guide →](providers/openai-setup.md)

=== "🔮 Anthropic Claude"
    
    **Recommended for**: High-quality reasoning, ethical AI
    
    **Quick Setup**:
    1. Visit [Anthropic Console](https://console.anthropic.com/)
    2. Create API key
    3. Copy key (starts with `sk-ant-`)
    4. Set environment variable:
       ```bash
       export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
       ```
    
    **Models Available**:
    - `claude-3-5-sonnet-20241022` (Most capable)
    - `claude-3-haiku-20240307` ✅ (Fast and efficient)
    
    [📖 Detailed Anthropic Setup Guide →](providers/anthropic-setup.md)

=== "🌟 Google Gemini"
    
    **Recommended for**: Cost-effective, multimodal capabilities
    
    **⚠️ Important**: Uses `GEMINI_API_KEY` (not `GOOGLE_API_KEY`)
    
    **Quick Setup**:
    1. Visit [Google AI Studio](https://aistudio.google.com/)
    2. Create API key
    3. Copy key (starts with `AIzaSy`)
    4. Set environment variable:
       ```bash
       export GEMINI_API_KEY="AIzaSy-your-key-here"
       ```
    
    **Models Available**:
    - `gemini-1.5-pro` ✅ (Most capable, longer context)
    - `gemini-pro` (Fast responses)
    
    [📖 Detailed Google Gemini Setup Guide →](providers/google-gemini-setup.md)

## Testing Your Setup

### 1. Automated Testing

Run the comprehensive test suite:

```bash
python test_multi_provider.py
```

Expected output:
```
✅ OPENAI: Available with 4 models
✅ ANTHROPIC: Available with 2 models  
✅ GOOGLE: Available with 2 models

🎉 Multi-provider support is working!
```

### 2. Manual Testing

Launch the application and check provider status:

```bash
streamlit run run_chat.py
```

In the sidebar, verify you see:
- ✅ **openai** is ready
- ✅ **anthropic** is ready  
- ✅ **google** is ready

### 3. Test Switching

Try switching between providers in the UI:
1. Select different provider from dropdown
2. Choose a model for that provider
3. Send a test message
4. Verify response quality

## Troubleshooting

### Common Issues

=== "❌ No Providers Available"
    
    **Symptoms**: Empty provider dropdown, "No API keys configured" message
    
    **Solutions**:
    1. Check environment variables are set:
       ```bash
       echo $OPENAI_API_KEY
       echo $ANTHROPIC_API_KEY  
       echo $GEMINI_API_KEY
       ```
    2. Restart your terminal/IDE after setting variables
    3. For persistent setup, add to `~/.bashrc` or `~/.zshrc`

=== "⚠️ Invalid API Key Errors"
    
    **Symptoms**: "Invalid API key for [provider]" messages
    
    **Solutions**:
    1. **OpenAI**: Verify key starts with `sk-` and has sufficient credits
    2. **Anthropic**: Verify key starts with `sk-ant-api03-`
    3. **Google**: Verify key starts with `AIzaSy` and Generative AI API is enabled
    
    **Test API keys directly**:
    ```bash
    # OpenAI
    curl -H "Authorization: Bearer $OPENAI_API_KEY" \
         https://api.openai.com/v1/models
    
    # Anthropic  
    curl -H "x-api-key: $ANTHROPIC_API_KEY" \
         https://api.anthropic.com/v1/models
         
    # Google Gemini
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY" \
         -H "Content-Type: application/json" \
         -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
    ```

=== "🔄 Fallback Not Working"
    
    **Symptoms**: App fails when primary provider is down
    
    **Solutions**:
    1. Ensure multiple providers are configured
    2. Check provider priority settings
    3. Enable fallback in UI settings
    4. Monitor provider status indicators

## Advanced Configuration

### Environment File Setup

Create a `.env` file for persistent configuration:

```bash
# Copy example and customize
cp .env.example .env

# Edit with your API keys
nano .env
```

Example `.env` file:
```bash
# Multi-Provider LLM Configuration
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
GEMINI_API_KEY=AIzaSy-your-gemini-key-here

# Optional: Default preferences
DEFAULT_LLM_PROVIDER=openai
OPENAI_DEFAULT_MODEL=gpt-4o-mini
ANTHROPIC_DEFAULT_MODEL=claude-3-haiku-20240307
GOOGLE_DEFAULT_MODEL=gemini-1.5-pro
```

### Custom Provider Priority

Set provider priority for fallback behavior:

```python
# In your configuration
PROVIDER_PRIORITY = ["openai", "anthropic", "google"]

# Or via environment
export PROVIDER_PRIORITY="anthropic,openai,google"
```

### Rate Limiting and Costs

Monitor usage and costs:

| Provider | Free Tier | Rate Limits | Cost/1K Tokens |
|----------|-----------|-------------|-----------------|
| OpenAI | $5 credit | 3 RPM → 3500 RPM | $0.15-$60 |
| Anthropic | $5 credit | 5 RPM → 1000 RPM | $0.25-$15 |
| Google | Free quota | 15 RPM → 360 RPM | Free → $0.35 |

### Production Deployment

For production environments:

```bash
# Use secure secret management
export OPENAI_API_KEY=$(vault kv get -field=api_key secret/openai)
export ANTHROPIC_API_KEY=$(kubectl get secret anthropic-key -o jsonpath='{.data.key}' | base64 -d)
export GEMINI_API_KEY=$(aws ssm get-parameter --name /convoscope/gemini-key --with-decryption --query 'Parameter.Value' --output text)
```

## Getting Help

### Provider-Specific Issues
- [OpenAI Setup Help](providers/openai-setup.md#troubleshooting)
- [Anthropic Setup Help](providers/anthropic-setup.md#troubleshooting)  
- [Google Gemini Setup Help](providers/google-gemini-setup.md#troubleshooting)

### General Support
1. Run diagnostics: `python test_multi_provider.py`
2. Check logs for specific error messages
3. Verify API key permissions and quotas
4. Test providers individually before using together

---

**Next Steps**: Once you have at least one provider working, explore [Advanced Configuration](configuration.md) for customization options.