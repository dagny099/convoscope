"""
Basic app loading and health integration tests for Convoscope.
"""
import pytest
from tests.integration.utils.streamlit_helpers import StreamlitTestHelper

@pytest.mark.integration
@pytest.mark.playwright
def test_app_loads_successfully(page, streamlit_app):
    """Test that the Streamlit app loads without errors."""
    helper = StreamlitTestHelper(page)
    
    # Verify app loads and title is present
    assert helper.wait_for_streamlit_ready()
    title = helper.get_page_title()
    assert "Curious and Curiouser" in title

@pytest.mark.integration
@pytest.mark.playwright
def test_main_ui_components_present(page, streamlit_app):
    """Test that main UI components are present and visible."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Check main tabs are present
    tabs = ["Chat", "Converation History", "Topics Extracted"]
    for tab in tabs:
        tab_element = page.locator(f"button[role='tab']:has-text('{tab}')")
        assert tab_element.is_visible()
    
    # Check sidebar is present
    sidebar = page.locator(".sidebar")
    assert sidebar.is_visible()
    
    # Check chat input is present
    chat_input = page.locator("[data-testid='stChatInput']")
    assert chat_input.is_visible()

@pytest.mark.integration
@pytest.mark.playwright
def test_sidebar_configuration_loads(page, streamlit_app):
    """Test that sidebar configuration options are available."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Check for key sidebar elements
    sidebar_text = page.locator(".sidebar").inner_text()
    assert "HISTORY AND SETTINGS" in sidebar_text
    assert "LLM Configuration" in sidebar_text
    
    # Check for provider selection
    provider_dropdown = page.locator(".sidebar .stSelectbox")
    assert provider_dropdown.count() > 0

@pytest.mark.integration
@pytest.mark.playwright 
def test_no_console_errors(page, streamlit_app):
    """Test that there are no critical JavaScript errors on page load."""
    # Collect console messages
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))
    
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Check for critical errors (warnings are acceptable)
    error_messages = [msg for msg in console_messages if msg.type == "error"]
    
    # Filter out known Streamlit-related non-critical errors
    critical_errors = [
        msg for msg in error_messages 
        if not any(ignore in msg.text for ignore in [
            "favicon.ico", 
            "sw.js",
            "Failed to register service worker"
        ])
    ]
    
    assert len(critical_errors) == 0, f"Found critical console errors: {[msg.text for msg in critical_errors]}"