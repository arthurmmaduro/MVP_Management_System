from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.test import TestCase

from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerDeleteFailed,
    CustomerSaveFailed,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestDjangoCustomerRepository(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_repository', password='testpassword'
        )
        self.repository = DjangoCustomerRepository()

    def test_save_raises_customer_save_failed_when_integrity_error_is_not_duplicate_name(  # noqa: E501
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
                filter_mock.return_value.exclude.return_value.exists.return_value = (
                    False
                )

                with self.assertRaises(CustomerSaveFailed) as context:
                    self.repository.save(customer)

        self.assertEqual(
            str(context.exception), 'Erro ao salvar o cliente: Repository Customer'
        )

    def test_save_raises_customer_already_exists_when_active_name_is_duplicated(self):
        customer = Customer(
            name='Duplicated Customer',
            created_by=self.user,
            updated_by=self.user,
        )

        with patch.object(customer, 'save', side_effect=IntegrityError('boom')):
            with patch(
                'customer.infrastructure.django_customer_repository.Customer.objects.filter'
            ) as filter_mock:
                filter_mock.return_value.exclude.return_value.exists.return_value = True

                with self.assertRaises(CustomerAlreadyExists) as context:
                    self.repository.save(customer)

        self.assertEqual(
            str(context.exception),
            str(CustomerAlreadyExists('Duplicated Customer')),
        )

    def test_soft_delete_marks_customer_as_inactive(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by=self.user,
            updated_by=self.user,
        )
        other_user = get_user_model().objects.create_user(
            username='testuser_repository_other', password='testpassword'
        )

        self.repository.soft_delete(customer.id, updated_by=other_user.id)

        customer.refresh_from_db()

        self.assertFalse(customer.is_active)
        self.assertEqual(customer.updated_by_id, other_user.id)

    def test_soft_delete_raises_customer_delete_failed_on_database_error(self):
        customer = Customer.objects.create(
            name='Customer To Delete',
            created_by=self.user,
            updated_by=self.user,
        )

        with patch.object(Customer, 'save', side_effect=DatabaseError('boom')):
            with self.assertRaises(CustomerDeleteFailed) as context:
                self.repository.soft_delete(
                    customer_id=customer.id,
                    updated_by=self.user.id,
                )

        self.assertEqual(
            str(context.exception),
            f'Erro ao deletar o cliente: {customer.id}',
        )

    def test_list_active_returns_only_active_customers_ordered_by_name(self):
        alpha_customer = Customer.objects.create(
            name='Alpha Customer',
            created_by=self.user,
            updated_by=self.user,
        )
        Customer.all_objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by=self.user,
            updated_by=self.user,
        )
        zulu_customer = Customer.objects.create(
            name='Zulu Customer',
            created_by=self.user,
            updated_by=self.user,
        )

        customers = self.repository.list_active()

        self.assertEqual(customers, [alpha_customer, zulu_customer])

    def test_list_active_returns_empty_list_when_there_are_no_active_customers(self):
        Customer.all_objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by=self.user,
            updated_by=self.user,
        )

        customers = self.repository.list_active()

        self.assertEqual(customers, [])

    def test_list_active_filters_customers_by_search(self):
        alpha_customer = Customer.objects.create(
            name='Alpha Customer',
            created_by=self.user,
            updated_by=self.user,
        )
        Customer.objects.create(
            name='Zulu Customer',
            created_by=self.user,
            updated_by=self.user,
        )
        Customer.all_objects.create(
            name='Inactive Alpha Customer',
            is_active=False,
            created_by=self.user,
            updated_by=self.user,
        )

        customers = self.repository.list_active(search='Alpha')

        self.assertEqual(customers, [alpha_customer])
