from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.create_customer import CreateCustomerService
from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerNameIsEmpty,
    CustomerNameIsTooShort,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestCreateCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.repository = DjangoCustomerRepository()

    def test_execute_creates_customer_and_returns_id(self):
        service = CreateCustomerService(self.repository)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)

        self.assertIsNotNone(output.customer_id)
        self.assertTrue(Customer.objects.filter(pk=output.customer_id).exists())

    def test_execute_uses_default_is_active_true(self):
        service = CreateCustomerService(self.repository)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertTrue(customer.is_active)

    def test_execute_creates_timestamp(self):
        service = CreateCustomerService(self.repository)
        input_dto = CreateCustomerInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)
        self.assertLessEqual(customer.created_at, customer.updated_at)

    def test_execute_raises_when_customer_name_already_exists(self):
        service = CreateCustomerService(self.repository)
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
        service = CreateCustomerService(self.repository)

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
