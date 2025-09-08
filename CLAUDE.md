# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Convoscope is a Streamlit-powered AI chat application that provides an interactive interface for conversations with Language Learning Models (LLMs), featuring conversation history management, topic summarization, and HTML export capabilities.

## Architecture

### Single-File Application
- **`run_chat.py`**: The main application file (696 lines) containing the entire Streamlit application
- Monolithic structure with all features implemented in one Python file
- Uses Streamlit session state for maintaining conversation history and settings

### Data Storage
- **`conversation_history/`**: Directory for storing conversation JSON files
- Auto-save functionality saves to `conversation_history/restore_last_convo.json`
- Manual saves create timestamped JSON files in the same directory

### Key Components in `run_chat.py`
- Chat interface with streaming responses
- Conversation management (save/load/auto-save)
- Topic summarization using OpenAI API
- HTML export with embedded CSS and FontAwesome icons
- Multiple LLM provider support (currently OpenAI, with Anthropic/Llama planned)

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
- **Data processing**: `pandas`, `numpy`, `pyarrow`
- **Web scraping**: `newspaper3k`, `beautifulsoup4`, `selenium`
- **Additional**: `markdown`, `httpx`, `protobuf`

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access

### LLM Providers Configuration
Located in `run_chat.py:34-38`:
- OpenAI: `gpt-3.5-turbo`, `gpt-4`, `davinci`
- Planned: Anthropic Claude models, Llama models

### System Prompts
Predefined prompts for different use cases (lines 43-50):
- Default, Python, Recipe, Software, Web, Data, Marketing, etc.

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

## File Structure
```
convoscope/
├── run_chat.py              # Main Streamlit application
├── requirements.txt         # Python dependencies
├── requirements_llama-st.txt # Extended dependencies (unused)
├── conversation_history/    # Conversation storage
│   ├── zettle.json         # Example conversation file
│   └── restore_last_convo.json # Auto-save file
├── README.md               # Project documentation
└── .gitignore             # Git ignore rules
```

## Development Notes

- The application is designed as a single-file Streamlit app for simplicity
- All conversation data is stored locally as JSON files
- The interface uses tabs for Chat, History, and Topics sections
- Temperature settings control response creativity (0.0-1.0)
- Maximum display limits can be configured for performance with long conversations