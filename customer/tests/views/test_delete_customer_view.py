from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from customer.application.soft_delete_customer import SoftDeleteCustomerService
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.views.delete_customer_view import DeleteCustomerView


class DeleteCustomerViewTest(TestCase):
    def setUp(self):
        self.customer_id = 7
        self.url = reverse('customer:delete', args=[self.customer_id])
        self.list_url = reverse('customer:list')
        self.user = get_user_model().objects.create_user(
            username='delete-view-user',
            password='testpassword',
        )

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

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_customer')
    def test_delete_customer_view_get_service_returns_service_instance(
        self, get_customer_mock
    ):
        get_customer_mock.return_value = SimpleNamespace(
            pk=self.customer_id,
            name='Alpha Customer',
        )
        response = self.client.get(self.url)

        self.assertIsInstance(
            response.context['view'].get_service(), SoftDeleteCustomerService
        )
        self.assertIsInstance(
            response.context['view'].get_service().repository,
            DjangoCustomerRepository,
        )

    @patch('customer.views.delete_customer_view.DjangoCustomerRepository.get_by_id')
    def test_delete_customer_view_get_customer_caches_repository_result(
        self, get_by_id_mock
    ):
        customer = SimpleNamespace(pk=self.customer_id, name='Alpha Customer')
        get_by_id_mock.return_value = customer

        response = self.client.get(self.url)
        view = response.context['view']

        first_customer = view.get_customer()
        second_customer = view.get_customer()

        self.assertIs(first_customer, customer)
        self.assertIs(second_customer, customer)
        get_by_id_mock.assert_called_once_with(self.customer_id)

    @patch('customer.views.delete_customer_view.DjangoCustomerRepository.get_by_id')
    def test_delete_customer_view_get_customer_raises_404_when_repository_returns_none(
        self, get_by_id_mock
    ):
        get_by_id_mock.return_value = None
        view = DeleteCustomerView()
        view.kwargs = {'pk': self.customer_id}

        with self.assertRaises(Http404):
            view.get_customer()

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_service')
    def test_delete_customer_view_soft_deletes_customer_and_redirects(
        self, get_service_mock
    ):
        self.client.force_login(self.user)
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customer_id=self.customer_id
        )
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url)

        self.assertRedirects(response, self.list_url)
        executed_input = service_mock.execute.call_args.args[0]
        self.assertEqual(executed_input.customer_id, self.customer_id)
        self.assertEqual(executed_input.updated_by, self.user.id)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            [message.message for message in messages],
            [f'Cliente {self.customer_id} excluído com sucesso.'],
        )

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_service')
    def test_delete_customer_view_returns_404_when_customer_is_not_found(
        self, get_service_mock
    ):
        self.client.force_login(self.user)
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerNotFound(self.customer_id)
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)

    @patch('customer.views.delete_customer_view.DeleteCustomerView.get_service')
    def test_delete_customer_view_requires_authenticated_user_for_post(
        self, get_service_mock
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['location'])
        get_service_mock.assert_not_called()
