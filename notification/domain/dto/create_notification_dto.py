from dataclasses import dataclass

from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience


@dataclass(frozen=True, slots=True)
class CreateNotificationInput:
    action: NotificationAction
    entity_type: str
    entity_id: int | None
    triggered_by: int
    audience: NotificationAudience


@dataclass(frozen=True, slots=True)
class CreateNotificationOutput:
    notification_id: int
