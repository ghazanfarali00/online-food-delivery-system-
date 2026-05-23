"""
Helper utility functions for the Online Food Delivery System.
Provides password hashing, ID generation, date formatting, etc.
"""

import hashlib
import uuid
from datetime import datetime


def hash_password(password):
    """
    Hash a password using SHA-256.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password string.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """
    Verify a password against its hash.

    Args:
        password (str): Plain text password.
        password_hash (str): Stored hash to compare against.

    Returns:
        bool: True if password matches.
    """
    return hash_password(password) == password_hash


def generate_order_id():
    """
    Generate a unique order ID.

    Returns:
        str: Unique order ID in format 'FE-XXXXXXXX'.
    """
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"FE-{unique_part}"


def format_datetime(dt_string):
    """
    Format a datetime string for display.

    Args:
        dt_string (str): Datetime string from database.

    Returns:
        str: Formatted datetime string.
    """
    try:
        if isinstance(dt_string, str):
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        elif isinstance(dt_string, datetime):
            dt = dt_string
        else:
            return str(dt_string)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except (ValueError, TypeError):
        return str(dt_string) if dt_string else "N/A"


def format_date(dt_string):
    """
    Format a datetime string to show only the date.

    Args:
        dt_string (str): Datetime string from database.

    Returns:
        str: Formatted date string.
    """
    try:
        if isinstance(dt_string, str):
            dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        elif isinstance(dt_string, datetime):
            dt = dt_string
        else:
            return str(dt_string)
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return str(dt_string) if dt_string else "N/A"


def format_currency(amount):
    """
    Format a number as currency (PKR).

    Args:
        amount (float): Amount to format.

    Returns:
        str: Formatted currency string.
    """
    try:
        amount = float(amount)
        return f"Rs. {amount:,.0f}"
    except (ValueError, TypeError):
        return "Rs. 0"


def truncate_text(text, max_length=50):
    """
    Truncate text to a maximum length with ellipsis.

    Args:
        text (str): Text to truncate.
        max_length (int): Maximum length.

    Returns:
        str: Truncated text.
    """
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_star_display(rating, max_stars=5):
    """
    Get a star display string for a rating.

    Args:
        rating (float): Rating value (0-5).
        max_stars (int): Maximum number of stars.

    Returns:
        str: Star display string (e.g., '★★★★☆').
    """
    try:
        rating = float(rating)
        filled = int(round(rating))
        filled = max(0, min(filled, max_stars))
        return "★" * filled + "☆" * (max_stars - filled)
    except (ValueError, TypeError):
        return "☆" * max_stars
