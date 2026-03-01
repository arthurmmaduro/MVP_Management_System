from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from customer.models import Customer


class CustomerLifecycleViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='customer-lifecycle-user',
            password='testpassword',
        )
        self.create_url = reverse('customer:create')
        self.list_url = reverse('customer:list')

    def test_customer_lifecycle_from_create_to_soft_delete(self):
        self.client.force_login(self.user)

        create_response = self.client.post(
            self.create_url,
            data={'name': 'Lifecycle Customer'},
        )

        self.assertRedirects(create_response, self.list_url)
        customer = Customer.objects.get(name='Lifecycle Customer')

        list_response = self.client.get(self.list_url)

        self.assertContains(list_response, 'Lifecycle Customer')
        self.assertContains(
            list_response,
            reverse('customer:detail', args=[customer.id]),
        )

        detail_url = reverse('customer:detail', args=[customer.id])
        detail_response = self.client.get(detail_url)

        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, f'ID: {customer.id}')
        self.assertContains(detail_response, 'Nome: Lifecycle Customer')

        update_url = reverse('customer:update', args=[customer.id])
        update_response = self.client.post(
            update_url,
            data={'name': 'Lifecycle Customer Updated'},
        )

        self.assertRedirects(
            update_response,
            reverse('customer:detail', args=[customer.id]),
            fetch_redirect_response=False,
        )
        customer.refresh_from_db()
        self.assertEqual(customer.name, 'Lifecycle Customer Updated')
        self.assertEqual(customer.updated_by_id, self.user.id)

        updated_detail_response = self.client.get(detail_url)

        self.assertContains(updated_detail_response, 'Nome: Lifecycle Customer Updated')

        delete_url = reverse('customer:delete', args=[customer.id])
        delete_response = self.client.post(delete_url)

        self.assertRedirects(delete_response, self.list_url)
        customer.refresh_from_db()
        self.assertFalse(customer.is_active)
        self.assertEqual(customer.updated_by_id, self.user.id)
        self.assertFalse(Customer.objects.filter(id=customer.id).exists())

        list_after_delete_response = self.client.get(self.list_url)

        self.assertNotContains(list_after_delete_response, 'Lifecycle Customer Updated')

        detail_after_delete_response = self.client.get(detail_url)

        self.assertEqual(detail_after_delete_response.status_code, 404)
