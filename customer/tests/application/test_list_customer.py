from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.list_customer import ListCustomerService
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class TestListCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_list_customer',
            password='testpassword',
        )
        self.repository = DjangoCustomerRepository()

    def test_execute_returns_active_customers_mapped_and_ordered(self):
        alpha_customer = Customer.objects.create(
            name='Alpha Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        Customer.all_objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        zulu_customer = Customer.objects.create(
            name='Zulu Customer',
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = ListCustomerService(self.repository)

        output = service.execute()

        self.assertEqual(
            output.customers,
            [
                type(output.customers[0])(
                    customer_id=alpha_customer.id, name='Alpha Customer'
                ),
                type(output.customers[0])(
                    customer_id=zulu_customer.id, name='Zulu Customer'
                ),
            ],
        )

    def test_execute_returns_empty_list_when_there_are_no_active_customers(self):
        Customer.all_objects.create(
            name='Inactive Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = ListCustomerService(self.repository)

        output = service.execute()

        self.assertEqual(output.customers, [])

    def test_execute_filters_active_customers_by_search(self):
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
        Customer.all_objects.create(
            name='Inactive Alpha Customer',
            is_active=False,
            created_by_id=self.user.id,
            updated_by_id=self.user.id,
        )
        service = ListCustomerService(self.repository)

        output = service.execute(search='Alpha')

        self.assertEqual(len(output.customers), 1)
        self.assertEqual(output.customers[0].name, 'Alpha Customer')
