"""Unit tests for validators module."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from utils.validators import (validate_email, validate_phone, validate_password,
    validate_name, validate_price, validate_quantity, validate_rating, validate_required)
from utils.exceptions import ValidationError


class TestValidateEmail(unittest.TestCase):
    """Tests for email validation."""

    def test_valid_email(self):
        self.assertEqual(validate_email("test@example.com"), "test@example.com")

    def test_valid_email_uppercase(self):
        self.assertEqual(validate_email("Test@Example.COM"), "test@example.com")

    def test_empty_email_raises(self):
        with self.assertRaises(ValidationError):
            validate_email("")

    def test_none_email_raises(self):
        with self.assertRaises(ValidationError):
            validate_email(None)

    def test_invalid_format_raises(self):
        with self.assertRaises(ValidationError):
            validate_email("notanemail")

    def test_missing_domain_raises(self):
        with self.assertRaises(ValidationError):
            validate_email("test@")


class TestValidatePhone(unittest.TestCase):
    """Tests for phone validation."""

    def test_valid_phone(self):
        self.assertEqual(validate_phone("03001234567"), "03001234567")

    def test_valid_phone_with_plus(self):
        result = validate_phone("+923001234567")
        self.assertIsNotNone(result)

    def test_empty_phone_raises(self):
        with self.assertRaises(ValidationError):
            validate_phone("")

    def test_short_phone_raises(self):
        with self.assertRaises(ValidationError):
            validate_phone("12345")


class TestValidatePassword(unittest.TestCase):
    """Tests for password validation."""

    def test_valid_password(self):
        self.assertEqual(validate_password("abcdef"), "abcdef")

    def test_short_password_raises(self):
        with self.assertRaises(ValidationError):
            validate_password("abc")

    def test_empty_password_raises(self):
        with self.assertRaises(ValidationError):
            validate_password("")

    def test_none_password_raises(self):
        with self.assertRaises(ValidationError):
            validate_password(None)


class TestValidateName(unittest.TestCase):
    """Tests for name validation."""

    def test_valid_name(self):
        self.assertEqual(validate_name("John"), "John")

    def test_strips_whitespace(self):
        self.assertEqual(validate_name("  Ali  "), "Ali")

    def test_short_name_raises(self):
        with self.assertRaises(ValidationError):
            validate_name("A")

    def test_empty_raises(self):
        with self.assertRaises(ValidationError):
            validate_name("")


class TestValidatePrice(unittest.TestCase):
    """Tests for price validation."""

    def test_valid_price(self):
        self.assertEqual(validate_price(99.99), 99.99)

    def test_string_price(self):
        self.assertEqual(validate_price("250"), 250.0)

    def test_zero_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_price(0)

    def test_negative_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_price(-10)

    def test_invalid_string_raises(self):
        with self.assertRaises(ValidationError):
            validate_price("abc")


class TestValidateQuantity(unittest.TestCase):
    """Tests for quantity validation."""

    def test_valid_quantity(self):
        self.assertEqual(validate_quantity(5), 5)

    def test_string_quantity(self):
        self.assertEqual(validate_quantity("3"), 3)

    def test_zero_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity(0)

    def test_over_max_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity(100)


class TestValidateRating(unittest.TestCase):
    """Tests for rating validation."""

    def test_valid_rating(self):
        self.assertEqual(validate_rating(5), 5)

    def test_min_rating(self):
        self.assertEqual(validate_rating(1), 1)

    def test_zero_raises(self):
        with self.assertRaises(ValidationError):
            validate_rating(0)

    def test_over_five_raises(self):
        with self.assertRaises(ValidationError):
            validate_rating(6)


class TestValidateRequired(unittest.TestCase):
    """Tests for required field validation."""

    def test_valid_value(self):
        self.assertEqual(validate_required("hello", "Field"), "hello")

    def test_empty_raises(self):
        with self.assertRaises(ValidationError):
            validate_required("", "Field")

    def test_none_raises(self):
        with self.assertRaises(ValidationError):
            validate_required(None, "Field")


if __name__ == '__main__':
    unittest.main()
