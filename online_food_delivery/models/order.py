"""
Order and OrderItem models for the Online Food Delivery System.
Handles order creation, status management, and order history.
"""

from database import Database
from utils.helpers import generate_order_id
from utils.exceptions import DatabaseError, NotFoundError, OrderError


class OrderModel:
    """Model for order-related database operations."""

    def __init__(self):
        self.db = Database()

    def create_order(self, customer_id, restaurant_id, items, payment_method,
                     delivery_address, address_id=None):
        """
        Create a new order with items.

        Args:
            customer_id (int): Customer user ID.
            restaurant_id (int): Restaurant ID.
            items (list): List of dicts with keys: menu_item_id, item_name,
                          quantity, unit_price.
            payment_method (str): Payment method (cod/card/wallet).
            delivery_address (str): Full delivery address text.
            address_id (int, optional): Saved address ID.

        Returns:
            str: The unique order ID (e.g., 'FE-A1B2C3D4').

        Raises:
            OrderError: If order could not be created.
        """
        if not items:
            raise OrderError("Cannot create an order with no items")

        order_uid = generate_order_id()
        total_amount = sum(
            item['quantity'] * item['unit_price'] for item in items
        )

        try:
            # Create the order
            cursor = self.db.execute("""
                INSERT INTO orders (order_uid, customer_id, restaurant_id,
                                    address_id, payment_method, total_amount,
                                    delivery_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_uid, customer_id, restaurant_id, address_id,
                  payment_method, total_amount, delivery_address))
            order_id = cursor.lastrowid

            # Add order items
            for item in items:
                subtotal = item['quantity'] * item['unit_price']
                self.db.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, item_name,
                                            quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (order_id, item['menu_item_id'], item['item_name'],
                      item['quantity'], item['unit_price'], subtotal))

            # Set payment status for non-COD orders
            if payment_method != 'cod':
                self.db.execute(
                    "UPDATE orders SET payment_status = 'paid' WHERE id = ?",
                    (order_id,)
                )

            return order_uid
        except DatabaseError as e:
            raise OrderError(f"Failed to create order: {e}")

    def get_order_by_uid(self, order_uid):
        """
        Get an order by its unique ID.

        Args:
            order_uid (str): Unique order ID.

        Returns:
            sqlite3.Row: Order record.

        Raises:
            NotFoundError: If order is not found.
        """
        order = self.db.fetch_one(
            "SELECT * FROM orders WHERE order_uid = ?", (order_uid,)
        )
        if not order:
            raise NotFoundError("Order")
        return order

    def get_order_by_id(self, order_id):
        """Get an order by internal ID."""
        order = self.db.fetch_one(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        )
        if not order:
            raise NotFoundError("Order")
        return order

    def get_order_items(self, order_id):
        """
        Get all items for an order.

        Args:
            order_id (int): Order internal ID.

        Returns:
            list: List of order item records.
        """
        return self.db.fetch_all(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
        )

    def get_customer_orders(self, customer_id):
        """
        Get all orders for a customer.

        Args:
            customer_id (int): Customer user ID.

        Returns:
            list: List of order records, most recent first.
        """
        return self.db.fetch_all("""
            SELECT o.*, r.name as restaurant_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.customer_id = ?
            ORDER BY o.created_at DESC
        """, (customer_id,))

    def get_restaurant_orders(self, restaurant_id, status=None):
        """
        Get all orders for a restaurant.

        Args:
            restaurant_id (int): Restaurant ID.
            status (str, optional): Filter by status.

        Returns:
            list: List of order records.
        """
        if status:
            return self.db.fetch_all("""
                SELECT o.*, u.name as customer_name, u.phone as customer_phone
                FROM orders o
                JOIN users u ON o.customer_id = u.id
                WHERE o.restaurant_id = ? AND o.status = ?
                ORDER BY o.created_at DESC
            """, (restaurant_id, status))
        return self.db.fetch_all("""
            SELECT o.*, u.name as customer_name, u.phone as customer_phone
            FROM orders o
            JOIN users u ON o.customer_id = u.id
            WHERE o.restaurant_id = ?
            ORDER BY o.created_at DESC
        """, (restaurant_id,))

    def get_delivery_orders(self, delivery_person_id, status=None):
        """
        Get all orders assigned to a delivery person.

        Args:
            delivery_person_id (int): Delivery person user ID.
            status (str, optional): Filter by status.

        Returns:
            list: List of order records.
        """
        if status:
            return self.db.fetch_all("""
                SELECT o.*, r.name as restaurant_name,
                       u.name as customer_name, u.phone as customer_phone
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.id
                JOIN users u ON o.customer_id = u.id
                WHERE o.delivery_person_id = ? AND o.status = ?
                ORDER BY o.created_at DESC
            """, (delivery_person_id, status))
        return self.db.fetch_all("""
            SELECT o.*, r.name as restaurant_name,
                   u.name as customer_name, u.phone as customer_phone
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            JOIN users u ON o.customer_id = u.id
            WHERE o.delivery_person_id = ?
            ORDER BY o.created_at DESC
        """, (delivery_person_id,))

    def get_unassigned_orders(self):
        """Get orders that need delivery person assignment."""
        return self.db.fetch_all("""
            SELECT o.*, r.name as restaurant_name, r.location as restaurant_location,
                   u.name as customer_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            JOIN users u ON o.customer_id = u.id
            WHERE o.delivery_person_id IS NULL
                AND o.status IN ('placed', 'preparing')
            ORDER BY o.created_at ASC
        """)

    def update_status(self, order_id, new_status):
        """
        Update an order's status.

        Args:
            order_id (int): Order internal ID.
            new_status (str): New status value.

        Raises:
            OrderError: If status transition is invalid.
        """
        valid_statuses = ['placed', 'preparing', 'out_for_delivery',
                          'delivered', 'cancelled']
        if new_status not in valid_statuses:
            raise OrderError(f"Invalid status: {new_status}")

        self.db.execute("""
            UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, order_id))

        # Mark payment as paid when delivered with COD
        if new_status == 'delivered':
            self.db.execute(
                "UPDATE orders SET payment_status = 'paid' WHERE id = ?",
                (order_id,)
            )

    def assign_delivery_person(self, order_id, delivery_person_id):
        """
        Assign a delivery person to an order.

        Args:
            order_id (int): Order internal ID.
            delivery_person_id (int): Delivery person user ID.
        """
        self.db.execute("""
            UPDATE orders SET delivery_person_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (delivery_person_id, order_id))

    def get_all_orders(self, status=None):
        """Get all orders (admin), optionally filtered by status."""
        if status:
            return self.db.fetch_all("""
                SELECT o.*, r.name as restaurant_name, u.name as customer_name
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.id
                JOIN users u ON o.customer_id = u.id
                WHERE o.status = ?
                ORDER BY o.created_at DESC
            """, (status,))
        return self.db.fetch_all("""
            SELECT o.*, r.name as restaurant_name, u.name as customer_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            JOIN users u ON o.customer_id = u.id
            ORDER BY o.created_at DESC
        """)

    def get_order_stats(self):
        """Get order statistics for admin dashboard."""
        stats = {}
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM orders")
        stats['total_orders'] = result['count'] if result else 0

        result = self.db.fetch_one(
            "SELECT SUM(total_amount) as total FROM orders WHERE payment_status = 'paid'"
        )
        stats['total_revenue'] = result['total'] if result and result['total'] else 0

        result = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM orders WHERE status = 'delivered'"
        )
        stats['delivered_orders'] = result['count'] if result else 0

        result = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM orders WHERE status IN ('placed', 'preparing', 'out_for_delivery')"
        )
        stats['active_orders'] = result['count'] if result else 0

        return stats

    def get_revenue_by_restaurant(self):
        """Get revenue breakdown by restaurant."""
        return self.db.fetch_all("""
            SELECT r.name, SUM(o.total_amount) as revenue, COUNT(o.id) as order_count
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.payment_status = 'paid'
            GROUP BY r.id
            ORDER BY revenue DESC
        """)
