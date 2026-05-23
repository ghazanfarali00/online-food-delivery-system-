"""
Configuration module for the Online Food Delivery System.
Contains all constants, color schemes, fonts, and application settings.
"""

import os

# =============================================================================
# Application Settings
# =============================================================================
APP_NAME = "FoodExpress — Online Food Delivery"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 650

# =============================================================================
# Database Configuration
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "food_delivery.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# =============================================================================
# Color Palette — Modern Dark/Light Theme
# =============================================================================
COLORS = {
    # Primary brand colors
    "primary": "#FF6B35",          # Vibrant orange
    "primary_dark": "#E55A2B",     # Darker orange (hover)
    "primary_light": "#FF8C5A",    # Light orange
    "primary_bg": "#FFF3ED",       # Very light orange background

    # Accent colors
    "accent": "#004E89",           # Deep blue
    "accent_light": "#1A6FB5",     # Lighter blue
    "success": "#2ECC71",          # Green
    "success_dark": "#27AE60",     # Dark green
    "warning": "#F39C12",          # Amber
    "warning_dark": "#E67E22",     # Dark amber
    "danger": "#E74C3C",           # Red
    "danger_dark": "#C0392B",      # Dark red
    "info": "#3498DB",             # Sky blue

    # Neutral colors
    "white": "#FFFFFF",
    "bg_light": "#F8F9FA",        # Light gray background
    "bg_medium": "#EDF2F7",       # Medium gray background
    "border": "#E2E8F0",          # Border color
    "border_dark": "#CBD5E0",     # Darker border
    "text_primary": "#1A202C",    # Dark text
    "text_secondary": "#718096",  # Gray text
    "text_muted": "#A0AEC0",     # Muted text
    "dark": "#2D3748",            # Dark background
    "darker": "#1A202C",          # Darker background

    # Sidebar
    "sidebar_bg": "#1A202C",      # Dark sidebar
    "sidebar_hover": "#2D3748",   # Sidebar hover
    "sidebar_active": "#FF6B35",  # Active item (orange)
    "sidebar_text": "#A0AEC0",    # Sidebar text
    "sidebar_text_active": "#FFFFFF",  # Active text

    # Status colors
    "status_placed": "#3498DB",
    "status_preparing": "#F39C12",
    "status_out": "#9B59B6",
    "status_delivered": "#2ECC71",
    "status_cancelled": "#E74C3C",

    # Star rating
    "star_filled": "#F39C12",
    "star_empty": "#E2E8F0",
}

# =============================================================================
# Font Configuration
# =============================================================================
FONTS = {
    "heading_xl": ("Segoe UI", 24, "bold"),
    "heading_lg": ("Segoe UI", 20, "bold"),
    "heading_md": ("Segoe UI", 16, "bold"),
    "heading_sm": ("Segoe UI", 14, "bold"),
    "body_lg": ("Segoe UI", 13),
    "body": ("Segoe UI", 11),
    "body_sm": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 11, "bold"),
    "body_lg_bold": ("Segoe UI", 13, "bold"),
    "caption": ("Segoe UI", 9),
    "button": ("Segoe UI", 11, "bold"),
    "sidebar": ("Segoe UI", 11),
    "sidebar_heading": ("Segoe UI", 9, "bold"),
    "icon": ("Segoe UI", 16),
    "icon_lg": ("Segoe UI", 20),
    "price": ("Segoe UI", 14, "bold"),
    "badge": ("Segoe UI", 9, "bold"),
}

# =============================================================================
# User Roles
# =============================================================================
ROLES = {
    "admin": "Admin",
    "customer": "Customer",
    "vendor": "Vendor",
    "delivery": "Delivery Person",
}

# =============================================================================
# Order Status Flow
# =============================================================================
ORDER_STATUSES = ["placed", "preparing", "out_for_delivery", "delivered", "cancelled"]

ORDER_STATUS_LABELS = {
    "placed": "Order Placed",
    "preparing": "Preparing",
    "out_for_delivery": "Out for Delivery",
    "delivered": "Delivered",
    "cancelled": "Cancelled",
}

# =============================================================================
# Payment Methods
# =============================================================================
PAYMENT_METHODS = {
    "cod": "Cash on Delivery",
    "card": "Credit/Debit Card",
    "wallet": "Digital Wallet",
}

PAYMENT_STATUSES = ["pending", "paid", "failed"]

# =============================================================================
# Cuisine Categories
# =============================================================================
CUISINE_TYPES = [
    "Pakistani",
    "Chinese",
    "Fast Food",
    "Italian",
    "BBQ & Grill",
    "Desi",
    "Continental",
    "Desserts",
    "Beverages",
    "Other",
]

# =============================================================================
# Menu Item Categories
# =============================================================================
MENU_CATEGORIES = [
    "Starters",
    "Main Course",
    "Rice & Biryani",
    "BBQ",
    "Burgers",
    "Pizza",
    "Sandwiches",
    "Desserts",
    "Beverages",
    "Deals",
    "Other",
]

# =============================================================================
# Validation Constants
# =============================================================================
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 50
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_PRICE = 0.01
MAX_PRICE = 99999.99
MAX_QUANTITY = 50
PHONE_PATTERN = r"^(\+92|0)?[0-9]{10}$"
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# =============================================================================
# Security Questions (for password reset)
# =============================================================================
SECURITY_QUESTIONS = [
    "What is your pet's name?",
    "What is your mother's maiden name?",
    "What city were you born in?",
    "What is your favorite food?",
    "What was the name of your first school?",
]

# =============================================================================
# Pagination
# =============================================================================
ITEMS_PER_PAGE = 10
