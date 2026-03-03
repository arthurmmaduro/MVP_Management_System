from django.contrib.auth import get_user_model
from django.test import TestCase

from notification.infrastructure.django_notification_repository import (
    DjangoNotificationRepository,
)


class TestNotificationService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.respository = DjangoNotificationRepository()

    def test_execute_creates_notification_and_returns_id(self):
        pass
