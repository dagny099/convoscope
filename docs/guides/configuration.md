# Configuration Guide

## Overview

Convoscope provides flexible configuration options for customizing behavior, managing LLM providers, and optimizing performance. This guide covers all configuration aspects from basic setup to advanced customization.

## Environment Configuration

### Required Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# LLM Provider API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here  
GEMINI_API_KEY=AIza-your-google-api-key-here

# Application Settings (optional)
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2000
MAX_CONVERSATION_HISTORY=100

# File Storage (optional)
CONVERSATION_STORAGE_PATH=./conversation_history
AUTO_BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30

# Performance Settings (optional)  
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Security Settings (optional)
ENABLE_INPUT_SANITIZATION=true
MAX_INPUT_LENGTH=10000
ALLOWED_FILE_EXTENSIONS=.json,.txt,.md
```

### Environment Variable Details

=== "🔑 API Keys"
    
    **OpenAI Configuration:**
    ```bash
    OPENAI_API_KEY=sk-proj-abc123...
    OPENAI_ORG_ID=org-abc123  # Optional: Organization ID
    OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: Custom endpoint
    ```
    
    **Anthropic Configuration:**
    ```bash
    ANTHROPIC_API_KEY=sk-ant-api03-abc123...
    ANTHROPIC_BASE_URL=https://api.anthropic.com  # Optional: Custom endpoint
    ```
    
    **Google Configuration:**
    ```bash
    GEMINI_API_KEY=AIzaSyAbc123...
    GOOGLE_PROJECT_ID=my-project-id  # Optional: For advanced features
    ```

=== "⚙️ Application Settings"
    
    **Provider Preferences:**
    ```bash
    # Primary provider selection
    DEFAULT_LLM_PROVIDER=openai
    FALLBACK_PROVIDER=anthropic
    PROVIDER_PRIORITY=openai,anthropic,google
    
    # Model preferences by provider
    OPENAI_DEFAULT_MODEL=gpt-3.5-turbo
    ANTHROPIC_DEFAULT_MODEL=claude-3-haiku-20240307
    GOOGLE_DEFAULT_MODEL=gemini-pro
    ```
    
    **Response Configuration:**
    ```bash
    DEFAULT_TEMPERATURE=0.7  # Response creativity (0.0-1.0)
    MAX_TOKENS=2000         # Maximum response length
    STREAM_RESPONSES=true   # Enable response streaming
    ```

=== "📁 Storage Settings"
    
    **File Storage:**
    ```bash
    CONVERSATION_STORAGE_PATH=./conversation_history
    AUTO_SAVE_INTERVAL=30   # Auto-save every 30 seconds
    MAX_FILE_SIZE_MB=10     # Maximum conversation file size
    
    # Backup configuration
    AUTO_BACKUP_ENABLED=true
    BACKUP_RETENTION_DAYS=30
    BACKUP_COMPRESSION=true
    ```

=== "🚀 Performance Tuning"
    
    **Request Handling:**
    ```bash
    REQUEST_TIMEOUT=30      # API request timeout (seconds)
    MAX_RETRIES=3          # Maximum retry attempts
    RETRY_BACKOFF_FACTOR=2 # Exponential backoff multiplier
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE=60
    BURST_LIMIT=10         # Allow brief bursts
    ```

## Provider Configuration

### Multi-Provider Setup

Configure multiple LLM providers for resilience and flexibility:

```python
# src/config/providers.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProviderConfig:
    name: str
    api_key_env: str
    models: List[str]
    default_model: str
    base_url: Optional[str] = None
    priority: int = 1
    enabled: bool = True

PROVIDER_CONFIGS = {
    "openai": ProviderConfig(
        name="openai",
        api_key_env="OPENAI_API_KEY",
        models=["gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"],
        default_model="gpt-3.5-turbo",
        priority=1
    ),
    
    "anthropic": ProviderConfig(
        name="anthropic", 
        api_key_env="ANTHROPIC_API_KEY",
        models=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        default_model="claude-3-haiku-20240307",
        priority=2
    ),
    
    "google": ProviderConfig(
        name="google",
        api_key_env="GEMINI_API_KEY", 
        models=["gemini-pro", "gemini-1.5-pro"],
        default_model="gemini-pro",
        priority=3
    )
}
```

### Custom Provider Implementation

Add support for custom LLM providers:

```python
# src/services/custom_provider.py
from typing import List, Dict, Optional
from src.services.llm_service import ILLMProvider

class CustomLLMProvider(ILLMProvider):
    """Custom LLM provider implementation."""
    
    def __init__(self, api_key: str, base_url: str, models: List[str]):
        self.api_key = api_key
        self.base_url = base_url
        self.models = models
        
    def get_completion(self, model: str, messages: List[Dict]) -> Optional[str]:
        """Implement custom provider API calls."""
        # Custom implementation here
        pass
        
    def validate_api_key(self) -> bool:
        """Validate custom provider API key."""
        # Custom validation logic
        pass
        
    def get_available_models(self) -> List[str]:
        """Return list of available models."""
        return self.models

