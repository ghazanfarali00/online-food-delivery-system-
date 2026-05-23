"""
Restaurant and MenuItem models for the Online Food Delivery System.
Handles CRUD operations for restaurants and their menu items.
"""

from database import Database
from utils.exceptions import DatabaseError, NotFoundError


class RestaurantModel:
    """Model for restaurant-related database operations."""

    def __init__(self):
        self.db = Database()

    def create_restaurant(self, vendor_id, name, description, cuisine_type,
                          location):
        """
        Create a new restaurant.

        Args:
            vendor_id (int): Vendor user ID.
            name (str): Restaurant name.
            description (str): Restaurant description.
            cuisine_type (str): Type of cuisine.
            location (str): Restaurant location.

        Returns:
            int: ID of the newly created restaurant.
        """
        cursor = self.db.execute("""
            INSERT INTO restaurants (vendor_id, name, description, cuisine_type, location)
            VALUES (?, ?, ?, ?, ?)
        """, (vendor_id, name, description, cuisine_type, location))
        return cursor.lastrowid

    def get_restaurant_by_id(self, restaurant_id):
        """
        Get a restaurant by its ID.

        Args:
            restaurant_id (int): Restaurant ID.

        Returns:
            sqlite3.Row: Restaurant record.

        Raises:
            NotFoundError: If restaurant is not found.
        """
        restaurant = self.db.fetch_one(
            "SELECT * FROM restaurants WHERE id = ?", (restaurant_id,)
        )
        if not restaurant:
            raise NotFoundError("Restaurant")
        return restaurant

    def get_vendor_restaurant(self, vendor_id):
        """
        Get the restaurant owned by a vendor.

        Args:
            vendor_id (int): Vendor user ID.

        Returns:
            sqlite3.Row or None: Restaurant record.
        """
        return self.db.fetch_one(
            "SELECT * FROM restaurants WHERE vendor_id = ?", (vendor_id,)
        )

    def get_all_restaurants(self, active_only=True):
        """
        Get all restaurants.

        Args:
            active_only (bool): If True, return only active restaurants.

        Returns:
            list: List of restaurant records.
        """
        if active_only:
            return self.db.fetch_all(
                "SELECT * FROM restaurants WHERE is_active = 1 ORDER BY avg_rating DESC"
            )
        return self.db.fetch_all(
            "SELECT * FROM restaurants ORDER BY created_at DESC"
        )

    def search_restaurants(self, query):
        """
        Search restaurants by name or cuisine type.

        Args:
            query (str): Search term.

        Returns:
            list: Matching restaurant records.
        """
        search_term = f"%{query}%"
        return self.db.fetch_all("""
            SELECT * FROM restaurants
            WHERE is_active = 1 AND (name LIKE ? OR cuisine_type LIKE ? OR location LIKE ?)
            ORDER BY avg_rating DESC
        """, (search_term, search_term, search_term))

    def filter_restaurants(self, cuisine_type=None, min_rating=None,
                           location=None):
        """
        Filter restaurants by various criteria.

        Args:
            cuisine_type (str, optional): Filter by cuisine.
            min_rating (float, optional): Minimum rating.
            location (str, optional): Filter by location.

        Returns:
            list: Filtered restaurant records.
        """
        query = "SELECT * FROM restaurants WHERE is_active = 1"
        params = []
        if cuisine_type:
            query += " AND cuisine_type = ?"
            params.append(cuisine_type)
        if min_rating:
            query += " AND avg_rating >= ?"
            params.append(min_rating)
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        query += " ORDER BY avg_rating DESC"
        return self.db.fetch_all(query, params)

    def update_restaurant(self, restaurant_id, **kwargs):
        """
        Update restaurant details.

        Args:
            restaurant_id (int): Restaurant ID.
            **kwargs: Fields to update (name, description, cuisine_type, location).
        """
        allowed_fields = ['name', 'description', 'cuisine_type', 'location']
        updates = []
        params = []
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = ?")
                params.append(kwargs[field])
        if updates:
            params.append(restaurant_id)
            self.db.execute(
                f"UPDATE restaurants SET {', '.join(updates)} WHERE id = ?",
                params
            )

    def update_rating(self, restaurant_id):
        """
        Recalculate and update a restaurant's average rating.

        Args:
            restaurant_id (int): Restaurant ID.
        """
        result = self.db.fetch_one("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_reviews
            FROM reviews WHERE restaurant_id = ?
        """, (restaurant_id,))
        if result:
            avg = result['avg_rating'] or 0.0
            total = result['total_reviews'] or 0
            self.db.execute("""
                UPDATE restaurants SET avg_rating = ?, total_reviews = ?
                WHERE id = ?
            """, (round(avg, 1), total, restaurant_id))

    def toggle_active(self, restaurant_id, is_active):
        """Toggle restaurant active status."""
        self.db.execute(
            "UPDATE restaurants SET is_active = ? WHERE id = ?",
            (int(is_active), restaurant_id)
        )

    def get_restaurant_count(self):
        """Get total count of restaurants."""
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM restaurants")
        return result['count'] if result else 0


class MenuItemModel:
    """Model for menu item operations."""

    def __init__(self):
        self.db = Database()

    def add_item(self, restaurant_id, name, description, category, price):
        """
        Add a new menu item to a restaurant.

        Args:
            restaurant_id (int): Restaurant ID.
            name (str): Item name.
            description (str): Item description.
            category (str): Item category.
            price (float): Item price.

        Returns:
            int: ID of the new menu item.
        """
        cursor = self.db.execute("""
            INSERT INTO menu_items (restaurant_id, name, description, category, price)
            VALUES (?, ?, ?, ?, ?)
        """, (restaurant_id, name, description, category, price))
        return cursor.lastrowid

    def get_item_by_id(self, item_id):
        """
        Get a menu item by ID.

        Args:
            item_id (int): Menu item ID.

        Returns:
            sqlite3.Row: Menu item record.

        Raises:
            NotFoundError: If item is not found.
        """
        item = self.db.fetch_one(
            "SELECT * FROM menu_items WHERE id = ?", (item_id,)
        )
        if not item:
            raise NotFoundError("Menu Item")
        return item

    def get_restaurant_menu(self, restaurant_id, available_only=True):
        """
        Get all menu items for a restaurant.

        Args:
            restaurant_id (int): Restaurant ID.
            available_only (bool): If True, only return available items.

        Returns:
            list: List of menu item records.
        """
        if available_only:
            return self.db.fetch_all("""
                SELECT * FROM menu_items
                WHERE restaurant_id = ? AND is_available = 1
                ORDER BY category, name
            """, (restaurant_id,))
        return self.db.fetch_all("""
            SELECT * FROM menu_items
            WHERE restaurant_id = ?
            ORDER BY category, name
        """, (restaurant_id,))

    def update_item(self, item_id, **kwargs):
        """
        Update a menu item.

        Args:
            item_id (int): Item ID.
            **kwargs: Fields to update (name, description, category, price).
        """
        allowed_fields = ['name', 'description', 'category', 'price']
        updates = []
        params = []
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = ?")
                params.append(kwargs[field])
        if updates:
            params.append(item_id)
            self.db.execute(
                f"UPDATE menu_items SET {', '.join(updates)} WHERE id = ?",
                params
            )

    def toggle_availability(self, item_id, is_available):
        """Toggle menu item availability."""
        self.db.execute(
            "UPDATE menu_items SET is_available = ? WHERE id = ?",
            (int(is_available), item_id)
        )

    def delete_item(self, item_id):
        """Delete a menu item."""
        self.db.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))

    def search_items(self, restaurant_id, query):
        """Search menu items by name or category within a restaurant."""
        search_term = f"%{query}%"
        return self.db.fetch_all("""
            SELECT * FROM menu_items
            WHERE restaurant_id = ? AND is_available = 1
                AND (name LIKE ? OR category LIKE ? OR description LIKE ?)
            ORDER BY category, name
        """, (restaurant_id, search_term, search_term, search_term))
