# Troubleshooting Guide

Common issues and solutions for Convoscope users.

## Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# Check if the app starts
streamlit run run_chat.py

# Verify API keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GEMINI_API_KEY

# Check Python and dependencies
python --version
pip list | grep streamlit
```

## Installation & Setup Issues

### "Command not found: streamlit"

**Problem**: Streamlit isn't installed or not in PATH

**Solutions**:
```bash
# Install streamlit
pip install streamlit

# Or install all dependencies
pip install -r requirements.txt

# Verify installation
streamlit --version
```

### "No module named 'src'"

**Problem**: Python can't find the source modules

**Solutions**:
```bash
# Run from project root directory
cd convoscope
streamlit run run_chat.py

# Or set Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### "Permission denied" errors

**Problem**: File/folder permission issues

**Solutions**:
```bash
# Fix conversation directory permissions
chmod 755 conversation_history/
chmod 644 conversation_history/*.json

# Create directory if missing
mkdir -p conversation_history
```

## API Key Issues

### "No API keys configured"

**Problem**: No valid API keys found

[![Error Example](../assets/screenshots/04-error-handling-stAlert.png){: target="_blank"}](../assets/screenshots/04-error-handling-stAlert.png)
*API key error message - click to enlarge*

**Solutions**:
```bash
# Set at least one API key
export OPENAI_API_KEY="sk-your-key-here"

# Or set in .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Restart terminal after setting
```

**Verify API keys**:
```bash
# Check OpenAI key format (starts with sk-)
echo $OPENAI_API_KEY | grep "^sk-"

# Check Anthropic key format (starts with sk-ant-)
echo $ANTHROPIC_API_KEY | grep "^sk-ant-"

# Check Google key format (starts with AIza)
echo $GEMINI_API_KEY | grep "^AIza"
```

### "Invalid API key" errors

**Problem**: API key is wrong format or expired

