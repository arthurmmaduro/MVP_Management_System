from django.test import TestCase

from customer.domain.constants.constants import (
    CUSTOMER_NAME_MAX_LENGTH,
    CUSTOMER_NAME_MIN_LENGTH,
)
from customer.domain.exceptions.customer_exceptions import (
    CustomerNameIsEmpty,
    CustomerNameIsTooLong,
    CustomerNameIsTooShort,
)
from customer.domain.value_objects.customer_name import CustomerName


class TestCustomerName(TestCase):
    def test_parse_normalize_spaces(self):
        name = CustomerName.parse('   Test   Customer   ')
        self.assertEqual(name.name, 'Test Customer')

    def teste_parse_raises_whem_empty_name(self):
        with self.assertRaises(CustomerNameIsEmpty):
            CustomerName.parse('')

    def test_parse_raises_whem_only_whitespaces(self):
        with self.assertRaises(CustomerNameIsEmpty):
            CustomerName.parse('  \t  \n   ')

    def test_parse_raises_whem_name_is_too_long(self):
        raw = 'a' * (CUSTOMER_NAME_MAX_LENGTH + 1)
        with self.assertRaises(CustomerNameIsTooLong):
            CustomerName.parse(raw)

    def test_parse_raises_whem_name_is_too_short(self):
        raw = 'a' * (CUSTOMER_NAME_MIN_LENGTH - 1)
        with self.assertRaises(CustomerNameIsTooShort):
            CustomerName.parse(raw)

    def test_parse_accepts_whem_max_length(self):
        raw = 'a' * CUSTOMER_NAME_MAX_LENGTH
        name = CustomerName.parse(raw)
        self.assertEqual(name.name, raw)

    def test_parse_accepts_whem_min_length(self):
        raw = 'a' * CUSTOMER_NAME_MIN_LENGTH
        name = CustomerName.parse(raw)
        self.assertEqual(name.name, raw)

    def test_parse_returns_name(self):
        name = CustomerName.parse('Test Customer')
        self.assertEqual(str(name), 'Test Customer')

    def test_constructor_normalizes_name_in_post_init(self):
        name = CustomerName(name='  Maria   Silva  ')
        self.assertEqual(name.name, 'Maria Silva')

    def test_constructor_raises_when_name_is_invalid(self):
        with self.assertRaises(CustomerNameIsEmpty):
            CustomerName(name='   ')
