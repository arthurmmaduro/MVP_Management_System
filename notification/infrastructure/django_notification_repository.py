from __future__ import annotations

from django.db import IntegrityError

from notification.domain.exceptions.notification_exception import NotificationSaveFailed
from notification.domain.repository.notification_repository import (
    NotificationRepository,
)
from notification.models import Notification


class DjangoNotificationRepository(NotificationRepository):
    def save(self, notification: Notification) -> None:
        try:
            notification.save()
        except IntegrityError as exc:
            raise NotificationSaveFailed(
                notification.action, notification.entity_type
            ) from exc
