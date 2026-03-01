from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.detail_customer import DetailCustomerService
from customer.domain.dto.detail_customer_dto import CustomerDetailInput
from customer.domain.dto.detail_customer_dto import CustomerDetailOutput
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestDetailCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_detail_customer',
            password='testpassword',
        )
        self.other_user = get_user_model().objects.create_user(
            username='testuser_detail_customer_other',
            password='testpassword',
        )
        self.repository = DjangoCustomerRepository()

    def test_execute_returns_customer_details(self):
        customer = Customer.objects.create(
            name='Detail Customer',
            created_by_id=self.user.id,
            updated_by_id=self.other_user.id,
        )
        service = DetailCustomerService(self.repository)

        output = service.execute(CustomerDetailInput(customer_id=customer.id))

        self.assertEqual(
            output,
            CustomerDetailOutput(
                customer_id=customer.id,
                name='Detail Customer',
                created_by=self.user.id,
                updated_by=self.other_user.id,
            ),
        )

    def test_execute_raises_when_customer_not_found(self):
        service = DetailCustomerService(self.repository)

        with self.assertRaises(CustomerNotFound):
            service.execute(CustomerDetailInput(customer_id=9999))

    def test_execute_logs_successful_detail_lookup(self):
        customer = Customer.objects.create(
            name='Detail Customer',
            created_by_id=self.user.id,
            updated_by_id=self.other_user.id,
        )
        service = DetailCustomerService(self.repository)

        with patch('customer.application.detail_customer.logger') as logger_mock:
            service.execute(CustomerDetailInput(customer_id=customer.id))

        logger_mock.info.assert_any_call('Starting customer detail id=%s', customer.id)
        logger_mock.info.assert_any_call(
            'Customer detail loaded successfully id=%s', customer.id
        )

    def test_execute_logs_warning_when_customer_is_not_found(self):
        service = DetailCustomerService(self.repository)

        with patch('customer.application.detail_customer.logger') as logger_mock:
            with self.assertRaises(CustomerNotFound):
                service.execute(CustomerDetailInput(customer_id=9999))

        logger_mock.info.assert_called_once_with('Starting customer detail id=%s', 9999)
        logger_mock.warning.assert_called_once_with(
            'Customer not found for detail id=%s', 9999
        )
