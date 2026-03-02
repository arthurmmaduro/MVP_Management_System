from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.update_customer import UpdateCustomerService
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestUpdateCustomerServiceLogging(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='testuser_update_logging',
            password='testpassword',
        )
        self.other_user = user_model.objects.create_user(
            username='testuser_update_logging_other',
            password='testpassword',
        )
        self.repository = DjangoCustomerRepository()
        self.audit_gateway = Mock(spec=CustomerAuditGateway)

    def test_execute_logs_successful_update(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(self.repository, self.audit_gateway)

        with patch('customer.application.update_customer.logger') as logger_mock:
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='Updated Customer',
                    updated_by=self.other_user.id,
                )
            )

        logger_mock.info.assert_any_call('Starting customer update id=%s', customer.id)
        logger_mock.info.assert_any_call(
            'Customer updated successfully id=%s', customer.id
        )

    def test_execute_logs_warning_when_customer_is_not_found(self):
        service = UpdateCustomerService(self.repository, self.audit_gateway)

        with patch('customer.application.update_customer.logger') as logger_mock:
            with self.assertRaises(CustomerNotFound):
                service.execute(
                    UpdateCustomerInput(
                        customer_id=9999,
                        name='Updated Customer',
                        updated_by=self.user.id,
                    )
                )

        logger_mock.info.assert_called_once_with('Starting customer update id=%s', 9999)
        logger_mock.warning.assert_called_once_with(
            'Customer not found for update id=%s', 9999
        )
