from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.application.create_customer import CreateCustomerService
from customer.domain.dto.create_customer_dto import CustomerCreateInput
from customer.models import Customer


class TestCreateCustomerService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_execute_creates_customer_and_returns_id(self):
        service = CreateCustomerService()
        input_dto = CustomerCreateInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)

        self.assertIsNotNone(output.customer_id)
        self.assertTrue(Customer.objects.filter(pk=output.customer_id).exists())

    def test_execute_uses_default_is_active_true(self):
        service = CreateCustomerService()
        input_dto = CustomerCreateInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertTrue(customer.is_active)

    def test_execute_creates_timestamp(self):
        service = CreateCustomerService()
        input_dto = CustomerCreateInput(
            name='Test Customer', created_by=self.user.id, updated_by=self.user.id
        )
        output = service.execute(input_dto)
        customer = Customer.objects.get(id=output.customer_id)

        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)
        self.assertLessEqual(customer.created_at, customer.updated_at)
