from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.domain.exceptions.customer_exceptions import CustomerAlreadyExists
from customer.domain.rules.ensure_customer_name_is_unique import ensure_name_unique
from customer.domain.value_objects.customer_name import CustomerName
from customer.models import Customer


class TestEnsureCustomerNameIsUnique(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_rules', password='testpassword'
        )

    def test_ensure_name_unique(self):
        Customer.objects.create(
            name='Test Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        with self.assertRaises(CustomerAlreadyExists):
            ensure_name_unique(CustomerName.parse('Test Customer'))

    def test_ensure_name_unique_ignores_inactive_customer(self):
        Customer.objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )

        try:
            ensure_name_unique(CustomerName.parse('Inactive Customer'))
        except CustomerAlreadyExists:
            self.fail('ensure_name_unique raised CustomerAlreadyExists unexpectedly')
