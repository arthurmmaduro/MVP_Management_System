from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from customer.application.create_customer import CreateCustomerService
from customer.domain.exceptions.customer_exceptions import CustomerAlreadyExists
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository


class CreateCustomerViewTest(TestCase):
    def setUp(self):
        self.url = reverse('customer:create')
        self.list_url = reverse('customer:list')
        self.user = get_user_model().objects.create_user(
            username='create-view-user',
            password='testpassword',
        )

    def test_create_customer_view_returns_status_code_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_create_customer_view_returns_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'customer/form_customer.html')

    def test_create_customer_view_sets_expected_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['cancel_url'], self.list_url)
        self.assertFalse(response.context['is_update'])

    def test_create_customer_view_get_service_returns_service_instance(self):
        response = self.client.get(self.url)

        self.assertIsInstance(
            response.context['view'].get_service(), CreateCustomerService
        )
        self.assertIsInstance(
            response.context['view'].get_service().repository,
            DjangoCustomerRepository,
        )

    @patch('customer.views.create_customer_view.CreateCustomerView.get_service')
    def test_create_customer_view_creates_customer_and_redirects(
        self, get_service_mock
    ):
        self.client.force_login(self.user)
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(customer_id=1)
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url, data={'name': 'Alpha Customer'})

        self.assertRedirects(response, self.list_url)
        executed_input = service_mock.execute.call_args.args[0]
        self.assertEqual(executed_input.name, 'Alpha Customer')
        self.assertEqual(executed_input.created_by, self.user.id)
        self.assertEqual(executed_input.updated_by, self.user.id)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            [message.message for message in messages],
            ['Cliente Alpha Customer salvo com sucesso.'],
        )

    @patch('customer.views.create_customer_view.CreateCustomerView.get_service')
    def test_create_customer_view_returns_name_error_when_service_raises_domain_error(
        self, get_service_mock
    ):
        self.client.force_login(self.user)
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerAlreadyExists('Alpha Customer')
        get_service_mock.return_value = service_mock

        response = self.client.post(self.url, data={'name': 'Alpha Customer'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('name', response.context['form'].errors)
        self.assertIn('Alpha Customer', response.context['form'].errors['name'][0])

    @patch('customer.views.create_customer_view.CreateCustomerView.get_service')
    def test_create_customer_view_returns_form_error_when_name_is_missing(
        self, get_service_mock
    ):
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={'name': ''})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertTrue(response.context['form'].errors['name'])
        self.assertIn('obrigat', response.context['form'].errors['name'][0].lower())
        get_service_mock.return_value.execute.assert_not_called()

    @patch('customer.views.create_customer_view.CreateCustomerView.get_service')
    def test_create_customer_view_requires_authenticated_user(self, get_service_mock):
        response = self.client.post(self.url, data={'name': 'Alpha Customer'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('__all__', response.context['form'].errors)
        self.assertIn(
            'autenticado', response.context['form'].errors['__all__'][0].lower()
        )
        get_service_mock.assert_not_called()
