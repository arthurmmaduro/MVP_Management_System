from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from customer.domain.exceptions.customer_exceptions import CustomerSaveFailed
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestDjangoCustomerRepository(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_repository', password='testpassword'
        )
        self.repository = DjangoCustomerRepository()

    def test_save_raises_customer_save_failed_when_integrity_error_is_not_duplicate_name(
        self,
    ):
        customer = Customer(
            name='Repository Customer',
            created_by=self.user,
            updated_by=self.user,
        )

        with patch.object(customer, 'save', side_effect=IntegrityError('boom')):
            with patch(
                'customer.infrastructure.django_customer_repository.Customer.objects.filter'
            ) as filter_mock:
                filter_mock.return_value.exclude.return_value.exists.return_value = False

                with self.assertRaises(CustomerSaveFailed) as context:
                    self.repository.save(customer)

        self.assertEqual(
            str(context.exception), 'Erro ao salvar o cliente: Repository Customer'
        )
