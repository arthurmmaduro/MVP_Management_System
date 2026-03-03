from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience
from notification.models import Notification


class TestNotificationModel(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            username='notification-user',
            password='notification-password',
        )

    def test_create_notification_successfully(self):
        notification = Notification.objects.create(
            action='create',
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
            audience='analyst',
        )

        self.assertEqual(notification.action, NotificationAction.CREATE.value)
        self.assertEqual(notification.entity_type, 'customer')
        self.assertEqual(notification.entity_id, 1)
        self.assertEqual(notification.triggered_by, self.user)
        self.assertEqual(notification.audience, NotificationAudience.ANALYST.value)
        self.assertIsNotNone(notification.created_at)

    def test_entity_id_can_be_null(self):
        notification = Notification.objects.create(
            action='create',
            entity_type='customer',
            entity_id=None,
            triggered_by=self.user,
            audience='analyst',
        )

        self.assertIsNone(notification.entity_id)

    def test_triggered_by_is_required(self):
        with self.assertRaises(IntegrityError):
            Notification.objects.create(
                action='create',
                entity_type='customer',
                entity_id=1,
                audience='analyst',
            )

    def test_string_representation(self):
        audit = Notification.objects.create(
            action=NotificationAction.UPDATE,
            entity_type='order',
            entity_id=7,
            triggered_by=self.user,
            audience=NotificationAudience.ANALYST,
        )

        self.assertEqual(str(audit), 'update order #7')
