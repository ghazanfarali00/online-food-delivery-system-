"""
Review model for the Online Food Delivery System.
Handles CRUD operations for restaurant reviews and ratings.
"""

from database import Database
from utils.exceptions import DatabaseError


class ReviewModel:
    """Model for review and rating operations."""

    def __init__(self):
        self.db = Database()

    def add_review(self, user_id, restaurant_id, rating, comment="",
                   order_id=None):
        """
        Add a new review for a restaurant.

        Args:
            user_id (int): Reviewer's user ID.
            restaurant_id (int): Restaurant being reviewed.
            rating (int): Rating from 1-5.
            comment (str): Review text.
            order_id (int, optional): Associated order ID.

        Returns:
            int: ID of the new review.
        """
        cursor = self.db.execute("""
            INSERT INTO reviews (user_id, restaurant_id, order_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, restaurant_id, order_id, rating, comment))
        return cursor.lastrowid

    def get_restaurant_reviews(self, restaurant_id):
        """
        Get all reviews for a restaurant.

        Args:
            restaurant_id (int): Restaurant ID.

        Returns:
            list: List of review records with reviewer name.
        """
        return self.db.fetch_all("""
            SELECT r.*, u.name as reviewer_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.restaurant_id = ?
            ORDER BY r.created_at DESC
        """, (restaurant_id,))

    def get_user_reviews(self, user_id):
        """
        Get all reviews by a user.

        Args:
            user_id (int): User ID.

        Returns:
            list: List of review records with restaurant name.
        """
        return self.db.fetch_all("""
            SELECT r.*, rest.name as restaurant_name
            FROM reviews r
            JOIN restaurants rest ON r.restaurant_id = rest.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
        """, (user_id,))

    def get_review_by_id(self, review_id):
        """Get a review by ID."""
        return self.db.fetch_one(
            "SELECT * FROM reviews WHERE id = ?", (review_id,)
        )

    def delete_review(self, review_id):
        """Delete a review by ID (admin moderation)."""
        self.db.execute("DELETE FROM reviews WHERE id = ?", (review_id,))

    def get_all_reviews(self):
        """Get all reviews (for admin moderation)."""
        return self.db.fetch_all("""
            SELECT r.*, u.name as reviewer_name, rest.name as restaurant_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN restaurants rest ON r.restaurant_id = rest.id
            ORDER BY r.created_at DESC
        """)

    def has_reviewed(self, user_id, restaurant_id):
        """Check if a user has already reviewed a restaurant."""
        result = self.db.fetch_one("""
            SELECT COUNT(*) as count FROM reviews
            WHERE user_id = ? AND restaurant_id = ?
        """, (user_id, restaurant_id))
        return result['count'] > 0 if result else False
