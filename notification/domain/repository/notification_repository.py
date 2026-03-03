from __future__ import annotations

from abc import ABC, abstractmethod

from notification.models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def save(self, notification: Notification) -> None:
        raise NotImplementedError
