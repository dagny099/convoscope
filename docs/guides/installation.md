# Installation & Setup Guide

## Prerequisites

Before installing Convoscope, ensure your system meets these requirements:

- **Python 3.8+** (tested with Python 3.12)
- **pip** package manager
- **Git** for version control
- At least one LLM provider API key (OpenAI, Anthropic, or Google)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd convoscope

# Switch to the improved branch (if applicable)
git checkout portfolio-improvements
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install core application dependencies
pip install -r requirements.txt

# Install development and documentation dependencies (optional)
pip install pytest pytest-asyncio mkdocs mkdocs-material
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy environment template
cp .env.example .env  # If template exists

# Or create manually
touch .env
```

Add your API keys to `.env`:

```bash
# Required: At least one provider API key
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
GEMINI_API_KEY=your-google-api-key-here

# Optional: Application configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_TEMPERATURE=0.7
MAX_CONVERSATION_HISTORY=50
```

### 5. Verify Installation

```bash
# Run tests to verify everything is working
python -m pytest tests/ -v

# Expected output: All 56 tests should pass
# ===== 56 passed in X.XX seconds =====
```

### 6. Launch Application

```bash
# Start the Streamlit application
streamlit run run_chat.py

# Application should open in your browser at:
# http://localhost:8501
```

## Detailed Setup Instructions

### API Key Configuration

Each LLM provider requires different setup:

=== "🤖 OpenAI"

    **1. Get API Key:**
    - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
    - Create a new API key
    - Copy the key (starts with `sk-`)
    
    **2. Set Environment Variable:**
    ```bash
    export OPENAI_API_KEY="sk-your-key-here"
    ```
    
    **3. Verify Setup:**
    ```bash
    python -c "
    import os
    from src.services.llm_service import LLMService
    service = LLMService()
    available = service.get_available_providers()
    print('OpenAI available:', 'openai' in available)
    "
    ```

=== "🧠 Anthropic"

    **1. Get API Key:**
    - Visit [Anthropic Console](https://console.anthropic.com/)
    - Generate a new API key  
    - Copy the key (starts with `sk-ant-api03-`)
    
    **2. Set Environment Variable:**
    ```bash
    export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
    ```
    
    **3. Verify Setup:**
    ```bash
    python -c "
    from src.services.llm_service import LLMService
    service = LLMService()
    models = service.get_available_models('anthropic')
    print('Anthropic models:', models)
    "
    ```

=== "🔍 Google"

    **1. Get API Key:**
    - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
    - Create a new API key
    - Copy the key (starts with `AIza`)
    
    **2. Set Environment Variable:**
    ```bash
    export GEMINI_API_KEY="AIza-your-key-here"
    ```
    
    **3. Verify Setup:**
    ```bash  
    python -c "
    from src.services.llm_service import LLMService
    service = LLMService()
    available = service.get_available_models('google')
    print('Google available:', len(available) > 0)
    "
    ```

### Development Environment Setup

For contributors and developers who want to modify the codebase:

#### Install Development Dependencies

```bash
# Install testing framework
pip install pytest pytest-asyncio pytest-cov

# Install code quality tools  
pip install black isort flake8 mypy

# Install documentation tools
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin "mkdocstrings[python]"
```

#### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks (if .pre-commit-config.yaml exists)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

## Deployment Options

### Local Development

```bash
# Standard development server
streamlit run run_chat.py

# With specific configuration
streamlit run run_chat.py --server.port 8502 --server.address 0.0.0.0
```

### Docker Deployment

**Dockerfile** (if available):
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "run_chat.py", "--server.address", "0.0.0.0"]
```

**Docker Commands:**
```bash
# Build image
docker build -t convoscope .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  convoscope
```

### Production Deployment

For production environments, consider these additional steps:

#### Security Configuration

```bash
# Use secrets management instead of environment variables
export OPENAI_API_KEY_FILE="/path/to/secret/openai-key"
export ANTHROPIC_API_KEY_FILE="/path/to/secret/anthropic-key"
```

#### Performance Optimization

```bash
# Configure Streamlit for production
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0" 
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
EOF
```

#### Monitoring Setup

```bash  
# Add logging configuration
export STREAMLIT_LOG_LEVEL=INFO
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Health check endpoint (if implemented)
curl http://localhost:8501/health
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Add src directory to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or run from project root with module syntax
python -m src.services.llm_service
```

#### API Key Issues

```bash
# Test API key validity
python -c "
import os
key = os.getenv('OPENAI_API_KEY')
if not key:
    print('❌ OPENAI_API_KEY not set')
elif not key.startswith('sk-'):
    print('❌ Invalid OpenAI key format')
else:
    print('✅ OpenAI key format looks correct')
"
```

#### Permission Errors

```bash  
# Fix conversation directory permissions
chmod 755 conversation_history/
chmod 644 conversation_history/*.json

# Or create with proper permissions
mkdir -p conversation_history
touch conversation_history/.gitkeep
```

#### Streamlit Issues

```bash
# Clear Streamlit cache
streamlit cache clear

# Reset Streamlit configuration
rm -rf ~/.streamlit/

# Check Streamlit version compatibility
pip list | grep streamlit
# Should show streamlit >= 1.28.0
```

### Testing Installation

Run comprehensive tests to verify everything works:

```bash  
# Run all tests with verbose output
python -m pytest tests/ -v --tb=short

# Run specific test categories
python -m pytest tests/test_llm_service.py -v
python -m pytest tests/test_conversation_manager.py -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Performance Verification

```bash
# Test LLM service performance
python -c "
import time
from src.services.llm_service import LLMService

service = LLMService()
messages = [{'role': 'user', 'content': 'Hello!'}]

start = time.time()
response = service.get_completion_with_fallback(messages)
duration = time.time() - start

print(f'Response time: {duration:.2f}s')
print(f'Response length: {len(response) if response else 0} chars')
print('✅ Service working correctly' if response else '❌ Service failed')
"
```

## Getting Help

If you encounter issues during installation:

1. **Check Requirements**: Verify Python version and dependencies
2. **Review Logs**: Check console output for specific error messages
3. **Test Components**: Use the verification scripts above
4. **API Limits**: Ensure API keys have sufficient credits/quota
5. **Network Issues**: Verify internet connectivity for API calls

---

*Next: [Configuration Guide](configuration.md) - Detailed customization options*