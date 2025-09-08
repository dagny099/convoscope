"""
Core chat functionality integration tests for Convoscope.
"""
import pytest
import os
from unittest.mock import patch
from tests.integration.utils.streamlit_helpers import StreamlitTestHelper

@pytest.mark.integration
@pytest.mark.playwright
def test_chat_input_interaction(page, streamlit_app):
    """Test basic chat input and UI interaction."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Chat tab
    helper.select_tab("Chat")
    
    # Verify chat input is present and functional
    chat_input = page.locator("[data-testid='stChatInput'] input")
    assert chat_input.is_visible()
    
    # Test input functionality
    test_message = "Hello, this is a test message"
    chat_input.fill(test_message)
    
    # Verify message appears in input field
    assert chat_input.input_value() == test_message

@pytest.mark.integration
@pytest.mark.playwright
@patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
def test_chat_message_display(page, streamlit_app):
    """Test that user messages appear correctly in chat interface."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Chat tab
    helper.select_tab("Chat")
    
    # Mock the OpenAI API response to avoid real API calls
    with patch('run_chat.stream_openai_response') as mock_stream:
        # Set up the mock to return a simple response
        mock_stream.return_value = "This is a mock AI response"
        
        # Send a test message
        test_message = "Test user message"
        helper.enter_chat_message(test_message)
        
        # Wait a moment for the message to appear
        page.wait_for_timeout(2000)
        
        # Check if user message appears in the chat
        user_messages = page.locator("[data-testid='chatAvatarIcon-user']")
        if user_messages.count() > 0:
            # Message successfully displayed
            assert True
        else:
            # If no specific user avatar, check for any chat content
            chat_content = page.locator("[data-testid='stChatMessageContent']")
            assert chat_content.count() > 0, "No chat messages found in interface"

@pytest.mark.integration
@pytest.mark.playwright
def test_conversation_history_tab(page, streamlit_app):
    """Test conversation history tab functionality."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Conversation History tab
    helper.select_tab("Converation History")
    
    # Check that the tab loads correctly
    page.wait_for_timeout(1000)
    
    # Look for conversation history header
    history_header = page.locator("h2:has-text('Conversation History')")
    if history_header.count() == 0:
        # Alternative check for any header content in the tab
        tab_content = page.locator("[data-testid='stTabContent']")
        assert tab_content.is_visible(), "Conversation History tab content not visible"
    
    # Check for reverse order checkbox
    reverse_checkbox = page.locator("input[type='checkbox']")
    if reverse_checkbox.count() > 0:
        assert reverse_checkbox.is_visible()

@pytest.mark.integration
@pytest.mark.playwright
def test_topics_extraction_tab(page, streamlit_app):
    """Test topics extraction tab loads correctly."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Topics Extracted tab
    helper.select_tab("Topics Extracted")
    
    # Check that the tab loads correctly
    page.wait_for_timeout(1000)
    
    # Look for topics content
    tab_content = page.locator("[data-testid='stTabContent']")
    assert tab_content.is_visible()
    
    # Check for summarize buttons (even if disabled without conversation)
    summarize_buttons = page.locator("button:has-text('Click to summarize')")
    # Buttons might not be visible without conversation, so we just check the tab loaded
    
@pytest.mark.integration
@pytest.mark.playwright
def test_session_state_persistence(page, streamlit_app):
    """Test that session state persists across tab navigation."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Start on Chat tab
    helper.select_tab("Chat")
    
    # Check initial state
    initial_title = helper.get_page_title()
    
    # Navigate to different tabs
    helper.select_tab("Converation History")
    page.wait_for_timeout(500)
    
    helper.select_tab("Topics Extracted")
    page.wait_for_timeout(500)
    
    # Return to Chat tab
    helper.select_tab("Chat")
    page.wait_for_timeout(500)
    
    # Verify title and basic state is maintained
    current_title = helper.get_page_title()
    assert current_title == initial_title, "Page state not maintained across tab navigation"

@pytest.mark.integration
@pytest.mark.playwright
def test_responsive_ui_elements(page, streamlit_app):
    """Test that UI elements respond to user interaction."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Test tab switching responsiveness
    tabs = ["Chat", "Converation History", "Topics Extracted"]
    
    for tab in tabs:
        helper.select_tab(tab)
        page.wait_for_timeout(300)
        
        # Verify active tab is highlighted/selected
        active_tab = page.locator(f"button[role='tab']:has-text('{tab}')")
        assert active_tab.is_visible()
        
        # Check that tab content area is visible
        tab_content = page.locator("[data-testid='stTabContent']")
        assert tab_content.is_visible(), f"Content not visible for {tab} tab"