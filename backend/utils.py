"""Utility functions."""
import re
from typing import Optional

def extract_phone_number(text: str) -> Optional[str]:
    """Extract phone number from text."""
    # Italian phone number patterns
    patterns = [
        r'\b\d{10}\b',  # 10 digits
        r'\b0\d{9}\b',  # Starts with 0
        r'\b\+39\s?\d{9,10}\b',  # International format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None

def extract_name(text: str) -> Optional[str]:
    """Extract name from text (simple heuristic)."""
    # Look for patterns like "mi chiamo X" or "sono X"
    patterns = [
        r'mi chiamo\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'sono\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'chiamo\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).title()
    
    return None

def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters that might interfere
    return text.strip()




