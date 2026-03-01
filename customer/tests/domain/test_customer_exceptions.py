from django.test import SimpleTestCase

from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerDeleteFailed,
    CustomerNameIsEmpty,
    CustomerNameIsTooLong,
    CustomerNameIsTooShort,
    CustomerNotFound,
    CustomerSaveFailed,
)


class TestCustomerExceptions(SimpleTestCase):
    def test_customer_already_exists_sets_expected_message(self):
        exception = CustomerAlreadyExists('Acme')

        self.assertEqual(
            str(exception), 'Já existe um cliente cadastrado com o nome Acme'
        )
        self.assertEqual(
            exception.message, 'Já existe um cliente cadastrado com o nome Acme'
        )

    def test_customer_name_is_empty_sets_expected_message(self):
        exception = CustomerNameIsEmpty()

        self.assertEqual(str(exception), 'O nome do cliente não pode estar vazio')
        self.assertEqual(exception.message, 'O nome do cliente não pode estar vazio')

    def test_customer_name_is_too_long_sets_expected_message(self):
        exception = CustomerNameIsTooLong(100)

        self.assertEqual(
            str(exception), 'O nome do cliente não pode ter mais de 100 caracteres'
        )
        self.assertEqual(
            exception.message,
            'O nome do cliente não pode ter mais de 100 caracteres',
        )

    def test_customer_name_is_too_short_sets_expected_message(self):
        exception = CustomerNameIsTooShort(3)

        self.assertEqual(
            str(exception), 'O nome do cliente não pode ter menos de 3 caracteres'
        )
        self.assertEqual(
            exception.message,
            'O nome do cliente não pode ter menos de 3 caracteres',
        )

    def test_customer_save_failed_sets_expected_message(self):
        exception = CustomerSaveFailed('Acme')

        self.assertEqual(str(exception), 'Erro ao salvar o cliente: Acme')
        self.assertEqual(exception.message, 'Erro ao salvar o cliente: Acme')

    def test_customer_not_found_sets_expected_message(self):
        exception = CustomerNotFound(1)

        self.assertEqual(str(exception), 'Cliente não encontrado: 1')
        self.assertEqual(exception.message, 'Cliente não encontrado: 1')

    def test_customer_delete_failed_sets_expected_message(self):
        exception = CustomerDeleteFailed(1)

        self.assertEqual(str(exception), 'Erro ao deletar o cliente: 1')
        self.assertEqual(exception.message, 'Erro ao deletar o cliente: 1')
