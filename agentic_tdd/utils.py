"""
Utility functions for the agentic-tdd system.
"""
import re
from pathlib import Path
from typing import Optional


def extract_kata_name(kata_content: str) -> str:
    """Extract a meaningful name from the kata content."""
    # Try to find a title in the first few lines
    lines = kata_content.strip().split('\n')[:10]  # Check first 10 lines
    
    for line in lines:
        # Look for a title (line starting with #)
        if line.strip().startswith('#'):
            title = line.strip().lstrip('#').strip()
            # Clean up the title to make it a valid Python module name
            # Remove special characters and spaces, convert to lowercase
            clean_title = re.sub(r'[^a-zA-Z0-9_]', '_', title)
            # Remove multiple underscores
            clean_title = re.sub(r'_+', '_', clean_title)
            # Remove leading/trailing underscores
            clean_title = clean_title.strip('_').lower()
            
            # If we have a meaningful name, return it
            if clean_title and len(clean_title) > 2:
                return clean_title
    
    # If no title found, try to extract from the first line
    if lines:
        first_line = lines[0].strip()
        if first_line:
            # Clean up the first line to make it a valid Python module name
            clean_title = re.sub(r'[^a-zA-Z0-9_]', '_', first_line)
            clean_title = re.sub(r'_+', '_', clean_title)
            clean_title = clean_title.strip('_').lower()
            
            if clean_title and len(clean_title) > 2:
                return clean_title
    
    # Default fallback
    return "kata_solution"


def generate_module_name(kata_content: str) -> str:
    """Generate a Python module name based on the kata content."""
    base_name = extract_kata_name(kata_content)
    
    # Ensure it's a valid Python identifier
    if not base_name[0].isalpha():
        base_name = "kata_" + base_name
    
    # Make sure it's not a Python keyword
    python_keywords = {
        'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
        'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'with', 'yield'
    }
    
    if base_name in python_keywords:
        base_name = base_name + "_module"
    
    return base_name


def generate_test_module_name(kata_content: str) -> str:
    """Generate a test module name based on the kata content."""
    module_name = generate_module_name(kata_content)
    return f"test_{module_name}"
