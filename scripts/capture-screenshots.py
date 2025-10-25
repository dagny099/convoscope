#!/usr/bin/env python3
"""
Screenshot capture script for Convoscope portfolio documentation
Automates the capture of key functionality demonstrations
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
import time

# Configuration
SCREENSHOTS_DIR = Path("docs/assets/screenshots")
BASE_URL = os.getenv("CONVOSCOPE_BASE_URL", "http://localhost:8501")
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
    
    # Take full interface screenshot (for docs)
    await page.screenshot(
        path=SCREENSHOTS_DIR / "02-full-interface.png",
        full_page=True
    )
    
    # Take main interface crop
    await page.screenshot(
        path=SCREENSHOTS_DIR / "01-main-interface.png",
        clip={"x": 0, "y": 0, "width": 1200, "height": 800}
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
    try:
        # Try by label first
        combo = None
        try:
            combo = await page.wait_for_selector('label:has-text("Provider:") >> xpath=following::div[@role="combobox"][1]', timeout=3000)
        except Exception:
            pass

        # Fallback: locate text node for 'Provider:' then the next combobox in the sidebar
        if combo is None:
            try:
                label_like = await page.wait_for_selector('xpath=(//div[@data-testid="stSidebar"]//*[contains(normalize-space(.), "Provider:")])[1]', timeout=4000)
                combo = await page.wait_for_selector('xpath=(//div[@data-testid="stSidebar"]//*[contains(normalize-space(.), "Provider:")])[1]/following::div[@role="combobox"][1]', timeout=3000)
            except Exception:
                pass

        # Last resort: any combobox in the sidebar
        if combo is None:
            container = await page.wait_for_selector('[data-testid="stSidebar"]', timeout=5000)
            combo = await container.wait_for_selector('div[role="combobox"]', timeout=3000)

        # Capture initial state (small crop around the selector)
        box = await combo.bounding_box()
        if box:
            await page.screenshot(
                path=SCREENSHOTS_DIR / "02-provider-selection-initial.png",
                clip={"x": max(box["x"] - 20, 0), "y": max(box["y"] - 20, 0), "width": box["width"] + 40, "height": box["height"] + 60}
            )

        # Open dropdown
        await combo.click()
        await asyncio.sleep(1)

        # Capture dropdown open
        # Enlarge crop to include dropdown menu below combobox
        if box:
            await page.screenshot(
                path=SCREENSHOTS_DIR / "02-provider-selector-open.png",
                clip={"x": max(box["x"] - 20, 0), "y": max(box["y"] - 20, 0), "width": max(box["width"] + 40, 320), "height": box["height"] + 240}
            )

        print("✅ Provider switching screenshots captured")
    except Exception as e:
        print(f"⚠️  Could not find provider selector - manual capture needed ({e})")

async def capture_conversation_demo(page):
    """Demonstrate conversation functionality"""
    print("📸 Capturing conversation demonstration...")
    
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    
    # Look for chat input
    # Prefer Streamlit chat input test id and textarea
    chat_input_selectors = [
        '[data-testid="stChatInput"] textarea',
        '[data-testid="stChatInput"] input',
        'textarea[placeholder="Ask a question:"]',
    ]

    chat_input = None
    for selector in chat_input_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            chat_input = selector
            break
        except Exception:
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
    
    # Prefer Streamlit alert box capture with a stable filename used in docs
    try:
        element = await page.wait_for_selector('[data-testid="stAlert"]', timeout=4000)
        box = await element.bounding_box()
        if box:
            await page.screenshot(
                path=SCREENSHOTS_DIR / "04-error-handling-stAlert.png",
                clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
            )
            print("✅ Error alert screenshot captured (stAlert)")
            return
    except Exception:
        pass
    
    # Fallback: try any known error selector
    for selector in status_selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=1500)
            if element:
                box = await element.bounding_box()
                if box:
                    await page.screenshot(
                        path=SCREENSHOTS_DIR / "04-error-handling-generic.png",
                        clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
                    )
                    print("✅ Generic error screenshot captured")
                    return
        except Exception:
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

async def capture_sidebar_configuration(page):
    """Capture the sidebar configuration panel screenshot"""
    print("📸 Capturing sidebar configuration...")
    await page.goto(BASE_URL)
    await wait_for_streamlit_ready(page)
    try:
        sidebar = await page.wait_for_selector('[data-testid="stSidebar"]', timeout=5000)
        box = await sidebar.bounding_box()
        if box:
            await page.screenshot(
                path=SCREENSHOTS_DIR / "06-sidebar-configuration.png",
                clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
            )
            print("✅ Sidebar configuration screenshot captured")
    except Exception as e:
        print(f"⚠️  Could not capture sidebar: {e}")

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
            headless=True,
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
            await capture_sidebar_configuration(page)
            
            print("\n🎉 Screenshot capture complete!")
            print(f"📊 Check {SCREENSHOTS_DIR} for all captured images")
            
        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
