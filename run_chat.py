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
    'google': ["gemini-pro", "gemini-1.5-pro"]
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

# Setup session
st.set_page_config(
    page_title="I wonder...",
    page_icon="🐇",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get help": "https://www.streamlit.io/", 
        "Report a bug": "mailto:dagny099@gmail.com", 
        "About": GET_HELP},
)

st.markdown(  #Font-Awesome icons
    '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">',
    unsafe_allow_html=True)

# ********** SETUP LAYOUT **********
titleCol1, titleCol2 = st.columns([2, 1])
tab1, tab2, tab3 = st.tabs(["Chat", "Converation History","Topics Extracted"])
headerCol1, headerCol2 = tab1.columns([2, 1])


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
    Display the sidebar configuration options for the chat
    """

    st.sidebar.markdown("<h2 style='padding: 0; margin-bottom: 10px;'> <u>HISTORY AND SETTINGS</u></h2>", unsafe_allow_html=True)

    # Load Chat History or Reset via radio button selection:
    st.sidebar.radio(
        label="CHAT HISTORY:",
        options = chat_history_options_labels, 
        key='set_convo_status',
        index=None,
        captions=chat_history_options_captions,
        on_change=choose_convo,
        label_visibility="collapsed"
    )
    #Save conversation history when you enter a name in the text box & click button:
    st.sidebar.markdown("Manually name & save this convo: ",unsafe_allow_html=True)
    val = ""
    if 'load_msg' in st.session_state:
        if st.session_state.load_msg['file'] != 'restore_last_convo.json':
            val = st.session_state.load_msg['file'].replace('.json','')
    st.sidebar.text_input(label="S", value=val, key="manual_name", label_visibility="collapsed", on_change=save_convo)  #, on_change=lambda: st.session_state.update(manual_name=)  #

    # LLM Configuration settings
    st.sidebar.markdown("<hr style='padding: 0px; margin-top: 5px;'>", unsafe_allow_html=True)
    sideC1, sideC2 = st.sidebar.columns([1, 1])
    sideC1.markdown("<h2 style='padding: 3px;'>LLM Configuration</h2>", unsafe_allow_html=True)

    # Pick a random priming message
    if "priming_text" not in st.session_state:
        st.session_state['priming_key'] = 'default'
        st.session_state['priming_text'] = priming_messages[st.session_state['priming_key']]
        st.session_state['selectbox_choice'] = st.session_state['priming_key']

    # Update priming text via button
    sideC2.button("Pick random 󠀠 󠀠:point_down: 󠀠", on_click=lambda: update_priming_text("button", new_value=random.choice(list(priming_messages.items()))))
    # Update priming text via typing into box
    st.sidebar.text_area(":rainbow[Prime the model with this message:]",  height=125, key="priming_text")
    # Update priming text via selecting from a dropdown menu
    st.sidebar.selectbox("Choose a priming message", 
                        options=list(priming_messages.keys()), 
                        key="selectbox_choice", 
                        index=get_index(list(priming_messages.keys()), st.session_state.priming_key), 
                        on_change=update_priming_text, # Pass the source and the new value
                        )  

    # Temperature setting
    if "temperature" not in st.session_state:
        value = 0.7
    else:
        value = st.session_state.temperature
    st.sidebar.slider("Predictablility of Responses (0: consistent, 1: varied)", min_value=0.0, max_value=1.0, step=0.1, format="%.1f", value=value, key="temperature")

    # LLM Provider selection - use dynamic providers
    dynamic_providers = get_providers_dict()
    available_provider_names = list(dynamic_providers.keys())
    
    # Set default provider to first available one
    if "llm_provider" not in st.session_state:
        # Try to default to 'openai' if available, otherwise first available
        if 'openai' in dynamic_providers:
            st.session_state.llm_provider = 'openai'
        else:
            # Get the clean provider name (remove "(API key needed)" suffix)
            clean_names = [name.split(' (')[0] for name in available_provider_names]
            st.session_state.llm_provider = clean_names[0] if clean_names else 'openai'
    
    # Get current provider index
    clean_current_provider = st.session_state.llm_provider.split(' (')[0]
    provider_index = 0
    for i, provider_name in enumerate(available_provider_names):
        if provider_name.startswith(clean_current_provider):
            provider_index = i
            break
    
    selected_provider_display = st.sidebar.selectbox(
        label="Choose a provider", 
        options=available_provider_names, 
        index=provider_index, 
        key="provider_display"
    )
    
    # Clean the provider name for internal use
    st.session_state.llm_provider = selected_provider_display.split(' (')[0]
    
    # Show provider status
    llm_service = st.session_state.llm_service
    if st.session_state.llm_provider in llm_service.PROVIDERS:
        provider_config = llm_service.PROVIDERS[st.session_state.llm_provider]
        if provider_config.available:
            st.sidebar.success(f"✅ {st.session_state.llm_provider.title()} is ready")
        else:
            st.sidebar.warning(f"⚠️ {st.session_state.llm_provider.title()} needs API key: {provider_config.env_key}")
    
    # Model selection - get models for the selected provider
    available_models = llm_service.get_available_models(st.session_state.llm_provider)
    if not available_models:
        available_models = dynamic_providers.get(selected_provider_display, ["No models available"])
    
    # Set default model - prioritize gpt-4o-mini for OpenAI
    if "selected_model" not in st.session_state or st.session_state.selected_model not in available_models:
        if st.session_state.llm_provider == 'openai' and 'gpt-4o-mini' in available_models:
            st.session_state.selected_model = 'gpt-4o-mini'
        else:
            st.session_state.selected_model = available_models[0] if available_models else "No models available"
    
    # Model selection dropdown
    model_index = 0
    if st.session_state.selected_model in available_models:
        model_index = available_models.index(st.session_state.selected_model)
    
    st.sidebar.selectbox(
        label="Choose a model", 
        options=available_models, 
        index=model_index, 
        key="selected_model"
    )

    # ------------ INTERACTIVE ELEMENTS ON THE PAGE ------------  #
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.subheader("Interactive Elements")

    # Limit the number of chats shown on screen
    if "max_show_chats" not in st.session_state:
        st.session_state.max_show_chats = None
    tmp = st.sidebar.number_input("Limit maximum # chats displayed", min_value=1, max_value=None, value=st.session_state.max_show_chats)
    st.session_state.max_show_chats = tmp

    # Edit the image
    if "where_image" not in st.session_state:  # Image location for the page header
        # st.session_state.where_image = "https://www.barbhs.com/assets/images/bio-photo-1.jpg"
        # st.session_state.where_image = "https://upload.wikimedia.org/wikipedia/commons/e/ec/Down_the_Rabbit_Hole.png"
        # st.session_state.where_image = "https://jeffersonairplane.com/wp-content/uploads/2020/02/Timekeeper-804x1024.jpg"
        st.session_state.where_image = "https://www.barbhs.com/assets/images/swirl_barb_logo.png"
    tmp = st.sidebar.text_input("Header image:", value=st.session_state.where_image)
    st.session_state.where_image = tmp

    # TODO this doesn't really seem necessary anymore; refactor
    # Aggregate chat settings to return to the main function 
    chat_settings = {
            "llm_provider": st.session_state.llm_provider,
            "selected_model": st.session_state.selected_model,
            "temperature": st.session_state.temperature,
            "priming_text": st.session_state.priming_text,
        }

    # Show Session State
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    with st.sidebar.expander("Show session state:", expanded=False):
        st.write(st.session_state)

    return chat_settings


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


# -------------------------------------------- #
# Main app function
def main():

    # RUN SIDEBAR
    chat_settings = sidebar_configuration()

    # STATEFUL CONVERSATION HANDLING
    if "conversation" not in st.session_state:
        st.session_state['conversation'] = list()

    titleCol1.title("Curious and Curiouser")
    headerCol1.subheader("Down the rabbit hole:")
    
    # DISPLAY TITLE & IMAGE
    titleCol2.markdown(image_with_aspect_ratio(st.session_state['where_image'], width=400, height=200), unsafe_allow_html=True)

    # MAIN LAYOUT: Tab 1 has chat convo, Tab 2 has reversable convo, Tab 3 is for topic summary

    # Tab 1: Chat functionality
    with tab1:
        if 'load_msg' in st.session_state:
            with headerCol2:
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

    # Tab 3: Display topic summary
    with tab3:
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

    # Tab 2: Running list of conversation history
    with tab2:
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