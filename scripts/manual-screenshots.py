#!/usr/bin/env python3
"""
Manual screenshot capture for specific Convoscope functionality
Captures provider switching and chat interaction with more flexible selectors
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("docs/assets/screenshots")
BASE_URL = "http://localhost:8501"
VIEWPORT_SIZE = {"width": 1920, "height": 1080}

async def capture_provider_and_chat(page):
    """Capture provider selection and chat interaction"""
    print("📸 Manual capture of provider and chat functionality...")
    
    await page.goto(BASE_URL)
    await asyncio.sleep(3)  # Wait for page load
    
    # Take a full interface screenshot
    await page.screenshot(
        path=SCREENSHOTS_DIR / "02-full-interface.png",
        full_page=True
    )
    
    # Try to find and interact with any selectbox (provider selector)
    try:
        # Look for Streamlit selectbox elements more broadly
        selectboxes = await page.query_selector_all('[data-testid*="select"], [data-testid*="Select"], .stSelectbox, select')
        if selectboxes:
            print(f"Found {len(selectboxes)} potential selectors")
            
            # Click the first selectbox to open it
            await selectboxes[0].click()
            await asyncio.sleep(1)
            
            # Capture dropdown open state
            await page.screenshot(
                path=SCREENSHOTS_DIR / "02-provider-selector-open.png",
                clip={"x": 0, "y": 0, "width": 1200, "height": 800}
            )
            
            # Get the options if available
            options = await page.query_selector_all('option, [role="option"], .stSelectbox option')
            print(f"Found {len(options)} options")
            
    except Exception as e:
        print(f"Note: Could not interact with selectors: {e}")
    
    # Look for chat input more broadly  
    try:
        chat_inputs = await page.query_selector_all([
            'input[type="text"]',
            'textarea', 
            '[data-testid*="chat"]',
            '[data-testid*="input"]',
            '.stChatInput',
            '.stTextInput'
        ])
        
        if chat_inputs:
            print(f"Found {len(chat_inputs)} potential chat inputs")
            
            # Focus and type in the first suitable input
            demo_text = "Hello! Can you explain the multi-provider architecture?"
            await chat_inputs[0].fill(demo_text)
            await asyncio.sleep(1)
            
            # Capture chat input with text
            await page.screenshot(
                path=SCREENSHOTS_DIR / "03-chat-input-filled.png",
                clip={"x": 0, "y": 0, "width": 1200, "height": 600}
            )
            
            print("✅ Chat input captured")
            
    except Exception as e:
        print(f"Note: Could not interact with chat inputs: {e}")
    
    # Capture the current sidebar state (if any)
    try:
        sidebar = await page.query_selector('[data-testid="stSidebar"], .stSidebar')
        if sidebar:
            # Capture just the sidebar
            sidebar_box = await sidebar.bounding_box()
            if sidebar_box:
                await page.screenshot(
                    path=SCREENSHOTS_DIR / "06-sidebar-configuration.png",
                    clip=sidebar_box
                )
                print("✅ Sidebar configuration captured")
    except Exception as e:
        print(f"Note: Could not capture sidebar: {e}")

async def main():
    print("🔧 Manual screenshot capture for missing functionality...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=VIEWPORT_SIZE)
        page = await context.new_page()
        
        try:
            await capture_provider_and_chat(page)
            print("\n✅ Manual screenshot capture complete!")
            
        except Exception as e:
            print(f"❌ Error during manual capture: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())