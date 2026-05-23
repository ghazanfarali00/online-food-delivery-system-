"""
Admin controller for the Online Food Delivery System.
Handles dashboard analytics, user management, and system administration.
"""

from models.user import UserModel
from models.restaurant import RestaurantModel
from models.order import OrderModel
from models.review import ReviewModel
from models.notification import NotificationModel, SupportTicketModel
from utils.exceptions import ValidationError


class AdminController:
    """Controller for admin-specific operations."""

    def __init__(self, current_user):
        """
        Initialize with the current logged-in admin.

        Args:
            current_user (dict): Currently logged-in admin data.
        """
        self.current_user = current_user
        self.user_model = UserModel()
        self.restaurant_model = RestaurantModel()
        self.order_model = OrderModel()
        self.review_model = ReviewModel()
        self.notification_model = NotificationModel()
        self.support_model = SupportTicketModel()

    # -------------------------------------------------------------------------
    # Dashboard Analytics
    # -------------------------------------------------------------------------

    def get_dashboard_stats(self):
        """
        Get aggregate statistics for the admin dashboard.

        Returns:
            dict: Dashboard statistics (orders, revenue, users, restaurants).
        """
        order_stats = self.order_model.get_order_stats()
        user_counts = self.user_model.get_user_count_by_role()
        restaurant_count = self.restaurant_model.get_restaurant_count()

        total_users = sum(row['count'] for row in user_counts)
        role_counts = {row['role']: row['count'] for row in user_counts}

        return {
            'total_orders': order_stats.get('total_orders', 0),
            'total_revenue': order_stats.get('total_revenue', 0),
            'delivered_orders': order_stats.get('delivered_orders', 0),
            'active_orders': order_stats.get('active_orders', 0),
            'total_users': total_users,
            'total_customers': role_counts.get('customer', 0),
            'total_vendors': role_counts.get('vendor', 0),
            'total_delivery': role_counts.get('delivery', 0),
            'total_restaurants': restaurant_count,
        }

    def get_revenue_by_restaurant(self):
        """Get revenue breakdown by restaurant."""
        return self.order_model.get_revenue_by_restaurant()

    # -------------------------------------------------------------------------
    # User Management
    # -------------------------------------------------------------------------

    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role."""
        return self.user_model.get_all_users(role)

    def toggle_user_status(self, user_id, is_active):
        """Activate or deactivate a user."""
        if user_id == self.current_user['id']:
            raise ValidationError("Cannot deactivate your own account")
        self.user_model.toggle_active(user_id, is_active)

    def get_user_details(self, user_id):
        """Get detailed user information."""
        return self.user_model.get_user_by_id(user_id)

    # -------------------------------------------------------------------------
    # Restaurant Management
    # -------------------------------------------------------------------------

    def get_all_restaurants(self):
        """Get all restaurants (including inactive)."""
        return self.restaurant_model.get_all_restaurants(active_only=False)

    def toggle_restaurant_status(self, restaurant_id, is_active):
        """Activate or deactivate a restaurant."""
        self.restaurant_model.toggle_active(restaurant_id, is_active)

    # -------------------------------------------------------------------------
    # Order Management
    # -------------------------------------------------------------------------

    def get_all_orders(self, status=None):
        """Get all orders, optionally filtered by status."""
        return self.order_model.get_all_orders(status)

    def get_order_details(self, order_id):
        """Get order details including items."""
        order = self.order_model.get_order_by_id(order_id)
        items = self.order_model.get_order_items(order_id)
        return order, items

    # -------------------------------------------------------------------------
    # Review Moderation
    # -------------------------------------------------------------------------

    def get_all_reviews(self):
        """Get all reviews for moderation."""
        return self.review_model.get_all_reviews()

    def delete_review(self, review_id):
        """Delete an inappropriate review."""
        review = self.review_model.get_review_by_id(review_id)
        if review:
            self.review_model.delete_review(review_id)
            # Recalculate restaurant rating
            self.restaurant_model.update_rating(review['restaurant_id'])

    # -------------------------------------------------------------------------
    # Support Tickets
    # -------------------------------------------------------------------------

    def get_all_tickets(self, status=None):
        """Get all support tickets."""
        return self.support_model.get_all_tickets(status)

    def update_ticket_status(self, ticket_id, status):
        """Update a support ticket's status."""
        self.support_model.update_ticket_status(ticket_id, status)

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    def get_notifications(self):
        """Get admin notifications."""
        return self.notification_model.get_user_notifications(
            self.current_user['id']
        )

    def get_unread_count(self):
        """Get unread notification count."""
        return self.notification_model.get_unread_count(
            self.current_user['id']
        )
