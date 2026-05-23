"""
Database module for the Online Food Delivery System.
Handles SQLite connection management and schema creation.
"""

import sqlite3
import hashlib
import os
import config
from utils.exceptions import DatabaseError


class Database:
    """Singleton database manager for SQLite connections and operations."""

    _instance = None

    def __new__(cls):
        """Ensure only one database instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize database connection and create tables."""
        if self._initialized:
            return
        try:
            self.connection = sqlite3.connect(config.DB_PATH)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._create_tables()
            self._seed_default_data()
            self._initialized = True
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}")

    def _create_tables(self):
        """Create all database tables if they don't exist."""
        cursor = self.connection.cursor()
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin','customer','vendor','delivery')),
                    security_question TEXT,
                    security_answer TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Addresses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    label TEXT NOT NULL,
                    address_line TEXT NOT NULL,
                    city TEXT NOT NULL,
                    zip_code TEXT,
                    is_default INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Restaurants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    cuisine_type TEXT,
                    location TEXT,
                    avg_rating REAL DEFAULT 0.0,
                    total_reviews INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Menu items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    price REAL NOT NULL CHECK(price > 0),
                    is_available INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
                )
            """)

            # Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_uid TEXT UNIQUE NOT NULL,
                    customer_id INTEGER NOT NULL,
                    restaurant_id INTEGER NOT NULL,
                    delivery_person_id INTEGER,
                    address_id INTEGER,
                    status TEXT DEFAULT 'placed'
                        CHECK(status IN ('placed','preparing','out_for_delivery','delivered','cancelled')),
                    payment_method TEXT DEFAULT 'cod'
                        CHECK(payment_method IN ('cod','card','wallet')),
                    payment_status TEXT DEFAULT 'pending'
                        CHECK(payment_status IN ('pending','paid','failed')),
                    total_amount REAL NOT NULL DEFAULT 0,
                    delivery_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Order items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    unit_price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                )
            """)

            # Reviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    restaurant_id INTEGER NOT NULL,
                    order_id INTEGER,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
                )
            """)

            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Support tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved','closed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to create tables: {e}")

    def _seed_default_data(self):
        """Insert default admin user and sample data if tables are empty."""
        cursor = self.connection.cursor()
        try:
            # Check if admin exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, security_question, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("Admin", "admin@foodexpress.com", "03001234567", admin_password,
                      "admin", "What is your pet's name?", hashlib.sha256("admin".encode()).hexdigest()))

                # Create sample vendor
                vendor_password = hashlib.sha256("vendor123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, security_question, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("Ali's Kitchen", "ali@kitchen.com", "03009876543", vendor_password,
                      "vendor", "What is your favorite food?", hashlib.sha256("biryani".encode()).hexdigest()))

                vendor_id = cursor.lastrowid

                # Create sample restaurant
                cursor.execute("""
                    INSERT INTO restaurants (vendor_id, name, description, cuisine_type, location, avg_rating)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (vendor_id, "Ali's Kitchen", "Authentic Pakistani cuisine with a modern twist",
                      "Pakistani", "Lahore", 4.5))
                rest_id = cursor.lastrowid

                # Create sample menu items
                sample_items = [
                    ("Chicken Biryani", "Aromatic basmati rice with tender chicken pieces", "Rice & Biryani", 350),
                    ("Beef Karahi", "Spicy beef cooked in traditional karahi", "Main Course", 650),
                    ("Chicken Tikka", "Juicy marinated chicken grilled to perfection", "BBQ", 450),
                    ("Seekh Kebab", "Minced meat kebabs with special spices", "BBQ", 300),
                    ("Naan", "Freshly baked tandoori naan bread", "Main Course", 50),
                    ("Raita", "Cool yogurt with cucumber and mint", "Starters", 80),
                    ("Gulab Jamun", "Sweet milk dumplings in sugar syrup", "Desserts", 150),
                    ("Lassi", "Traditional yogurt drink — sweet or salty", "Beverages", 120),
                ]
                for name, desc, cat, price in sample_items:
                    cursor.execute("""
                        INSERT INTO menu_items (restaurant_id, name, description, category, price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (rest_id, name, desc, cat, price))

                # Create second sample vendor + restaurant
                vendor2_password = hashlib.sha256("vendor123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, security_question, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("Burger Lab", "burger@lab.com", "03111234567", vendor2_password,
                      "vendor", "What city were you born in?", hashlib.sha256("karachi".encode()).hexdigest()))
                vendor2_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO restaurants (vendor_id, name, description, cuisine_type, location, avg_rating)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (vendor2_id, "Burger Lab", "Premium gourmet burgers and loaded fries",
                      "Fast Food", "Islamabad", 4.2))
                rest2_id = cursor.lastrowid

                burger_items = [
                    ("Classic Smash Burger", "Juicy smashed beef patty with cheese", "Burgers", 550),
                    ("Chicken Zinger", "Crispy fried chicken burger", "Burgers", 450),
                    ("Loaded Fries", "Fries topped with cheese and jalapenos", "Starters", 350),
                    ("Chocolate Shake", "Thick chocolate milkshake", "Beverages", 250),
                    ("Pepperoni Pizza", "Classic pizza with pepperoni and mozzarella", "Pizza", 800),
                    ("Chicken Wings", "Spicy buffalo wings — 6 pieces", "Starters", 400),
                ]
                for name, desc, cat, price in burger_items:
                    cursor.execute("""
                        INSERT INTO menu_items (restaurant_id, name, description, category, price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (rest2_id, name, desc, cat, price))

                # Create sample delivery person
                delivery_password = hashlib.sha256("delivery123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, security_question, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("Ahmed Rider", "ahmed@rider.com", "03211234567", delivery_password,
                      "delivery", "What is your pet's name?", hashlib.sha256("cat".encode()).hexdigest()))

                # Create sample customer
                customer_password = hashlib.sha256("customer123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, security_question, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("Sara Customer", "sara@gmail.com", "03331234567", customer_password,
                      "customer", "What city were you born in?", hashlib.sha256("lahore".encode()).hexdigest()))
                customer_id = cursor.lastrowid

                # Add sample address for customer
                cursor.execute("""
                    INSERT INTO addresses (user_id, label, address_line, city, zip_code, is_default)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (customer_id, "Home", "123 Main Street, Gulberg", "Lahore", "54000", 1))

            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to seed data: {e}")

    def execute(self, query, params=None):
        """Execute a query and return the cursor."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise DatabaseError(f"Query execution failed: {e}")

    def fetch_one(self, query, params=None):
        """Execute a query and return a single row."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise DatabaseError(f"Fetch failed: {e}")

    def fetch_all(self, query, params=None):
        """Execute a query and return all rows."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Fetch failed: {e}")

    def close(self):
        """Close the database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)."""
        if cls._instance and hasattr(cls._instance, 'connection'):
            try:
                cls._instance.connection.close()
            except Exception:
                pass
        cls._instance = None
