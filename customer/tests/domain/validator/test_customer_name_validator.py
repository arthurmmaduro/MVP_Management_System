from django.contrib.auth import get_user_model
from django.test import TestCase

from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.exceptions.customer_exceptions import CustomerAlreadyExists
from customer.domain.validator.customer_name_validator import CustomerNameValidator
from customer.domain.value_objects.customer_name import CustomerName
from customer.models import Customer


class TestCustomerNameValidator(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser_validator', password='testpassword'
        )

    def test_validate_returns_normalized_customer_name(self):
        input_dto = CreateCustomerInput(
            name='   Test   Customer   ',
            created_by=self.user.id,
            updated_by=self.user.id,
        )

        name = CustomerNameValidator.validate(input_dto)

        self.assertIsInstance(name, CustomerName)
        self.assertEqual(name.name, 'Test Customer')

    def test_validate_raises_when_name_is_not_unique(self):
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
            CustomerNameValidator.validate(input_dto)
