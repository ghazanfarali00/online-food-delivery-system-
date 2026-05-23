"""Unit tests for database module."""
import sys, os, unittest, sqlite3, tempfile, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config
from database import Database


class TestDatabase(unittest.TestCase):
    """Tests for the Database class."""

    def setUp(self):
        """Create a fresh database for each test."""
        Database.reset_instance()
        config.DB_PATH = os.path.join(tempfile.gettempdir(), f'test_db_{uuid.uuid4().hex[:8]}.db')
        self._db_path = config.DB_PATH
        self.db = Database()

    def tearDown(self):
        """Close and cleanup test database."""
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_singleton_pattern(self):
        """Database should return same instance."""
        db2 = Database()
        self.assertIs(self.db, db2)

    def test_tables_created(self):
        """All required tables should exist."""
        tables = self.db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t['name'] for t in tables]
        expected = ['users', 'addresses', 'restaurants', 'menu_items',
                    'orders', 'order_items', 'reviews', 'notifications',
                    'support_tickets']
        for t in expected:
            self.assertIn(t, table_names, f"Table '{t}' not found")

    def test_admin_seeded(self):
        """Default admin user should exist."""
        admin = self.db.fetch_one(
            "SELECT * FROM users WHERE role = 'admin'"
        )
        self.assertIsNotNone(admin)
        self.assertEqual(admin['email'], 'admin@foodexpress.com')

    def test_sample_restaurants_seeded(self):
        """Sample restaurants should exist."""
        restaurants = self.db.fetch_all("SELECT * FROM restaurants")
        self.assertGreaterEqual(len(restaurants), 2)

    def test_sample_menu_items_seeded(self):
        """Sample menu items should exist."""
        items = self.db.fetch_all("SELECT * FROM menu_items")
        self.assertGreater(len(items), 0)

    def test_execute_insert(self):
        """Should be able to insert data."""
        cursor = self.db.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)",
            (1, "Test", "Test message")
        )
        self.assertIsNotNone(cursor.lastrowid)

    def test_fetch_one(self):
        """Should fetch a single row."""
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM users")
        self.assertIsNotNone(result)
        self.assertGreater(result['count'], 0)

    def test_fetch_all(self):
        """Should fetch multiple rows."""
        results = self.db.fetch_all("SELECT * FROM users")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_foreign_keys_enabled(self):
        """Foreign keys should be enabled."""
        result = self.db.fetch_one("PRAGMA foreign_keys")
        self.assertEqual(result[0], 1)


if __name__ == '__main__':
    unittest.main()
