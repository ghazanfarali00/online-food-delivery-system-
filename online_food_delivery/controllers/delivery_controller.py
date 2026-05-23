"""
Delivery controller for the Online Food Delivery System.
Handles delivery queue, order acceptance, and status updates.
"""

from models.order import OrderModel
from models.notification import NotificationModel
from utils.exceptions import OrderError


class DeliveryController:
    """Controller for delivery person operations."""

    def __init__(self, current_user):
        """
        Initialize with the current logged-in delivery person.

        Args:
            current_user (dict): Currently logged-in delivery person data.
        """
        self.current_user = current_user
        self.order_model = OrderModel()
        self.notification_model = NotificationModel()

    # -------------------------------------------------------------------------
    # Delivery Queue
    # -------------------------------------------------------------------------

    def get_available_orders(self):
        """Get orders that are available for pickup (unassigned)."""
        return self.order_model.get_unassigned_orders()

    def get_my_deliveries(self, status=None):
        """Get all deliveries assigned to this delivery person."""
        return self.order_model.get_delivery_orders(
            self.current_user['id'], status
        )

    def get_active_deliveries(self):
        """Get currently active deliveries (not delivered/cancelled)."""
        all_deliveries = self.get_my_deliveries()
        return [
            d for d in all_deliveries
            if d['status'] in ('placed', 'preparing', 'out_for_delivery')
        ]

    def get_completed_deliveries(self):
        """Get completed deliveries."""
        return self.get_my_deliveries('delivered')

    # -------------------------------------------------------------------------
    # Order Actions
    # -------------------------------------------------------------------------

    def accept_order(self, order_id):
        """
        Accept an order for delivery.

        Args:
            order_id (int): Order internal ID.

        Raises:
            OrderError: If order is already assigned.
        """
        order = self.order_model.get_order_by_id(order_id)
        if order['delivery_person_id'] is not None:
            raise OrderError("This order has already been assigned")

        self.order_model.assign_delivery_person(
            order_id, self.current_user['id']
        )

        # Notify customer
        try:
            self.notification_model.create_notification(
                order['customer_id'],
                f"Order {order['order_uid']} — Rider Assigned",
                f"Your order has been assigned to {self.current_user['name']}."
            )
        except Exception:
            pass

    def update_delivery_status(self, order_id, new_status):
        """
        Update delivery status.

        Args:
            order_id (int): Order internal ID.
            new_status (str): New status (out_for_delivery, delivered).

        Raises:
            OrderError: If status update is invalid.
        """
        order = self.order_model.get_order_by_id(order_id)

        if order['delivery_person_id'] != self.current_user['id']:
            raise OrderError("You are not assigned to this order")

        valid_transitions = {
            'placed': ['out_for_delivery'],
            'preparing': ['out_for_delivery'],
            'out_for_delivery': ['delivered'],
        }

        current = order['status']
        allowed = valid_transitions.get(current, [])
        if new_status not in allowed:
            raise OrderError(
                f"Cannot change status from '{current}' to '{new_status}'"
            )

        self.order_model.update_status(order_id, new_status)

        # Notify customer
        try:
            status_msgs = {
                'out_for_delivery': 'Your order is on its way!',
                'delivered': 'Your order has been delivered. Enjoy your meal!'
            }
            if new_status in status_msgs:
                self.notification_model.create_notification(
                    order['customer_id'],
                    f"Order {order['order_uid']} Update",
                    status_msgs[new_status]
                )
        except Exception:
            pass

    def get_order_items(self, order_id):
        """Get items for a specific order."""
        return self.order_model.get_order_items(order_id)

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    def get_notifications(self):
        """Get delivery person's notifications."""
        return self.notification_model.get_user_notifications(
            self.current_user['id']
        )

    def get_unread_count(self):
        """Get unread notification count."""
        return self.notification_model.get_unread_count(
            self.current_user['id']
        )

    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------

    def get_delivery_stats(self):
        """
        Get delivery statistics for the current delivery person.

        Returns:
            dict: Stats with total, active, completed deliveries.
        """
        all_deliveries = self.get_my_deliveries()
        active = [d for d in all_deliveries
                  if d['status'] in ('placed', 'preparing', 'out_for_delivery')]
        completed = [d for d in all_deliveries if d['status'] == 'delivered']

        return {
            'total': len(all_deliveries),
            'active': len(active),
            'completed': len(completed),
        }
