from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse


class ListCustomerViewTest(TestCase):
    def setUp(self):
        self.url = reverse('customer:list')

    def test_list_customer_view_returns_status_code_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_customer_view_returns_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'customer/list_customer.html')

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_returns_customers(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=1, name='Alpha Customer'),
                SimpleNamespace(customer_id=2, name='Zulu Customer'),
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        service_mock.execute.assert_called_once_with(search='')
        self.assertEqual(len(response.context['customers']), 2)
        self.assertEqual(response.context['customers'][0].name, 'Alpha Customer')
        self.assertEqual(response.context['customers'][1].name, 'Zulu Customer')
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertFalse(response.context['is_paginated'])

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_shows_empty_state_when_there_are_no_customers(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(customers=[])
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        service_mock.execute.assert_called_once_with(search='')
        self.assertEqual(response.context['customers'], [])
        self.assertContains(response, 'Nenhum cliente cadastrado')
        self.assertContains(response, 'Cadastre o seu primeiro cliente')
        self.assertFalse(response.context['is_paginated'])

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_shows_empty_search_state_when_no_results_are_found(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(customers=[])
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url, {'search': 'Alpha'})

        service_mock.execute.assert_called_once_with(search='Alpha')
        self.assertContains(response, 'Nenhum cliente encontrado')
        self.assertContains(
            response,
            'Nenhum cliente corresponde à busca por "Alpha".',
            html=False,
        )
        self.assertNotContains(response, 'Nenhum cliente cadastrado')

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_renders_customer_names_in_html(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=1, name='Alpha Customer'),
                SimpleNamespace(customer_id=2, name='Zulu Customer'),
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        self.assertContains(response, 'Alpha Customer')
        self.assertContains(response, 'Zulu Customer')
        self.assertContains(response, '<table>', html=False)

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_renders_customers_in_order(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=2, name='Alpha Customer'),
                SimpleNamespace(customer_id=1, name='Zulu Customer'),
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        content = response.content.decode()
        alpha_index = content.index('Alpha Customer')
        zulu_index = content.index('Zulu Customer')

        self.assertLess(alpha_index, zulu_index)

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_paginates_customer_list(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=index, name=f'Customer {index}')
                for index in range(1, 13)
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        self.assertEqual(len(response.context['customers']), 10)
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertTrue(response.context['is_paginated'])
        self.assertContains(response, 'Página 1 de 2')
        self.assertContains(response, '?page=2')
        self.assertContains(response, 'Customer 1')
        self.assertNotContains(response, 'Customer 11')

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_returns_requested_page(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=index, name=f'Customer {index}')
                for index in range(1, 13)
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url, {'page': 2})

        self.assertEqual(len(response.context['customers']), 2)
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertTrue(response.context['is_paginated'])
        self.assertContains(response, 'Página 2 de 2')
        self.assertContains(response, 'Customer 11')
        self.assertContains(response, 'Customer 12')
        self.assertNotContains(response, 'href="/customers/1/"', html=False)

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_passes_search_to_service_and_context(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[SimpleNamespace(customer_id=1, name='Alpha Customer')]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url, {'search': ' Alpha '})

        service_mock.execute.assert_called_once_with(search='Alpha')
        self.assertEqual(response.context['search'], 'Alpha')
        self.assertContains(response, 'value="Alpha"', html=False)

    @patch('customer.views.list_customer_view.ListCustomerView.get_service')
    def test_list_customer_view_preserves_search_in_pagination_links(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customers=[
                SimpleNamespace(customer_id=index, name=f'Customer {index}')
                for index in range(1, 13)
            ]
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url, {'search': 'Alpha'})

        self.assertContains(response, '?page=2&amp;search=Alpha', html=False)
