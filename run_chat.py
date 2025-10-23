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
    'google': ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
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
    initial_sidebar_state="auto",
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
        /* Global Styles */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Modern Sidebar Styling */
        .settings-modal {
            padding: 1rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 0.75rem;
            margin-bottom: 1rem;
        }

        /* Button Enhancements */
        .stButton > button {
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
            border: none;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(100, 116, 139, 0.3);
        }

        /* Selectbox Styling */
        .stSelectbox > div > div {
            border-radius: 0.5rem;
            border: 1px solid #e2e8f0;
        }

        /* Sidebar Section Headers */
        .sidebar .markdown-text-container h4 {
            color: #374151;
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
            <h3 style="margin-top: 0; color: #1a202c; font-weight: 600;">
                <i class="fas fa-cog"></i> Settings
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Quick Actions Section
    st.sidebar.markdown("#### 🔄 Quick Actions")

    # Conversation management
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state['conversation'] = list()
            if 'user_input' in st.session_state:
                del st.session_state['user_input']
            st.success("Started new conversation")

    with col2:
        if st.button("🔀 Random", use_container_width=True):
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
                    color: #333;
                    margin-bottom: 10px;
                }
                .user {
                    background-color: #ECE4FF;
                    padding: 10px;
                    margin-bottom: 5px;
                    border-radius: 5px;
                }
                .bot {
                    background-color: #DCE1E9;
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
                    color: #5D5C61; /* Medium gray hex code */
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
                        <hr style="border: none; border-top: 5px solid #555555;" />
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
            <hr style="border: none; border-top: 1px solid #555555;" /> 
        """

    html_content = f"""{html_content}
        </details>
        <hr style="border: none; border-top: 10px solid #555555;" />
        </body>
    </html>
    """
    # weasyprint.HTML(string=html_content).write_pdf("pdf_file.pdf")
    return html_content    


def render_modern_header():
    """Render the modern header with gradient background and professional navigation"""

    # Get current provider for status chip (using correct session state key)
    current_provider = st.session_state.get('llm_provider', 'openai')
    provider_status = "✅" if st.session_state.llm_service.PROVIDERS[current_provider].available else "❌"

    # Initialize navigation state if not exists
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'chat'

    # Render header with gradient background
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
            margin: -1rem -1rem 2rem -1rem;
            padding: 1.5rem 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                ">
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: white;
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                        letter-spacing: -0.02em;
                    ">🔍 Convoscope</div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        backdrop-filter: blur(10px);
                        padding: 0.5rem 1rem;
                        border-radius: 2rem;
                        color: white;
                        font-size: 0.85rem;
                        font-weight: 500;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    ">{provider_status} {current_provider.title()}</div>
                </div>
                <div style="
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                ">
                    <div style="
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 0.9rem;
                        font-weight: 500;
                    ">Multi-Provider AI Evaluation Platform</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("💬 Chat", key="nav_chat", use_container_width=True):
            st.session_state.current_view = 'chat'
            st.rerun()

    with col2:
        if st.button("📚 History", key="nav_history", use_container_width=True):
            st.session_state.current_view = 'history'
            st.rerun()

    with col3:
        if st.button("🏷️ Topics", key="nav_topics", use_container_width=True):
            st.session_state.current_view = 'topics'
            st.rerun()

    with col4:
        comparison_text = "🔀 Compare" if not st.session_state.get('comparison_mode', False) else "🔄 Single"
        if st.button(comparison_text, key="nav_comparison", use_container_width=True):
            st.session_state.comparison_mode = not st.session_state.get('comparison_mode', False)
            st.rerun()


# -------------------------------------------- #
# Main app function
def main():

    # RUN SIDEBAR FIRST (to ensure provider state is updated)
    chat_settings = sidebar_configuration()

    # RENDER MODERN HEADER (after sidebar to get correct provider status)
    render_modern_header()

    # Session state is now initialized in sidebar_configuration()

    # MAIN LAYOUT: Conditional rendering based on navigation state
    current_view = st.session_state.get('current_view', 'chat')

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
                        <hr style="border: none; border-top: 2px solid #555555;" />  <!-- Divider between conversations -->
                        """,unsafe_allow_html=True)


if __name__ == "__main__":
    main()