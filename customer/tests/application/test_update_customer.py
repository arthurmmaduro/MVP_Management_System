from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.application.update_customer import UpdateCustomerService
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerAuditOperationFailed,
    CustomerNameIsEmpty,
    CustomerNameIsTooShort,
    CustomerNotFound,
)
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.domain.repository.customer_notification_gateway import (
    CustomerNotificationGateway,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer
from notification.domain.exceptions.notification_exception import NotificationSaveFailed


class TestUpdateCustomerService(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='testuser_update', password='testpassword'
        )
        self.other_user = user_model.objects.create_user(
            username='testuser_update_other', password='testpassword'
        )
        self.repository = DjangoCustomerRepository()
        self.audit_gateway = Mock(spec=CustomerAuditGateway)
        self.notification_gateway = Mock(spec=CustomerNotificationGateway)

    def test_execute_updates_customer_and_returns_same_id(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        output = service.execute(
            UpdateCustomerInput(
                customer_id=customer.id,
                name='Updated Customer',
                updated_by=self.other_user.id,
            )
        )

        customer.refresh_from_db()

        self.assertEqual(output.customer_id, customer.id)
        self.assertEqual(customer.name, 'Updated Customer')
        self.assertEqual(customer.updated_by_id, self.other_user.id)
        self.assertEqual(customer.created_by_id, self.user.id)
        self.audit_gateway.log_customer_updated.assert_called_once_with(
            customer_id=customer.id,
            updated_by=self.other_user.id,
            metadata={
                'before': {'name': 'Old Customer'},
                'after': {'name': 'Updated Customer'},
            },
        )
        self.notification_gateway.notify_customer_updated.assert_called_once_with(
            customer_id=customer.id,
            triggered_by=self.other_user.id,
            metadata={
                'before': {'name': 'Old Customer'},
                'after': {'name': 'Updated Customer'},
            },
        )

    def test_execute_raises_when_customer_not_found(self):
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with self.assertRaises(CustomerNotFound):
            service.execute(
                UpdateCustomerInput(
                    customer_id=9999,
                    name='Updated Customer',
                    updated_by=self.user.id,
                )
            )

    def test_execute_raises_when_customer_name_already_exists(self):
        customer = Customer.objects.create(
            name='Original Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        Customer.objects.create(
            name='Duplicated Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with self.assertRaises(CustomerAlreadyExists):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='Duplicated Customer',
                    updated_by=self.user.id,
                )
            )

    def test_execute_allows_name_used_by_inactive_customer(self):
        customer = Customer.objects.create(
            name='Original Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        Customer.objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        output = service.execute(
            UpdateCustomerInput(
                customer_id=customer.id,
                name='Inactive Customer',
                updated_by=self.user.id,
            )
        )

        customer.refresh_from_db()

        self.assertEqual(output.customer_id, customer.id)
        self.assertEqual(customer.name, 'Inactive Customer')

    def test_execute_raises_when_customer_name_is_invalid(self):
        customer = Customer.objects.create(
            name='Original Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with self.assertRaises(CustomerNameIsEmpty):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='   ',
                    updated_by=self.user.id,
                )
            )

    def test_execute_raises_customer_audit_operation_failed_when_audit_fails(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.audit_gateway.log_customer_updated.side_effect = AuditSaveFailed(
            'update', 'customer'
        )

        with self.assertRaises(CustomerAuditOperationFailed):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='Updated Customer',
                    updated_by=self.other_user.id,
                )
            )

        customer.refresh_from_db()
        self.assertEqual(customer.name, 'Old Customer')
        self.assertEqual(customer.updated_by_id, self.user.id)

    def test_execute_logs_exception_when_audit_fails(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.audit_gateway.log_customer_updated.side_effect = AuditSaveFailed(
            'update', 'customer'
        )

        with patch('customer.application.update_customer.logger') as logger_mock:
            with self.assertRaises(CustomerAuditOperationFailed):
                service.execute(
                    UpdateCustomerInput(
                        customer_id=customer.id,
                        name='Updated Customer',
                        updated_by=self.other_user.id,
                    )
                )

        logger_mock.info.assert_called_once_with(
            'Starting customer update id=%s', customer.id
        )
        logger_mock.exception.assert_called_once_with(
            'Audit failure during customer update customer_id=%s',
            customer.id,
        )

        with self.assertRaises(CustomerNameIsTooShort):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='ab',
                    updated_by=self.user.id,
                )
            )

    def test_execute_logs_exception_when_notification_fails_and_keeps_update(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.notification_gateway.notify_customer_updated.side_effect = (
            NotificationSaveFailed('update', 'customer')
        )

        with patch('customer.application.update_customer.logger') as logger_mock:
            output = service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='Updated Customer',
                    updated_by=self.other_user.id,
                )
            )

        customer.refresh_from_db()
        self.assertEqual(output.customer_id, customer.id)
        self.assertEqual(customer.name, 'Updated Customer')
        self.assertEqual(customer.updated_by_id, self.other_user.id)
        logger_mock.exception.assert_called_once_with(
            'Notification failure during customer update customer_id=%s',
            customer.id,
        )
