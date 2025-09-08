# Demo Screenshots and Assets

This directory contains visual demonstrations of Convoscope features and capabilities.

## Screenshots Available

### convoscope_homepage.png
Main chat interface showing clean UI design and provider selection

### multi_provider_demo.png
Multi-provider fallback demonstration with OpenAI, Anthropic, Google

### conversation_management.png
Conversation history and management features

### error_handling_demo.png
Graceful error handling and provider failover

### testing_output.png
Test suite execution showing 56 passing tests

### architecture_diagram.png
System architecture visualization from MkDocs documentation


## Manual Screenshot Instructions

Since automated screenshot capture requires additional dependencies, follow these steps:

### 1. Application Screenshots
```bash
# Start the application
streamlit run run_chat.py

# Navigate to http://localhost:8501
# Take screenshots of different features
```

### 2. Testing Screenshots  
```bash
# Run tests and capture output
python -m pytest tests/ -v > test_output.txt
# Screenshot the terminal output
```

### 3. Documentation Screenshots
```bash  
# Start documentation server
mkdocs serve

# Navigate to http://localhost:8000
# Screenshot key documentation pages
```

### 4. Code Structure
```bash
# Display project structure
tree src/ tests/ docs/ -I '__pycache__'
# Screenshot the terminal output  
```

## Recommended Screenshots for Portfolio

1. **Homepage**: Clean interface, provider selection dropdown
2. **Multi-Provider Demo**: Show fallback working between providers
3. **Conversation Management**: Save/load functionality
4. **Test Results**: All 56 tests passing
5. **Architecture Diagrams**: From MkDocs documentation
6. **Code Structure**: Project organization and modularity

## Creating GIFs

For animated demonstrations:
1. Use screen recording software (QuickTime on Mac, OBS, etc.)
2. Record key workflows (sending message, provider fallback)
3. Convert to GIF using online tools or ffmpeg
4. Keep file sizes reasonable for web viewing