# Register custom provider
def register_custom_provider():
    from src.services.llm_service import LLMService
    
    custom_provider = CustomLLMProvider(
        api_key=os.getenv("CUSTOM_API_KEY"),
        base_url=os.getenv("CUSTOM_BASE_URL"),
        models=["custom-model-1", "custom-model-2"]
    )
    
    # Add to LLM service
    llm_service = LLMService()
    llm_service.add_provider("custom", custom_provider)
```

## Streamlit Configuration

### Application Settings

Configure Streamlit-specific settings in `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
caching = true
displayEnabled = true

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true

[logger]
level = "info"
messageFormat = "%(asctime)s %(message)s"

[deprecation]
showfileUploaderEncoding = false
showImageFormat = false
```

### Custom Streamlit Configuration

Create dynamic configuration based on environment:

```python
# src/config/streamlit_config.py
import os
import streamlit as st
from typing import Dict, Any

def get_streamlit_config() -> Dict[str, Any]:
    """Get Streamlit configuration based on environment."""
    
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    config = {
        "page_title": "Convoscope - Multi-LLM Chat Interface",
        "page_icon": "🔭",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
        "menu_items": {
            "Get Help": None,
            "Report a bug": None,
            "About": "# Convoscope\nProfessional multi-LLM chat interface"
        }
    }
    
    if is_production:
        config["menu_items"]["Get Help"] = "https://your-domain.com/help"
        config["menu_items"]["Report a bug"] = "https://your-domain.com/bugs"
    
    return config

def apply_streamlit_config():
    """Apply configuration to current Streamlit session."""
    config = get_streamlit_config()
    st.set_page_config(**config)
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .provider-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    
    .provider-available {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .provider-unavailable {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)
```

## Logging Configuration

### Structured Logging Setup

Configure comprehensive logging for monitoring and debugging:

```python
# src/config/logging_config.py
import logging
import logging.config
import os
from datetime import datetime

def setup_logging():
    """Configure application logging."""
    
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = os.getenv("LOG_DIR", "./logs")
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s: %(message)s"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": f"{log_dir}/convoscope.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "errors": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": f"{log_dir}/errors.log",
                "maxBytes": 10485760,
                "backupCount": 3
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "convoscope": {
                "handlers": ["console", "file", "errors"],
                "level": log_level,
                "propagate": False
            },
            "llm_service": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": True
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log configuration completion
    logger = logging.getLogger("convoscope")
    logger.info(f"Logging configured with level: {log_level}")
```

### Application-Specific Loggers

Create specialized loggers for different components:

```python
# src/utils/logging.py
import logging
import functools
from typing import Any, Callable

def get_logger(name: str) -> logging.Logger:
    """Get logger with application-specific configuration."""
    return logging.getLogger(f"convoscope.{name}")

def log_function_calls(logger: logging.Logger = None):
    """Decorator to log function calls and results."""
    def decorator(func: Callable) -> Callable:
        if logger is None:
            func_logger = get_logger(func.__module__)
        else:
            func_logger = logger
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                func_logger.debug(f"{func.__name__} returned: {type(result).__name__}")
                return result
            except Exception as e:
                func_logger.error(f"{func.__name__} failed: {e}")
                raise
                
        return wrapper
    return decorator

# Usage examples
llm_logger = get_logger("llm_service")
conversation_logger = get_logger("conversation_manager")

@log_function_calls(llm_logger)
def get_completion(provider, model, messages):
    # Function implementation
    pass
```

## Security Configuration

### Input Validation Settings

Configure input validation and sanitization:

```python
# src/config/security.py
from typing import Dict, List, Any
import re

class SecurityConfig:
    """Security configuration settings."""
    
    # Input validation
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
    MAX_FILENAME_LENGTH = int(os.getenv("MAX_FILENAME_LENGTH", "255"))
    
    # Content filtering
    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'data:text/html',            # Data URLs
        r'vbscript:',                 # VBScript URLs
    ]
    
    # File upload restrictions
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS", ".json,.txt,.md").split(",")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    # Directory traversal prevention
    FILENAME_SANITIZATION = {
        "remove_patterns": [r'\.\./', r'\.\.\\', r'/', r'\\'],
        "replace_chars": {'<': '_', '>': '_', ':': '_', '"': '_', '|': '_', 
                         '?': '_', '*': '_'},
        "max_length": MAX_FILENAME_LENGTH
    }
    
    @classmethod
    def is_content_safe(cls, content: str) -> tuple[bool, List[str]]:
        """Check if content is safe from security perspective."""
        issues = []
        
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Blocked pattern found: {pattern}")
        
        if len(content) > cls.MAX_INPUT_LENGTH:
            issues.append(f"Content too long: {len(content)} > {cls.MAX_INPUT_LENGTH}")
        
        return len(issues) == 0, issues