**Solutions**:
1. **OpenAI**: Visit [API Keys page](https://platform.openai.com/api-keys)
   - Create new key if needed
   - Check billing/credits
   - Key should start with `sk-`

2. **Anthropic**: Visit [Console](https://console.anthropic.com/)
   - Generate new API key
   - Key should start with `sk-ant-api03-`

3. **Google**: Visit [AI Studio](https://aistudio.google.com/)
   - Create API key
   - Enable Generative AI API
   - Key should start with `AIzaSy`

### "Rate limit exceeded"

**Problem**: Too many API requests

**Visual Indicator**: Error message in chat interface

**Solutions**:
- **Wait**: Rate limits reset after time (usually 1 minute)
- **Switch providers**: Use dropdown to change to different AI
- **Upgrade plan**: Higher tiers have higher limits
- **Check usage**: Monitor your API dashboard

## Chat Interface Issues

### No response from AI

**Problem**: Messages sent but no AI response

**Debugging steps**:
1. **Check provider status** in sidebar (should show ✅)
2. **Look for error messages** in red alerts
3. **Try different provider** from dropdown
4. **Check browser console** for JavaScript errors

**Common causes**:
- API key issues
- Network connectivity problems
- Provider service outage
- Rate limiting

### Chat interface freezes

**Problem**: Interface stops responding

**Solutions**:
```bash
# Refresh the page
Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

# Clear browser cache
# Chrome: Settings > Privacy > Clear browsing data

# Restart Streamlit
Ctrl+C to stop, then:
streamlit run run_chat.py
```

### Messages not displaying properly

**Problem**: Formatting issues or missing messages

**Solutions**:
1. **Clear Streamlit cache**:
   ```bash
   streamlit cache clear
   ```
2. **Check browser compatibility**: Use Chrome, Firefox, or Safari
3. **Disable browser extensions**: Ad blockers can interfere
4. **Try incognito mode**: Rules out browser state issues

## Provider-Specific Issues

### OpenAI Issues

**"Model not found" errors**:
```bash
# Check available models
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**"Insufficient credits" errors**:
- Add billing method at [OpenAI Billing](https://platform.openai.com/account/billing)
- Check usage limits and quotas

### Anthropic Issues

**"Authentication failed"**:
- Verify key starts with `sk-ant-api03-`
- Check [Anthropic Console](https://console.anthropic.com/) for key status

**"Model overloaded" errors**:
- Try again in a few seconds
- Switch to different model (haiku vs sonnet)

### Google Gemini Issues

**"API not enabled"**:
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Generative Language API"
3. Wait a few minutes for activation

**"Quota exceeded"**:
- Check [AI Studio](https://aistudio.google.com/) for quota limits
- Upgrade to paid tier if needed

## Conversation Management Issues

### Can't save conversations

**Problem**: Save button doesn't work or fails

**Solutions**:
1. **Check permissions**:
   ```bash
   ls -la conversation_history/
   chmod 755 conversation_history/
   ```

2. **Check disk space**:
   ```bash
   df -h .
   ```

3. **Check filename**: Avoid special characters in conversation names

### Can't load conversations

**Problem**: Saved conversations don't appear in dropdown

**Debugging**:
```bash
# Check if files exist
ls conversation_history/*.json

# Check file format
head conversation_history/your_file.json

# Test JSON validity
python -m json.tool conversation_history/your_file.json
```

**Solutions**:
- Fix JSON syntax errors
- Rename files to match expected format
- Check file encoding (should be UTF-8)

### Conversations corrupted

**Problem**: JSON files are corrupted or unreadable

**Recovery steps**:
1. **Check for backups**:
   ```bash
   ls conversation_history/*.backup
   ls conversation_history/auto_backup.json
   ```

2. **Restore from backup**:
   ```bash
   cp conversation_history/auto_backup.json conversation_history/recovered.json
   ```

3. **Fix JSON manually**: Use text editor to fix syntax errors

## Network & Connection Issues

### "Connection timeout" errors

**Problem**: Slow or unreliable internet connection

**Solutions**:
- **Check internet**: Try loading other websites
- **Try different network**: Switch to mobile hotspot to test
- **Increase timeout**: Add to environment variables:
  ```bash
  export REQUEST_TIMEOUT=60
  ```
- **Use different provider**: Some APIs may be faster

### "SSL/Certificate" errors

**Problem**: HTTPS connection issues

**Solutions**:
```bash
# Update certificates
pip install --upgrade certifi

# Check system time (affects SSL)
date

# Try different network (corporate firewalls can cause issues)
```

## Performance Issues

### Slow responses

**Problem**: AI takes long time to respond

**Causes & Solutions**:
- **Large conversations**: Start new chat for better performance
- **Complex prompts**: Simplify your questions
- **Provider load**: Try different AI provider
- **Network speed**: Test internet connection

### High memory usage

**Problem**: Application uses too much RAM

**Solutions**:
```bash
# Restart Streamlit to clear memory
Ctrl+C
streamlit run run_chat.py

# Clear old conversations
rm conversation_history/very_old_*.json

# Use smaller model (e.g., gpt-3.5-turbo instead of gpt-4)
```

## Browser-Specific Issues

### Chrome Issues
- **Clear cache**: Chrome Settings > Privacy > Clear browsing data
- **Disable extensions**: Try incognito mode
- **Update Chrome**: Help > About Google Chrome

### Firefox Issues
- **Clear cache**: Options > Privacy & Security > Clear Data
- **Check tracking protection**: May block some features
- **Try safe mode**: Help > Troubleshoot Mode

### Safari Issues
- **Enable JavaScript**: Safari > Preferences > Security
- **Clear cache**: Safari > Clear History
- **Check content blockers**: May interfere with app

## Environment-Specific Issues

### Windows Issues
```cmd
# Use Command Prompt or PowerShell
set OPENAI_API_KEY=sk-your-key-here
streamlit run run_chat.py

# Check Python installation
where python
python --version
```

### macOS Issues
```bash
# Use Terminal
export OPENAI_API_KEY="sk-your-key-here"
streamlit run run_chat.py

# Fix PATH issues
echo $PATH
which python3
```

### Linux Issues
```bash
# Permission issues
sudo chown -R $USER:$USER convoscope/
chmod +x run_chat.py

# Package manager issues
sudo apt update
sudo apt install python3-pip
```

## Getting Help

### Collect Debug Information

Before asking for help, gather this information:

```bash
# System info
python --version
pip list | grep -E "(streamlit|openai|anthropic)"
echo $OPENAI_API_KEY | head -c 10

# Error logs
# Copy any error messages from terminal
# Screenshot any browser error messages
```

### Where to Get Help

1. **Check this guide**: Most issues are covered here
2. **Review error messages**: They usually indicate the problem
3. **Test with minimal setup**: Single API key, fresh conversation
4. **Check provider status**: Visit provider status pages
5. **Try different browser**: Rule out browser-specific issues

### Reporting Issues

If you need to report a bug:

1. **Include error messages**: Copy full text
2. **Describe steps**: What were you doing when it failed?
3. **Environment details**: OS, Python version, browser
4. **Provider info**: Which AI provider was selected?
5. **Screenshots**: Visual errors are easier to diagnose

---

**Still need help?** Try the [Configuration Guide](configuration.md) for advanced settings or [Installation Guide](installation.md) for setup issues.