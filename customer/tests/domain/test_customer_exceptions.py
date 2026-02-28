from django.test import SimpleTestCase

from customer.domain.exceptions.customer_exceptions import CustomerSaveFailed


class TestCustomerExceptions(SimpleTestCase):
    def test_customer_save_failed_sets_expected_message(self):
        exception = CustomerSaveFailed('Acme')

        self.assertEqual(str(exception), 'Erro ao salvar o cliente: Acme')
        self.assertEqual(exception.message, 'Erro ao salvar o cliente: Acme')
