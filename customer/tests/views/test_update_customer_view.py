from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from customer.application.update_customer import UpdateCustomerService
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerNotFound,
)
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.views.update_customer_view import UpdateCustomerView


class UpdateCustomerViewTest(TestCase):
    def setUp(self):
        self.customer_id = 7
        self.url = reverse('customer:update', args=[self.customer_id])
        self.detail_url = reverse('customer:detail', args=[self.customer_id])
        self.user = get_user_model().objects.create_user(
            username='update-view-user',
            password='testpassword',
        )

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    def test_update_customer_view_returns_status_code_200(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    def test_update_customer_view_returns_correct_template(self, get_customer_mock):
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'customer/form_customer.html')

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    def test_update_customer_view_sets_expected_context_and_initial_data(
        self, get_customer_mock
    ):
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.context['cancel_url'], self.detail_url)
        self.assertTrue(response.context['is_update'])
        self.assertEqual(response.context['customer'].id, self.customer_id)
        self.assertEqual(response.context['form'].initial['name'], 'Alpha Customer')

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    def test_update_customer_view_get_service_returns_service_instance(
        self, get_customer_mock
    ):
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.get(self.url)

        self.assertIsInstance(
            response.context['view'].get_service(), UpdateCustomerService
        )
        self.assertIsInstance(
            response.context['view'].get_service().repository,
            DjangoCustomerRepository,
        )

    @patch('customer.views.update_customer_view.DjangoCustomerRepository.get_by_id')
    def test_update_customer_view_get_customer_caches_repository_result(
        self, get_by_id_mock
    ):
        customer = SimpleNamespace(id=self.customer_id, name='Alpha Customer')
        get_by_id_mock.return_value = customer

        response = self.client.get(self.url)
        view = response.context['view']

        first_customer = view.get_customer()
        second_customer = view.get_customer()

        self.assertIs(first_customer, customer)
        self.assertIs(second_customer, customer)
        get_by_id_mock.assert_called_once_with(self.customer_id)

    @patch('customer.views.update_customer_view.DjangoCustomerRepository.get_by_id')
    def test_update_customer_view_get_customer_raises_404_when_repository_returns_none(
        self, get_by_id_mock
    ):
        get_by_id_mock.return_value = None
        view = UpdateCustomerView()
        view.kwargs = {'pk': self.customer_id}

        with self.assertRaises(Http404):
            view.get_customer()

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    @patch('customer.views.update_customer_view.UpdateCustomerView.get_service')
    def test_update_customer_view_updates_customer_and_redirects(
        self, get_service_mock, get_customer_mock
    ):
        self.client.force_login(self.user)
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customer_id=self.customer_id
        )
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url, data={'name': 'Updated Customer'})

        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        executed_input = service_mock.execute.call_args.args[0]
        self.assertEqual(executed_input.customer_id, self.customer_id)
        self.assertEqual(executed_input.name, 'Updated Customer')
        self.assertEqual(executed_input.updated_by, self.user.id)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            [message.message for message in messages],
            ['Cliente Updated Customer atualizado com sucesso.'],
        )

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    @patch('customer.views.update_customer_view.UpdateCustomerView.get_service')
    def test_update_customer_view_returns_name_error_when_service_raises_domain_error(
        self, get_service_mock, get_customer_mock
    ):
        self.client.force_login(self.user)
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerAlreadyExists('Updated Customer')
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url, data={'name': 'Updated Customer'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertIn('Updated Customer', response.context['form'].errors['name'][0])

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    @patch('customer.views.update_customer_view.UpdateCustomerView.get_service')
    def test_update_customer_view_returns_form_error_when_name_is_missing(
        self, get_service_mock, get_customer_mock
    ):
        self.client.force_login(self.user)
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )

        response = self.client.post(self.url, data={'name': ''})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertTrue(response.context['form'].errors['name'])
        self.assertIn('obrigat', response.context['form'].errors['name'][0].lower())
        get_service_mock.return_value.execute.assert_not_called()

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    def test_update_customer_view_returns_404_when_customer_is_not_found_on_get(
        self, get_customer_mock
    ):
        get_customer_mock.side_effect = Http404(
            f'Cliente não encontrado: {self.customer_id}'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    @patch('customer.views.update_customer_view.UpdateCustomerView.get_service')
    def test_update_customer_view_returns_404_when_service_reports_missing_customer(
        self, get_service_mock, get_customer_mock
    ):
        self.client.force_login(self.user)
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerNotFound(self.customer_id)
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url, data={'name': 'Updated Customer'})

        self.assertEqual(response.status_code, 404)

    @patch('customer.views.update_customer_view.UpdateCustomerView.get_customer')
    @patch('customer.views.update_customer_view.UpdateCustomerView.get_service')
    def test_update_customer_view_requires_authenticated_user(
        self, get_service_mock, get_customer_mock
    ):
        get_customer_mock.return_value = SimpleNamespace(
            id=self.customer_id,
            name='Alpha Customer',
        )
        response = self.client.post(self.url, data={'name': 'Updated Customer'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('__all__', response.context['form'].errors)
        self.assertIn(
            'autenticado', response.context['form'].errors['__all__'][0].lower()
        )
        get_service_mock.assert_not_called()
