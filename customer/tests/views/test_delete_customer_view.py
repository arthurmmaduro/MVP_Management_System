from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from customer.domain.exceptions.customer_exceptions import CustomerNotFound


class DeleteCustomerViewTest(TestCase):
    def setUp(self):
        self.customer_id = 7
        self.url = reverse('customer:delete', args=[self.customer_id])
        self.list_url = reverse('customer:list')

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_customer')
    def test_delete_customer_view_returns_status_code_200(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            pk=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_customer')
    def test_delete_customer_view_returns_correct_template(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            pk=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'customer/confirm_delete_customer.html')

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_customer')
    def test_delete_customer_view_returns_customer_in_context(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            pk=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.context['customer'].pk, self.customer_id)
        self.assertEqual(response.context['customer'].name, 'Alpha Customer')

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_customer')
    def test_delete_customer_view_renders_confirmation_in_html(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            pk=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertContains(response, 'Confirmar exclus')
        self.assertContains(response, 'Alpha Customer')
        self.assertContains(
            response, reverse('customer:detail', args=[self.customer_id])
        )

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_service')
    def test_delete_customer_view_soft_deletes_customer_and_redirects(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customer_id=self.customer_id
        )
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url)

        self.assertRedirects(response, self.list_url)
        executed_input = service_mock.execute.call_args.args[0]
        self.assertEqual(executed_input.customer_id, self.customer_id)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            [message.message for message in messages],
            [f'Cliente {self.customer_id} excluído com sucesso.'],
        )

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_service')
    def test_delete_customer_view_returns_404_when_customer_is_not_found(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerNotFound(self.customer_id)
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
