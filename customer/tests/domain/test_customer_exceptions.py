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

        self.assertEqual(str(exception), exception.message)

    def test_customer_name_is_empty_sets_expected_message(self):
        exception = CustomerNameIsEmpty()

        self.assertEqual(str(exception), exception.message)

    def test_customer_name_is_too_long_sets_expected_message(self):
        exception = CustomerNameIsTooLong(100)

        self.assertEqual(str(exception), exception.message)

    def test_customer_name_is_too_short_sets_expected_message(self):
        exception = CustomerNameIsTooShort(3)

        self.assertEqual(str(exception), exception.message)

    def test_customer_save_failed_sets_expected_message(self):
        exception = CustomerSaveFailed('Acme')

        self.assertEqual(str(exception), 'Erro ao salvar o cliente: Acme')
        self.assertEqual(exception.message, 'Erro ao salvar o cliente: Acme')

    def test_customer_not_found_sets_expected_message(self):
        exception = CustomerNotFound(1)

        self.assertEqual(str(exception), exception.message)

    def test_customer_delete_failed_sets_expected_message(self):
        exception = CustomerDeleteFailed(1)

        self.assertEqual(str(exception), exception.message)
