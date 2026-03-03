from django.contrib.auth import get_user_model
from django.test import TestCase

from notification.application.create_notification import CreateNotificationService
from notification.domain.dto.create_notification_dto import CreateNotificationInput
from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience
from notification.domain.exceptions.notification_exception import (
    EntityTypeEmpty,
    NotificationSaveFailed,
)
from notification.domain.repository.notification_repository import (
    NotificationRepository,
)
from notification.infrastructure.django_notification_repository import (
    DjangoNotificationRepository,
)
from notification.models import Notification


class TestNotificationService(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.repository = DjangoNotificationRepository()

    def test_execute_creates_notification_and_returns_id(self):
        service = CreateNotificationService(self.repository)
        input_dto = CreateNotificationInput(
            action=NotificationAction.CREATE,
            entity_type='customer',
            entity_id=1,
            triggered_by=self.user.id,
            audience=NotificationAudience.MANAGER,
            description='Cliente criado',
            metadata={'after': {'name': 'Test Customer'}},
        )

        output = service.execute(input_dto)
        notification = Notification.objects.get(pk=output.notification_id)

        self.assertIsNotNone(output.notification_id)
        self.assertEqual(notification.action, NotificationAction.CREATE.value)
        self.assertEqual(notification.entity_type, 'customer')
        self.assertEqual(notification.entity_id, 1)
        self.assertEqual(notification.triggered_by_id, self.user.id)
        self.assertEqual(notification.audience, NotificationAudience.MANAGER.value)
        self.assertEqual(notification.description, 'Cliente criado')
        self.assertEqual(notification.metadata, {'after': {'name': 'Test Customer'}})
        self.assertIsNotNone(notification.created_at)

    def test_execute_allows_entity_id_to_be_null(self):
        service = CreateNotificationService(self.repository)
        input_dto = CreateNotificationInput(
            action=NotificationAction.CREATE,
            entity_type='customer',
            entity_id=None,
            triggered_by=self.user.id,
            audience=NotificationAudience.MANAGER,
            description='Cliente criado sem entity_id',
            metadata={},
        )
        output = service.execute(input_dto)
        notification = Notification.objects.get(pk=output.notification_id)

        self.assertIsNone(notification.entity_id)
        self.assertEqual(notification.audience, NotificationAudience.MANAGER.value)
        self.assertEqual(notification.description, 'Cliente criado sem entity_id')
        self.assertEqual(notification.metadata, {})

    def test_execute_raises_when_entity_type_is_blank(self):
        service = CreateNotificationService(self.repository)

        with self.assertRaises(EntityTypeEmpty):
            service.execute(
                CreateNotificationInput(
                    action=NotificationAction.CREATE,
                    entity_type='   ',
                    entity_id=1,
                    triggered_by=self.user.id,
                    audience=NotificationAudience.MANAGER,
                    description='Descricao irrelevante',
                    metadata={},
                )
            )

    def test_execute_raises_when_repository_save_fails(self):
        class FailingNotificationRepository(NotificationRepository):
            def save(self, notification: Notification) -> None:
                raise NotificationSaveFailed(
                    notification.action, notification.entity_type
                )

        service = CreateNotificationService(FailingNotificationRepository())

        with self.assertRaises(NotificationSaveFailed):
            service.execute(
                CreateNotificationInput(
                    action=NotificationAction.UPDATE,
                    entity_type='customer',
                    entity_id=1,
                    triggered_by=self.user.id,
                    audience=NotificationAudience.ANALYST,
                    description='Cliente atualizado',
                    metadata={'changed_fields': ['name']},
                )
            )
