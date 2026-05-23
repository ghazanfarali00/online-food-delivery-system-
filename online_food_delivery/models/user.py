"""
User and Address models for the Online Food Delivery System.
Handles CRUD operations for users and their delivery addresses.
"""

from database import Database
from utils.helpers import hash_password
from utils.exceptions import DatabaseError, NotFoundError


class UserModel:
    """Model for user-related database operations."""

    def __init__(self):
        self.db = Database()

    def create_user(self, name, email, phone, password, role,
                    security_question=None, security_answer=None):
        """
        Create a new user account.

        Args:
            name (str): User's full name.
            email (str): User's email address.
            phone (str): User's phone number.
            password (str): Plain text password (will be hashed).
            role (str): User role (admin/customer/vendor/delivery).
            security_question (str): Security question for password reset.
            security_answer (str): Answer to the security question.

        Returns:
            int: ID of the newly created user.

        Raises:
            DatabaseError: If the user could not be created.
        """
        password_hash = hash_password(password)
        answer_hash = hash_password(security_answer) if security_answer else None
        try:
            cursor = self.db.execute("""
                INSERT INTO users (name, email, phone, password_hash, role,
                                   security_question, security_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, password_hash, role,
                  security_question, answer_hash))
            return cursor.lastrowid
        except DatabaseError:
            raise DatabaseError("Email already exists or invalid data provided")

    def get_user_by_email(self, email):
        """
        Fetch a user by email address.

        Args:
            email (str): Email to search for.

        Returns:
            sqlite3.Row or None: User record if found.
        """
        return self.db.fetch_one(
            "SELECT * FROM users WHERE email = ?", (email,)
        )

    def get_user_by_id(self, user_id):
        """
        Fetch a user by ID.

        Args:
            user_id (int): User ID.

        Returns:
            sqlite3.Row: User record.

        Raises:
            NotFoundError: If user is not found.
        """
        user = self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        if not user:
            raise NotFoundError("User")
        return user

    def update_user(self, user_id, name=None, phone=None, email=None):
        """
        Update user profile details.

        Args:
            user_id (int): User ID.
            name (str, optional): New name.
            phone (str, optional): New phone number.
            email (str, optional): New email address.
        """
        updates = []
        params = []
        if name:
            updates.append("name = ?")
            params.append(name)
        if phone:
            updates.append("phone = ?")
            params.append(phone)
        if email:
            updates.append("email = ?")
            params.append(email)
        if updates:
            params.append(user_id)
            self.db.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params
            )

    def update_password(self, user_id, new_password):
        """
        Update user's password.

        Args:
            user_id (int): User ID.
            new_password (str): New plain text password.
        """
        password_hash = hash_password(new_password)
        self.db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id)
        )

    def toggle_active(self, user_id, is_active):
        """
        Activate or deactivate a user account.

        Args:
            user_id (int): User ID.
            is_active (bool): New active status.
        """
        self.db.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (int(is_active), user_id)
        )

    def get_all_users(self, role=None):
        """
        Get all users, optionally filtered by role.

        Args:
            role (str, optional): Filter by role.

        Returns:
            list: List of user records.
        """
        if role:
            return self.db.fetch_all(
                "SELECT * FROM users WHERE role = ? ORDER BY created_at DESC",
                (role,)
            )
        return self.db.fetch_all(
            "SELECT * FROM users ORDER BY created_at DESC"
        )

    def get_user_count_by_role(self):
        """
        Get count of users grouped by role.

        Returns:
            list: List of (role, count) records.
        """
        return self.db.fetch_all(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        )

    def verify_security_answer(self, email, answer):
        """
        Verify a user's security answer for password reset.

        Args:
            email (str): User's email.
            answer (str): Answer to verify.

        Returns:
            sqlite3.Row or None: User record if answer matches.
        """
        user = self.get_user_by_email(email)
        if user and user['security_answer'] == hash_password(answer):
            return user
        return None


class AddressModel:
    """Model for delivery address operations."""

    def __init__(self):
        self.db = Database()

    def add_address(self, user_id, label, address_line, city, zip_code="",
                    is_default=False):
        """
        Add a new delivery address for a user.

        Args:
            user_id (int): User ID.
            label (str): Address label (e.g., "Home", "Office").
            address_line (str): Street address.
            city (str): City name.
            zip_code (str): Postal/ZIP code.
            is_default (bool): Whether this is the default address.

        Returns:
            int: ID of the new address.
        """
        if is_default:
            # Unset other defaults
            self.db.execute(
                "UPDATE addresses SET is_default = 0 WHERE user_id = ?",
                (user_id,)
            )
        cursor = self.db.execute("""
            INSERT INTO addresses (user_id, label, address_line, city, zip_code, is_default)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, label, address_line, city, zip_code, int(is_default)))
        return cursor.lastrowid

    def get_user_addresses(self, user_id):
        """
        Get all addresses for a user.

        Args:
            user_id (int): User ID.

        Returns:
            list: List of address records.
        """
        return self.db.fetch_all(
            "SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC",
            (user_id,)
        )

    def get_default_address(self, user_id):
        """
        Get the default address for a user.

        Args:
            user_id (int): User ID.

        Returns:
            sqlite3.Row or None: Default address record.
        """
        return self.db.fetch_one(
            "SELECT * FROM addresses WHERE user_id = ? AND is_default = 1",
            (user_id,)
        )

    def update_address(self, address_id, label=None, address_line=None,
                       city=None, zip_code=None):
        """Update an existing address."""
        updates = []
        params = []
        if label:
            updates.append("label = ?")
            params.append(label)
        if address_line:
            updates.append("address_line = ?")
            params.append(address_line)
        if city:
            updates.append("city = ?")
            params.append(city)
        if zip_code is not None:
            updates.append("zip_code = ?")
            params.append(zip_code)
        if updates:
            params.append(address_id)
            self.db.execute(
                f"UPDATE addresses SET {', '.join(updates)} WHERE id = ?",
                params
            )

    def delete_address(self, address_id):
        """Delete an address by ID."""
        self.db.execute("DELETE FROM addresses WHERE id = ?", (address_id,))

    def set_default(self, user_id, address_id):
        """Set an address as the default for a user."""
        self.db.execute(
            "UPDATE addresses SET is_default = 0 WHERE user_id = ?",
            (user_id,)
        )
        self.db.execute(
            "UPDATE addresses SET is_default = 1 WHERE id = ?",
            (address_id,)
        )
