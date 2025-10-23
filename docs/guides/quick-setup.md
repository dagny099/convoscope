# ⚡ Quick Setup (5 Minutes)

Get Convoscope running with minimal configuration for immediate testing.

## Prerequisites

- Python 3.8+
- At least one AI provider API key

## 1-Minute Setup

### Option A: Use OpenAI (Recommended)

```bash
# Clone and setup
git clone https://github.com/dagny099/convoscope.git
cd convoscope
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-your-openai-key-here"

# Run
streamlit run run_chat.py
```

### Option B: Use Anthropic Claude

```bash
# Same setup as above, but use:
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
streamlit run run_chat.py
```

### Option C: Use Google Gemini

```bash
# Same setup as above, but use:
export GEMINI_API_KEY="AIza-your-gemini-key-here"
streamlit run run_chat.py
```

## Verify It's Working

1. **App opens**: Browser should open to `http://localhost:8501`
2. **Provider shows**: You should see your provider in the sidebar (✅ **openai** is ready)
3. **Send test message**: Try "Hello, are you working?"
4. **Get response**: You should get an AI response within a few seconds

[![Interface Working](../assets/screenshots/01-hero-interface.png){: target="_blank"}](../assets/screenshots/01-hero-interface.png)
*Working interface - click to enlarge*

## What You Get

With this minimal setup:
- ✅ **AI Chat**: Full conversation capability
- ✅ **Auto-save**: Conversations saved automatically
- ✅ **Error handling**: Graceful error messages
- ❌ **Multi-provider fallback**: Need multiple API keys for this

## Add More Providers (Optional)

To get the full reliability benefits, add more API keys:

```bash
# Add all three for maximum reliability
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key"
export GEMINI_API_KEY="AIza-your-gemini-key"

# Restart the app
streamlit run run_chat.py
```

You should now see multiple providers available:

[![Multiple Providers](../assets/screenshots/02-provider-selector-open.png){: target="_blank"}](../assets/screenshots/02-provider-selector-open.png)
*Multiple providers available - click to enlarge*

## Troubleshooting

### "No API keys configured"
- Check your environment variable: `echo $OPENAI_API_KEY`
- Make sure it starts with `sk-` (OpenAI) or `sk-ant-` (Anthropic) or `AIza` (Google)
- Restart your terminal after setting the variable

### "Invalid API key"
- Verify your API key is correct and has credits
- For OpenAI: Check [API Keys page](https://platform.openai.com/api-keys)
- For Anthropic: Check [Console](https://console.anthropic.com/)
- For Google: Check [AI Studio](https://aistudio.google.com/)

### App won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check for error messages in the terminal

## Next Steps

- **[📖 Full Installation Guide](installation.md)** - Complete setup with all options
- **[🎯 Multi-Provider Setup](multi-provider-setup.md)** - Configure all three providers
- **[🔧 Configuration](configuration.md)** - Customize settings and behavior

---

**Need help?** Check the [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.