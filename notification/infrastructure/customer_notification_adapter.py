from collections.abc import Mapping

from customer.domain.repository.customer_notification_gateway import (
    CustomerNotificationGateway,
)
from notification.application.create_notification import CreateNotificationService
from notification.domain.dto.create_notification_dto import CreateNotificationInput
from notification.domain.enums.notification_action import NotificationAction
from notification.domain.enums.notification_audience import NotificationAudience


class CustomerNotificationAdapter(CustomerNotificationGateway):
    def __init__(self, create_notification_service: CreateNotificationService) -> None:
        self._create_notification_service = create_notification_service

    def notify_customer_created(self, *, customer_id: int, triggered_by: int) -> None:
        self._create_notification_service.execute(
            CreateNotificationInput(
                action=NotificationAction.CREATE,
                entity_type='customer',
                entity_id=customer_id,
                triggered_by=triggered_by,
                audience=NotificationAudience.ALL,
                description='Cliente criado',
                metadata={},
            )
        )

    def notify_customer_updated(
        self, *, customer_id: int, triggered_by: int, metadata: Mapping[str, object]
    ) -> None:
        self._create_notification_service.execute(
            CreateNotificationInput(
                action=NotificationAction.UPDATE,
                entity_type='customer',
                entity_id=customer_id,
                triggered_by=triggered_by,
                audience=NotificationAudience.ALL,
                description='Cliente atualizado',
                metadata=metadata,
            )
        )

    def notify_customer_deleted(self, *, customer_id: int, triggered_by: int) -> None:
        self._create_notification_service.execute(
            CreateNotificationInput(
                action=NotificationAction.DELETE,
                entity_type='customer',
                entity_id=customer_id,
                triggered_by=triggered_by,
                audience=NotificationAudience.ALL,
                description='Cliente deletado',
                metadata={},
            )
        )
