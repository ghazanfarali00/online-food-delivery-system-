"""
Custom exception classes for the Online Food Delivery System.
Provides a hierarchy of specific exceptions for different error scenarios.
"""


class FoodDeliveryException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message="An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(FoodDeliveryException):
    """Raised when a database operation fails."""

    def __init__(self, message="Database operation failed"):
        super().__init__(message)


class AuthenticationError(FoodDeliveryException):
    """Raised when authentication fails (login, registration, etc.)."""

    def __init__(self, message="Authentication failed"):
        super().__init__(message)


class ValidationError(FoodDeliveryException):
    """Raised when input validation fails."""

    def __init__(self, message="Validation failed", field=None):
        self.field = field
        if field:
            message = f"{field}: {message}"
        super().__init__(message)


class OrderError(FoodDeliveryException):
    """Raised when an order operation fails."""

    def __init__(self, message="Order operation failed"):
        super().__init__(message)


class PaymentError(FoodDeliveryException):
    """Raised when a payment operation fails."""

    def __init__(self, message="Payment processing failed"):
        super().__init__(message)


class PermissionError(FoodDeliveryException):
    """Raised when a user doesn't have permission for an action."""

    def __init__(self, message="You don't have permission to perform this action"):
        super().__init__(message)


class NotFoundError(FoodDeliveryException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource="Resource", message=None):
        if message is None:
            message = f"{resource} not found"
        super().__init__(message)
