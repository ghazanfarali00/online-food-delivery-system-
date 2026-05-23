"""
Customer controller for the Online Food Delivery System.
Handles browsing, cart management, ordering, reviews, and profile.
"""

from models.restaurant import RestaurantModel, MenuItemModel
from models.order import OrderModel
from models.review import ReviewModel
from models.user import UserModel, AddressModel
from models.notification import NotificationModel, SupportTicketModel
from utils.validators import (validate_quantity, validate_rating,
                               validate_required, validate_name,
                               validate_phone)
from utils.helpers import format_currency
from utils.exceptions import OrderError, ValidationError


class CustomerController:
    """Controller for customer-specific operations."""

    def __init__(self, current_user):
        """
        Initialize with the current logged-in user.

        Args:
            current_user (dict): Currently logged-in user data.
        """
        self.current_user = current_user
        self.restaurant_model = RestaurantModel()
        self.menu_model = MenuItemModel()
        self.order_model = OrderModel()
        self.review_model = ReviewModel()
        self.user_model = UserModel()
        self.address_model = AddressModel()
        self.notification_model = NotificationModel()
        self.support_model = SupportTicketModel()
        self.cart = {}  # {restaurant_id: [{'item': ..., 'quantity': ...}, ...]}
        self.cart_restaurant_id = None

    # -------------------------------------------------------------------------
    # Restaurant Browsing
    # -------------------------------------------------------------------------

    def get_all_restaurants(self):
        """Get all active restaurants."""
        return self.restaurant_model.get_all_restaurants(active_only=True)

    def search_restaurants(self, query):
        """Search restaurants by name, cuisine, or location."""
        if not query or not query.strip():
            return self.get_all_restaurants()
        return self.restaurant_model.search_restaurants(query.strip())

    def filter_restaurants(self, cuisine_type=None, min_rating=None,
                           location=None):
        """Filter restaurants by criteria."""
        return self.restaurant_model.filter_restaurants(
            cuisine_type, min_rating, location
        )

    def get_restaurant(self, restaurant_id):
        """Get a restaurant by ID."""
        return self.restaurant_model.get_restaurant_by_id(restaurant_id)

    def get_restaurant_menu(self, restaurant_id):
        """Get the menu for a restaurant."""
        return self.menu_model.get_restaurant_menu(restaurant_id)

    def search_menu(self, restaurant_id, query):
        """Search menu items within a restaurant."""
        return self.menu_model.search_items(restaurant_id, query)

    # -------------------------------------------------------------------------
    # Cart Management
    # -------------------------------------------------------------------------

    def add_to_cart(self, restaurant_id, item, quantity=1):
        """
        Add an item to the cart.

        Args:
            restaurant_id (int): Restaurant ID.
            item (dict): Menu item data (id, name, price).
            quantity (int): Quantity to add.

        Raises:
            OrderError: If adding items from a different restaurant.
            ValidationError: If quantity is invalid.
        """
        quantity = validate_quantity(quantity)

        # Only allow items from one restaurant at a time
        if self.cart_restaurant_id and self.cart_restaurant_id != restaurant_id:
            raise OrderError(
                "You can only order from one restaurant at a time. "
                "Clear your cart first."
            )

        self.cart_restaurant_id = restaurant_id

        # Check if item already in cart
        for cart_item in self.cart.get(restaurant_id, []):
            if cart_item['item']['id'] == item['id']:
                cart_item['quantity'] += quantity
                return

        # Add new item
        if restaurant_id not in self.cart:
            self.cart[restaurant_id] = []
        self.cart[restaurant_id].append({
            'item': dict(item),
            'quantity': quantity
        })

    def update_cart_quantity(self, restaurant_id, item_id, quantity):
        """
        Update item quantity in cart.

        Args:
            restaurant_id (int): Restaurant ID.
            item_id (int): Menu item ID.
            quantity (int): New quantity (0 to remove).
        """
        if quantity == 0:
            self.remove_from_cart(restaurant_id, item_id)
            return

        quantity = validate_quantity(quantity)
        for cart_item in self.cart.get(restaurant_id, []):
            if cart_item['item']['id'] == item_id:
                cart_item['quantity'] = quantity
                return

    def remove_from_cart(self, restaurant_id, item_id):
        """Remove an item from the cart."""
        if restaurant_id in self.cart:
            self.cart[restaurant_id] = [
                ci for ci in self.cart[restaurant_id]
                if ci['item']['id'] != item_id
            ]
            if not self.cart[restaurant_id]:
                del self.cart[restaurant_id]
                self.cart_restaurant_id = None

    def clear_cart(self):
        """Clear the entire cart."""
        self.cart = {}
        self.cart_restaurant_id = None

    def get_cart_items(self):
        """
        Get all items in the cart.

        Returns:
            list: List of cart item dicts with item data and quantity.
        """
        items = []
        for restaurant_id, cart_items in self.cart.items():
            for ci in cart_items:
                items.append({
                    'restaurant_id': restaurant_id,
                    'item': ci['item'],
                    'quantity': ci['quantity'],
                    'subtotal': ci['quantity'] * ci['item']['price']
                })
        return items

    def get_cart_total(self):
        """
        Calculate the total price of all items in the cart.

        Returns:
            float: Total cart price.
        """
        total = 0
        for cart_items in self.cart.values():
            for ci in cart_items:
                total += ci['quantity'] * ci['item']['price']
        return total

    def get_cart_count(self):
        """Get total number of items in cart."""
        count = 0
        for cart_items in self.cart.values():
            for ci in cart_items:
                count += ci['quantity']
        return count

    # -------------------------------------------------------------------------
    # Order Placement
    # -------------------------------------------------------------------------

    def place_order(self, payment_method, delivery_address, address_id=None):
        """
        Place an order from the current cart.

        Args:
            payment_method (str): Payment method (cod/card/wallet).
            delivery_address (str): Delivery address text.
            address_id (int, optional): Saved address ID.

        Returns:
            str: Unique order ID.

        Raises:
            OrderError: If cart is empty or order fails.
        """
        if not self.cart:
            raise OrderError("Your cart is empty")

        if not delivery_address or not delivery_address.strip():
            raise OrderError("Delivery address is required")

        restaurant_id = self.cart_restaurant_id
        cart_items = self.cart.get(restaurant_id, [])

        items = []
        for ci in cart_items:
            items.append({
                'menu_item_id': ci['item']['id'],
                'item_name': ci['item']['name'],
                'quantity': ci['quantity'],
                'unit_price': ci['item']['price']
            })

        try:
            order_uid = self.order_model.create_order(
                customer_id=self.current_user['id'],
                restaurant_id=restaurant_id,
                items=items,
                payment_method=payment_method,
                delivery_address=delivery_address.strip(),
                address_id=address_id
            )

            # Create notification
            self.notification_model.create_notification(
                self.current_user['id'],
                "Order Placed!",
                f"Your order {order_uid} has been placed successfully. "
                f"Total: {format_currency(self.get_cart_total())}"
            )

            # Clear cart after successful order
            self.clear_cart()
            return order_uid
        except Exception as e:
            raise OrderError(f"Failed to place order: {e}")

    # -------------------------------------------------------------------------
    # Order History & Tracking
    # -------------------------------------------------------------------------

    def get_my_orders(self):
        """Get all orders for the current customer."""
        return self.order_model.get_customer_orders(self.current_user['id'])

    def get_order_details(self, order_uid):
        """Get order details including items."""
        order = self.order_model.get_order_by_uid(order_uid)
        items = self.order_model.get_order_items(order['id'])
        return order, items

    def cancel_order(self, order_id):
        """
        Cancel an order (only if status is 'placed').

        Args:
            order_id (int): Order internal ID.

        Raises:
            OrderError: If order cannot be cancelled.
        """
        order = self.order_model.get_order_by_id(order_id)
        if order['status'] != 'placed':
            raise OrderError("Only orders with 'placed' status can be cancelled")
        self.order_model.update_status(order_id, 'cancelled')

    # -------------------------------------------------------------------------
    # Reviews
    # -------------------------------------------------------------------------

    def add_review(self, restaurant_id, rating, comment="", order_id=None):
        """
        Add a review for a restaurant.

        Args:
            restaurant_id (int): Restaurant ID.
            rating (int): Rating (1-5).
            comment (str): Review comment.
            order_id (int, optional): Associated order ID.

        Returns:
            int: New review ID.
        """
        rating = validate_rating(rating)
        review_id = self.review_model.add_review(
            self.current_user['id'], restaurant_id, rating, comment, order_id
        )
        # Update restaurant average rating
        self.restaurant_model.update_rating(restaurant_id)
        return review_id

    def get_restaurant_reviews(self, restaurant_id):
        """Get all reviews for a restaurant."""
        return self.review_model.get_restaurant_reviews(restaurant_id)

    def has_reviewed(self, restaurant_id):
        """Check if current user has reviewed a restaurant."""
        return self.review_model.has_reviewed(
            self.current_user['id'], restaurant_id
        )

    # -------------------------------------------------------------------------
    # Profile Management
    # -------------------------------------------------------------------------

    def update_profile(self, name, phone):
        """Update current user's profile."""
        name = validate_name(name)
        phone = validate_phone(phone)
        self.user_model.update_user(
            self.current_user['id'], name=name, phone=phone
        )
        self.current_user['name'] = name
        self.current_user['phone'] = phone

    def get_addresses(self):
        """Get all addresses for the current user."""
        return self.address_model.get_user_addresses(self.current_user['id'])

    def add_address(self, label, address_line, city, zip_code="",
                    is_default=False):
        """Add a new delivery address."""
        label = validate_required(label, "Label")
        address_line = validate_required(address_line, "Address")
        city = validate_required(city, "City")
        return self.address_model.add_address(
            self.current_user['id'], label, address_line, city,
            zip_code, is_default
        )

    def delete_address(self, address_id):
        """Delete a delivery address."""
        self.address_model.delete_address(address_id)

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    def get_notifications(self):
        """Get all notifications for current user."""
        return self.notification_model.get_user_notifications(
            self.current_user['id']
        )

    def get_unread_count(self):
        """Get count of unread notifications."""
        return self.notification_model.get_unread_count(
            self.current_user['id']
        )

    def mark_notification_read(self, notification_id):
        """Mark a notification as read."""
        self.notification_model.mark_as_read(notification_id)

    def mark_all_notifications_read(self):
        """Mark all notifications as read."""
        self.notification_model.mark_all_as_read(self.current_user['id'])

    # -------------------------------------------------------------------------
    # Help & Support
    # -------------------------------------------------------------------------

    def submit_ticket(self, subject, message):
        """Submit a support ticket."""
        subject = validate_required(subject, "Subject")
        message = validate_required(message, "Message")
        return self.support_model.create_ticket(
            self.current_user['id'], subject, message
        )

    def get_my_tickets(self):
        """Get all support tickets for current user."""
        return self.support_model.get_user_tickets(self.current_user['id'])
