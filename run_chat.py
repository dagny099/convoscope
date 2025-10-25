# THIS IS A CHAT HELPER TOOL:
# Developed a chatbot with configurable LLM features (see below) and the ability to store conversations, 
# summarize their topics, and download the summary as a formatted HTML file.
# ------------------
# NEXT STEPS (for the tool) => 
# * Generate summary snippets & cards with images representing the conversation
# * Add open source foundational model
# * Connect a database to store the conversation history, perhaps with profiles?
# ------------------

import streamlit as st
import os
import json
from datetime import datetime
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
import asyncio
import random
import markdown

# Import the multi-provider LLM service
from src.services.llm_service import LLMService, LLMServiceError
from pathlib import Path

# From the official OpenAI package (for topic extraction only)
import openai as OfficialOpenAI
OfficialOpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OfficialOpenAI

save_convo_path = 'conversation_history'
if not os.path.exists(save_convo_path):
    os.makedirs(save_convo_path)

# Check if it's the first time running
if 'num_updates' not in st.session_state:
    st.session_state.num_updates = 0

# Initialize the multi-provider LLM service
if 'llm_service' not in st.session_state:
    st.session_state.llm_service = LLMService()

# Get providers from the LLM service for dynamic updates
def get_providers_dict():
    """Get available providers and models from the LLM service."""
    service = st.session_state.llm_service
    providers = {}
    
    for provider_name, provider_config in service.PROVIDERS.items():
        if provider_config.available:
            providers[provider_name] = provider_config.models
        else:
            providers[f"{provider_name} (API key needed)"] = provider_config.models
    
    return providers

# Legacy provider dict (kept for compatibility, but will be replaced by dynamic version)
providers = {
    'openai': ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"],
    'anthropic': ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    'google': ["gemini-2.5-flash", "gemini-2.5-pro"]
}

chat_history_options_labels = ["Load a conversation? 󠀠 󠀠:file_folder:", "Reload last auto-save? 󠀠 󠀠:relieved:", "Start anew 󠀠 󠀠:city_sunrise:"]
chat_history_options_captions = ["Get a list of saved conversations.", "Restore session before page reloaded.", "Reset the conversation." ]

priming_messages = {
    "default": "You are a helpful assistant.",
    "python": "You are an expert in writing well documented python code. Provide your responses with documented python code. But you always begin the response with a line of text instead of code.",
    "recipe": "You are a professional chef. You are asked to provide a recipe for a dish. You always begin your response with a line of text.",
    "software": "You are a Software Architect with expertise in designing and programming web based applications that support enterprises in a variety of industries.",
    "web": "You are a web developer with expertise in designing and programming web based applications that support enterprises in a variety of industries.",
    "data": "You are a data scientist with expertise in analyzing and interpreting complex data sets to help organizations make informed decisions.",
    "marketing": "You are a marketing professional with expertise in developing and implementing marketing strategies to promote products and services.",
    "finance": "You are a financial analyst with expertise in analyzing financial data to help organizations make informed investment decisions.",
    "healthcare": "You are a healthcare professional with expertise in providing medical care to patients in a variety of settings.",
    "education": "You are an educator with expertise in teaching students in a variety of subjects and grade levels.",
    "law": "You are a lawyer with expertise in providing legal advice and representation to clients in a variety of legal matters.",
    "engineering": "You are an engineer with expertise in designing and building complex systems to solve a variety of problems.",
    "science": "You are a scientist with expertise in conducting research and experiments to advance scientific knowledge in a variety of fields.",
    "art": "You are an artist with expertise in creating visual, performing, or literary works to express ideas and emotions.",
    "music": "You are a musician with expertise in performing, composing, or teaching music to entertain and inspire audiences.",
    "sports": "You are an athlete with expertise in competing in sports to achieve personal and team goals.",
    "entertainment": "You are an entertainer with expertise in performing or producing entertainment to engage and delight audiences.",
    "journalism": "You are a journalist with expertise in researching and reporting news and information to inform and educate the public.",
    "politics": "You are a politician with expertise in governing and leading communities to create positive change and improve people's lives.",
    "business": "You are a business professional with expertise in managing organizations and resources to achieve strategic goals and objectives.",
    "technology": "You are a technology professional with expertise in developing and implementing innovative solutions to solve complex problems.",
    "leadership": "You are a leader with expertise in inspiring and guiding individuals and teams to achieve common goals and objectives.",
    "custom": ""  # Placeholder for manually edited custom prompts
}

GET_HELP = f"""
Here's a quick guide to help you get started:

#### 1. Configure your chat settings (OPTIONAL)
- **Priming the Model**: You can choose from the available priming messages or enter your own. This message will help the AI understand the context of your conversation.
- **Choose a Model**: Select from the available models (e.g., `gpt-3.5-turbo`, `gpt-4`) in the dropdown to fit your needs.
- **Adjust Parameters**: Set the temperature to control the randomness of the AI's responses. A higher value (e.g., 0.9) will result in more creative responses, while a lower value (e.g., 0.2) will keep the output more focused and deterministic.

#### 2. Start chatting!
- **Start a Conversation**: Enter your questions or commands in the text box, and the AI will respond in real-time.
- **Review the Conversation**: You can review all your past interactions in the conversation panel.

#### 3. Explore Features
- **Chat History**: View your entire conversation in the "Conversation History" tab.
- **Topic Summary**: Generate and download summaries of your chat in the "Topics Extracted" tab
- **Download the Report**: When you're finished, click the **Download Report** button to save a summary of your conversation and key insights in HTML or PDF format.
- **Load a Previous Conversation**: You can also upload a previously saved conversation using the "Upload File" option to continue from where you left off.

#### 4. Advanced Options
- **Manual Settings**: You can manually name your sessions or adjust additional parameters to fine-tune the behavior of the AI.
- **Help and Feedback**: If you need assistance or have feedback, feel free to click the **Help** button.

---
"""
# ============================================= #

# STREAMLIT CODING STANDARDS:
# - When using key= parameter for widgets, NEVER use value= parameter
# - Let Streamlit manage values automatically through session state
# - This prevents "widget created with default value + Session State API" warnings

# Setup session
st.set_page_config(
    page_title="I wonder...",
    page_icon="circle_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": "https://www.streamlit.io/", 
        "Report a bug": "mailto:dagny099@gmail.com", 
        "About": GET_HELP},
)

