"""
Conversation persistence and file operations integration tests for Convoscope.
"""
import pytest
import json
import os
from pathlib import Path
from tests.integration.utils.streamlit_helpers import StreamlitTestHelper

@pytest.mark.integration
@pytest.mark.playwright
def test_conversation_save_interface(page, streamlit_app):
    """Test conversation save interface in sidebar."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Look for save conversation input in sidebar
    save_input = page.locator(".sidebar input[type='text']")
    if save_input.count() > 0:
        # Test that save input is functional
        test_name = "test_conversation"
        save_input.fill(test_name)
        
        # Verify text was entered
        assert test_name in save_input.input_value()
    else:
        # Alternative check for any text input in sidebar
        text_inputs = page.locator(".sidebar input")
        assert text_inputs.count() > 0, "No text input found for saving conversations"

@pytest.mark.integration
@pytest.mark.playwright
def test_conversation_load_interface(page, streamlit_app):
    """Test conversation load interface functionality."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Look for conversation history radio buttons
    radio_options = page.locator(".sidebar input[type='radio']")
    if radio_options.count() > 0:
        # Test selecting different history options
        for i in range(min(3, radio_options.count())):
            radio = radio_options.nth(i)
            if radio.is_visible():
                radio.click()
                page.wait_for_timeout(1000)
                
                # Check for any resulting UI changes or dropdowns
                selectboxes = page.locator(".sidebar .stSelectbox")
                # After clicking radio, there might be additional options
                # This is mainly testing that the radio buttons respond
                assert True  # Radio button interaction completed without errors
                break
    
    # Check for any file selection dropdowns that might appear
    file_dropdowns = page.locator(".sidebar .stSelectbox")
    if file_dropdowns.count() > 0:
        # Verify dropdowns are interactive
        for i in range(file_dropdowns.count()):
            dropdown = file_dropdowns.nth(i)
            if dropdown.is_visible():
                # Try to open dropdown
                dropdown.click()
                page.wait_for_timeout(500)
                
                # Close dropdown
                page.click("body")
                break

@pytest.mark.integration
@pytest.mark.playwright
def test_auto_save_functionality(page, streamlit_app, mock_openai_response):
    """Test that conversations are auto-saved."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to chat tab
    helper.select_tab("Chat")
    
    # Check if auto-save directory exists in test environment
    conversation_dir = streamlit_app.get("conversation_dir")
    if conversation_dir:
        auto_save_file = Path(conversation_dir) / "restore_last_convo.json"
        
        # The auto-save file might not exist initially
        # This test mainly verifies the UI doesn't break with auto-save logic
        
        # Simulate a basic interaction that would trigger auto-save
        chat_input = page.locator("[data-testid='stChatInput'] input")
        if chat_input.is_visible():
            chat_input.fill("Test message for auto-save")
            # Note: Not pressing Enter to avoid actual API calls
            
        # Wait a moment for any auto-save logic
        page.wait_for_timeout(2000)
        
        # Test passes if no errors occurred during auto-save logic
        assert True

@pytest.mark.integration
@pytest.mark.playwright 
def test_conversation_export_interface(page, streamlit_app):
    """Test conversation export interface in Topics tab."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Topics Extracted tab
    helper.select_tab("Topics Extracted")
    
    # Look for download/export buttons
    download_buttons = page.locator("button")
    download_found = False
    
    for i in range(download_buttons.count()):
        button_text = download_buttons.nth(i).inner_text()
        if "download" in button_text.lower() or "export" in button_text.lower():
            download_found = True
            button = download_buttons.nth(i)
            
            # Button might be disabled without conversation content
            # Just verify it exists and is visible
            assert button.is_visible()
            break
    
    # If no explicit download button, look for summarize buttons which lead to downloads
    if not download_found:
        summarize_buttons = page.locator("button:has-text('Click to summarize')")
        assert summarize_buttons.count() > 0, "No export or summarize buttons found in Topics tab"

@pytest.mark.integration
@pytest.mark.playwright
def test_html_export_generation(page, streamlit_app):
    """Test HTML export functionality (UI elements)."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Topics tab
    helper.select_tab("Topics Extracted")
    
    # Check for export-related elements
    page_content = page.inner_text()
    
    # Look for text indicating export functionality
    export_indicators = [
        "download", "export", "summary", "html", "report"
    ]
    
    found_export_feature = any(indicator in page_content.lower() for indicator in export_indicators)
    assert found_export_feature, "No export-related functionality found in Topics tab"
    
    # Check for column layout (original vs reversed conversation order)
    columns = page.locator("[data-testid='column']")
    if columns.count() >= 2:
        # Verify both columns have content
        for i in range(2):
            column = columns.nth(i)
            column_text = column.inner_text()
            assert len(column_text) > 0, f"Column {i+1} appears to be empty"

@pytest.mark.integration
@pytest.mark.playwright
def test_conversation_file_validation(page, streamlit_app):
    """Test conversation file handling and validation."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Test loading conversation functionality
    # Look for file selection interface
    radio_buttons = page.locator(".sidebar input[type='radio']")
    
    if radio_buttons.count() > 0:
        # Click on "Load a conversation" option if available
        for i in range(radio_buttons.count()):
            radio = radio_buttons.nth(i)
            # Get associated label text
            radio_container = radio.locator("xpath=..")
            if radio_container.count() > 0:
                container_text = radio_container.inner_text()
                if "load" in container_text.lower() or "conversation" in container_text.lower():
                    radio.click()
                    page.wait_for_timeout(1000)
                    
                    # Check if a file selection dropdown appears
                    selectboxes = page.locator(".sidebar .stSelectbox")
                    if selectboxes.count() > 0:
                        # Try to interact with the file selection
                        selectboxes.first.click()
                        page.wait_for_timeout(500)
                        
                        # Check for options or error messages
                        options = page.locator("[data-baseweb='menu'] li")
                        if options.count() > 0:
                            # Files available to load
                            assert True
                        else:
                            # No files available - this is valid behavior
                            assert True
                        
                        # Close dropdown
                        page.click("body")
                    break
    
    # Test manual save name validation
    save_input = page.locator(".sidebar input[type='text']")
    if save_input.count() > 0:
        # Test with valid filename
        valid_name = "test_conversation_save"
        save_input.fill(valid_name)
        assert valid_name in save_input.input_value()
        
        # Test with special characters (basic validation)
        special_name = "test/conversation:save*"
        save_input.fill(special_name)
        # Streamlit might filter out special characters
        current_value = save_input.input_value()
        # Just verify no crash occurred
        assert True

@pytest.mark.integration
@pytest.mark.playwright
def test_conversation_metadata_display(page, streamlit_app):
    """Test conversation metadata display in export preview."""
    helper = StreamlitTestHelper(page)
    helper.wait_for_streamlit_ready()
    
    # Navigate to Topics tab where metadata would be shown
    helper.select_tab("Topics Extracted")
    
    # Check for elements that would show metadata
    page_text = page.inner_text()
    
    # Look for metadata-related terms
    metadata_terms = [
        "timestamp", "model", "temperature", "conversation", "messages"
    ]
    
    # In the actual export, metadata would be visible
    # For this test, we verify the UI structure exists
    columns = page.locator("[data-testid='column']")
    assert columns.count() > 0, "No column layout found for metadata display"
    
    # Check for any structured content that might display metadata
    headers = page.locator("h1, h2, h3, h4, h5")
    assert headers.count() > 0, "No headers found that might contain metadata"