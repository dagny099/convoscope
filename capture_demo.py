#!/usr/bin/env python3
"""
Demo capture script for Convoscope application
Creates screenshots and demo content for portfolio presentation
"""

import time
import requests
from pathlib import Path

def check_app_running(url="http://localhost:8502", timeout=30):
    """Check if Streamlit app is running and accessible."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ App is running at {url}")
                return True
        except requests.exceptions.RequestException:
            print(f"⏳ Waiting for app to be ready...")
            time.sleep(2)
    
    print(f"❌ App not accessible at {url} after {timeout} seconds")
    return False

def create_demo_assets():
    """Create demo assets for portfolio presentation."""
    
    # Ensure screenshots directory exists
    Path("demo_screenshots").mkdir(exist_ok=True)
    
    # Create placeholder screenshots with descriptions
    screenshots = [
        {
            "name": "convoscope_homepage.png",
            "description": "Main chat interface showing clean UI design and provider selection"
        },
        {
            "name": "multi_provider_demo.png", 
            "description": "Multi-provider fallback demonstration with OpenAI, Anthropic, Google"
        },
        {
            "name": "conversation_management.png",
            "description": "Conversation history and management features"
        },
        {
            "name": "error_handling_demo.png",
            "description": "Graceful error handling and provider failover"
        },
        {
            "name": "testing_output.png",
            "description": "Test suite execution showing 56 passing tests"
        },
        {
            "name": "architecture_diagram.png",
            "description": "System architecture visualization from MkDocs documentation"
        }
    ]
    
    # Create README for screenshots
    readme_content = """# Demo Screenshots and Assets

This directory contains visual demonstrations of Convoscope features and capabilities.

## Screenshots Available

"""
    
    for screenshot in screenshots:
        readme_content += f"### {screenshot['name']}\n{screenshot['description']}\n\n"
        
        # Create placeholder file with description
        placeholder_path = Path("demo_screenshots") / screenshot['name']
        with open(placeholder_path.with_suffix('.txt'), 'w') as f:
            f.write(f"Placeholder for {screenshot['name']}\n\n")
            f.write(f"Description: {screenshot['description']}\n\n")
            f.write("To capture this screenshot:\n")
            f.write("1. Ensure Streamlit app is running: streamlit run run_chat.py\n")
            f.write(f"2. Navigate to appropriate section\n")
            f.write(f"3. Capture screenshot and save as {screenshot['name']}\n")
    
    readme_content += """
## Manual Screenshot Instructions

Since automated screenshot capture requires additional dependencies, follow these steps:

### 1. Application Screenshots
```bash
# Start the application
streamlit run run_chat.py

# Navigate to http://localhost:8501
# Take screenshots of different features
```

### 2. Testing Screenshots  
```bash
# Run tests and capture output
python -m pytest tests/ -v > test_output.txt
# Screenshot the terminal output
```

### 3. Documentation Screenshots
```bash  
# Start documentation server
mkdocs serve

# Navigate to http://localhost:8000
# Screenshot key documentation pages
```

### 4. Code Structure
```bash
# Display project structure
tree src/ tests/ docs/ -I '__pycache__'
# Screenshot the terminal output  
```

## Recommended Screenshots for Portfolio

1. **Homepage**: Clean interface, provider selection dropdown
2. **Multi-Provider Demo**: Show fallback working between providers
3. **Conversation Management**: Save/load functionality
4. **Test Results**: All 56 tests passing
5. **Architecture Diagrams**: From MkDocs documentation
6. **Code Structure**: Project organization and modularity

## Creating GIFs

For animated demonstrations:
1. Use screen recording software (QuickTime on Mac, OBS, etc.)
2. Record key workflows (sending message, provider fallback)
3. Convert to GIF using online tools or ffmpeg
4. Keep file sizes reasonable for web viewing

"""
    
    with open("demo_screenshots/README.md", 'w') as f:
        f.write(readme_content)
    
    print("✅ Demo asset templates created in demo_screenshots/")
    print("📝 Check demo_screenshots/README.md for manual capture instructions")

def main():
    """Main demo capture workflow."""
    print("🔭 Convoscope Demo Capture Tool")
    print("=" * 40)
    
    # Check if app is running
    if check_app_running():
        print("✅ Streamlit app is accessible")
    else:
        print("❌ Please start the Streamlit app first:")
        print("   streamlit run run_chat.py")
        return
    
    # Create demo assets
    create_demo_assets()
    
    print("\n🎯 Next Steps:")
    print("1. Review demo_screenshots/README.md for capture instructions")
    print("2. Manually capture screenshots of key features")
    print("3. Update README.md with actual screenshot references")
    print("4. Create GIFs of key workflows for enhanced portfolio presentation")

if __name__ == "__main__":
    main()