# Modern CSS styling and Font-Awesome icons
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --header-from: #0f172a; /* slate-900 */
            --header-to:   #1e293b; /* slate-800 */
            --tab-active-bg: #14b8a6; /* teal-500 (tweaked) */
            --tab-active-fg: #ffffff;
            --tab-inactive-bg: #475569; /* slate-600 */
            --tab-inactive-bg-2: #3b4a5a; /* subtle darker end */
            --tab-inactive-fg: #e5e7eb; /* slate-200 */
            --text-on-dark: #ffffff;
            --text-muted-on-dark: rgba(255,255,255,0.9);
            --panel-grad-from: #f8fafc;
            --panel-grad-to: #e2e8f0;
            --shadow-soft: rgba(100,116,139,0.3);
            --border-color: #e2e8f0;
            --sidebar-header-color: #374151;
            --chip-bg: rgba(255,255,255,0.18);
            --chip-border: rgba(255,255,255,0.28);
            --chip-fg: #ffffff;
            --divider: #555555;
            --report-text: #333333;
            --report-user-bg: #ECE4FF;
            --report-bot-bg: #DCE1E9;
            --report-paragraph: #5D5C61;
            --heading-color: #1a202c;
        }
        /* Global Styles */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Modern Sidebar Styling */
        .settings-modal {
            padding: 1rem;
            background: linear-gradient(135deg, var(--panel-grad-from) 0%, var(--panel-grad-to) 100%);
            border-radius: 0.75rem;
            margin-bottom: 1rem;
        }

        /* Button Enhancements */
        .stButton > button {
            background: linear-gradient(135deg, var(--tab-inactive-bg) 0%, var(--tab-inactive-bg-2) 100%);
            border: none;
            border-radius: 0.5rem;
            color: var(--tab-inactive-fg);
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow-soft);
        }

        /* Selectbox Styling */
        .stSelectbox > div > div {
            border-radius: 0.5rem;
            border: 1px solid var(--border-color);
        }

        /* Sidebar Section Headers */
        .sidebar .markdown-text-container h4 {
            color: var(--sidebar-header-color);
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ********** SETUP LAYOUT **********


def load_convo(name=None):
    """
    Load a conversation from a JSON file.
    """
    if name is None:
        name = st.session_state.selected_file + '.json'
    elif name.endswith('.json')==False:
        name = name + '.json'
    
    #LOAD THE CONVERSATION
    try:
        with open(os.path.join(save_convo_path, name), 'r') as f:
            st.session_state.conversation = json.load(f)
            st.session_state.load_msg = {'success': f"Conversation loaded from '{name.replace('.json','')}'.", "file": name}
            if 'topics_from_LLM' in st.session_state:
                del st.session_state['topics_from_LLM']
            if 'topics_from_LLM_rev' in st.session_state:
                del st.session_state['topics_from_LLM_rev']

    except FileNotFoundError:
        st.session_state.load_msg = {'warning': f"No saved conversation '{name}' found. Please save a conversation first.", "file": name}
    except json.JSONDecodeError:
        st.session_state.load_msg = {'error': f"Error: '{name}' is not a valid JSON file.", "file": name}
    

def choose_convo():
    """
    Choose the conversation to load based on the selected option.
    """
    if st.session_state.set_convo_status == chat_history_options_labels[1]: 
        load_convo('restore_last_convo.json')
        
    elif st.session_state.set_convo_status == chat_history_options_labels[0]:
        history_files = [f.replace('.json','') for f in os.listdir(save_convo_path) if f.endswith(".json") & (f != 'restore_last_convo.json')]
        if len(history_files) == 0:
            history_files = ["No saved conversations yet! Save one first."]
        
        st.sidebar.selectbox(" 󠀠 󠀠 󠀠:chipmunk: 󠀠 󠀠 󠀠 List Saved Conversations:", index=None, options=history_files, key='selected_file', on_change=load_convo)

    elif st.session_state.set_convo_status == chat_history_options_labels[2]: 
        st.session_state['conversation'] = list()
        del st.session_state['user_input']
        if 'load_msg' in st.session_state:
            del st.session_state['load_msg']
        if ('selected_file' in st.session_state):
            del st.session_state['selected_file']
        if ('manual_name' in st.session_state):
            del st.session_state['manual_name']
        if ('topics_from_LLM' in st.session_state):
            del st.session_state['topics_from_LLM']
        if ('topics_from_LLM_rev' in st.session_state):
            del st.session_state['topics_from_LLM_rev']
        headerCol2.info("Cleared conversation history.")
        st.session_state.num_updates = 0


def save_convo(name=None):
    """
    Save the conversation to a JSON file with a user-generated name.
    """
    timestamp = datetime.now().strftime("%b %d, %Y %H:%M")

    if name is None:
        name = st.session_state.manual_name + '.json'
    elif name.endswith('.json')==False:
        name = name + '.json'
    
    try:
        with open(os.path.join(save_convo_path, name), 'w') as f:
            json.dump(st.session_state.conversation, f)
            st.session_state.save_msg = {'success': f"Conversation saved to: \n {name} \n\n ({len(st.session_state.conversation)}  msgs as of {timestamp})."} 
    except:
        st.session_state.save_msg = {'error': f"Error: conversation not saved, tried -  {os.path.join(save_convo_path, name)}"}
    #PRINT THE MEESSAGE
    if 'success' in st.session_state.save_msg:
        st.sidebar.success(st.session_state.save_msg['success'])
    elif 'error' in st.session_state.save_msg:
        st.sidebar.warning(st.session_state.save_msg['error'])
    else:
        st.sidebar.info("No message to display.")


def get_index(orig_list, item):
    """
    Get the index of an item in a list if it exists.
    """
    try:
        return orig_list.index(item)
    except ValueError:
        return None


def update_priming_text(source=None, new_value=None):
    """
    Update the priming text based on the source of the change.
    """
    if source is None:
        st.session_state["priming_key"] = st.session_state.selectbox_choice
        st.session_state["priming_text"] = priming_messages[st.session_state.selectbox_choice]
    elif source == "button":
        st.session_state["priming_key"] = new_value[0]
        st.session_state["priming_text"] = new_value[1]


def topic_extraction(conversation):
    """
    Extract topics from a conversation using the OpenAI API.
    """

    # Concatenate the conversation into a single string
    concatenated_string = ""
    for item in conversation:
        for key, value in item.items():
            # Capitalize the key and concatenate with the value
            concatenated_string += f"{key.upper()}: {value} "

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # "gpt-4"  
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI trained in language comprehension and summarization. Read the following conversation and identify the MAIN TOPICS discussed and the relevant points for each topic. Each side of the conversation will be labeled with the speaker ('user' or 'ai'). Always give your output in well-formatted markdown for readability. Use smaller headers rather than larger ones.", #"For each of the MAIN TOPICS, summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."
            },
            {
                "role": "user",
                "content": concatenated_string
            }
        ]
    )
    return response.choices[0].message.content


