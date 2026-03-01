from django.test import SimpleTestCase

from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerNameIsTooShort,
)
from customer.forms.customer_forms import CreateCustomerForm, UpdateCustomerForm


class TestCreateCustomerForm(SimpleTestCase):
    def test_to_dto_returns_create_customer_input(self):
        form = CreateCustomerForm(data={'name': 'Test Customer'})
        self.assertTrue(form.is_valid())

        dto = form.to_dto(created_by=10)

        self.assertEqual(
            dto,
            CreateCustomerInput(
                name='Test Customer',
                created_by=10,
                updated_by=10,
            ),
        )

    def test_apply_domain_error_adds_name_error_for_domain_exception(self):
        form = CreateCustomerForm(data={'name': 'ab'})
        form.is_valid()

        form.apply_domain_error(CustomerNameIsTooShort(3))

        self.assertEqual(
            form.errors['name'],
            ['O nome do cliente não pode ter menos de 3 caracteres'],
        )
        self.assertNotIn('__all__', form.errors)

    def test_apply_domain_error_adds_non_field_error_for_generic_exception(self):
        form = CreateCustomerForm(data={'name': 'Test Customer'})
        form.is_valid()

        form.apply_domain_error(Exception('boom'))

        self.assertEqual(
            form.non_field_errors(),
            ['Não foi possível processar a requisição.'],
        )


class TestUpdateCustomerForm(SimpleTestCase):
    def test_to_dto_returns_update_customer_input(self):
        form = UpdateCustomerForm(data={'name': 'Updated Customer'})
        self.assertTrue(form.is_valid())

        dto = form.to_dto(customer_id=7, updated_by=11)

        self.assertEqual(
            dto,
            UpdateCustomerInput(
                customer_id=7,
                name='Updated Customer',
                updated_by=11,
            ),
        )

    def test_apply_domain_error_adds_name_error_without_generic_error(self):
        form = UpdateCustomerForm(data={'name': 'Duplicated Customer'})
        form.is_valid()

        form.apply_domain_error(CustomerAlreadyExists('Duplicated Customer'))

        self.assertEqual(
            form.errors['name'],
            ['Já existe um cliente cadastrado com o nome Duplicated Customer'],
        )
        self.assertNotIn('__all__', form.errors)
