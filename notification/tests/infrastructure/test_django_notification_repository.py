from unittest.mock import Mock

from django.db import IntegrityError
from django.test import SimpleTestCase

from notification.domain.exceptions.notification_exception import (
    NotificationSaveFailed,
)
from notification.infrastructure.django_notification_repository import (
    DjangoNotificationRepository,
)


class TestDjangoNotificationRepository(SimpleTestCase):
    def test_save_calls_model_save_successfully(self):
        repository = DjangoNotificationRepository()
        notification = Mock()

        repository.save(notification)

        notification.save.assert_called_once_with()

    def test_save_raises_notification_save_failed_when_model_save_raises_integrity_error(  # noqa: E501
        self,
    ):
        repository = DjangoNotificationRepository()
        notification = Mock()
        notification.action = 'create'
        notification.entity_type = 'customer'
        notification.save.side_effect = IntegrityError()

        with self.assertRaises(NotificationSaveFailed):
            repository.save(notification)
