from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.update_customer import UpdateCustomerService
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerNameIsEmpty,
    CustomerNameIsTooShort,
    CustomerNotFound,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


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

    def test_execute_updates_customer_and_returns_same_id(self):
        customer = Customer.objects.create(
            name='Old Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = UpdateCustomerService(self.repository)

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

    def test_execute_raises_when_customer_not_found(self):
        service = UpdateCustomerService(self.repository)

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
        service = UpdateCustomerService(self.repository)

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
        service = UpdateCustomerService(self.repository)

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
        service = UpdateCustomerService(self.repository)

        with self.assertRaises(CustomerNameIsEmpty):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='   ',
                    updated_by=self.user.id,
                )
            )

        with self.assertRaises(CustomerNameIsTooShort):
            service.execute(
                UpdateCustomerInput(
                    customer_id=customer.id,
                    name='ab',
                    updated_by=self.user.id,
                )
            )
