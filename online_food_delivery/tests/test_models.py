"""Unit tests for model classes."""
import sys, os, unittest, tempfile, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config

from database import Database
from models.user import UserModel, AddressModel
from models.restaurant import RestaurantModel, MenuItemModel
from models.order import OrderModel
from models.review import ReviewModel
from models.notification import NotificationModel, SupportTicketModel
from utils.exceptions import NotFoundError


def fresh_db():
    """Create a fresh database with a unique filename."""
    Database.reset_instance()
    config.DB_PATH = os.path.join(tempfile.gettempdir(), f'test_models_{uuid.uuid4().hex[:8]}.db')
    return Database()


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self.model = UserModel()
        self._db_path = config.DB_PATH

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_create_user(self):
        uid = self.model.create_user("Test User", "test@test.com", "03001111111",
            "password123", "customer", "Pet name?", "dog")
        self.assertIsNotNone(uid)

    def test_get_user_by_email(self):
        self.model.create_user("Test2", "test2@test.com", "03002222222",
            "pass", "customer")
        user = self.model.get_user_by_email("test2@test.com")
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "Test2")

    def test_get_user_by_id(self):
        # Admin is seeded with id 1
        user = self.model.get_user_by_id(1)
        self.assertIsNotNone(user)

    def test_get_nonexistent_user_raises(self):
        with self.assertRaises(NotFoundError):
            self.model.get_user_by_id(9999)

    def test_update_user(self):
        uid = self.model.create_user("Old", "old@test.com", "03003333333",
            "pass", "customer")
        self.model.update_user(uid, name="New Name")
        user = self.model.get_user_by_id(uid)
        self.assertEqual(user['name'], "New Name")

    def test_toggle_active(self):
        uid = self.model.create_user("Active", "active@test.com", "03004444444",
            "pass", "customer")
        self.model.toggle_active(uid, False)
        user = self.model.get_user_by_id(uid)
        self.assertEqual(user['is_active'], 0)

    def test_get_all_users(self):
        users = self.model.get_all_users()
        self.assertGreater(len(users), 0)

    def test_get_users_by_role(self):
        users = self.model.get_all_users(role='admin')
        for u in users:
            self.assertEqual(u['role'], 'admin')


class TestAddressModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = AddressModel()
        self.user_model = UserModel()
        self.uid = self.user_model.create_user("Addr User", "addr@test.com",
            "03005555555", "pass", "customer")

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_add_address(self):
        aid = self.model.add_address(self.uid, "Home", "123 St", "Lahore", "54000")
        self.assertIsNotNone(aid)

    def test_get_user_addresses(self):
        self.model.add_address(self.uid, "Home", "123 St", "Lahore")
        addrs = self.model.get_user_addresses(self.uid)
        self.assertEqual(len(addrs), 1)

    def test_delete_address(self):
        aid = self.model.add_address(self.uid, "Work", "456 Ave", "Karachi")
        self.model.delete_address(aid)
        addrs = self.model.get_user_addresses(self.uid)
        self.assertEqual(len([a for a in addrs if a['id'] == aid]), 0)


class TestRestaurantModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = RestaurantModel()

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_get_all_restaurants(self):
        restaurants = self.model.get_all_restaurants()
        self.assertGreater(len(restaurants), 0)

    def test_search_restaurants(self):
        results = self.model.search_restaurants("Kitchen")
        self.assertGreater(len(results), 0)

    def test_get_restaurant_by_id(self):
        rest = self.model.get_restaurant_by_id(1)
        self.assertIsNotNone(rest)

    def test_nonexistent_restaurant_raises(self):
        with self.assertRaises(NotFoundError):
            self.model.get_restaurant_by_id(9999)


class TestMenuItemModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = MenuItemModel()

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_get_restaurant_menu(self):
        items = self.model.get_restaurant_menu(1)
        self.assertGreater(len(items), 0)

    def test_add_item(self):
        iid = self.model.add_item(1, "New Item", "Desc", "Starters", 100)
        self.assertIsNotNone(iid)

    def test_toggle_availability(self):
        iid = self.model.add_item(1, "Toggle", "Desc", "Main", 200)
        self.model.toggle_availability(iid, False)
        item = self.model.get_item_by_id(iid)
        self.assertEqual(item['is_available'], 0)

    def test_delete_item(self):
        iid = self.model.add_item(1, "Delete Me", "Desc", "Main", 50)
        self.model.delete_item(iid)
        with self.assertRaises(NotFoundError):
            self.model.get_item_by_id(iid)


class TestOrderModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = OrderModel()

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_create_order(self):
        items = [{'menu_item_id': 1, 'item_name': 'Biryani', 'quantity': 2, 'unit_price': 350}]
        # Use seeded customer id
        customers = Database().fetch_all("SELECT id FROM users WHERE role='customer'")
        cid = customers[0]['id']
        uid = self.model.create_order(cid, 1, items, 'cod', '123 Street')
        self.assertTrue(uid.startswith('FE-'))

    def test_empty_items_raises(self):
        from utils.exceptions import OrderError
        with self.assertRaises(OrderError):
            self.model.create_order(1, 1, [], 'cod', 'Addr')

    def test_get_order_stats(self):
        stats = self.model.get_order_stats()
        self.assertIn('total_orders', stats)
        self.assertIn('total_revenue', stats)


class TestReviewModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = ReviewModel()
        customers = self.db.fetch_all("SELECT id FROM users WHERE role='customer'")
        self.cid = customers[0]['id']

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_add_review(self):
        rid = self.model.add_review(self.cid, 1, 5, "Great food!")
        self.assertIsNotNone(rid)

    def test_get_restaurant_reviews(self):
        self.model.add_review(self.cid, 1, 4, "Good")
        reviews = self.model.get_restaurant_reviews(1)
        self.assertGreater(len(reviews), 0)

    def test_has_reviewed(self):
        self.model.add_review(self.cid, 1, 3, "Ok")
        self.assertTrue(self.model.has_reviewed(self.cid, 1))

    def test_delete_review(self):
        rid = self.model.add_review(self.cid, 1, 2, "Bad")
        self.model.delete_review(rid)
        r = self.model.get_review_by_id(rid)
        self.assertIsNone(r)


class TestNotificationModel(unittest.TestCase):
    def setUp(self):
        self.db = fresh_db()
        self._db_path = config.DB_PATH
        self.model = NotificationModel()

    def tearDown(self):
        Database.reset_instance()
        try: os.remove(self._db_path)
        except OSError: pass

    def test_create_notification(self):
        nid = self.model.create_notification(1, "Test", "Test message")
        self.assertIsNotNone(nid)

    def test_unread_count(self):
        self.model.create_notification(1, "N1", "Msg1")
        self.model.create_notification(1, "N2", "Msg2")
        count = self.model.get_unread_count(1)
        self.assertGreaterEqual(count, 2)

    def test_mark_as_read(self):
        nid = self.model.create_notification(1, "Read", "Read me")
        self.model.mark_as_read(nid)
        notifs = self.model.get_user_notifications(1)
        found = [n for n in notifs if n['id'] == nid]
        self.assertEqual(found[0]['is_read'], 1)


if __name__ == '__main__':
    unittest.main()
