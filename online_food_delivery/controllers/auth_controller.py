"""
Authentication controller for the Online Food Delivery System.
Handles login, registration, password reset, and session management.
"""

from models.user import UserModel
from utils.validators import validate_email, validate_password, validate_name, validate_phone
from utils.helpers import hash_password, verify_password
from utils.exceptions import AuthenticationError, ValidationError


class AuthController:
    """Controller for authentication operations."""

    def __init__(self):
        self.user_model = UserModel()
        self.current_user = None

    def register(self, name, email, phone, password, confirm_password, role,
                 security_question, security_answer):
        """
        Register a new user.

        Args:
            name (str): User's full name.
            email (str): User's email.
            phone (str): User's phone number.
            password (str): Password.
            confirm_password (str): Password confirmation.
            role (str): User role.
            security_question (str): Security question.
            security_answer (str): Answer to security question.

        Returns:
            int: New user ID.

        Raises:
            ValidationError: If any input is invalid.
            AuthenticationError: If registration fails.
        """
        # Validate all inputs
        name = validate_name(name)
        email = validate_email(email)
        phone = validate_phone(phone)
        password = validate_password(password)

        if password != confirm_password:
            raise ValidationError("Passwords do not match", field="Password")

        if not security_question:
            raise ValidationError("Security question is required",
                                  field="Security Question")
        if not security_answer or not security_answer.strip():
            raise ValidationError("Security answer is required",
                                  field="Security Answer")

        # Check if email already exists
        existing = self.user_model.get_user_by_email(email)
        if existing:
            raise AuthenticationError("An account with this email already exists")

        try:
            user_id = self.user_model.create_user(
                name, email, phone, password, role,
                security_question, security_answer.strip().lower()
            )
            return user_id
        except Exception as e:
            raise AuthenticationError(f"Registration failed: {e}")

    def login(self, email, password):
        """
        Authenticate a user.

        Args:
            email (str): User's email.
            password (str): User's password.

        Returns:
            dict: User data dictionary.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        if not email or not password:
            raise AuthenticationError("Email and password are required")

        email = email.strip().lower()
        user = self.user_model.get_user_by_email(email)

        if not user:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user['password_hash']):
            raise AuthenticationError("Invalid email or password")

        if not user['is_active']:
            raise AuthenticationError(
                "Your account has been deactivated. Contact admin."
            )

        # Set current user session
        self.current_user = dict(user)
        return self.current_user

    def logout(self):
        """Clear the current user session."""
        self.current_user = None

    def get_current_user(self):
        """
        Get the currently logged-in user.

        Returns:
            dict or None: Current user data or None.
        """
        return self.current_user

    def is_logged_in(self):
        """Check if a user is currently logged in."""
        return self.current_user is not None

    def get_security_question(self, email):
        """
        Get the security question for a user (password reset step 1).

        Args:
            email (str): User's email.

        Returns:
            str: Security question.

        Raises:
            AuthenticationError: If user is not found.
        """
        email = email.strip().lower()
        user = self.user_model.get_user_by_email(email)
        if not user:
            raise AuthenticationError("No account found with this email")
        return user['security_question']

    def reset_password(self, email, security_answer, new_password,
                       confirm_password):
        """
        Reset a user's password after verifying security answer.

        Args:
            email (str): User's email.
            security_answer (str): Answer to security question.
            new_password (str): New password.
            confirm_password (str): Confirmation of new password.

        Raises:
            AuthenticationError: If verification fails.
            ValidationError: If new password is invalid.
        """
        email = email.strip().lower()
        new_password = validate_password(new_password)

        if new_password != confirm_password:
            raise ValidationError("Passwords do not match", field="Password")

        user = self.user_model.verify_security_answer(
            email, security_answer.strip().lower()
        )
        if not user:
            raise AuthenticationError("Incorrect security answer")

        self.user_model.update_password(user['id'], new_password)
