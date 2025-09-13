#!/usr/bin/env python3
"""
Screenshot capture script for Convoscope portfolio documentation
Automates the capture of key functionality demonstrations
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import time

# Configuration
SCREENSHOTS_DIR = Path("docs/assets/screenshots")
BASE_URL = "http://localhost:8501"
VIEWPORT_SIZE = {"width": 1920, "height": 1080}
MOBILE_VIEWPORT = {"width": 375, "height": 667}

# Ensure screenshots directory exists
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def wait_for_streamlit_ready(page):
    """Wait for Streamlit to be fully loaded"""
    try:
        # Wait for Streamlit's running indicator to appear and disappear
        await page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
        await asyncio.sleep(2)  # Additional wait for components to settle
        return True
    except Exception as e:
        print(f"Warning: Could not detect Streamlit ready state: {e}")
        return False

async def capture_main_interface(page):
    """Capture the main chat interface"""
    print("📸 Capturing main chat interface...")
    
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Wait for any dynamic content to load
    await asyncio.sleep(3)
    
    # Take full page screenshot
    await page.screenshot(
        path=SCREENSHOTS_DIR / "01-main-interface.png",
        full_page=True,
        clip={"x": 0, "y": 0, "width": 1200, "height": 800}  # Crop to main content
    )
    
    # Take hero section screenshot (for README)
    await page.screenshot(
        path=SCREENSHOTS_DIR / "01-hero-interface.png", 
        clip={"x": 0, "y": 0, "width": 1200, "height": 600}
    )
    
    print("✅ Main interface screenshots captured")

async def capture_provider_switching(page):
    """Demonstrate provider switching functionality"""
    print("📸 Capturing provider switching demo...")
    
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Look for provider selector (adjust selector based on your UI)
    provider_selectors = [
        'select[aria-label*="provider"]',
        'select[aria-label*="Provider"]', 
        'div[data-testid="stSelectbox"] select',
        '.stSelectbox select'
    ]
    
    provider_selector = None
    for selector in provider_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            provider_selector = selector
            break
        except:
            continue
    
    if provider_selector:
        # Capture initial state
        await page.screenshot(
            path=SCREENSHOTS_DIR / "02-provider-selection-initial.png",
            clip={"x": 0, "y": 0, "width": 400, "height": 300}
        )
        
        # Open dropdown
        await page.click(provider_selector)
        await asyncio.sleep(1)
        
        # Capture dropdown open
        await page.screenshot(
            path=SCREENSHOTS_DIR / "02-provider-dropdown-open.png",
            clip={"x": 0, "y": 0, "width": 400, "height": 400}
        )
        
        # Select different provider (if options available)
        options = await page.query_selector_all(f"{provider_selector} option")
        if len(options) > 1:
            await page.select_option(provider_selector, index=1)
            await asyncio.sleep(2)
            
            # Capture after selection
            await page.screenshot(
                path=SCREENSHOTS_DIR / "02-provider-switched.png",
                clip={"x": 0, "y": 0, "width": 400, "height": 300}
            )
        
        print("✅ Provider switching screenshots captured")
    else:
        print("⚠️  Could not find provider selector - manual capture needed")

async def capture_conversation_demo(page):
    """Demonstrate conversation functionality"""
    print("📸 Capturing conversation demonstration...")
    
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Look for chat input
    chat_input_selectors = [
        'input[placeholder*="message"]',
        'input[placeholder*="question"]',
        'textarea[placeholder*="message"]',
        '.stChatInput input',
        '[data-testid="stChatInput"] input'
    ]
    
    chat_input = None
    for selector in chat_input_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            chat_input = selector
            break
        except:
            continue
    
    if chat_input:
        # Type a demo message
        demo_message = "Hello! Can you explain multi-provider architecture?"
        await page.fill(chat_input, demo_message)
        
        # Capture input state
        await page.screenshot(
            path=SCREENSHOTS_DIR / "03-chat-input-ready.png",
            clip={"x": 0, "y": 50, "width": 1000, "height": 600}
        )
        
        # Submit message (look for enter key or submit button)
        await page.press(chat_input, "Enter")
        
        # Wait for response to start appearing
        await asyncio.sleep(3)
        
        # Capture streaming response
        await page.screenshot(
            path=SCREENSHOTS_DIR / "03-chat-streaming.png",
            clip={"x": 0, "y": 50, "width": 1000, "height": 700}
        )
        
        # Wait for complete response
        await asyncio.sleep(8)
        
        # Capture complete conversation
        await page.screenshot(
            path=SCREENSHOTS_DIR / "03-chat-complete.png",
            full_page=True
        )
        
        print("✅ Conversation demonstration screenshots captured")
    else:
        print("⚠️  Could not find chat input - manual capture needed")

async def capture_error_handling_demo(page):
    """Simulate and capture error handling (requires API key manipulation)"""
    print("📸 Capturing error handling demo...")
    
    # This would require manipulating environment variables or API keys
    # For now, capture the UI elements that show error states
    
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Look for any existing error indicators or status messages
    status_selectors = [
        '.stAlert',
        '.stError', 
        '.stWarning',
        '[data-testid="stAlert"]',
        '.error-message'
    ]
    
    for selector in status_selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=2000)
            if element:
                await page.screenshot(
                    path=SCREENSHOTS_DIR / f"04-error-handling-{selector.replace('[', '').replace(']', '').replace('.', '')}.png",
                    clip={"x": 0, "y": 0, "width": 800, "height": 200}
                )
        except:
            continue
    
    print("✅ Error handling UI screenshots captured")

async def capture_mobile_responsive(page):
    """Capture mobile responsive views"""
    print("📸 Capturing mobile responsive design...")
    
    # Set mobile viewport
    await page.set_viewport_size(MOBILE_VIEWPORT)
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Mobile main interface
    await page.screenshot(
        path=SCREENSHOTS_DIR / "05-mobile-interface.png",
        full_page=True
    )
    
    # Reset to desktop viewport
    await page.set_viewport_size(VIEWPORT_SIZE)
    print("✅ Mobile responsive screenshots captured")

async def main():
    """Main screenshot capture workflow"""
    print("🚀 Starting Convoscope screenshot capture...")
    print(f"📁 Screenshots will be saved to: {SCREENSHOTS_DIR}")
    print(f"🌐 Using base URL: {BASE_URL}")
    print("\n⚠️  Make sure Convoscope is running at the base URL before continuing!")
    
    # Check if the app is running
    import requests
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Convoscope detected running - proceeding with screenshot capture...")
        else:
            print("❌ Convoscope not responding - please start the app first")
            return
    except Exception as e:
        print(f"❌ Could not connect to {BASE_URL} - please start Convoscope first")
        return
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport=VIEWPORT_SIZE,
            device_scale_factor=1
        )
        
        page = await context.new_page()
        
        try:
            # Capture all screenshots
            await capture_main_interface(page)
            await capture_provider_switching(page) 
            await capture_conversation_demo(page)
            await capture_error_handling_demo(page)
            await capture_mobile_responsive(page)
            
            print("\n🎉 Screenshot capture complete!")
            print(f"📊 Check {SCREENSHOTS_DIR} for all captured images")
            
        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())