"""General utility helper functions for Convoscope."""

from typing import List, Any, Optional


def get_index(orig_list: List[Any], item: Any) -> Optional[int]:
    """
    Get the index of an item in a list if it exists.
    
    Args:
        orig_list: List to search in
        item: Item to find
        
    Returns:
        Index of item if found, None otherwise
    """
    try:
        return orig_list.index(item)
    except ValueError:
        return None


def image_with_aspect_ratio(image_url: str, width: int = 300, height: int = 300) -> str:
    """
    Generate HTML/CSS for displaying an image with a fixed aspect ratio.
    
    Args:
        image_url: URL of the image to display
        width: Width in pixels
        height: Height in pixels
        
    Returns:
        HTML string with embedded CSS for the image container
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