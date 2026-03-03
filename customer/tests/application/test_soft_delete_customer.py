from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.application.soft_delete_customer import SoftDeleteCustomerService
from customer.domain.dto.soft_delete_customer_dto import SoftDeleteCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAuditOperationFailed,
    CustomerNotFound,
)
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.domain.repository.customer_notification_gateway import (
    CustomerNotificationGateway,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer
from notification.domain.exceptions.notification_exception import NotificationSaveFailed


class TestSoftDeleteCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_soft_delete',
            password='testpassword',
        )
        self.repository = DjangoCustomerRepository()
        self.audit_gateway = Mock(spec=CustomerAuditGateway)
        self.notification_gateway = Mock(spec=CustomerNotificationGateway)

    def test_execute_soft_deletes_customer_and_returns_id(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        other_user = get_user_model().objects.create_user(
            username='testuser_soft_delete_other',
            password='testpassword',
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        output = service.execute(
            SoftDeleteCustomerInput(
                customer_id=customer.id,
                updated_by=other_user.id,
            )
        )

        customer.refresh_from_db()

        self.assertEqual(output.customer_id, customer.id)
        self.assertFalse(customer.is_active)
        self.assertEqual(customer.updated_by_id, other_user.id)
        self.assertFalse(Customer.objects.filter(id=customer.id).exists())
        self.audit_gateway.log_customer_deleted.assert_called_once_with(
            customer_id=customer.id,
            deleted_by=other_user.id,
        )
        self.notification_gateway.notify_customer_deleted.assert_called_once_with(
            customer_id=customer.id,
            triggered_by=other_user.id,
        )

    def test_execute_raises_when_customer_not_found(self):
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with self.assertRaises(CustomerNotFound):
            service.execute(
                SoftDeleteCustomerInput(customer_id=9999, updated_by=self.user.id)
            )

    def test_execute_raises_when_customer_is_already_inactive(self):
        customer = Customer.all_objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with self.assertRaises(CustomerNotFound):
            service.execute(
                SoftDeleteCustomerInput(
                    customer_id=customer.id,
                    updated_by=self.user.id,
                )
            )

    def test_execute_logs_successful_soft_delete(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with patch('customer.application.soft_delete_customer.logger') as logger_mock:
            service.execute(
                SoftDeleteCustomerInput(
                    customer_id=customer.id,
                    updated_by=self.user.id,
                )
            )

        logger_mock.info.assert_any_call(
            'Starting customer soft delete id=%s', customer.id
        )
        logger_mock.info.assert_any_call(
            'Customer soft deleted successfully id=%s', customer.id
        )

    def test_execute_logs_warning_when_soft_delete_customer_is_not_found(self):
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )

        with patch('customer.application.soft_delete_customer.logger') as logger_mock:
            with self.assertRaises(CustomerNotFound):
                service.execute(
                    SoftDeleteCustomerInput(
                        customer_id=9999,
                        updated_by=self.user.id,
                    )
                )

        logger_mock.info.assert_called_once_with(
            'Starting customer soft delete id=%s', 9999
        )
        logger_mock.warning.assert_called_once_with(
            'Customer not found for soft delete id=%s', 9999
        )

    def test_execute_raises_customer_audit_operation_failed_when_audit_fails(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.audit_gateway.log_customer_deleted.side_effect = AuditSaveFailed(
            'soft_delete', 'customer'
        )

        with self.assertRaises(CustomerAuditOperationFailed):
            service.execute(
                SoftDeleteCustomerInput(
                    customer_id=customer.id,
                    updated_by=self.user.id,
                )
            )

        customer.refresh_from_db()
        self.assertTrue(customer.is_active)
        self.assertEqual(customer.updated_by_id, self.user.id)

    def test_execute_logs_exception_when_audit_fails(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.audit_gateway.log_customer_deleted.side_effect = AuditSaveFailed(
            'soft_delete', 'customer'
        )

        with patch('customer.application.soft_delete_customer.logger') as logger_mock:
            with self.assertRaises(CustomerAuditOperationFailed):
                service.execute(
                    SoftDeleteCustomerInput(
                        customer_id=customer.id,
                        updated_by=self.user.id,
                    )
                )

        logger_mock.info.assert_called_once_with(
            'Starting customer soft delete id=%s', customer.id
        )
        logger_mock.exception.assert_called_once_with(
            'Audit failure during customer soft delete customer_id=%s',
            customer.id,
        )

    def test_execute_logs_exception_when_notification_fails_and_keeps_delete(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = SoftDeleteCustomerService(
            self.repository, self.audit_gateway, self.notification_gateway
        )
        self.notification_gateway.notify_customer_deleted.side_effect = (
            NotificationSaveFailed('delete', 'customer')
        )

        with patch('customer.application.soft_delete_customer.logger') as logger_mock:
            output = service.execute(
                SoftDeleteCustomerInput(
                    customer_id=customer.id,
                    updated_by=self.user.id,
                )
            )

        customer.refresh_from_db()
        self.assertEqual(output.customer_id, customer.id)
        self.assertFalse(customer.is_active)
        logger_mock.exception.assert_called_once_with(
            'Notification failure during customer soft delete customer_id=%s',
            customer.id,
        )
