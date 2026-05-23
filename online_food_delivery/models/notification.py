"""
Notification model for the Online Food Delivery System.
Handles creating and managing in-app notifications and support tickets.
"""

from database import Database
from utils.exceptions import DatabaseError


class NotificationModel:
    """Model for notification operations."""

    def __init__(self):
        self.db = Database()

    def create_notification(self, user_id, title, message):
        """
        Create a new notification for a user.

        Args:
            user_id (int): Recipient user ID.
            title (str): Notification title.
            message (str): Notification message.

        Returns:
            int: ID of the new notification.
        """
        cursor = self.db.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (?, ?, ?)
        """, (user_id, title, message))
        return cursor.lastrowid

    def get_user_notifications(self, user_id, unread_only=False):
        """
        Get notifications for a user.

        Args:
            user_id (int): User ID.
            unread_only (bool): If True, only return unread notifications.

        Returns:
            list: List of notification records.
        """
        if unread_only:
            return self.db.fetch_all("""
                SELECT * FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
            """, (user_id,))
        return self.db.fetch_all("""
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

    def mark_as_read(self, notification_id):
        """Mark a notification as read."""
        self.db.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notification_id,)
        )

    def mark_all_as_read(self, user_id):
        """Mark all notifications for a user as read."""
        self.db.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
            (user_id,)
        )

    def get_unread_count(self, user_id):
        """
        Get the count of unread notifications.

        Args:
            user_id (int): User ID.

        Returns:
            int: Number of unread notifications.
        """
        result = self.db.fetch_one("""
            SELECT COUNT(*) as count FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))
        return result['count'] if result else 0

    def delete_notification(self, notification_id):
        """Delete a notification."""
        self.db.execute(
            "DELETE FROM notifications WHERE id = ?", (notification_id,)
        )


class SupportTicketModel:
    """Model for support ticket operations."""

    def __init__(self):
        self.db = Database()

    def create_ticket(self, user_id, subject, message):
        """
        Create a new support ticket.

        Args:
            user_id (int): User ID who submitted the ticket.
            subject (str): Ticket subject.
            message (str): Ticket message/description.

        Returns:
            int: ID of the new ticket.
        """
        cursor = self.db.execute("""
            INSERT INTO support_tickets (user_id, subject, message)
            VALUES (?, ?, ?)
        """, (user_id, subject, message))
        return cursor.lastrowid

    def get_user_tickets(self, user_id):
        """Get all tickets submitted by a user."""
        return self.db.fetch_all("""
            SELECT * FROM support_tickets
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

    def get_all_tickets(self, status=None):
        """Get all tickets (admin), optionally filtered by status."""
        if status:
            return self.db.fetch_all("""
                SELECT st.*, u.name as user_name, u.email as user_email
                FROM support_tickets st
                JOIN users u ON st.user_id = u.id
                WHERE st.status = ?
                ORDER BY st.created_at DESC
            """, (status,))
        return self.db.fetch_all("""
            SELECT st.*, u.name as user_name, u.email as user_email
            FROM support_tickets st
            JOIN users u ON st.user_id = u.id
            ORDER BY st.created_at DESC
        """)

    def update_ticket_status(self, ticket_id, status):
        """Update a ticket's status."""
        self.db.execute(
            "UPDATE support_tickets SET status = ? WHERE id = ?",
            (status, ticket_id)
        )
