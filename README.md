# 🐇 Curious and Curiouser: An AI Chat Experience

*"Begin at the beginning," the King said, very gravely, "and go on till you come to the end: then stop."* - Lewis Carroll

Welcome to a whimsical yet powerful chat interface that lets you dive down the AI rabbit hole! This Streamlit-powered application provides an intuitive way to interact with various Language Learning Models (LLMs), while maintaining a complete history of your conversations and their summaries.

## ✨ Features

### 🗣️ Chat Interface
- Real-time streaming responses from AI models
- Configurable chat settings including temperature and model selection
- Rich markdown support for formatted responses
- Auto-saving of conversations to prevent loss of data

### 💾 Conversation Management
- Save and load conversation histories
- Auto-save feature to recover from unexpected closures
- Manual naming and organization of chat sessions
- Limit the number of displayed chat messages for better performance

### 📊 Analysis & Export
- Generate topic summaries of your conversations
- View summaries in both original and reverse chronological order
- Export beautifully formatted HTML reports with:
  - Complete conversation history
  - Topic summaries
  - Metadata (timestamp, model settings, etc.)
  - FontAwesome icons for visual enhancement

### ⚙️ Customization Options
- Choose from multiple LLM providers (OpenAI, with Anthropic and Llama coming soon)
- Select from various models within each provider
- Adjust response temperature (0.0-1.0) for controlling creativity vs consistency
- Customize system prompts with pre-defined or custom messages

## 🚀 Getting Started

### Prerequisites
```bash
pip install streamlit
pip install llama_index
pip install openai
pip install markdown
```

### Configuration
1. Create a `secrets.toml` file in the `.streamlit` directory
2. Add your OpenAI API key:
```toml
openai_key = "your-api-key-here"
```

### Running the Application
```bash
streamlit run run_chat_forLLM.py
```

## 🎨 Interface Sections

### Main Chat Area
- Input field for questions
- Real-time streaming responses
- Markdown-formatted messages
- Alternating message colors for readability

### Sidebar Controls
- Chat history management
- LLM configuration settings
- Interface customization options
- Session state viewer (expandable)

### Tabs
1. **Chat**: Main conversation interface
2. **Conversation History**: Complete chat log with reverse order option
3. **Topics Extracted**: AI-generated summaries with export options

## 🔧 Technical Details

### Auto-save Feature
- Conversations are automatically saved after each update
- Restore functionality for recovering from page reloads
- Save location: `conversation_history/restore_last_convo.json`

### Export Format
- HTML reports with embedded CSS styling
- FontAwesome icons for visual enhancement
- Collapsible conversation sections
- Comprehensive metadata section

### State Management
- Streamlit session state for persistent settings
- Conversation history maintained across page reloads
- Configurable display limits for performance

## 📝 Notes
- The image URL in the header can be customized through the sidebar
- Temperature settings affect response creativity (0.0 = consistent, 1.0 = creative)
- Support for Anthropic and Llama models coming soon
- Maximum display limit can be set to improve performance with long conversations

## 🎯 Future Enhancements
- PDF export functionality
- Additional LLM providers integration
- Enhanced visualization options
- Chat analytics dashboard
- Custom theming options

## 🐛 Troubleshooting

If you encounter issues:
1. Check your API key configuration
2. Verify the `conversation_history` directory exists
3. Ensure all dependencies are installed
4. Check the session state viewer in the sidebar for debugging

---

*"Why, sometimes I've believed as many as six impossible things before breakfast."* - Lewis Carroll

Happy chatting! 🎩🐇☕
