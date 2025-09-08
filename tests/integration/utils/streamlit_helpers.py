"""
Streamlit-specific test utilities for Playwright integration tests.
"""
import time
from playwright.sync_api import Page, expect

class StreamlitTestHelper:
    """Helper class for interacting with Streamlit components in tests."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def wait_for_streamlit_ready(self, timeout=30000):
        """Wait for Streamlit to be fully loaded and ready."""
        # Wait for the main title to appear
        self.page.wait_for_selector("h1", timeout=timeout)
        
        # Wait for any loading indicators to disappear
        try:
            self.page.wait_for_selector("[data-testid='stSpinner']", state="hidden", timeout=5000)
        except:
            pass  # Spinner might not be present
        
        return True
    
    def select_tab(self, tab_name: str):
        """Select a tab by its text content."""
        tab_selector = f"button[role='tab']:has-text('{tab_name}')"
        self.page.click(tab_selector)
        self.page.wait_for_timeout(500)  # Brief wait for tab content to load
    
    def enter_chat_message(self, message: str):
        """Enter a message in the chat input field."""
        # Look for the chat input field
        chat_input = self.page.locator("[data-testid='stChatInput'] input")
        chat_input.fill(message)
        chat_input.press("Enter")
    
    def wait_for_chat_response(self, timeout=15000):
        """Wait for a chat response to appear."""
        # Wait for AI response to appear in chat
        self.page.wait_for_selector("[data-testid='chatAvatarIcon-assistant']", timeout=timeout)
    
    def get_chat_messages(self):
        """Get all chat messages from the conversation."""
        messages = []
        
        # Get all chat message containers
        message_containers = self.page.locator("[data-testid='chat-message']").all()
        
        for container in message_containers:
            # Determine if it's user or assistant message
            avatar = container.locator("[data-testid='chatAvatarIcon-user']")
            if avatar.count() > 0:
                role = "user"
            else:
                role = "assistant"
            
            # Get message text
            text = container.locator("[data-testid='stChatMessageContent']").inner_text()
            messages.append({"role": role, "content": text})
        
        return messages
    
    def select_sidebar_option(self, option_text: str):
        """Select an option from the sidebar."""
        sidebar_option = self.page.locator(f".sidebar button:has-text('{option_text}')")
        sidebar_option.click()
        self.page.wait_for_timeout(500)
    
    def fill_sidebar_input(self, placeholder: str, value: str):
        """Fill a sidebar input field by its placeholder text."""
        input_field = self.page.locator(f".sidebar input[placeholder*='{placeholder}']")
        input_field.fill(value)
    
    def select_dropdown_option(self, dropdown_label: str, option_value: str):
        """Select an option from a selectbox dropdown."""
        # Click on the selectbox to open it
        selectbox = self.page.locator(f"label:has-text('{dropdown_label}') + div .stSelectbox")
        selectbox.click()
        
        # Select the option
        option = self.page.locator(f"[data-value='{option_value}']")
        option.click()
    
    def click_button(self, button_text: str):
        """Click a button by its text content."""
        button = self.page.locator(f"button:has-text('{button_text}')")
        button.click()
    
    def wait_for_success_message(self, timeout=5000):
        """Wait for a success message to appear."""
        self.page.wait_for_selector("[data-testid='stAlert'][data-baseweb='notification']", timeout=timeout)
    
    def get_page_title(self):
        """Get the main page title."""
        return self.page.locator("h1").inner_text()
    
    def is_element_visible(self, selector: str):
        """Check if an element is visible."""
        try:
            element = self.page.locator(selector)
            return element.is_visible()
        except:
            return False
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)