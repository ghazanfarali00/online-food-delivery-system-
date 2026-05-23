"""
Main entry point for the Online Food Delivery System.
Initializes the application, database, and handles view routing.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, COLORS
from database import Database
from controllers.auth_controller import AuthController
from controllers.customer_controller import CustomerController
from controllers.vendor_controller import VendorController
from controllers.admin_controller import AdminController
from controllers.delivery_controller import DeliveryController
from views.auth_views import AuthView
from views.customer_views import CustomerView
from views.vendor_views import VendorView
from views.admin_views import AdminView
from views.delivery_views import DeliveryView


class FoodExpressApp:
    """Main application class that manages the Tkinter root and view routing."""

    def __init__(self):
        """Initialize the application."""
        # Initialize database
        try:
            self.db = Database()
        except Exception as e:
            print(f"Database initialization failed: {e}")
            sys.exit(1)

        # Setup main window
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.configure(bg=COLORS['bg_light'])

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"+{x}+{y}")

        # Configure ttk styles
        self._configure_styles()

        # Initialize auth controller
        self.auth_controller = AuthController()

        # Current view reference
        self.current_view = None

        # Show login screen
        self.show_auth()

    def _configure_styles(self):
        """Configure ttk widget styles for a modern look."""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TCombobox', padding=5)
        style.configure('TScrollbar', background=COLORS['border'])
        style.configure('TRadiobutton', background=COLORS['white'])

    def _clear_view(self):
        """Remove current view from the window."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    def show_auth(self):
        """Show the authentication (login/register) screen."""
        self._clear_view()
        self.current_view = AuthView(
            self.root,
            self.auth_controller,
            on_login_success=self._on_login
        )

    def _on_login(self, user):
        """
        Handle successful login — route to the appropriate dashboard.

        Args:
            user (dict): Authenticated user data.
        """
        self._clear_view()
        role = user.get('role', 'customer')

        try:
            if role == 'customer':
                controller = CustomerController(user)
                self.current_view = CustomerView(
                    self.root, user, controller, self._on_logout
                )
            elif role == 'vendor':
                controller = VendorController(user)
                self.current_view = VendorView(
                    self.root, user, controller, self._on_logout
                )
            elif role == 'admin':
                controller = AdminController(user)
                self.current_view = AdminView(
                    self.root, user, controller, self._on_logout
                )
            elif role == 'delivery':
                controller = DeliveryController(user)
                self.current_view = DeliveryView(
                    self.root, user, controller, self._on_logout
                )
            else:
                # Default to customer
                controller = CustomerController(user)
                self.current_view = CustomerView(
                    self.root, user, controller, self._on_logout
                )
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load dashboard: {e}")
            self.show_auth()

    def _on_logout(self):
        """Handle user logout."""
        self.auth_controller.logout()
        self.show_auth()

    def run(self):
        """Start the application main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.destroy()
        finally:
            self.db.close()


if __name__ == "__main__":
    app = FoodExpressApp()
    app.run()
