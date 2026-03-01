from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.list_customer import ListCustomerService
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestListCustomerServiceLogging(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_list_customer_logging',
            password='testpassword',
        )
        self.repository = DjangoCustomerRepository()

    def test_execute_logs_start_and_result_count(self):
        Customer.objects.create(
            name='Alpha Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        Customer.objects.create(
            name='Zulu Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = ListCustomerService(self.repository)

        with patch('customer.application.list_customer.logger') as logger_mock:
            service.execute()

        logger_mock.info.assert_any_call('Starting customer list')
        logger_mock.info.assert_any_call(
            'Customer list loaded successfully count=%s', 2
        )
