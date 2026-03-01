from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from customer.domain.exceptions.customer_exceptions import CustomerNotFound


class DetailCustomerViewTest(TestCase):
    def setUp(self):
        self.customer_id = 7
        self.url = reverse('customer:detail', args=[self.customer_id])

    def test_detail_customer_view_returns_status_code_200(self):
        with patch(
            'customer.views.detail_customer_view.DetailCustomerView.get_service'
        ) as get_service_mock:
            service_mock = Mock()
            service_mock.execute.return_value = SimpleNamespace(
                customer_id=self.customer_id,
                name='Alpha Customer',
                created_by=1,
                updated_by=1,
            )
            get_service_mock.return_value = service_mock

            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_detail_customer_view_returns_correct_template(self):
        with patch(
            'customer.views.detail_customer_view.DetailCustomerView.get_service'
        ) as get_service_mock:
            service_mock = Mock()
            service_mock.execute.return_value = SimpleNamespace(
                customer_id=self.customer_id,
                name='Alpha Customer',
                created_by=1,
                updated_by=1,
            )
            get_service_mock.return_value = service_mock

            response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'customer/detail_customer.html')

    @patch('customer.views.detail_customer_view.DetailCustomerView.get_service')
    def test_detail_customer_view_returns_customer_in_context(self, get_service_mock):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customer_id=self.customer_id,
            name='Alpha Customer',
            created_by=1,
            updated_by=1,
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        self.assertEqual(response.context['customer'].customer_id, self.customer_id)
        self.assertEqual(response.context['customer'].name, 'Alpha Customer')

    @patch('customer.views.detail_customer_view.DetailCustomerView.get_service')
    def test_detail_customer_view_renders_customer_details_in_html(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.return_value = SimpleNamespace(
            customer_id=self.customer_id,
            name='Alpha Customer',
            created_by=1,
            updated_by=1,
        )
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        self.assertContains(response, 'Informa')
        self.assertContains(response, f'ID: {self.customer_id}')
        self.assertContains(response, 'Nome: Alpha Customer')

    @patch('customer.views.detail_customer_view.DetailCustomerView.get_service')
    def test_detail_customer_view_returns_404_when_customer_is_not_found(
        self, get_service_mock
    ):
        service_mock = Mock()
        service_mock.execute.side_effect = CustomerNotFound(self.customer_id)
        get_service_mock.return_value = service_mock

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
