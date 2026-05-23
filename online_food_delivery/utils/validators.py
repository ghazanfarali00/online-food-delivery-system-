"""
Input validation utilities for the Online Food Delivery System.
All validation functions raise ValidationError on failure.
"""

import re
from utils.exceptions import ValidationError
from config import (
    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MIN_NAME_LENGTH, MAX_NAME_LENGTH,
    MIN_PRICE, MAX_PRICE, MAX_QUANTITY,
    PHONE_PATTERN, EMAIL_PATTERN
)


def validate_email(email):
    """
    Validate email format.

    Args:
        email (str): Email address to validate.

    Returns:
        str: Cleaned email address.

    Raises:
        ValidationError: If email format is invalid.
    """
    if not email or not email.strip():
        raise ValidationError("Email is required", field="Email")
    email = email.strip().lower()
    if not re.match(EMAIL_PATTERN, email):
        raise ValidationError("Invalid email format", field="Email")
    return email


def validate_phone(phone):
    """
    Validate phone number format (Pakistani format supported).

    Args:
        phone (str): Phone number to validate.

    Returns:
        str: Cleaned phone number.

    Raises:
        ValidationError: If phone format is invalid.
    """
    if not phone or not phone.strip():
        raise ValidationError("Phone number is required", field="Phone")
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not re.match(PHONE_PATTERN, phone):
        raise ValidationError("Invalid phone number (e.g., 03001234567)", field="Phone")
    return phone


def validate_password(password):
    """
    Validate password strength.

    Args:
        password (str): Password to validate.

    Returns:
        str: The password if valid.

    Raises:
        ValidationError: If password doesn't meet requirements.
    """
    if not password:
        raise ValidationError("Password is required", field="Password")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
            field="Password"
        )
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters",
            field="Password"
        )
    return password


def validate_name(name, field_name="Name"):
    """
    Validate a name field.

    Args:
        name (str): Name to validate.
        field_name (str): Name of the field for error messages.

    Returns:
        str: Cleaned name.

    Raises:
        ValidationError: If name is invalid.
    """
    if not name or not name.strip():
        raise ValidationError(f"{field_name} is required", field=field_name)
    name = name.strip()
    if len(name) < MIN_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} must be at least {MIN_NAME_LENGTH} characters",
            field=field_name
        )
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {MAX_NAME_LENGTH} characters",
            field=field_name
        )
    return name


def validate_price(price):
    """
    Validate a price value.

    Args:
        price: Price to validate (can be string or number).

    Returns:
        float: Validated price.

    Raises:
        ValidationError: If price is invalid.
    """
    try:
        price = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Price must be a valid number", field="Price")
    if price < MIN_PRICE:
        raise ValidationError(f"Price must be at least {MIN_PRICE}", field="Price")
    if price > MAX_PRICE:
        raise ValidationError(f"Price cannot exceed {MAX_PRICE}", field="Price")
    return round(price, 2)


def validate_quantity(quantity):
    """
    Validate a quantity value.

    Args:
        quantity: Quantity to validate (can be string or number).

    Returns:
        int: Validated quantity.

    Raises:
        ValidationError: If quantity is invalid.
    """
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be a whole number", field="Quantity")
    if quantity < 1:
        raise ValidationError("Quantity must be at least 1", field="Quantity")
    if quantity > MAX_QUANTITY:
        raise ValidationError(f"Quantity cannot exceed {MAX_QUANTITY}", field="Quantity")
    return quantity


def validate_rating(rating):
    """
    Validate a rating value (1-5).

    Args:
        rating: Rating to validate.

    Returns:
        int: Validated rating.

    Raises:
        ValidationError: If rating is invalid.
    """
    try:
        rating = int(rating)
    except (ValueError, TypeError):
        raise ValidationError("Rating must be a number", field="Rating")
    if rating < 1 or rating > 5:
        raise ValidationError("Rating must be between 1 and 5", field="Rating")
    return rating


def validate_required(value, field_name="Field"):
    """
    Validate that a field is not empty.

    Args:
        value: Value to check.
        field_name (str): Name of the field for error messages.

    Returns:
        str: Stripped value.

    Raises:
        ValidationError: If the field is empty.
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)
    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{field_name} is required", field=field_name)
    if isinstance(value, str):
        return value.strip()
    return value
