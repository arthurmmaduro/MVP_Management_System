from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
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
            description='Cliente criado',
            metadata={'after': {'name': 'Test Customer'}},
        )

        self.assertEqual(notification.action, NotificationAction.CREATE.value)
        self.assertEqual(notification.entity_type, 'customer')
        self.assertEqual(notification.entity_id, 1)
        self.assertEqual(notification.triggered_by, self.user)
        self.assertEqual(notification.audience, NotificationAudience.ANALYST.value)
        self.assertEqual(notification.description, 'Cliente criado')
        self.assertEqual(notification.metadata, {'after': {'name': 'Test Customer'}})
        self.assertIsNotNone(notification.created_at)

    def test_entity_id_can_be_null(self):
        notification = Notification.objects.create(
            action='create',
            entity_type='customer',
            entity_id=None,
            triggered_by=self.user,
            audience='analyst',
            description='Cliente criado sem entidade persistida',
            metadata={},
        )

        self.assertIsNone(notification.entity_id)

    def test_metadata_defaults_to_empty_dict(self):
        notification = Notification.objects.create(
            action='create',
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
            audience='analyst',
            description='Cliente criado',
        )

        self.assertEqual(notification.metadata, {})

    def test_description_allows_empty_string(self):
        notification = Notification.objects.create(
            action='create',
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
            audience='analyst',
            description='',
            metadata={},
        )

        self.assertEqual(notification.description, '')

    def test_triggered_by_is_required(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Notification.objects.create(
                    action='create',
                    entity_type='customer',
                    entity_id=1,
                    audience='analyst',
                )

    def test_action_is_required(self):
        notification = Notification(
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
            audience='analyst',
        )

        with self.assertRaises(ValidationError):
            notification.full_clean()

    def test_audience_is_required(self):
        notification = Notification(
            action='create',
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
        )

        with self.assertRaises(ValidationError):
            notification.full_clean()

    def test_string_representation(self):
        notification = Notification.objects.create(
            action=NotificationAction.UPDATE,
            entity_type='order',
            entity_id=7,
            triggered_by=self.user,
            audience=NotificationAudience.ANALYST,
            description='Pedido atualizado',
            metadata={'changed_fields': ['status']},
        )

        self.assertEqual(str(notification), 'update order #7')

    def test_string_representation_without_entity_id(self):
        notification = Notification.objects.create(
            action=NotificationAction.CREATE,
            entity_type='order',
            entity_id=None,
            triggered_by=self.user,
            audience=NotificationAudience.MANAGER,
            description='Pedido criado',
            metadata={'after': {'status': 'open'}},
        )

        self.assertEqual(str(notification), 'create order')

    def test_triggered_by_delete_is_protected(self):
        Notification.objects.create(
            action=NotificationAction.CREATE,
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user,
            audience=NotificationAudience.SUPPORT,
            description='Cliente criado',
            metadata={},
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.user.delete()
