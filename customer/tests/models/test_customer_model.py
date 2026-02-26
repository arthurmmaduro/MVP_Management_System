from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from customer.models import Customer


class TestCustomerModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test-user',
            password='test-pass-123',
        )

    def _create_customer(self, **kwargs):
        defaults = {
            'name': 'Test Customer',
            'created_by': self.user,
            'updated_by': self.user,
        }
        defaults.update(kwargs)
        return Customer.objects.create(**defaults)

    def test_customer_creation(self):
        customer = self._create_customer()
        self.assertEqual(customer.name, 'Test Customer')
        self.assertTrue(customer.is_active)

    def test_customer_str_method(self):
        customer = self._create_customer(name='String Representation')
        self.assertEqual(str(customer), 'String Representation')

    def test_same_name_for_two_active_customers_is_not_allowed(self):
        self._create_customer(name='Duplicated Name', is_active=True)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_customer(name='Duplicated Name', is_active=True)

    def test_same_name_for_inactive_customers_is_allowed(self):
        self._create_customer(name='Inactive Name', is_active=False)
        customer = self._create_customer(name='Inactive Name', is_active=False)

        self.assertFalse(customer.is_active)

    def test_same_name_for_active_and_inactive_customers_is_allowed(self):
        self._create_customer(name='Mixed Name', is_active=True)
        customer = self._create_customer(name='Mixed Name', is_active=False)

        self.assertFalse(customer.is_active)

    def test_customer_manager_returns_only_active_customers(self):
        active_customer = self._create_customer(name='Active Customer', is_active=True)
        self._create_customer(name='Inactive Customer', is_active=False)

        customers = list(Customer.objects.all())

        self.assertEqual(customers, [active_customer])

    def test_created_by_is_required(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Customer.objects.create(
                    name='Missing Created By',
                    updated_by=self.user,
                )

    def test_updated_by_is_required(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Customer.objects.create(
                    name='Missing Updated By',
                    created_by=self.user,
                )
