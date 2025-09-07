"""Tests for utility helper functions."""

import pytest
from src.utils.helpers import get_index, image_with_aspect_ratio


class TestGetIndex:
    """Tests for get_index function."""
    
    def test_get_index_item_exists(self):
        """Test getting index of existing item."""
        test_list = ['a', 'b', 'c', 'd']
        assert get_index(test_list, 'b') == 1
        assert get_index(test_list, 'a') == 0
        assert get_index(test_list, 'd') == 3
    
    def test_get_index_item_not_exists(self):
        """Test getting index of non-existing item."""
        test_list = ['a', 'b', 'c', 'd']
        assert get_index(test_list, 'z') is None
        assert get_index(test_list, 'e') is None
    
    def test_get_index_empty_list(self):
        """Test getting index from empty list."""
        assert get_index([], 'a') is None
    
    def test_get_index_with_duplicates(self):
        """Test getting index when item appears multiple times."""
        test_list = ['a', 'b', 'a', 'd']
        # Should return first occurrence
        assert get_index(test_list, 'a') == 0
    
    def test_get_index_different_types(self):
        """Test getting index with different data types."""
        test_list = [2, 'hello', 3.14, True]  # Changed 1 to 2 to avoid True == 1
        assert get_index(test_list, 2) == 0
        assert get_index(test_list, 'hello') == 1
        assert get_index(test_list, 3.14) == 2
        assert get_index(test_list, True) == 3
        assert get_index(test_list, 'world') is None


class TestImageWithAspectRatio:
    """Tests for image_with_aspect_ratio function."""
    
    def test_image_with_default_dimensions(self):
        """Test image generation with default dimensions."""
        result = image_with_aspect_ratio("https://example.com/image.jpg")
        
        # Check that the result contains expected elements
        assert "width: 300px" in result
        assert "height: 300px" in result
        assert "https://example.com/image.jpg" in result
        assert ".image-container" in result
        assert "object-fit: contain" in result
    
    def test_image_with_custom_dimensions(self):
        """Test image generation with custom dimensions."""
        result = image_with_aspect_ratio("https://example.com/custom.jpg", width=500, height=200)
        
        assert "width: 500px" in result
        assert "height: 200px" in result
        assert "https://example.com/custom.jpg" in result
    
    def test_image_html_structure(self):
        """Test that generated HTML has proper structure."""
        result = image_with_aspect_ratio("test-url")
        
        # Check for proper HTML structure
        assert "<style>" in result
        assert "</style>" in result
        assert '<div class="image-container">' in result
        assert "</div>" in result
        assert '<img src="test-url">' in result
    
    def test_image_css_properties(self):
        """Test that CSS properties are properly included."""
        result = image_with_aspect_ratio("test-url", width=400, height=300)
        
        # Check for specific CSS properties
        assert "position: relative" in result
        assert "overflow: hidden" in result
        assert "object-fit: contain" in result
        assert "width: 100%" in result
        assert "height: 100%" in result
    
    def test_image_with_special_characters_in_url(self):
        """Test image generation with special characters in URL."""
        special_url = "https://example.com/image%20with%20spaces.jpg?param=value&other=123"
        result = image_with_aspect_ratio(special_url)
        
        assert special_url in result