```

## Development vs Production

### Environment-Specific Configuration

Create different configurations for development and production:

```python
# src/config/environments.py
import os
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConfig(ABC):
    """Base configuration class."""
    
    # Shared settings
    APP_NAME = "Convoscope"
    VERSION = "1.0.0"
    
    @property
    @abstractmethod
    def debug(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def log_level(self) -> str:
        pass

class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    debug = True
    log_level = "DEBUG"
    
    # Development-specific settings
    ENABLE_MOCK_PROVIDERS = True
    ENABLE_DETAILED_ERRORS = True
    CACHE_DISABLED = True
    
    # Relaxed security for development
    ENABLE_INPUT_SANITIZATION = False
    ALLOW_ALL_ORIGINS = True

class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    debug = False
    log_level = "INFO"
    
    # Production-specific settings
    ENABLE_MOCK_PROVIDERS = False
    ENABLE_DETAILED_ERRORS = False
    CACHE_ENABLED = True
    
    # Strict security for production
    ENABLE_INPUT_SANITIZATION = True
    ALLOWED_ORIGINS = ["https://your-domain.com"]
    RATE_LIMITING_ENABLED = True

class TestConfig(BaseConfig):
    """Test environment configuration."""
    
    debug = True
    log_level = "ERROR"  # Reduce noise during testing
    
    # Test-specific settings
    USE_MOCK_PROVIDERS = True
    DISABLE_EXTERNAL_CALLS = True
    CONVERSATION_STORAGE_PATH = "./test_conversations"

def get_config() -> BaseConfig:
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()
```

## Configuration Validation

### Startup Configuration Check

Validate configuration at application startup:

```python
# src/config/validator.py
import os
import logging
from typing import List, Tuple
from src.config.environments import get_config

logger = logging.getLogger("convoscope.config")

def validate_configuration() -> Tuple[bool, List[str]]:
    """Validate application configuration."""
    
    errors = []
    warnings = []
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    available_providers = []
    
    for var in required_vars:
        if os.getenv(var):
            provider = var.replace("_API_KEY", "").lower()
            available_providers.append(provider)
        
    if not available_providers:
        errors.append("No LLM provider API keys configured")
    else:
        logger.info(f"Available providers: {', '.join(available_providers)}")
    
    # Validate file paths
    storage_path = os.getenv("CONVERSATION_STORAGE_PATH", "./conversation_history")
    try:
        os.makedirs(storage_path, exist_ok=True)
        if not os.access(storage_path, os.W_OK):
            errors.append(f"Cannot write to storage path: {storage_path}")
    except Exception as e:
        errors.append(f"Storage path error: {e}")
    
    # Validate numeric settings
    numeric_settings = {
        "DEFAULT_TEMPERATURE": (0.0, 1.0),
        "MAX_TOKENS": (1, 10000),
        "REQUEST_TIMEOUT": (5, 300)
    }
    
    for setting, (min_val, max_val) in numeric_settings.items():
        value = os.getenv(setting)
        if value:
            try:
                num_value = float(value)
                if not min_val <= num_value <= max_val:
                    warnings.append(f"{setting}={value} outside recommended range [{min_val}, {max_val}]")
            except ValueError:
                errors.append(f"Invalid numeric value for {setting}: {value}")
    
    # Log validation results
    config = get_config()
    logger.info(f"Configuration validation completed for {config.__class__.__name__}")
    
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    return len(errors) == 0, errors

# Run validation at startup
def ensure_valid_configuration():
    """Ensure configuration is valid before starting application."""
    is_valid, errors = validate_configuration()
    
    if not is_valid:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise SystemExit("Invalid configuration - cannot start application")
    
    logger.info("Configuration validation passed")
```

## Dynamic Configuration

### Runtime Configuration Updates

Allow certain configuration updates at runtime:

```python
# src/config/dynamic.py
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RuntimeConfig:
    """Runtime configuration that can be updated."""
    temperature: float = 0.7
    max_tokens: int = 2000
    stream_responses: bool = True
    provider_priority: List[str] = None
    auto_save_interval: int = 30
    
    def __post_init__(self):
        if self.provider_priority is None:
            self.provider_priority = ["openai", "anthropic", "google"]

class ConfigManager:
    """Thread-safe configuration manager."""
    
    def __init__(self):
        self._config = RuntimeConfig()
        self._lock = threading.RLock()
        self._observers = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        with self._lock:
            return getattr(self._config, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        with self._lock:
            if hasattr(self._config, key):
                old_value = getattr(self._config, key)
                setattr(self._config, key, value)
                
                # Notify observers
                for observer in self._observers:
                    observer(key, old_value, value)
                
                return True
            return False
    
    def update(self, **kwargs) -> Dict[str, bool]:
        """Update multiple configuration values."""
        results = {}
        for key, value in kwargs.items():
            results[key] = self.set(key, value)
        return results
    
    def add_observer(self, callback):
        """Add configuration change observer."""
        self._observers.append(callback)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        with self._lock:
            return self._config.__dict__.copy()

# Global configuration manager instance
config_manager = ConfigManager()

# Usage example
def update_temperature(new_temp: float):
    """Update response temperature."""
    if 0.0 <= new_temp <= 1.0:
        return config_manager.set("temperature", new_temp)
    return False
```

This configuration system provides comprehensive control over all aspects of the Convoscope application while maintaining security and flexibility across different deployment environments.

---

*Next: [Advanced Usage](advanced-usage.md) - Complex scenarios and customization patterns*