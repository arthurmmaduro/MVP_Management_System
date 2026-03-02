from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from audit.domain.exception.audit_exception import AuditSaveFailed
from customer.application.create_customer import CreateCustomerService
from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerAuditFailed,
    CustomerNameIsEmpty,
    CustomerNameIsTooShort,
)
from customer.domain.repository.customer_audit_gateway import CustomerAuditGateway
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestCreateCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.repository = DjangoCustomerRepository()
        self.audit_gateway = Mock(spec=CustomerAuditGateway)

    def test_execute_creates_customer_and_returns_id(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)

        self.assertIsNotNone(output.customer_id)
        self.assertTrue(Customer.objects.filter(pk=output.customer_id).exists())
        self.audit_gateway.log_customer_created.assert_called_once_with(
            customer_id=output.customer_id,
            created_by=self.user.id,
        )

    def test_execute_uses_default_is_active_true(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertTrue(customer.is_active)

    def test_execute_creates_timestamp(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)
        self.assertLessEqual(customer.created_at, customer.updated_at)

    def test_execute_raises_when_customer_name_already_exists(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        Customer.objects.create(
            name='Duplicated Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        input_dto = CreateCustomerInput(
            name='Duplicated Customer',
            created_by=self.user.id,
            updated_by=self.user.id,
        )

        with self.assertRaises(CustomerAlreadyExists):
            service.execute(input_dto)

    def test_execute_raises_when_customer_name_is_invalid(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)

        with self.assertRaises(CustomerNameIsEmpty):
            service.execute(
                CreateCustomerInput(
                    name='   ',
                    created_by=self.user.id,
                    updated_by=self.user.id,
                )
            )

        with self.assertRaises(CustomerNameIsTooShort):
            service.execute(
                CreateCustomerInput(
                    name='ab',
                    created_by=self.user.id,
                    updated_by=self.user.id,
                )
            )

    def test_execute_raises_customer_audit_failed_when_audit_fails(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        self.audit_gateway.log_customer_created.side_effect = AuditSaveFailed(
            'create', 'customer'
        )

        with self.assertRaises(CustomerAuditFailed):
            service.execute(
                CreateCustomerInput(
                    name='Test Customer',
                    created_by=self.user.id,
                    updated_by=self.user.id,
                )
            )

        self.assertFalse(Customer.objects.filter(name='Test Customer').exists())

    def test_execute_logs_exception_when_audit_fails(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)
        self.audit_gateway.log_customer_created.side_effect = AuditSaveFailed(
            'create', 'customer'
        )

        with patch('customer.application.create_customer.logger') as logger_mock:
            with self.assertRaises(CustomerAuditFailed):
                service.execute(
                    CreateCustomerInput(
                        name='Test Customer',
                        created_by=self.user.id,
                        updated_by=self.user.id,
                    )
                )

        logger_mock.info.assert_called_once_with('Starting customer creation')
        logger_mock.exception.assert_called_once()
        self.assertEqual(
            logger_mock.exception.call_args.args,
            ('Audit failure during customer creation customer_id=%s', 1),
        )

    def test_execute_logs_start_and_success(self):
        service = CreateCustomerService(self.repository, self.audit_gateway)

        with patch('customer.application.create_customer.logger') as logger_mock:
            output = service.execute(
                CreateCustomerInput(
                    name='Test Customer',
                    created_by=self.user.id,
                    updated_by=self.user.id,
                )
            )

        logger_mock.info.assert_any_call('Starting customer creation')
        logger_mock.info.assert_any_call(
            'Customer created successfully id=%s', output.customer_id
        )
