from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def get_first_image(content):
    """Extract the first image URL from HTML content"""
    if not content:
        return None
    
    # Try to find img tag with regex
    # Look for <img> tags and extract src attribute
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    match = re.search(img_pattern, content, re.IGNORECASE)
    
    if match:
        return match.group(1)
    
    return None

@register.filter
def has_image(post):
    """Check if post has any image (featured or embedded)"""
    if post.featured_image:
        return True
    
    first_image = get_first_image(post.content)
    return first_image is not None