"""
Vendor controller for the Online Food Delivery System.
Handles restaurant profile, menu management, and order processing.
"""

from models.restaurant import RestaurantModel, MenuItemModel
from models.order import OrderModel
from models.review import ReviewModel
from models.notification import NotificationModel
from utils.validators import (validate_name, validate_price,
                               validate_required)
from utils.exceptions import ValidationError


class VendorController:
    """Controller for vendor-specific operations."""

    def __init__(self, current_user):
        """
        Initialize with the current logged-in vendor.

        Args:
            current_user (dict): Currently logged-in vendor data.
        """
        self.current_user = current_user
        self.restaurant_model = RestaurantModel()
        self.menu_model = MenuItemModel()
        self.order_model = OrderModel()
        self.review_model = ReviewModel()
        self.notification_model = NotificationModel()

    # -------------------------------------------------------------------------
    # Restaurant Profile
    # -------------------------------------------------------------------------

    def get_my_restaurant(self):
        """Get the vendor's restaurant."""
        return self.restaurant_model.get_vendor_restaurant(
            self.current_user['id']
        )

    def create_restaurant(self, name, description, cuisine_type, location):
        """
        Create a new restaurant for this vendor.

        Args:
            name (str): Restaurant name.
            description (str): Description.
            cuisine_type (str): Cuisine type.
            location (str): Location.

        Returns:
            int: New restaurant ID.
        """
        name = validate_name(name, "Restaurant Name")
        description = validate_required(description, "Description")
        location = validate_required(location, "Location")
        return self.restaurant_model.create_restaurant(
            self.current_user['id'], name, description, cuisine_type, location
        )

    def update_restaurant(self, restaurant_id, **kwargs):
        """Update restaurant details."""
        if 'name' in kwargs:
            kwargs['name'] = validate_name(kwargs['name'], "Restaurant Name")
        self.restaurant_model.update_restaurant(restaurant_id, **kwargs)

    # -------------------------------------------------------------------------
    # Menu Management
    # -------------------------------------------------------------------------

    def get_menu_items(self, restaurant_id):
        """Get all menu items (including unavailable)."""
        return self.menu_model.get_restaurant_menu(restaurant_id,
                                                    available_only=False)

    def add_menu_item(self, restaurant_id, name, description, category, price):
        """
        Add a new menu item.

        Args:
            name (str): Item name.
            description (str): Item description.
            category (str): Item category.
            price: Item price.

        Returns:
            int: New item ID.
        """
        name = validate_name(name, "Item Name")
        price = validate_price(price)
        return self.menu_model.add_item(
            restaurant_id, name, description, category, price
        )

    def update_menu_item(self, item_id, **kwargs):
        """Update a menu item."""
        if 'name' in kwargs:
            kwargs['name'] = validate_name(kwargs['name'], "Item Name")
        if 'price' in kwargs:
            kwargs['price'] = validate_price(kwargs['price'])
        self.menu_model.update_item(item_id, **kwargs)

    def toggle_item_availability(self, item_id, is_available):
        """Toggle menu item availability."""
        self.menu_model.toggle_availability(item_id, is_available)

    def delete_menu_item(self, item_id):
        """Delete a menu item."""
        self.menu_model.delete_item(item_id)

    # -------------------------------------------------------------------------
    # Order Processing
    # -------------------------------------------------------------------------

    def get_orders(self, restaurant_id, status=None):
        """Get all orders for the restaurant."""
        return self.order_model.get_restaurant_orders(restaurant_id, status)

    def get_order_items(self, order_id):
        """Get items for a specific order."""
        return self.order_model.get_order_items(order_id)

    def update_order_status(self, order_id, new_status):
        """
        Update order status (vendor can set preparing/ready).

        Args:
            order_id (int): Order internal ID.
            new_status (str): New status.
        """
        self.order_model.update_status(order_id, new_status)

        # Notify customer
        try:
            order = self.order_model.get_order_by_id(order_id)
            status_messages = {
                'preparing': 'Your order is being prepared!',
                'out_for_delivery': 'Your order is out for delivery!',
                'delivered': 'Your order has been delivered. Enjoy!',
                'cancelled': 'Your order has been cancelled.'
            }
            if new_status in status_messages:
                self.notification_model.create_notification(
                    order['customer_id'],
                    f"Order {order['order_uid']} Update",
                    status_messages[new_status]
                )
        except Exception:
            pass  # Don't fail order update if notification fails

    # -------------------------------------------------------------------------
    # Reviews
    # -------------------------------------------------------------------------

    def get_restaurant_reviews(self, restaurant_id):
        """Get reviews for the vendor's restaurant."""
        return self.review_model.get_restaurant_reviews(restaurant_id)