def sidebar_configuration():
    """
    Modern settings panel in sidebar with clean organization and preserved provider chip functionality
    """
    # Initialize session state first
    if "conversation" not in st.session_state:
        st.session_state['conversation'] = list()
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "priming_text" not in st.session_state:
        st.session_state.priming_text = "You are a helpful assistant."
        st.session_state.priming_key = 'default'
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = 'openai'
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = 'gpt-4o-mini'

    st.sidebar.markdown("""
        <div class="settings-modal">
            <h3 style="margin-top: 0; color: var(--heading-color); font-weight: 600;">
                <i class="fas fa-cog"></i> Settings
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Quick Actions Section
    st.sidebar.markdown("#### 🔄 Quick Actions")

    # Conversation management
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🆕 New Chat", width='stretch'):
            st.session_state['conversation'] = list()
            if 'user_input' in st.session_state:
                del st.session_state['user_input']
            st.success("Started new conversation")

    with col2:
        if st.button("🔀 Random", width='stretch'):
            # Randomize some settings
            st.session_state.priming_text = random.choice(list(priming_messages.values()))
            st.session_state.temperature = round(random.uniform(0.3, 0.9), 1)
            st.success("Settings randomized!")

    # Load/Save conversations
    st.sidebar.markdown("#### 💾 Conversations")

    # Save current conversation
    if st.session_state.conversation:
        save_name = st.sidebar.text_input("💾 Save as:", placeholder="Enter conversation name")
        if save_name:
            save_convo(save_name)

    # Load existing conversations
    history_files = [f.replace('.json','') for f in os.listdir(save_convo_path) if f.endswith(".json") and f != 'restore_last_convo.json']
    if history_files:
        selected_convo = st.sidebar.selectbox("📁 Load conversation:", options=[None] + history_files, index=0)
        if selected_convo:
            load_convo(selected_convo)
            st.sidebar.success(f"Loaded: {selected_convo}")

    st.sidebar.markdown("---")

    # LLM Configuration
    st.sidebar.markdown("#### 🤖 LLM Configuration")

    # Provider Selection - CRITICAL: This preserves our chip update functionality
    dynamic_providers = get_providers_dict()
    available_provider_names = list(dynamic_providers.keys())

    # Clean provider names for display
    clean_provider_names = [name.split(' (')[0] for name in available_provider_names]

    if st.session_state.llm_provider not in clean_provider_names and clean_provider_names:
        st.session_state.llm_provider = clean_provider_names[0]

    current_index = 0
    if st.session_state.llm_provider in clean_provider_names:
        current_index = clean_provider_names.index(st.session_state.llm_provider)

    selected_provider = st.sidebar.selectbox(
        "Provider:",
        options=clean_provider_names,
        index=current_index
    )
    # CRITICAL: Direct assignment preserves chip update functionality
    st.session_state.llm_provider = selected_provider

    # Model Selection
    available_models = st.session_state.llm_service.get_available_models(st.session_state.llm_provider)
    if available_models and st.session_state.selected_model not in available_models:
        st.session_state.selected_model = available_models[0]

    if available_models:
        model_index = available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
        st.sidebar.selectbox(
            "Model:",
            options=available_models,
            index=model_index,
            key="selected_model"
        )

    # Temperature
    st.sidebar.slider(
        "🌡️ Temperature (creativity):",
        min_value=0.0, max_value=1.0, step=0.1,
        key="temperature",
        help="Lower values = more consistent, Higher values = more creative"
    )

    st.sidebar.markdown("---")

    # System Prompt
    st.sidebar.markdown("#### 📝 System Prompt")

    # Quick preset selection with automatic "custom" detection
    priming_options = list(priming_messages.keys())
    current_key = st.session_state.get('priming_key', 'default')
    current_text = st.session_state.get('priming_text', priming_messages['default'])

    # Check if current text matches any preset (except "custom")
    matching_preset = None
    for key, text in priming_messages.items():
        if key != "custom" and text == current_text:
            matching_preset = key
            break

    # If text doesn't match any preset, it's custom
    if matching_preset is None and current_text and current_text != priming_messages.get('custom', ''):
        current_key = 'custom'
        priming_messages['custom'] = current_text  # Update custom placeholder
        st.session_state.priming_key = 'custom'
    elif matching_preset and current_key != matching_preset:
        # Update key to match the content
        current_key = matching_preset
        st.session_state.priming_key = matching_preset

    if current_key not in priming_options:
        current_key = 'default'
        st.session_state.priming_key = current_key
        st.session_state.priming_text = priming_messages[current_key]

    preset_index = priming_options.index(current_key)
    selected_preset = st.sidebar.selectbox(
        "Preset:",
        options=priming_options,
        index=preset_index,
        format_func=lambda x: x.title()
    )

    if selected_preset != current_key:
        st.session_state.priming_key = selected_preset
        if selected_preset != 'custom':
            st.session_state.priming_text = priming_messages[selected_preset]

    # Custom prompt
    # STREAMLIT BEST PRACTICE: When using key= parameter, do NOT use value= - let Streamlit manage via session state automatically
    st.sidebar.text_area(
        "Custom prompt:",
        height=100,
        key="priming_text",
        help="Customize how the AI should behave"
    )

    # Advanced Settings
    with st.sidebar.expander("⚙️ Advanced Settings"):
        st.number_input(
            "Max messages to display:",
            min_value=1, max_value=50,
            value=st.session_state.get('max_show_chats', 10) or 10,
            key="max_show_chats"
        )

        # Debug info
        if st.checkbox("Show debug info"):
            st.write("**Current Settings:**")
            st.write(f"Provider: {st.session_state.llm_provider}")
            st.write(f"Model: {st.session_state.selected_model}")
            st.write(f"Temperature: {st.session_state.temperature}")
            st.write(f"Messages: {len(st.session_state.conversation)}")

        # Session State Display
        if st.checkbox("Show session state"):
            st.write("**Full Session State:**")
            st.write(st.session_state)

    # Return aggregated settings
    return {
        "llm_provider": st.session_state.llm_provider,
        "selected_model": st.session_state.selected_model,
        "temperature": st.session_state.temperature,
        "priming_text": st.session_state.priming_text,
    }


def get_multi_provider_response(settings, question):
    """
    Get response from the selected LLM provider using the multi-provider service.
    """
    # Build messages for the LLM service format
    messages = [{"role": "system", "content": settings['priming_text']}]
    
    # Append previous conversation history
    for chat in st.session_state.conversation:
        messages.append({"role": "user", "content": chat['user']})
        messages.append({"role": "assistant", "content": chat['ai']})
    
    # Add the new user question
    messages.append({"role": "user", "content": question})
    
    try:
        # Use the multi-provider service
        llm_service = st.session_state.llm_service
        response = llm_service.get_completion(
            provider=settings["llm_provider"], 
            model=settings["selected_model"],
            messages=messages,
            temperature=settings["temperature"]
        )
        return response
        
    except LLMServiceError as e:
        st.error(f"LLM Service Error: {str(e)}")
        
        # Try fallback if primary provider fails
        try:
            available_providers = llm_service.get_available_providers()
            if len(available_providers) > 1:
                # Find a different available provider
                fallback_provider = None
                fallback_model = None
                
                for provider_name, provider_config in available_providers.items():
                    if provider_name != settings["llm_provider"]:
                        fallback_provider = provider_name
                        fallback_model = provider_config.models[0]  # Use first available model
                        break
                
                if fallback_provider:
                    st.warning(f"Falling back to {fallback_provider} with {fallback_model}")
                    response = llm_service.get_completion(
                        provider=fallback_provider,
                        model=fallback_model,
                        messages=messages,
                        temperature=settings["temperature"]
                    )
                    return response
                    
        except LLMServiceError as fallback_error:
            st.error(f"Fallback also failed: {str(fallback_error)}")
        
        return "I'm sorry, I'm having trouble connecting to the AI service right now. Please check your API keys and try again."
    
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return "I'm sorry, something unexpected went wrong. Please try again."


async def stream_openai_response(settings, question):
    """
    Legacy function - now routes to multi-provider service.
    Kept for backward compatibility but updated to use new service.
    """
    # Get the response using the multi-provider service
    response_text = get_multi_provider_response(settings, question)
    
    # Placeholder for streaming output (simulate streaming for UI consistency)
    output_placeholder2 = st.empty()
    
    # Simulate streaming by displaying the response progressively
    partial_response = ""
    for char in response_text:
        partial_response += char
        
        # Update the session state conversation in real-time
        st.session_state.conversation[-1]['ai'] = partial_response
        
        # Update the UI
        output_placeholder2.chat_message("ai").markdown(partial_response)
        
        # Small delay to simulate streaming (optional)
        await asyncio.sleep(0.01)
    
    return partial_response


def image_with_aspect_ratio(image_url, width=300, height=300):
    """
    Display an image at the top of the page with a fixed aspect ratio.
    """
    return f"""
        <style>
        .image-container {{
            width: {width}px;
            height: {height}px;
            position: relative;
            overflow: hidden;
        }}
        .image-container img {{
            object-fit: contain;
            width: 100%;
            height: 100%;
        }}
        </style>
        <div class="image-container"> 
            <img src="{image_url}">
        </div>
        """


def create_report(which_summary=None):
    """
    Create a report with the conversation and summary.
    """
    # Create the report content
    report_content = f"CONVERSATION:\n\n{st.session_state['conversation']}\n\nSUMMARY:\n\n{[which_summary]} \n\n"
    return report_content


def create_html_report(conversation, summary=None):
    """
    Create an HTML report with the conversation and summary.
    """

    # Extract metadata from session_state
    priming_text = st.session_state.get("priming_text", "No priming text provided.")
    model_selection = st.session_state.get("selected_model", "Unknown model")
    temperature = st.session_state.get("temperature", "Not specified")
    manual_name = st.session_state.get("manual_name", "Not specified")
    timestamp = datetime.now().strftime("%b %d, %Y %H:%M")  #strftime("%Y-%m-%d %H:%M")
    
    num_conversations = len(conversation)

    # Start HTML content with headers and styles
    html_content = """
    <html>
        <head>
            <style>
                .header {
                    font-family: 'Merriweather', serif; /* A nice serif font for headers */
                    font-size: 20px;
                    font-weight: bold;
                    color: var(--report-text);
                    margin-bottom: 10px;
                }
                .user {
                    background-color: var(--report-user-bg);
                    padding: 10px;
                    margin-bottom: 5px;
                    border-radius: 5px;
                }
                .bot {
                    background-color: var(--report-bot-bg);
                    padding: 10px;
                    margin-bottom: 5px;
                    border-radius: 5px;
                }
                .summary {
                    font-family: 'Merriweather', serif; /* A nice serif font for headers */
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 20px;
                }
                p {
                    font-family: 'Lora', serif; /* Elegant serif font for paragraphs */
                    color: var(--report-paragraph); /* Medium gray */
                }
    
            </style>
        </head>
        <body>
    """

    html_content += f"""
            <H1>Saved Conversation: {manual_name}</H1>
            <div class="metadata">
            <h3>Metadata Summary:</h3>
            <strong>Number of Chat Conversations:</strong> {num_conversations}<br>
            <strong>Timestamp Saved:</strong> {timestamp}<br>
            <strong>Priming Text:</strong> <i>{priming_text}</i><br>
            <strong>Model Selection:</strong> {model_selection}<br>
            <strong>Temperature:</strong> {temperature}<br>
            <strong>File location:</strong> {save_convo_path}/{manual_name}.json<br>
            </div>
            <hr style="border: 2px dotted lightgray; width: 100%;" />
    """
    # Add summary at the top
    if summary is not None:
        summary_html = markdown.markdown(summary)
        html_content += f"""
                        <div class="summary">SUMMARY</div>
                        <div>{summary_html}</div>
                        <hr style="border: none; border-top: 5px solid var(--divider);" />
                        <div class="header">Conversation</div>
                        <details>
                        <summary>Show/Hide the chat history</summary>
                        """
    else:
        html_content += f"""
                        <div class="header">Conversation</div>
                        <details>
                        <summary>Show/Hide the chat history</summary>
                        """

    for idx, chat in enumerate(conversation):
        # Determine background color based on the index (alternating colors)
        #background_color = "#f5f5f5" if idx % 2 == 0 else "#e6f7ff"   # Light shades for a white background (light gray, light blue )
        background_color = "#FFFFFF" if idx % 2 == 0 else "#FFFFFF"   # Light shades for a white background (light gray, light blue )
        #e5CCFF
        tmpAItext = markdown.markdown(chat['ai'])
        # Inline CSS for alternating background color
        which_convo = idx+1 

        html_content = f"""{html_content}
            <div style="background-color: {background_color}; padding: 10px; border-radius: 5px;">
                <p><strong>Chat {which_convo}:</strong></p>
                <div class="user"><p><strong><i class="fa fa-user-circle"></i> YOU: </strong> {chat['user']}</p></div>
                <div class="bot"><p><strong><i class="fa fa-robot"></i> AI: </strong> {tmpAItext}</p></div>
            </div>
            <hr style="border: none; border-top: 1px solid var(--divider);" /> 
        """

    html_content = f"""{html_content}
        </details>
        <hr style="border: none; border-top: 10px solid var(--divider);" />
        </body>
    </html>
    """
    # weasyprint.HTML(string=html_content).write_pdf("pdf_file.pdf")
    return html_content    


def render_modern_header():
    """Render the modern header with gradient background and professional navigation"""

    # Initialize navigation state if not exists
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'compare'

    # Build provider availability chips (OpenAI, Anthropic, Gemini)
    service = st.session_state.llm_service
    icon_map = {"openai": "", "anthropic": "", "google": ""}
    chips = []
    for name, cfg in service.PROVIDERS.items():
        status = "✅" if cfg.available else "❌"
        chips.append(f"<span style='background:var(--chip-bg);border:1px solid var(--chip-border);padding:0.25rem 0.6rem;border-radius:1rem;margin-right:0.35rem;color:var(--chip-fg);font-size:0.8rem;white-space:nowrap;'>{status} {icon_map.get(name,'')} {name.title()}</span>")
    chips_html = "".join(chips)

    # Render header with tighter padding and provider chips
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, var(--header-from) 0%, var(--header-to) 100%);margin: -1rem -1rem 1.2rem -1rem;padding: 1.0rem 1.25rem;border-radius: 1rem;box-shadow: 0 3px 5px rgba(0,0,0,0.08);">
            <div style="display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:0 auto;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    <div style="font-size:1.8rem;font-weight:700;color:var(--text-on-dark);font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;letter-spacing:-0.02em;">Convoscope</div>
                    <div>{chips_html}</div>
                </div>
                <div style="color:var(--text-muted-on-dark);font-size:0.88rem;font-weight:500;">Multi-Provider AI Evaluation Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation tabs (active tab styled, others clickable)
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    active = st.session_state.get('current_view', 'compare')

    def nav_tab(col, view_name, label, icon, key):
        with col:
            if active == view_name:
                st.markdown(f"<div style='background:var(--tab-active-bg);color:var(--tab-active-fg);padding:0.45rem 0.8rem;border-radius:0.5rem;font-weight:600;text-align:center'>{icon} {label}</div>", unsafe_allow_html=True)
            else:
                if st.button(f"{icon} {label}", key=key, width='stretch'):
                    st.session_state.current_view = view_name
                    st.rerun()

    nav_tab(col1, 'compare', 'Compare', '🔀', 'nav_compare')
    nav_tab(col2, 'chat', 'Chat', '💬', 'nav_chat')
    nav_tab(col3, 'history', 'History', '📚', 'nav_history')
    nav_tab(col4, 'topics', 'Topics', '🏷️', 'nav_topics')
    nav_tab(col5, 'results', 'Results', '📊', 'nav_results')


# -------------------------------------------- #
# Main app function
def main():

    # RUN SIDEBAR FIRST (to ensure provider state is updated)
    chat_settings = sidebar_configuration()

    # RENDER MODERN HEADER (after sidebar to get correct provider status)
    render_modern_header()

    # Session state is now initialized in sidebar_configuration()

    # MAIN LAYOUT: Conditional rendering based on navigation state
    current_view = st.session_state.get('current_view', 'compare')

    # Chat functionality
    if current_view == 'chat':
        st.markdown("### 💬 Chat Interface")

        if 'load_msg' in st.session_state:
            if 'success' in st.session_state.load_msg:
                st.success(st.session_state.load_msg['success'])
                # elif 'error' in st.session_state.load_msg:
                #     st.sidebar.error(st.session_state.load_msg['error'])
                # elif 'warning' in st.session_state.load_msg:
                #     st.sidebar.warning(st.session_state.load_msg['warning'])


        # CHAT INPUT 
        user_input = st.chat_input("Ask a question:", key="user_input") 
        
        # If user has JUST input a message, display it & the streaming output of the last message
        if user_input:
            # Append user's question to the conversation history
            st.session_state.conversation.append({"user": user_input, "ai": ""})

            # Increment the update counter        
            st.session_state.num_updates += 1

            # Use asyncio to stream the AI's response in real-time
            st.chat_message("user").markdown(user_input)
            asyncio.run(stream_openai_response(chat_settings, user_input))
            # st.rerun()
            skip_first = True
        else:
            skip_first = False
        
        # Display the Full conversation
        if len(st.session_state.conversation) > 0:
            ctr=0
            start_index = len(st.session_state.conversation) - 1 if not skip_first else len(st.session_state.conversation) - 2
            for i in range(start_index, -1, -1):  # Use -1 to include index 0
                if st.session_state.max_show_chats is not None: 
                    if ctr >= st.session_state.max_show_chats:
                        break
                    else:
                        ctr+=1
                        st.chat_message("user").write(st.session_state.conversation[i]['user'])
                        st.chat_message("ai").markdown(st.session_state.conversation[i]['ai'])
                else:
                    st.chat_message("user").write(st.session_state.conversation[i]['user'])
                    st.chat_message("ai").markdown(st.session_state.conversation[i]['ai'])
                st.sidebar.markdown("<hr>", unsafe_allow_html=True)

        #Auto-save conversation ever so often 
        if st.session_state.num_updates >= 1:
            st.session_state.num_updates = 0
            with open(os.path.join(save_convo_path,'restore_last_convo.json'), 'w') as f:
                json.dump(st.session_state.conversation, f)

    # Topics functionality
    elif current_view == 'topics':
        st.markdown("<h3>Topics extracted from current conversation</h3>", unsafe_allow_html=True)
        topicCols_Norm, topicCols_Reverse = st.columns([1, 1])
        orig_button_L, orig_button_R = topicCols_Norm.columns([1, 1])
        rev_button_L, rev_button_R = topicCols_Reverse.columns([1, 1])
        
        #Prepopulate the name of the conversation report to save
        if "manual_name" not in st.session_state:
            conversation_report = f"conversation_on_{datetime.now().strftime('%m-%d-%Y_%H-%M')}"
        else:
            conversation_report = f"{st.session_state.manual_name.upper()} {datetime.now().strftime('%m-%d-%Y_%H-%M')}"

        with topicCols_Norm:
            st.markdown("<h5><i>Original conversation order</i></h5>", unsafe_allow_html=True)
            if 'conversation' in st.session_state:
                orig_button_L.button("Click to summarize", key='sumOrig', on_click=lambda: st.session_state.update(topics_from_LLM=topic_extraction(st.session_state['conversation'])))

            if 'topics_from_LLM' in st.session_state:          
                # Print topics in LEFT column
                st.markdown(st.session_state['topics_from_LLM'])
                # Show "Download Summary" button (left)
                file_content = create_html_report(st.session_state['conversation'], st.session_state['topics_from_LLM'])
                orig_button_R.download_button(
                                            label="Download Summary", 
                                            key='reportOrig', 
                                            data=file_content,
                                            file_name=f"Summary - {conversation_report}.html",
                                            mime="text/html" ,
                                            type="primary"
                                        )

        with topicCols_Reverse:
            st.markdown("<h5><i>Reversed conversation order</i></h5>", unsafe_allow_html=True)
            if 'conversation' in st.session_state:
                rev_button_L.button("Click to summarize", key='sumRev', on_click=lambda: st.session_state.update(topics_from_LLM_rev=topic_extraction(st.session_state.conversation[::-1])))

            if 'topics_from_LLM_rev' in st.session_state:          
                # Print topics
                st.markdown(st.session_state['topics_from_LLM_rev'])
                # Show "Download Summary" button (right)
                file_content = create_html_report(st.session_state['conversation'], st.session_state['topics_from_LLM_rev'])
                rev_button_R.download_button(
                                            label="Download Summary", 
                                            key='reportRev', 
                                            data=file_content,
                                            file_name=f"Summary - {conversation_report} reverse.html",
                                            mime="text/html",
                                            type="primary"
                                        )

    # Compare functionality
    elif current_view == 'compare':
        render_compare_view()

    # Results viewer functionality
    elif current_view == 'results':
        render_results_view()

    # History functionality
    elif current_view == 'history':
        st.header("Conversation History")
        reverse_order = st.checkbox("Reverse order", value=False)
        # V3 - Display the full conversation history
        if 'conversation' in st.session_state:
            # Determine the conversation list based on the checkbox value
            conversation_list = (
                st.session_state.conversation[::-1] if reverse_order else st.session_state.conversation
            )
            # Display the full conversation history with alternating colors
            if conversation_list:
                for idx, chat in enumerate(conversation_list):
                    # Inline CSS for conversation formatting
                    which_convo = [idx+1 if not(reverse_order) else len(conversation_list)-idx]
                    st.markdown(
                        f"""
                        <div style="padding: 1px">
                            <strong>Conversation {str(which_convo)}:</strong><br>
                        """,unsafe_allow_html=True)
                    st.chat_message("user").write(chat['user'])
                    st.chat_message("ai").markdown(chat['ai'])
                    st.markdown(
                        f"""
                        </div>
                        <hr style="border: none; border-top: 2px solid var(--divider);" />  <!-- Divider between conversations -->
                        """,unsafe_allow_html=True)


def render_compare_view():
    """Render side-by-side model comparison with blind scoring.

    Design goals:
    - Keep it simple: single prompt -> 2–4 model responses.
    - Blind by default: label columns A/B/C/...; reveal identities on toggle.
    - JSONL logging for transparency and later analysis.
    """
    from src.experiments.compare import collect_comparisons
    from src.experiments.io import append_jsonl, RESULTS_PATH, sha256_text

    st.markdown("### 🔀 Model Comparison")

    # Default compare cache setup
    DEFAULT_COMPARE_QUESTION = "Why is the sky blue -- Explain it to a blind person."
    DEFAULT_CACHE_PATH = Path("experiments/default_compare_cache.json")
    # Gate display of results until user clicks "Run compare"
    if 'compare_show_results' not in st.session_state:
        st.session_state.compare_show_results = False

    # Slightly larger textarea font for better readability
    st.markdown("""
        <style>
            .stTextArea textarea { font-size: 1.05rem; }
        </style>
    """, unsafe_allow_html=True)

    # Lay out inputs in two columns (2/3 for prompt, 1/3 for controls)
    left, right = st.columns([2, 1])

    with left:
        # Ensure prompt state exists; preload sample prompt by default
        if 'compare_prompt' not in st.session_state:
            st.session_state.compare_prompt = DEFAULT_COMPARE_QUESTION
        prompt_text = st.text_area("Enter Prompt (sample prompt loaded by default):", key="compare_prompt", height=200)
        # Placeholder for a post-run notice (shown only after clicking Run)
        cache_notice_placeholder = st.empty()

    with right:
        blind_default = True
        # Provider/model selection (default 3)
        service = st.session_state.llm_service
        # Build list of available combos from configured providers
        available = []
        for pname, cfg in service.PROVIDERS.items():
            models = cfg.models if cfg.available else []
            for m in models:
                available.append(f"{pname}:{m}")

        # Defaults: lightest model from each vendor
        defaults = []
        for pname, m in [("openai", "gpt-4o-mini"), ("anthropic", "claude-3-haiku-20240307"), ("google", "gemini-2.5-flash")]:
            label = f"{pname}:{m}"
            if label in available:
                defaults.append(label)

        selected = st.multiselect(
            "Models to compare (2–4)",
            options=available,
            default=defaults,
            help="Choose up to 4 provider/model pairs"
        )

        blind_mode = st.checkbox("Blind scoring (hide identities)", value=blind_default, help="Show A/B/C labels until you reveal identities.")
        temperature = st.slider("Temperature", 0.0, 1.0, value=0.7, step=0.1)
        st.caption("Temperature is applied uniformly to all selected models. Note: OpenAI, Anthropic, and Gemini accept temperature; some models may clamp or ignore extreme values.")

    # If no cached results exist on first view, try to auto-generate once with defaults
    # We no longer auto-run or auto-display cached results on page load

    # Validation
    if len(selected) < 2:
        st.info("Select at least 2 models to compare.")

    # Run compare button (bottom of section)
    run_cols = st.columns([1, 1, 1])
    with run_cols[1]:
        run_clicked = st.button("Run compare", type="primary", disabled=(len(selected) < 2 or not prompt_text.strip()))

    if run_clicked:
        combos = [(s.split(":")[0], s.split(":")[1]) for s in selected]

        # Cache hit: if default prompt and cache exists, and combos+temperature match
        used_cache = False
        if (
            st.session_state.compare_prompt.strip() == DEFAULT_COMPARE_QUESTION
            and DEFAULT_CACHE_PATH.exists()
        ):
            try:
                import json as _json
                cached = _json.loads(DEFAULT_CACHE_PATH.read_text(encoding='utf-8'))
                cached_items = cached.get("result", {}).get("results", []) if isinstance(cached.get("result"), dict) else cached.get("result", [])
                cached_pairs = {(it.get("provider"), it.get("model")) for it in cached_items}
                selected_pairs = set(combos)
                # Temperature check: require all cached items to match selected temperature
                temps = {round(float(it.get("temperature", 0.7)), 3) for it in cached_items}
                temp_ok = (len(temps) == 1 and round(temperature, 3) in temps)
                if cached_pairs == selected_pairs and temp_ok:
                    # Serve cached results without re-calling providers
                    st.session_state["compare_last_run"] = {
                        **cached,
                        "blind": blind_mode,
                    }
                    st.session_state.compare_show_results = True
                    cache_notice_placeholder.info("Showing cached default comparison to avoid repeated API calls. Scores and preferences are reset; identities are blind by default.")
                    used_cache = True
                    # Optionally log a cache hit record (no duplicate results)
                    from src.experiments.io import append_jsonl as _append, RESULTS_PATH as _R, sha256_text as _sha
                    _append(_R, {
                        "version": 1,
                        "type": "cache_hit",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "run_id": cached.get("run_id"),
                        "prompt_id": _sha(DEFAULT_COMPARE_QUESTION),
                        "note": "Served from default cache",
                    })
            except Exception:
                used_cache = False

        if not used_cache:
            with st.spinner("Comparing models..."):
                result = collect_comparisons(
                    service=service,
                    prompt_text=st.session_state.compare_prompt.strip(),
                    combos=combos,
                    temperature=temperature,
                    blind=blind_mode,
                    priming_text=st.session_state.get("priming_text", "You are a helpful assistant."),
                )

        if not used_cache:
            # Persist raw results (one record per model)
            run_ts = datetime.utcnow().isoformat() + "Z"
            run_id = f"{run_ts}_adhoc"
            p_hash = sha256_text(st.session_state.compare_prompt.strip())
            for item in result["results"]:
                record = {
                    "version": 1,
                    "type": "result",
                    "timestamp": run_ts,
                    "run_id": run_id,
                    "prompt_id": p_hash,
                    "prompt_text": st.session_state.compare_prompt.strip(),
                    "blind_label": item.get("blind_label"),
                    "provider": item["provider"],
                    "model": item["model"],
                    "temperature": item["temperature"],
                    "latency_ms": item["latency_ms"],
                    "input_tokens": item["input_tokens_est"],
                    "output_tokens": item["output_tokens_est"],
                    "estimated_cost_usd": item["estimated_cost_usd"],
                    "response_text": item["response_text"],
                    "status": item["status"],
                    "error": item["error"],
                    "blind": bool(blind_mode),
                }
                append_jsonl(RESULTS_PATH, record)

            # Update session only once per run
            st.session_state["compare_last_run"] = {
                "run_id": run_id,
                "prompt_hash": p_hash,
                "prompt_text": st.session_state.compare_prompt.strip(),
                "blind": blind_mode,
                "result": result,
            }
            # Mark that results can be displayed now
            st.session_state.compare_show_results = True

            # Update default cache if this matches the default question
            if st.session_state.compare_prompt.strip() == DEFAULT_COMPARE_QUESTION:
                try:
                    import json as _json
                    DEFAULT_CACHE_PATH.write_text(_json.dumps(st.session_state["compare_last_run"], ensure_ascii=False), encoding='utf-8')
                except Exception:
                    pass
                # Show notice only after user clicks Run compare
                cache_notice_placeholder.info("Showing cached default comparison to avoid repeated API calls. Scores and preferences are reset; identities are blind by default.")

    # Display last results if present
    last = st.session_state.get("compare_last_run")
    if last and st.session_state.get("compare_show_results"):
        result = last["result"]
        reveal = st.toggle("Reveal identities", value=False)

        cols = st.columns(len(result["results"]))
        for i, item in enumerate(result["results"]):
            with cols[i]:
                label = item["blind_label"]
                title = f"### Response {label}"
                if reveal:
                    title += f" — {item['provider']}/{item['model']}"
                st.markdown(title)

                st.write(f"Latency: {item['latency_ms']} ms")
                st.write(f"Est. cost: ${item['estimated_cost_usd']}")
                st.write("")
                st.markdown(item.get("response_text") or "_(no response)_")

        st.markdown("---")
        st.markdown("#### Score the responses")
        st.caption("Blind scoring reduces bias; reveal identities after you’ve scored.")

        # Winner quick-pick
        labels = [r["blind_label"] for r in result["results"]]
        winner = st.radio("Select a winner", options=labels, horizontal=True, key="compare_winner")

        # Detailed sliders per label
        score_entries = []
        for label in labels:
            with st.expander(f"Scores for {label}"):
                s_correct = st.slider(f"{label} - Correctness", 1, 5, 3)
                s_useful = st.slider(f"{label} - Usefulness", 1, 5, 3)
                s_clarity = st.slider(f"{label} - Clarity", 1, 5, 3)
                s_safety = st.slider(f"{label} - Safety", 1, 5, 3)
                s_overall = st.slider(f"{label} - Overall", 1, 5, 3)
                note = st.text_area(f"{label} - Notes", height=60)
                score_entries.append({
                    "label": label,
                    "scores": {
                        "correctness": s_correct,
                        "usefulness": s_useful,
                        "clarity": s_clarity,
                        "safety": s_safety,
                        "overall": s_overall,
                    },
                    "notes": note,
                    "winner": (label == winner),
                })

        if st.button("Save scores", type="primary"):
            run_id = last["run_id"]
            ts = datetime.utcnow().isoformat() + "Z"
            for entry in score_entries:
                rec = {
                    "version": 1,
                    "type": "score",
                    "timestamp": ts,
                    "run_id": run_id,
                    "prompt_id": last["prompt_hash"],
                    "blind_label": entry["label"],
                    "scores": entry["scores"],
                    "notes": entry["notes"],
                    "winner": bool(entry["winner"]),
                    "scored_by": "human",
                }
                append_jsonl(RESULTS_PATH, rec)
            st.success("Scores saved.")

        # Preference mode (pairwise A/B only)
        st.markdown("---")
        st.markdown("#### Preference mode (pairwise A/B)")
        st.caption("Pick a winner for each pair. Use 'Tie/Skip' if you can't decide. Best practice: keep identities hidden while choosing.")

        # Build label -> provider/model map for logging
        label_to_combo = {r["blind_label"]: {"provider": r["provider"], "model": r["model"]} for r in result["results"]}

        # Generate all unordered label pairs
        labels = [r["blind_label"] for r in result["results"]]
        pairs = []
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                pairs.append((labels[i], labels[j]))

        pref_decisions = {}
        for a, b in pairs:
            choice = st.radio(
                label=f"{a} vs {b}",
                options=[f"{a} wins", f"{b} wins", "Tie/Skip"],
                horizontal=True,
                key=f"pref_{a}_{b}"
            )
            pref_decisions[(a, b)] = choice

        if st.button("Save preferences"):
            run_id = last["run_id"]
            ts = datetime.utcnow().isoformat() + "Z"
            saved = 0
            for (a, b), choice in pref_decisions.items():
                if choice == "Tie/Skip":
                    continue
                winner_label = a if choice.startswith(a) else b
                rec = {
                    "version": 1,
                    "type": "preference",
                    "timestamp": ts,
                    "run_id": run_id,
                    "prompt_id": last["prompt_hash"],
                    "pair": [a, b],
                    "winner_label": winner_label,
                    "left": {"label": a, **label_to_combo[a]},
                    "right": {"label": b, **label_to_combo[b]},
                    "scored_by": "human",
                }
                append_jsonl(RESULTS_PATH, rec)
                saved += 1
            if saved:
                st.success(f"Saved {saved} preference entries.")
            else:
                st.info("No preferences selected.")


def render_results_view():
    """Simple results viewer with filters and CSV export.

    - Loads experiments/results.jsonl and merges results with scores.
    - Adds prompt tags when present in experiments/prompts.yaml (by prompt hash).
    - Exports two CSVs: results_with_scores.csv and preferences.csv.
    """
    import pandas as pd
    from pathlib import Path
    from src.experiments.io import read_jsonl, RESULTS_PATH, build_prompt_index

    st.markdown("### 📊 Results Viewer")
    st.markdown("This view consolidates all comparison runs. Use the filters to narrow by date, provider/model, and prompt tags. Each row shows a single model’s response with basic metrics and any latest human score.")

    with st.spinner("Loading results..."):
        data = read_jsonl(RESULTS_PATH)
    if not data:
        st.info("No results found yet. Run a comparison first.")
        return

    # Split by record type
    df = pd.DataFrame(data)
    results_df = df[df.get("type").fillna("result") == "result"].copy()
    scores_df = df[df.get("type") == "score"].copy()
    prefs_df = df[df.get("type") == "preference"].copy()

    # Parse timestamps and normalize to naive (no tz) for consistent comparisons
    for frame in (results_df, scores_df, prefs_df):
        if not frame.empty:
            ts = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
            # drop timezone to match date input (naive)
            frame["timestamp"] = ts.dt.tz_convert(None)

    # Provider/model convenience columns
    if not results_df.empty:
        results_df["provider_model"] = results_df["provider"] + "/" + results_df["model"]

    # Add tags from prompt set index
    prompts_path = Path("experiments/prompts.yaml")
    pindex = build_prompt_index(prompts_path)
    if not results_df.empty:
        results_df["tags"] = results_df["prompt_id"].map(lambda h: pindex.get(h, {}).get("tags"))

    # Prepare defaults for filters from session state
    min_ts = results_df["timestamp"].min()
    max_ts = results_df["timestamp"].max()
    default_dates = (
        (min_ts.date() if pd.notnull(min_ts) else None),
        (max_ts.date() if pd.notnull(max_ts) else None),
    )
    date_range = st.session_state.get("results_date_range", default_dates)

    providers = sorted(results_df["provider_model"].dropna().unique().tolist())
    selected_models = st.session_state.get("results_selected_models", providers)

    all_tags = sorted({t for lst in results_df["tags"].dropna().tolist() for t in lst}) if "tags" in results_df else []
    selected_tags = st.session_state.get("results_selected_tags", all_tags)

    # Apply filters for the preview above
    if isinstance(date_range, (list, tuple)) and all(date_range):
        start_dt = pd.to_datetime(str(date_range[0]))
        end_dt = pd.to_datetime(str(date_range[1])) + pd.Timedelta(days=1)
        mask = (results_df["timestamp"] >= start_dt) & (results_df["timestamp"] < end_dt)
        results_df = results_df[mask]
    if selected_models:
        results_df = results_df[results_df["provider_model"].isin(selected_models)]
    if selected_tags:
        results_df = results_df[results_df["tags"].apply(lambda x: bool(set(selected_tags).intersection(set(x))) if isinstance(x, list) else False)]

    # Merge last score per (run_id, prompt_id, blind_label)
    if not scores_df.empty:
        scores_df = scores_df.sort_values("timestamp").groupby(["run_id", "prompt_id", "blind_label"], as_index=False).tail(1)
        merged = results_df.merge(
            scores_df[["run_id", "prompt_id", "blind_label", "scores", "notes", "winner"]],
            on=["run_id", "prompt_id", "blind_label"], how="left"
        )
    else:
        merged = results_df.copy()

    st.markdown("#### Results (preview)")
    st.caption("Columns: timestamp (when recorded), prompt_text (the question), blind_label (A/B/C used during scoring), provider_model (which model answered), latency_ms (wall‑clock time), estimated_cost_usd (based on pricing.yaml), scores/notes (your latest human rubric), winner (quick pick).")
    show_cols = [
        "timestamp", "prompt_text", "blind_label", "provider_model", "latency_ms", "estimated_cost_usd",
        "scores", "winner", "notes"
    ]
    for c in show_cols:
        if c not in merged.columns:
            merged[c] = None
    st.dataframe(merged[show_cols].sort_values("timestamp", ascending=False).head(200), width='stretch')

    # Exports
    st.markdown("---")
    st.markdown("#### Export")
    st.caption("Export your data for deeper analysis, dashboards, or sharing. results_with_scores.csv merges model outputs with your latest human scores. preferences.csv contains A/B choices for ranking methods like Elo/Bradley–Terry.")
    csv_results = merged.to_csv(index=False).encode("utf-8")
    st.download_button("Download results_with_scores.csv", csv_results, file_name="results_with_scores.csv", mime="text/csv")

    if not prefs_df.empty:
        # Ensure useful columns exist
        pref_cols = [
            "timestamp", "run_id", "prompt_id", "pair", "winner_label",
            "left", "right", "scored_by"
        ]
        for c in pref_cols:
            if c not in prefs_df.columns:
                prefs_df[c] = None
        # Flatten left/right details for export
        def flat_side(x, key):
            try:
                return x.get(key, {}).get("provider"), x.get(key, {}).get("model"), x.get(key, {}).get("label")
            except Exception:
                return None, None, None
        left_provider, left_model, left_label = zip(*prefs_df.apply(lambda r: flat_side(r, "left"), axis=1))
        right_provider, right_model, right_label = zip(*prefs_df.apply(lambda r: flat_side(r, "right"), axis=1))
        prefs_export = prefs_df.copy()
        prefs_export["left_provider"] = left_provider
        prefs_export["left_model"] = left_model
        prefs_export["left_label"] = left_label
        prefs_export["right_provider"] = right_provider
        prefs_export["right_model"] = right_model
        prefs_export["right_label"] = right_label
        prefs_export = prefs_export[[
            "timestamp", "run_id", "prompt_id", "pair", "winner_label",
            "left_provider", "left_model", "left_label",
            "right_provider", "right_model", "right_label",
            "scored_by",
        ]]
        st.dataframe(prefs_export.sort_values("timestamp", ascending=False).head(200), width='stretch')
        st.download_button("Download preferences.csv", prefs_export.to_csv(index=False).encode("utf-8"), file_name="preferences.csv", mime="text/csv")
    else:
        st.info("No preference entries yet. Save some from the Compare view.")

    # Filters (moved below the table)
    st.markdown("---")
    st.markdown("#### Filters")
    date_input = st.date_input("Date range", value=date_range, key="results_date_range")
    model_input = st.multiselect("Filter models", options=providers, default=selected_models, key="results_selected_models")
    tag_input = st.multiselect("Filter tags", options=all_tags, default=selected_tags, key="results_selected_tags")

if __name__ == "__main__":
    main()
