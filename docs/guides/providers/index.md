# LLM Provider Guides

## Overview

Convoscope supports three major LLM providers, each with unique strengths. This section provides detailed setup guides, troubleshooting, and optimization tips for each provider.

## Provider Comparison

### Quick Reference

| Provider | Best For | Strengths | Setup Complexity | Cost Range |
|----------|----------|-----------|------------------|------------|
| **OpenAI** | General use, Development | Reliable, Well-documented APIs | ⭐ Easy | $$ Moderate |
| **Anthropic Claude** | High-quality reasoning | Ethical, Safety-focused | ⭐ Easy | $$ Moderate |
| **Google Gemini** | Cost-effective, Multimodal | Free tier, Long context | ⭐⭐ Moderate | $ Low |

### Detailed Comparison

=== "🤖 OpenAI"
    
    **Environment Variable**: `OPENAI_API_KEY`
    
    **Strengths**:
    - Most mature API ecosystem
    - Excellent documentation
    - Wide model selection
    - Fast inference times
    - Strong community support
    
    **Best Use Cases**:
    - Production applications
    - Rapid prototyping
    - Code generation
    - General chat applications
    
    **Available Models**:
    - `gpt-4o-mini` - Cost-effective, fast (Default)
    - `gpt-4o` - Most capable, multimodal
    - `gpt-3.5-turbo` - Fast and affordable
    - `gpt-4-turbo` - High-quality responses
    
    **Pricing**: $0.15-$60 per 1M tokens
    
    [📖 OpenAI Setup Guide →](openai-setup.md)

=== "🔮 Anthropic Claude"
    
    **Environment Variable**: `ANTHROPIC_API_KEY`
    
    **Strengths**:
    - Excellent reasoning capabilities
    - Strong safety measures
    - Long context windows (200K+ tokens)
    - Helpful, harmless, honest approach
    - Great for complex analysis
    
    **Best Use Cases**:
    - Research and analysis
    - Content moderation
    - Complex reasoning tasks
    - Legal/medical applications
    - Educational content
    
    **Available Models**:
    - `claude-3-5-sonnet-20241022` - Most capable
    - `claude-3-haiku-20240307` - Fast and efficient (Default)
    
    **Pricing**: $0.25-$15 per 1M tokens
    
    [📖 Anthropic Setup Guide →](anthropic-setup.md)

=== "🌟 Google Gemini"
    
    **Environment Variable**: `GEMINI_API_KEY` ⚠️ (Not GOOGLE_API_KEY)
    
    **Strengths**:
    - Generous free tier
    - Native multimodal capabilities
    - Long context windows (1M+ tokens)
    - Google's latest AI technology
    - Cost-effective for high volume
    
    **Best Use Cases**:
    - Cost-conscious applications
    - Image and document analysis
    - Long document processing
    - Educational projects
    - Experimental features
    
    **Available Models**:
    - `gemini-1.5-pro` - Most capable, long context (Default)
    - `gemini-pro` - Fast responses
    
    **Pricing**: Free tier → $0.35 per 1M tokens
    
    [📖 Google Gemini Setup Guide →](google-gemini-setup.md)

## Setup Recommendations

### For Beginners
1. **Start with OpenAI** - Easiest setup, most documentation
2. **Add Anthropic** - Higher quality responses for complex tasks  
3. **Add Google Gemini** - Cost-effective scaling

### For Production
1. **OpenAI as primary** - Most reliable uptime
2. **Anthropic as fallback** - Different infrastructure, high quality
3. **Google Gemini for cost optimization** - Handle high-volume, low-complexity requests

### For Development
1. **Google Gemini** - Free tier for testing
2. **OpenAI** - When you need specific features
3. **Anthropic** - For quality validation

## Multi-Provider Benefits

### Resilience
- **Redundancy**: If one provider is down, others continue working
- **Rate Limit Mitigation**: Distribute load across providers
- **Geographic Availability**: Different providers work better in different regions

### Cost Optimization  
- **Model Selection**: Choose the most cost-effective model for each task
- **Free Tier Usage**: Maximize free quotas before paid usage
- **Load Balancing**: Route requests based on current pricing

### Quality Optimization
- **Task-Specific Routing**: Use each provider's strengths
- **A/B Testing**: Compare responses from different providers
- **Fallback Quality**: Maintain quality even if preferred provider fails

## Implementation Status

### Current Implementation
| Feature | Status | Description |
|---------|--------|-------------|
| ✅ Provider Detection | Complete | Automatic API key detection |
| ✅ Model Selection | Complete | Dynamic model lists per provider |
| ✅ Error Handling | Complete | Graceful failure with fallbacks |
| ✅ Rate Limiting | Complete | Built-in retry with exponential backoff |
| ✅ Configuration | Complete | Environment variable based setup |

### Advanced Features (Future)
| Feature | Status | Description |
|---------|--------|-------------|
| 🔄 Load Balancing | Planned | Intelligent request routing |
| 🔄 Cost Tracking | Planned | Usage monitoring per provider |
| 🔄 Performance Metrics | Planned | Response time and quality tracking |
| 🔄 Auto-Fallback Rules | Planned | Configurable fallback conditions |

## Getting Started

### Quick Start
1. Choose your primary provider from the comparison above
2. Follow the detailed setup guide for your chosen provider
3. Test your setup with the provided validation commands
4. Add additional providers for redundancy

### Need Help?
- [Multi-Provider Setup Guide](../multi-provider-setup.md) - Complete setup walkthrough
- [Configuration Guide](../configuration.md) - Advanced configuration options
- [Troubleshooting](#troubleshooting) - Common issues and solutions

## Troubleshooting

### Common Issues Across Providers

=== "🔑 API Key Issues"
    
    **Symptoms**: "Invalid API key" or "Unauthorized" errors
    
    **Solutions**:
    1. Verify environment variable names:
       - OpenAI: `OPENAI_API_KEY`
       - Anthropic: `ANTHROPIC_API_KEY`  
       - Google: `GEMINI_API_KEY` (not GOOGLE_API_KEY)
    2. Check key format and validity
    3. Ensure sufficient credits/quota
    4. Verify permissions for specific models

=== "🌐 Network Issues"
    
    **Symptoms**: Timeout or connection errors
    
    **Solutions**:
    1. Check internet connection
    2. Verify provider service status
    3. Configure proxy if needed
    4. Increase timeout settings

=== "📊 Rate Limiting"
    
    **Symptoms**: "Too many requests" errors
    
    **Solutions**:
    1. Reduce request frequency
    2. Upgrade to higher rate limit tier
    3. Use multiple providers for load distribution
    4. Implement request queuing

### Provider-Specific Troubleshooting
- [OpenAI Troubleshooting](openai-setup.md#troubleshooting)
- [Anthropic Troubleshooting](anthropic-setup.md#troubleshooting)
- [Google Gemini Troubleshooting](google-gemini-setup.md#troubleshooting)

---

Ready to set up your providers? Choose your starting point:

- [🤖 OpenAI Setup Guide →](openai-setup.md)
- [🔮 Anthropic Setup Guide →](anthropic-setup.md)
- [🌟 Google Gemini Setup Guide →](google-gemini-setup.md)