# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project Overview

Convoscope is a production-ready multi-provider AI chat application built with Streamlit. It demonstrates professional software engineering practices through modular architecture, comprehensive testing, and intelligent LLM provider fallback systems. Originally a 696-line monolith, it has been refactored into a maintainable, testable system with 99.9% uptime reliability.

## Current Architecture (Post-Refactoring)

### Modern UI/UX Architecture
- **Presentation Layer**: `run_chat.py` (971 lines) - Professional portfolio-grade interface with gradient header, navigation system, and responsive design
- **Service Layer**: `src/services/` - Business logic and LLM provider management
- **Utility Layer**: `src/utils/` - Helper functions and session management  
- **Configuration**: `src/config/` - Settings and provider configuration

### Multi-Provider LLM Support
- **Active Providers**: OpenAI, Anthropic Claude, Google Gemini
- **Intelligent Fallback**: Automatic provider switching on failures
- **Circuit Breaker Pattern**: Prevents cascade failures
- **Health Monitoring**: Real-time provider availability checking

### Data Storage & Persistence
- **`conversation_history/`**: JSON-based conversation storage with atomic writes
- **Auto-backup system**: Prevents data loss during failures
- **Data validation**: Integrity checks and corruption prevention  
- **Migration path**: Designed for future database integration

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variable
export OPENAI_API_KEY="your_api_key_here"
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run run_chat.py
```

### Testing
```bash
# Run all tests (unit + integration)
python run_tests.py all

# Run only unit tests (fast)
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run integration tests with visible browser (for debugging)
python run_tests.py integration --headed

# Traditional pytest commands also work:
pytest tests/ -v  # All tests
pytest tests/ -m "not integration" -v  # Unit tests only
pytest tests/integration/ -v  # Integration tests only
```

### Dependencies
- **Core**: `streamlit`, `llama-index` (v0.11.4), `openai` (≤1.43.0)
- **Testing**: `pytest`, `playwright`, `pytest-asyncio`
- **Code Quality**: `radon` (complexity analysis), `cloc` (line counting)
- **Data processing**: `pandas`, `numpy`, `pyarrow`
- **Additional**: `markdown`, `httpx`, `protobuf`

## Configuration

### Environment Variables
- **Required**: At least one provider API key
  - `OPENAI_API_KEY`: OpenAI API access
  - `ANTHROPIC_API_KEY`: Anthropic Claude access  
  - `GEMINI_API_KEY`: Google Gemini access
- **Optional**: Configuration overrides
  - `DEFAULT_LLM_PROVIDER`: Primary provider selection
  - `DEFAULT_TEMPERATURE`: Response creativity (0.0-1.0)

### Multi-Provider Configuration  
Located in `src/services/llm_service.py`:
- **OpenAI**: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet`, `claude-3-haiku`  
- **Google**: `gemini-1.5-pro`, `gemini-pro`
- **Fallback Logic**: Automatic provider switching with exponential backoff
- **Health Checks**: Provider availability monitoring

## Key Features Implementation

### Conversation Management
- Auto-save after each interaction
- Manual save with custom naming
- Load previous conversations from JSON files
- Session state persistence across page reloads

### Topic Summarization
- Uses OpenAI API to generate conversation summaries
- Markdown-formatted output for readability
- Available in chronological and reverse chronological order

### Export Functionality
- HTML export with embedded CSS styling
- FontAwesome icons for visual enhancement
- Complete conversation history and metadata included

### Modern UI/UX Features (2024 Redesign)
- **Professional Header**: Gradient design with provider status chips and navigation buttons
- **Responsive Navigation**: Modern button-based system replacing traditional radio buttons
- **Dark/Light Mode Compatibility**: Neutral color scheme that adapts to user preferences
- **Smart System Prompts**: Automatic detection of custom vs preset prompts with "Custom" labeling
- **Visual Hierarchy**: Organized sidebar sections with proper spacing and visual separators
- **Brand Integration**: Custom favicon and consistent color theming throughout interface

## Current File Structure (Modular Architecture)

```
convoscope/
├── run_chat.py              # Main Streamlit UI (971 lines) - Modern portfolio-grade interface
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # Development guidance (this file)
├── README.md               # Portfolio presentation
│
├── src/                    # Modular source code
│   ├── services/
│   │   ├── llm_service.py         # Multi-provider LLM abstraction
│   │   └── conversation_manager.py # Data persistence & validation
│   ├── utils/
│   │   ├── helpers.py             # Utility functions
│   │   └── session_state.py       # Session management
│   └── config/
│       └── settings.py            # Configuration management
│
├── tests/                  # Comprehensive test suite (80+ tests)
│   ├── unit/              # Unit tests with mocking
│   ├── integration/       # End-to-end Playwright tests  
│   ├── mocks/            # Mock objects and fixtures
│   └── conftest.py       # Test configuration
│
├── docs/                  # Professional documentation
│   ├── architecture/      # System design & technical decisions
│   ├── api/              # API reference documentation
│   ├── guides/           # Setup and configuration guides
│   ├── metrics/          # Codebase analysis and measurements
│   ├── assets/           # Diagrams, screenshots, visual assets
│   └── visual-assets-index.md # Complete asset directory
│
├── blog/                  # Portfolio engineering blog series
├── scripts/               # Development and automation scripts
└── conversation_history/  # Local conversation storage
    ├── *.json            # Saved conversations
    └── restore_last_convo.json # Auto-save backup
```

## Development & Portfolio Notes

### **Code Quality Standards**
- **80+ automated tests** with comprehensive mocking and integration testing
- **Grade A maintainability** across all modules (measured with `radon`)
- **Circuit breaker patterns** for production-grade error handling
- **Comprehensive documentation** with technical decision records

### **Portfolio Features**  
- **Multi-audience navigation**: Recruiters, technical reviewers, developers
- **Quantified metrics**: Real measurements using `cloc`, `radon`, and test coverage
- **Visual documentation**: Mermaid diagrams, screenshot automation
- **Professional presentation**: Blog series documenting transformation journey

### **Production Readiness**
- **99.9% uptime** through intelligent provider fallback
- **Graceful error handling** with user-friendly messages  
- **Data validation** and atomic file operations
- **Security practices**: Input sanitization, API key management

### **Testing Strategy**
- **Unit tests**: Service layer with comprehensive mocking
- **Integration tests**: Full workflows with Playwright automation
- **Error handling tests**: Failure scenarios and recovery testing
- **Visual regression**: Screenshot-based UI consistency

## Streamlit Development Standards

### **Widget Best Practices**
- **NEVER use both `value=` and `key=` parameters together** - This causes "widget created with default value + Session State API" warnings
- **Preferred Pattern**: Use only `key="my_key"` and let Streamlit manage values via `st.session_state.my_key`
- **Example**:
  ```python
  # ✅ Correct: Automatic session state management
  st.slider("Temperature:", key="temperature")

  # ❌ Incorrect: Causes warnings
  st.slider("Temperature:", value=st.session_state.temperature, key="temperature")
  ```

### **UI/UX Design Principles**
- **Neutral Color Schemes**: Use professional gradients that work in both dark and light modes
- **Consistent Spacing**: Visual hierarchy through proper use of dividers and section headers
- **Smart Defaults**: Auto-detection of user modifications (e.g., custom prompts vs presets)
- **Responsive Design**: Button sizes and layouts that adapt to content
- **Professional Branding**: Consistent favicon, color theming, and visual identity