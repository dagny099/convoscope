"""
Shared fixtures and configuration for integration tests.
"""
import os
import pytest
import subprocess
import time
from pathlib import Path
from threading import Thread
import tempfile
import shutil

@pytest.fixture(scope="session")
def streamlit_app():
    """Start Streamlit app for testing and return the URL."""
    # Use a test port to avoid conflicts
    test_port = "8502"
    app_file = Path(__file__).parent.parent.parent / "run_chat.py"
    
    # Create temporary conversation history directory for tests
    test_conv_dir = tempfile.mkdtemp(prefix="convoscope_test_")
    
    # Set environment variables for testing
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = test_port
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["OPENAI_API_KEY"] = "test-key-for-integration-testing"  # Set dummy API key
    
    # Start Streamlit app
    process = subprocess.Popen(
        [
            "streamlit", "run", str(app_file), 
            "--server.port", test_port, 
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--server.allowRunOnSave", "false"
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    url = f"http://localhost:{test_port}"
    max_wait = 45  # Increased wait time
    wait_time = 0
    
    print(f"Starting Streamlit app at {url}")
    
    while wait_time < max_wait:
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Streamlit app ready after {wait_time} seconds")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)  # Check every 2 seconds
        wait_time += 2
    
    if wait_time >= max_wait:
        # Print process output for debugging
        stdout, stderr = process.communicate(timeout=5)
        print(f"Streamlit stdout: {stdout.decode()}")
        print(f"Streamlit stderr: {stderr.decode()}")
        process.kill()
        raise RuntimeError(f"Streamlit app failed to start within {max_wait} seconds")
    
    yield {"url": url, "conversation_dir": test_conv_dir}
    
    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=10)
    except:
        process.kill()
    shutil.rmtree(test_conv_dir, ignore_errors=True)

@pytest.fixture
def page(playwright, streamlit_app):
    """Create a new browser page for each test."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate to the Streamlit app
    page.goto(streamlit_app["url"], wait_until="networkidle", timeout=30000)
    
    # Wait for Streamlit to fully load - look for the main container
    page.wait_for_selector("[data-testid='stApp']", timeout=15000)
    
    yield page
    
    context.close()
    browser.close()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "choices": [{
            "message": {
                "content": "This is a test response from the AI assistant."
            }
        }]
    }