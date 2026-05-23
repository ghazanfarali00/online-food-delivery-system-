"""Unit tests for controller classes."""
import sys, os, unittest, tempfile, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config
from database import Database
from controllers.auth_controller import AuthController
from controllers.customer_controller import CustomerController
from utils.exceptions import AuthenticationError, ValidationError, OrderError


class TestAuthController(unittest.TestCase):
    def setUp(self):
        Database.reset_instance()
        config.DB_PATH = os.path.join(tempfile.gettempdir(), f'test_ctrl_{uuid.uuid4().hex[:8]}.db')
        self._db_path = config.DB_PATH
        Database()
        self.auth = AuthController()

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_login_success(self):
        user = self.auth.login("admin@foodexpress.com", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'admin')

    def test_login_wrong_password(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("admin@foodexpress.com", "wrong")

    def test_login_nonexistent_email(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("nobody@test.com", "pass")

    def test_login_empty_fields(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("", "")

    def test_register_success(self):
        uid = self.auth.register("New User", "new@test.com", "03009999999",
            "password123", "password123", "customer", "Pet name?", "dog")
        self.assertIsNotNone(uid)

    def test_register_duplicate_email(self):
        with self.assertRaises(AuthenticationError):
            self.auth.register("Dup", "admin@foodexpress.com", "03008888888",
                "pass123", "pass123", "customer", "Q?", "a")

    def test_register_password_mismatch(self):
        with self.assertRaises(ValidationError):
            self.auth.register("Mis", "mis@test.com", "03007777777",
                "pass123", "pass456", "customer", "Q?", "a")

    def test_logout(self):
        self.auth.login("admin@foodexpress.com", "admin123")
        self.assertTrue(self.auth.is_logged_in())
        self.auth.logout()
        self.assertFalse(self.auth.is_logged_in())

    def test_get_security_question(self):
        q = self.auth.get_security_question("admin@foodexpress.com")
        self.assertIsNotNone(q)

    def test_security_question_nonexistent(self):
        with self.assertRaises(AuthenticationError):
            self.auth.get_security_question("nope@test.com")

    def test_reset_password(self):
        self.auth.reset_password("admin@foodexpress.com", "admin",
            "newpass123", "newpass123")
        user = self.auth.login("admin@foodexpress.com", "newpass123")
        self.assertIsNotNone(user)


class TestCustomerController(unittest.TestCase):
    def setUp(self):
        Database.reset_instance()
        config.DB_PATH = os.path.join(tempfile.gettempdir(), f'test_ctrl_{uuid.uuid4().hex[:8]}.db')
        self._db_path = config.DB_PATH
        Database()
        auth = AuthController()
        user = auth.login("sara@gmail.com", "customer123")
        self.ctrl = CustomerController(user)

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_get_all_restaurants(self):
        r = self.ctrl.get_all_restaurants()
        self.assertGreater(len(r), 0)

    def test_search_restaurants(self):
        r = self.ctrl.search_restaurants("Kitchen")
        self.assertGreater(len(r), 0)

    def test_get_restaurant_menu(self):
        items = self.ctrl.get_restaurant_menu(1)
        self.assertGreater(len(items), 0)

    def test_add_to_cart(self):
        items = self.ctrl.get_restaurant_menu(1)
        item = dict(items[0])
        self.ctrl.add_to_cart(1, item, 2)
        self.assertEqual(self.ctrl.get_cart_count(), 2)

    def test_cart_total(self):
        items = self.ctrl.get_restaurant_menu(1)
        item = dict(items[0])
        self.ctrl.add_to_cart(1, item, 1)
        self.assertEqual(self.ctrl.get_cart_total(), item['price'])

    def test_clear_cart(self):
        items = self.ctrl.get_restaurant_menu(1)
        self.ctrl.add_to_cart(1, dict(items[0]), 1)
        self.ctrl.clear_cart()
        self.assertEqual(self.ctrl.get_cart_count(), 0)

    def test_remove_from_cart(self):
        items = self.ctrl.get_restaurant_menu(1)
        item = dict(items[0])
        self.ctrl.add_to_cart(1, item, 1)
        self.ctrl.remove_from_cart(1, item['id'])
        self.assertEqual(self.ctrl.get_cart_count(), 0)

    def test_place_order(self):
        items = self.ctrl.get_restaurant_menu(1)
        self.ctrl.add_to_cart(1, dict(items[0]), 2)
        uid = self.ctrl.place_order('cod', '123 Test Street')
        self.assertTrue(uid.startswith('FE-'))

    def test_place_order_empty_cart(self):
        with self.assertRaises(OrderError):
            self.ctrl.place_order('cod', '123 Street')

    def test_get_my_orders(self):
        items = self.ctrl.get_restaurant_menu(1)
        self.ctrl.add_to_cart(1, dict(items[0]), 1)
        self.ctrl.place_order('cod', '123 Street')
        orders = self.ctrl.get_my_orders()
        self.assertGreater(len(orders), 0)

    def test_multi_restaurant_cart_blocked(self):
        items1 = self.ctrl.get_restaurant_menu(1)
        self.ctrl.add_to_cart(1, dict(items1[0]), 1)
        items2 = self.ctrl.get_restaurant_menu(2)
        with self.assertRaises(OrderError):
            self.ctrl.add_to_cart(2, dict(items2[0]), 1)


if __name__ == '__main__':
    unittest.main()
